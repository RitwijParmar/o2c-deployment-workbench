from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any


REQUIRED_FIELDS = {
    "customers": ["customer_id", "customer_name", "country"],
    "invoices": ["invoice_id", "customer_id", "invoice_number", "invoice_date", "due_date", "currency", "gross_amount"],
    "payments": ["payment_id", "customer_id", "payment_date", "currency", "amount", "bank_txn_id"],
    "remittances": ["remittance_id", "payment_id"],
    "deductions": ["deduction_id", "customer_id", "invoice_id", "amount"],
    "promises_to_pay": ["promise_id", "customer_id", "invoice_id", "promise_date", "promised_amount"],
    "collection_activities": ["activity_id", "customer_id", "activity_date", "activity_type"],
}

PRIMARY_KEYS = {
    "customers": "customer_id",
    "invoices": "invoice_id",
    "payments": "payment_id",
    "remittances": "remittance_id",
    "deductions": "deduction_id",
    "promises_to_pay": "promise_id",
    "collection_activities": "activity_id",
}


def validate(canonical: dict[str, list[dict[str, Any]]], configured_currencies: set[str]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    customers = {row["customer_id"] for row in canonical["customers"]}

    for entity, rows in canonical.items():
        required = REQUIRED_FIELDS[entity]
        for row_number, row in enumerate(rows, start=2):
            for field in required:
                if row.get(field) in (None, ""):
                    issues.append({"check_id": "VAL-001", "severity": "ERROR", "entity": entity, "record_id": row.get(PRIMARY_KEYS[entity], f"row-{row_number}"), "field": field, "message": "Required value is blank"})
            if "customer_id" in row and entity != "customers" and row.get("customer_id") not in customers:
                issues.append({"check_id": "VAL-003", "severity": "ERROR", "entity": entity, "record_id": row.get(PRIMARY_KEYS[entity], "unknown"), "field": "customer_id", "message": "Customer foreign key does not resolve"})
            for amount_field in ("gross_amount", "open_amount", "amount", "stated_amount", "promised_amount"):
                if amount_field in row and float(row.get(amount_field, 0) or 0) < 0:
                    issues.append({"check_id": "VAL-004", "severity": "ERROR", "entity": entity, "record_id": row.get(PRIMARY_KEYS[entity], "unknown"), "field": amount_field, "message": "Negative amount is not allowed"})
            if row.get("currency") and row["currency"] not in configured_currencies:
                issues.append({"check_id": "VAL-005", "severity": "ERROR", "entity": entity, "record_id": row.get(PRIMARY_KEYS[entity], "unknown"), "field": "currency", "message": "Currency has no configured FX rate"})
            if entity == "invoices" and row.get("invoice_date") and row.get("due_date"):
                if date.fromisoformat(row["due_date"]) < date.fromisoformat(row["invoice_date"]):
                    issues.append({"check_id": "VAL-006", "severity": "ERROR", "entity": entity, "record_id": row["invoice_id"], "field": "due_date", "message": "Due date precedes invoice date"})

        pk = PRIMARY_KEYS[entity]
        counts = Counter(row.get(pk) for row in rows)
        for duplicate_id, count in counts.items():
            if duplicate_id and count > 1:
                issues.append({"check_id": "VAL-002", "severity": "ERROR", "entity": entity, "record_id": duplicate_id, "field": pk, "message": f"Primary identifier appears {count} times"})

    bank_counts = Counter(row.get("bank_txn_id") for row in canonical["payments"] if row.get("bank_txn_id"))
    for bank_ref, count in bank_counts.items():
        if count > 1:
            issues.append({"check_id": "VAL-007", "severity": "WARN", "entity": "payments", "record_id": bank_ref, "field": "bank_txn_id", "message": f"Bank transaction appears {count} times"})

    total_records = sum(len(rows) for rows in canonical.values())
    error_count = sum(issue["severity"] == "ERROR" for issue in issues)
    warning_count = sum(issue["severity"] == "WARN" for issue in issues)
    return {
        "status": "PASS" if error_count == 0 else "FAIL",
        "total_records": total_records,
        "error_count": error_count,
        "warning_count": warning_count,
        "quality_rate": 1 - (error_count / total_records if total_records else 0),
        "issues": issues,
    }
