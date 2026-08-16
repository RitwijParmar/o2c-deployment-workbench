# Requirements traceability matrix

| ID | Requirement | Design/config | Evidence | UAT |
|---|---|---|---|---|
| REQ-001 | Three differently structured simulated ERP sources | `sources` mapping | `data/raw/*_SIM` | UAT-01–03 |
| REQ-002 | Seven canonical receivables entities | Adapter base and mappings | `data/canonical` | UAT-04 |
| REQ-003 | Required-field, key, amount, date and currency controls | `validation_checks` | DQ JSON/report | UAT-05–09 |
| REQ-004 | Exact invoice payment | Matching engine | future allocations | UAT-10 |
| REQ-005 | Partial and overpayment handling | Tolerances and overpayment flag | match methods/residual | UAT-11–12 |
| REQ-006 | One-to-many and many-to-one | Remittance list and remaining balance | allocations | UAT-13–14 |
| REQ-007 | Missing remittance inference | amount inference flag | match reason/confidence | UAT-15 |
| REQ-008 | Currency and tolerance difference | FX and tolerance config | match evidence | UAT-16–17 |
| REQ-009 | Duplicate and deduction short-pay | duplicate control/deduction limit | exception/allocation | UAT-18–19 |
| REQ-010 | Unmatched cash routing | exception routes | exception queue | UAT-20–21 |
| REQ-011 | Baseline and future KPI comparison | targets/assumptions | dashboard and workbook | UAT-22 |
| REQ-012 | Configurable collections priority | priority weights | worklist | UAT-23 |
| REQ-013 | Multi-agent specialist handoffs | agent control policy | decisions and traces | UAT-24 |
| REQ-014 | Human approval for controlled actions | approval policy | recommendation-only status | UAT-25 |
| REQ-015 | MCP tools, resources and prompts | MCP server | server discovery | UAT-26 |
| REQ-016 | Agent/pipeline observability without content capture | observability config | JSONL spans/summary | UAT-27 |
| REQ-017 | Conditional go-live based on evidence | go-live monitor | agent summary | UAT-28 |

