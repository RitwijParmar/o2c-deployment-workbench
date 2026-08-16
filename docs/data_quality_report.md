# Data-quality report

Seed-42 controlled run, 2026-07-31.

| Control result | Value |
|---|---:|
| Canonical records tested | 1,908 |
| Validation errors | 0 |
| Warnings | 18 |
| Quality rate | 100.0% |
| Batch gate | PASS WITH WARNINGS |

The 18 warnings are intentional duplicate bank-transaction identifiers. The duplicate rows are not counted as valid cash, are given a zero residual to avoid overstating unapplied cash, and are routed to the Cash Application Data Steward. No warning is silently discarded.

Checks executed:

1. Required identifiers populated.
2. Primary identifiers unique after canonicalization.
3. Customer foreign keys resolve where the entity carries a customer key.
4. Monetary amounts are non-negative.
5. Every currency has a configured reporting FX rate.
6. Invoice due date is not before invoice date.
7. Duplicate bank transaction identifiers are identified.

Machine-readable evidence: `output/data_quality_report.json`. This report describes generated synthetic data only.

