from __future__ import annotations

from pathlib import Path
from typing import Any

from o2c_workbench.io_utils import read_csv


DATE_FIELDS = {"invoice_date", "due_date", "payment_date", "promise_date", "activity_date"}
FLOAT_FIELDS = {"gross_amount", "open_amount", "amount", "stated_amount", "promised_amount"}
INT_FIELDS = {"payment_terms_days"}


class MappingDrivenAdapter:
    """Maps a simulated ERP export into the canonical O2C entities."""

    def __init__(self, source_code: str, source_config: dict[str, Any], raw_root: Path):
        self.source_code = source_code
        self.source_config = source_config
        self.raw_root = raw_root / source_code

    def extract(self) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for entity, entity_config in self.source_config["entities"].items():
            source_rows = read_csv(self.raw_root / entity_config["file"])
            mapped_rows: list[dict[str, Any]] = []
            for source_row in source_rows:
                row: dict[str, Any] = {"source_system": self.source_code}
                for canonical_field, source_field in entity_config["fields"].items():
                    value: Any = source_row.get(source_field, "")
                    if canonical_field in FLOAT_FIELDS:
                        value = float(value or 0)
                    elif canonical_field in INT_FIELDS:
                        value = int(float(value or 0))
                    else:
                        value = value.strip() if isinstance(value, str) else value
                    row[canonical_field] = value
                mapped_rows.append(row)
            result[entity] = mapped_rows
        return result

