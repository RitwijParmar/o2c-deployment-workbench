from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date
from typing import Any


def _usd(amount: float, currency: str, fx: dict[str, float]) -> float:
    return round(float(amount) * float(fx[currency]), 2)


def _tolerance(amount_usd: float, config: dict[str, Any]) -> float:
    return max(float(config["amount_tolerance_absolute_usd"]), abs(amount_usd) * float(config["amount_tolerance_percent"]))


def _refs_for(payment: dict[str, Any], remittances: dict[str, list[dict[str, Any]]]) -> list[str]:
    refs: list[str] = []
    for remittance in remittances.get(payment["payment_id"], []):
        raw = remittance.get("invoice_refs", "")
        for delimiter in ("|", ";", ","):
            raw = raw.replace(delimiter, "|")
        refs.extend(ref.strip() for ref in raw.split("|") if ref.strip())
    if not refs and payment.get("reference", "").upper().startswith("INV-"):
        refs.append(payment["reference"].strip())
    return list(dict.fromkeys(refs))


def run_matching(canonical: dict[str, list[dict[str, Any]]], config: dict[str, Any], mode: str) -> dict[str, Any]:
    if mode not in {"baseline", "future"}:
        raise ValueError("mode must be baseline or future")
    fx = config["fx_to_usd"]
    rules = config["matching"]
    invoices = deepcopy(canonical["invoices"])
    by_number = {row["invoice_number"]: row for row in invoices}
    by_customer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for invoice in invoices:
        invoice["remaining_usd"] = _usd(invoice["open_amount"], invoice["currency"], fx)
        by_customer[invoice["customer_id"]].append(invoice)
    remittances: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in canonical["remittances"]:
        remittances[row["payment_id"]].append(row)
    deductions_by_payment: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in canonical["deductions"]:
        deductions_by_payment[row.get("payment_id", "")].append(row)

    bank_counts = Counter(row["bank_txn_id"] for row in canonical["payments"] if row.get("bank_txn_id"))
    seen_banks: set[str] = set()
    matches: list[dict[str, Any]] = []
    allocations: list[dict[str, Any]] = []

    for payment in sorted(canonical["payments"], key=lambda row: (row["payment_date"], row["payment_id"])):
        payment_usd = _usd(payment["amount"], payment["currency"], fx)
        result = {
            "payment_id": payment["payment_id"],
            "customer_id": payment["customer_id"],
            "benchmark_case": payment.get("benchmark_case", ""),
            "payment_amount_usd": payment_usd,
            "matched_invoice_ids": "",
            "applied_amount_usd": 0.0,
            "residual_amount_usd": payment_usd,
            "status": "MANUAL_REVIEW",
            "match_method": "UNMATCHED",
            "confidence": 0.0,
            "exception_code": "UNMATCHED_CASH",
            "reason": "No deterministic match found",
            "is_duplicate_record": False,
        }
        bank_ref = payment.get("bank_txn_id", "")
        if bank_ref and bank_counts[bank_ref] > 1 and bank_ref in seen_banks:
            result.update({"status": "MANUAL_REVIEW", "match_method": "DUPLICATE_DETECTED", "exception_code": "DUPLICATE_PAYMENT", "reason": "Repeated bank transaction identifier", "residual_amount_usd": 0.0, "is_duplicate_record": True})
            matches.append(result)
            continue
        if bank_ref:
            seen_banks.add(bank_ref)

        refs = _refs_for(payment, remittances)
        candidates = [by_number[ref] for ref in refs if ref in by_number and by_number[ref]["customer_id"] == payment["customer_id"]]

        if mode == "baseline":
            if len(candidates) == 1:
                invoice = candidates[0]
                raw_equal = payment["currency"] == invoice["currency"] and abs(float(payment["amount"]) - float(invoice["open_amount"])) < 0.005
                if raw_equal and invoice["remaining_usd"] > 0:
                    applied = min(payment_usd, invoice["remaining_usd"])
                    invoice["remaining_usd"] -= applied
                    result.update({"matched_invoice_ids": invoice["invoice_id"], "applied_amount_usd": applied, "residual_amount_usd": payment_usd - applied, "status": "AUTO_MATCHED", "match_method": "EXACT_REFERENCE_AMOUNT", "confidence": 1.0, "exception_code": "", "reason": "Exact invoice reference, currency, and amount"})
                    allocations.append({"payment_id": payment["payment_id"], "invoice_id": invoice["invoice_id"], "applied_amount_usd": applied, "method": result["match_method"]})
            matches.append(result)
            continue

        if not candidates and rules.get("allow_customer_amount_inference", False):
            amount_candidates = []
            for invoice in by_customer[payment["customer_id"]]:
                if invoice["remaining_usd"] <= 0:
                    continue
                if abs(invoice["remaining_usd"] - payment_usd) <= _tolerance(invoice["remaining_usd"], rules):
                    amount_candidates.append(invoice)
            if len(amount_candidates) == 1:
                candidates = amount_candidates
                inferred = True
            else:
                inferred = False
        else:
            inferred = False

        if candidates:
            open_total = sum(max(0.0, row["remaining_usd"]) for row in candidates)
            deductions_usd = sum(_usd(row["amount"], "USD", fx) for row in deductions_by_payment.get(payment["payment_id"], []) if row.get("status") == "VALIDATED")
            effective_payment = payment_usd + deductions_usd
            tolerance = _tolerance(open_total, rules)
            method = "AMOUNT_INFERENCE" if inferred else ("ONE_TO_MANY_REMITTANCE" if len(candidates) > 1 else "REFERENCE")
            can_auto = False
            exception_code = ""
            reason = ""
            if deductions_usd and deductions_usd <= float(rules["deduction_auto_clear_limit_usd"]) and abs(effective_payment - open_total) <= tolerance:
                can_auto, method, reason = True, "DEDUCTION_SUPPORTED_SHORT_PAY", "Validated deduction plus payment clears referenced invoice"
            elif abs(payment_usd - open_total) <= tolerance:
                can_auto, reason = True, "Payment falls within configured amount tolerance"
            elif payment_usd < open_total and len(candidates) == 1 and payment_usd / max(open_total, 0.01) >= float(rules["min_partial_payment_ratio"]):
                can_auto, method, reason = True, "PARTIAL_REFERENCE", "Referenced partial payment exceeds configured minimum ratio"
            elif payment_usd > open_total and rules.get("overpayment_auto_apply", False):
                can_auto, method, exception_code, reason = True, "OVERPAYMENT_APPLY", "OVERPAYMENT_RESIDUAL", "Invoice cleared; residual retained as unapplied customer credit"

            if can_auto:
                remaining_cash = payment_usd
                matched_ids = []
                for invoice in sorted(candidates, key=lambda row: (row["due_date"], row["invoice_id"])):
                    applied = min(remaining_cash, max(0.0, invoice["remaining_usd"]))
                    if applied > 0:
                        invoice["remaining_usd"] -= applied
                        remaining_cash -= applied
                        matched_ids.append(invoice["invoice_id"])
                        allocations.append({"payment_id": payment["payment_id"], "invoice_id": invoice["invoice_id"], "applied_amount_usd": round(applied, 2), "method": method})
                applied_total = payment_usd - remaining_cash
                result.update({"matched_invoice_ids": ";".join(matched_ids), "applied_amount_usd": round(applied_total, 2), "residual_amount_usd": round(remaining_cash, 2), "status": "AUTO_MATCHED" if remaining_cash <= tolerance else "AUTO_APPLIED_WITH_RESIDUAL", "match_method": method, "confidence": 0.93 if inferred else 0.99, "exception_code": exception_code, "reason": reason})
        matches.append(result)

    for invoice in invoices:
        invoice["remaining_usd"] = round(max(0.0, invoice["remaining_usd"]), 2)
    return {"matches": matches, "allocations": allocations, "invoices": invoices}

