from __future__ import annotations

from datetime import date
from typing import Any


RISK_SCORE = {"LOW": 0.2, "MEDIUM": 0.6, "HIGH": 1.0}


def build_collection_worklist(canonical: dict[str, list[dict[str, Any]]], matched_invoices: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    as_of = date.fromisoformat(config["implementation"]["as_of_date"])
    weights = config["collection_priority_weights"]
    customers = {row["customer_id"]: row for row in canonical["customers"]}
    broken_promises = {row["invoice_id"] for row in canonical["promises_to_pay"] if row["status"] == "BROKEN"}
    deduction_invoices = {row["invoice_id"] for row in canonical["deductions"] if row["status"] not in {"CLOSED", "REJECTED"}}
    max_balance = max((row["remaining_usd"] for row in matched_invoices), default=1.0)
    worklist = []
    for invoice in matched_invoices:
        if invoice["remaining_usd"] <= 0:
            continue
        days_past_due = max(0, (as_of - date.fromisoformat(invoice["due_date"])).days)
        broken = invoice["invoice_id"] in broken_promises
        active_deduction = invoice["invoice_id"] in deduction_invoices
        customer = customers[invoice["customer_id"]]
        score = 100 * (
            weights["days_past_due"] * min(days_past_due / 120, 1)
            + weights["open_balance"] * min(invoice["remaining_usd"] / max_balance, 1)
            + weights["broken_promise"] * int(broken)
            + weights["customer_risk"] * RISK_SCORE.get(customer["credit_risk"], 0.5)
            + weights["active_deduction"] * int(active_deduction)
        )
        priority = "CRITICAL" if score >= 70 else "HIGH" if score >= 50 else "MEDIUM" if score >= 30 else "LOW"
        route = config["exception_routing"]["BROKEN_PROMISE"] if broken else "Collections Specialist"
        worklist.append({"invoice_id": invoice["invoice_id"], "invoice_number": invoice["invoice_number"], "customer_id": invoice["customer_id"], "customer_name": customer["customer_name"], "open_balance_usd": invoice["remaining_usd"], "days_past_due": days_past_due, "broken_promise": broken, "active_deduction": active_deduction, "credit_risk": customer["credit_risk"], "priority_score": round(score, 1), "priority": priority, "route_to": route})
    return sorted(worklist, key=lambda row: (-row["priority_score"], -row["open_balance_usd"]))

