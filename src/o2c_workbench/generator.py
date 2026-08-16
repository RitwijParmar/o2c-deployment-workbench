from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from o2c_workbench.io_utils import write_csv


SCENARIOS = [
    "EXACT",
    "PARTIAL",
    "OVERPAYMENT",
    "ONE_PAYMENT_MULTI_INVOICE",
    "MULTI_PAYMENT_ONE_INVOICE",
    "MISSING_REMITTANCE",
    "CURRENCY_TOLERANCE",
    "SHORT_PAY_DEDUCTION",
    "UNMATCHED_CASH",
    "OPEN_PAST_DUE",
    "BROKEN_PROMISE",
    "EXACT",
]


def _source_value_rows(canonical_rows: list[dict[str, Any]], field_map: dict[str, str]) -> list[dict[str, Any]]:
    output = []
    for row in canonical_rows:
        output.append({source_field: row.get(canonical_field, "") for canonical_field, source_field in field_map.items()})
    return output


def _build_source_records(source_code: str, source_index: int, as_of: date, seed: int) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed + source_index * 1000)
    customers: list[dict[str, Any]] = []
    invoices: list[dict[str, Any]] = []
    payments: list[dict[str, Any]] = []
    remittances: list[dict[str, Any]] = []
    deductions: list[dict[str, Any]] = []
    promises: list[dict[str, Any]] = []
    activities: list[dict[str, Any]] = []

    for customer_no in range(1, 19):
        customer_id = f"{source_code[:3]}-C{customer_no:03d}"
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": f"Synthetic Customer {source_index + 1}-{customer_no:03d}",
                "country": rng.choice(["US", "US", "CA", "GB", "DE"]),
                "credit_risk": rng.choice(["LOW", "MEDIUM", "MEDIUM", "HIGH"]),
                "payment_terms_days": rng.choice([30, 30, 45, 60]),
            }
        )
        customer_invoice_ids: list[str] = []
        for inv_no, scenario in enumerate(SCENARIOS, start=1):
            invoice_id = f"{source_code[:3]}-I{customer_no:03d}-{inv_no:02d}"
            customer_invoice_ids.append(invoice_id)
            age_days = 132 - inv_no * 9 + rng.randint(-3, 3)
            invoice_date = as_of - timedelta(days=max(8, age_days))
            terms = customers[-1]["payment_terms_days"]
            amount = round(1800 + customer_no * 137 + inv_no * 211 + rng.uniform(0, 700), 2)
            currency = "EUR" if scenario == "CURRENCY_TOLERANCE" else "USD"
            invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "invoice_number": f"INV-{source_index + 1}{customer_no:03d}{inv_no:02d}",
                    "invoice_date": invoice_date.isoformat(),
                    "due_date": (invoice_date + timedelta(days=terms)).isoformat(),
                    "currency": currency,
                    "gross_amount": amount,
                    "open_amount": amount,
                    "status": "OPEN",
                    "benchmark_case": scenario,
                }
            )

        inv = invoices[-12:]

        def payment(suffix: str, amount: float, currency: str, reference: str, scenario: str, bank_ref: str | None = None) -> dict[str, Any]:
            payment_id = f"{source_code[:3]}-P{customer_no:03d}-{suffix}"
            row = {
                "payment_id": payment_id,
                "customer_id": customer_id,
                "payment_date": (as_of - timedelta(days=rng.randint(1, 18))).isoformat(),
                "currency": currency,
                "amount": round(amount, 2),
                "reference": reference,
                "bank_txn_id": bank_ref or f"BANK-{source_index + 1}-{customer_no:03d}-{suffix}",
                "benchmark_case": scenario,
            }
            payments.append(row)
            return row

        p_exact = payment("01", inv[0]["gross_amount"], "USD", inv[0]["invoice_number"], "EXACT")
        remittances.append({"remittance_id": f"R-{p_exact['payment_id']}", "payment_id": p_exact["payment_id"], "invoice_refs": inv[0]["invoice_number"], "stated_amount": p_exact["amount"]})

        p_partial = payment("02", inv[1]["gross_amount"] * 0.60, "USD", inv[1]["invoice_number"], "PARTIAL")
        remittances.append({"remittance_id": f"R-{p_partial['payment_id']}", "payment_id": p_partial["payment_id"], "invoice_refs": inv[1]["invoice_number"], "stated_amount": p_partial["amount"]})

        p_over = payment("03", inv[2]["gross_amount"] + 125.0, "USD", inv[2]["invoice_number"], "OVERPAYMENT")
        remittances.append({"remittance_id": f"R-{p_over['payment_id']}", "payment_id": p_over["payment_id"], "invoice_refs": inv[2]["invoice_number"], "stated_amount": p_over["amount"]})

        multi_total = inv[3]["gross_amount"] + inv[4]["gross_amount"]
        p_multi = payment("04", multi_total, "USD", "BULK REMIT", "ONE_PAYMENT_MULTI_INVOICE")
        remittances.append({"remittance_id": f"R-{p_multi['payment_id']}", "payment_id": p_multi["payment_id"], "invoice_refs": f"{inv[3]['invoice_number']}|{inv[4]['invoice_number']}", "stated_amount": multi_total})

        first_half = round(inv[5]["gross_amount"] * 0.45, 2)
        for suffix, amount in [("05A", first_half), ("05B", inv[5]["gross_amount"] - first_half)]:
            p_split = payment(suffix, amount, "USD", inv[5]["invoice_number"], "MULTI_PAYMENT_ONE_INVOICE")
            remittances.append({"remittance_id": f"R-{p_split['payment_id']}", "payment_id": p_split["payment_id"], "invoice_refs": inv[5]["invoice_number"], "stated_amount": amount})

        payment("06", inv[6]["gross_amount"], "USD", "", "MISSING_REMITTANCE")

        usd_equivalent = inv[7]["gross_amount"] * 1.10 + rng.uniform(-1.25, 1.25)
        p_fx = payment("07", usd_equivalent, "USD", inv[7]["invoice_number"], "CURRENCY_TOLERANCE")
        remittances.append({"remittance_id": f"R-{p_fx['payment_id']}", "payment_id": p_fx["payment_id"], "invoice_refs": inv[7]["invoice_number"], "stated_amount": p_fx["amount"]})

        deduction_amount = 100.0
        p_short = payment("08", inv[8]["gross_amount"] - deduction_amount, "USD", inv[8]["invoice_number"], "SHORT_PAY_DEDUCTION")
        remittances.append({"remittance_id": f"R-{p_short['payment_id']}", "payment_id": p_short["payment_id"], "invoice_refs": inv[8]["invoice_number"], "stated_amount": p_short["amount"]})
        deductions.append({"deduction_id": f"D-{p_short['payment_id']}", "customer_id": customer_id, "invoice_id": inv[8]["invoice_id"], "payment_id": p_short["payment_id"], "reason_code": "FREIGHT_SHORTAGE", "amount": deduction_amount, "status": "VALIDATED"})

        payment("09", round(inv[9]["gross_amount"] * 0.83, 2), "USD", "UNKNOWN-REFERENCE", "UNMATCHED_CASH")

        promises.append({"promise_id": f"PTP-{source_code[:3]}-{customer_no:03d}", "customer_id": customer_id, "invoice_id": inv[10]["invoice_id"], "promise_date": (as_of - timedelta(days=12)).isoformat(), "promised_amount": inv[10]["gross_amount"], "status": "BROKEN"})
        activities.append({"activity_id": f"ACT-{source_code[:3]}-{customer_no:03d}-1", "customer_id": customer_id, "invoice_id": inv[10]["invoice_id"], "activity_date": (as_of - timedelta(days=18)).isoformat(), "activity_type": "CALL", "outcome": "PROMISE_RECEIVED"})
        activities.append({"activity_id": f"ACT-{source_code[:3]}-{customer_no:03d}-2", "customer_id": customer_id, "invoice_id": inv[10]["invoice_id"], "activity_date": (as_of - timedelta(days=6)).isoformat(), "activity_type": "EMAIL", "outcome": "NO_RESPONSE"})

        if customer_no % 3 == 0:
            duplicate = dict(p_exact)
            duplicate["payment_id"] = f"{p_exact['payment_id']}-DUP"
            duplicate["benchmark_case"] = "DUPLICATE_PAYMENT"
            payments.append(duplicate)

    return {
        "customers": customers,
        "invoices": invoices,
        "payments": payments,
        "remittances": remittances,
        "deductions": deductions,
        "promises_to_pay": promises,
        "collection_activities": activities,
    }


def generate_raw_exports(config: dict[str, Any], raw_root: Path, seed: int = 42) -> dict[str, int]:
    as_of = date.fromisoformat(config["implementation"]["as_of_date"])
    counts: dict[str, int] = {}
    for source_index, (source_code, source_config) in enumerate(config["sources"].items()):
        records = _build_source_records(source_code, source_index, as_of, seed)
        source_dir = raw_root / source_code
        source_dir.mkdir(parents=True, exist_ok=True)
        for entity, entity_config in source_config["entities"].items():
            source_rows = _source_value_rows(records[entity], entity_config["fields"])
            write_csv(source_dir / entity_config["file"], source_rows, list(entity_config["fields"].values()))
            counts[f"{source_code}.{entity}"] = len(source_rows)
    return counts
