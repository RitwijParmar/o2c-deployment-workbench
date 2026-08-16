from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def calculate_kpis(canonical: dict[str, list[dict[str, Any]]], matching: dict[str, Any], config: dict[str, Any], mode: str) -> dict[str, float]:
    as_of = date.fromisoformat(config["implementation"]["as_of_date"])
    period_days = int(config["implementation"]["benchmark_period_days"])
    fx = config["fx_to_usd"]
    valid_matches = [row for row in matching["matches"] if not row["is_duplicate_record"]]
    all_rows = matching["matches"]
    auto = [row for row in valid_matches if row["status"].startswith("AUTO")]
    manual = [row for row in all_rows if row["status"] == "MANUAL_REVIEW"]
    unapplied = sum(row["residual_amount_usd"] for row in valid_matches)
    ending_ar = sum(row["remaining_usd"] for row in matching["invoices"])
    past_due_ar = sum(row["remaining_usd"] for row in matching["invoices"] if date.fromisoformat(row["due_date"]) < as_of)
    current_ar = ending_ar - past_due_ar
    period_start = as_of - timedelta(days=period_days)
    beginning_ar = sum(float(row["gross_amount"]) * fx[row["currency"]] for row in canonical["invoices"] if date.fromisoformat(row["invoice_date"]) < period_start)
    credit_sales = sum(float(row["gross_amount"]) * fx[row["currency"]] for row in canonical["invoices"] if date.fromisoformat(row["invoice_date"]) >= period_start)
    dso = ending_ar / max(credit_sales, 1.0) * period_days
    cei_denominator = beginning_ar + credit_sales - current_ar
    cei = (beginning_ar + credit_sales - ending_ar) / max(cei_denominator, 1.0) * 100
    assumptions = config["processing_assumptions"]
    if mode == "baseline":
        minutes = len(auto) * assumptions["baseline_auto_minutes_per_payment"] + len(manual) * assumptions["baseline_manual_minutes_per_payment"]
    else:
        minutes = len(auto) * assumptions["future_auto_minutes_per_payment"] + len(manual) * assumptions["future_manual_minutes_per_payment"]
    return {
        "payment_records": len(all_rows),
        "valid_cash_records": len(valid_matches),
        "auto_match_rate": len(auto) / max(len(valid_matches), 1),
        "manual_review_rate": len(manual) / max(len(all_rows), 1),
        "unapplied_cash_usd": round(unapplied, 2),
        "ending_ar_usd": round(ending_ar, 2),
        "dso_days": round(dso, 1),
        "cei_percent": round(max(0.0, min(100.0, cei)), 1),
        "past_due_percent": past_due_ar / max(ending_ar, 1.0),
        "processing_time_hours": round(minutes / 60, 1),
    }


def compare_kpis(baseline: dict[str, float], future: dict[str, float], targets: dict[str, float]) -> list[dict[str, Any]]:
    metadata = {
        "auto_match_rate": ("Auto-match rate", "percent", "higher"),
        "manual_review_rate": ("Manual-review rate", "percent", "lower"),
        "unapplied_cash_usd": ("Unapplied cash", "currency", "lower"),
        "dso_days": ("DSO", "days", "lower"),
        "cei_percent": ("CEI", "percent_points", "higher"),
        "past_due_percent": ("Past-due AR", "percent", "lower"),
        "processing_time_hours": ("Processing time", "hours", "lower"),
    }
    rows = []
    for key, (label, unit, direction) in metadata.items():
        before, after, target = baseline[key], future[key], targets[key]
        target_met = after >= target if direction == "higher" else after <= target
        rows.append({"metric": key, "label": label, "unit": unit, "direction": direction, "baseline": before, "future": after, "change": after - before, "target": target, "target_met": target_met})
    return rows

