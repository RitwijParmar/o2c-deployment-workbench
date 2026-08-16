# Go-live monitoring dashboard specification

## Decision for the seed-42 controlled run

**CONDITIONAL GO** — data quality passes, auto-match, manual review, and processing-time targets are met; unapplied cash, DSO, CEI, and past-due AR remain outside stretch targets.

| Signal | Green | Amber | Red | Owner | Cadence |
|---|---:|---:|---:|---|---|
| Validation errors | 0 | 1–5 | >5 | ERP Data Steward | Every batch |
| Auto-match rate | ≥78% | 70–77.9% | <70% | Cash Application Lead | Daily |
| Manual-review rate | ≤22% | 22.1–30% | >30% | Cash Application Lead | Daily |
| Unapplied cash | ≤$125k | $125k–$600k | >$600k | AR Manager | Daily |
| Duplicate leakage | 0 | — | ≥1 | Data Quality Lead | Every batch |
| Trace error spans | 0 | 1–2 | >2 | Platform Engineer | Hourly |
| Agent approval bypass | 0 | — | ≥1 | Risk/Controls Owner | Real time |
| MCP tool error rate | <1% | 1–3% | >3% | Platform Engineer | Hourly |
| P95 agent latency | <3s | 3–8s | >8s | AI Platform Owner | Hourly |

Hypercare actions:

- Daily unapplied-cash aging and residual-overpayment review.
- Twice-daily review of high-value unmatched cash and broken promises.
- Sample 20 auto-match allocations daily for precision during week one.
- Review agent recommendations for evidence completeness, route accuracy, and approval compliance.
- Compare trace counts to processed case counts; investigate gaps.

The runnable HTML dashboard is `output/dashboard.html`; the formula-driven monitoring view is also in the implementation workbook.

