# User acceptance testing

All cases use synthetic data. Expected financial changes are allocation proposals only.

| ID | Scenario | Test action | Expected result |
|---|---|---|---|
| UAT-01 | SAP-style ingestion | Run seed-42 benchmark | Seven configured SAP-style files load with lineage |
| UAT-02 | Oracle-style ingestion | Run seed-42 benchmark | Seven configured Oracle-style files load with lineage |
| UAT-03 | NetSuite-style ingestion | Run seed-42 benchmark | Seven configured NetSuite-style files load with lineage |
| UAT-04 | Canonical completeness | Inspect canonical directory | All seven entities exist and total 1,908 records |
| UAT-05 | Missing required ID | Blank a test identifier | VAL-001 error blocks the batch |
| UAT-06 | Duplicate primary ID | Repeat a test entity ID | VAL-002 error blocks the batch |
| UAT-07 | Broken customer FK | Supply unknown customer ID | VAL-003 error blocks the batch |
| UAT-08 | Unsupported currency | Supply currency without FX | VAL-005 error blocks the batch |
| UAT-09 | Invalid invoice dates | Set due date before invoice date | VAL-006 error blocks the batch |
| UAT-10 | Exact payment | Process `EXACT` case | One invoice auto-matches with exact evidence |
| UAT-11 | Partial payment | Process `PARTIAL` case | Cash applies; invoice retains remaining balance |
| UAT-12 | Overpayment | Process `OVERPAYMENT` case | Invoice clears; residual routes as customer credit |
| UAT-13 | One payment/multiple invoices | Process bulk remittance | Two allocations created for one payment |
| UAT-14 | Multiple payments/one invoice | Process split payments | Successive allocations reduce the same invoice to zero |
| UAT-15 | Missing remittance | Process unique amount case | Unique customer/amount inference can auto-match; ambiguous case cannot |
| UAT-16 | Cross-currency | Process EUR invoice/USD cash | Configured FX translates evidence before comparison |
| UAT-17 | Amount tolerance | Process small FX variance | Difference inside max absolute/percentage tolerance is accepted |
| UAT-18 | Duplicate payment | Process repeated bank transaction | Later record is quarantined and routed to steward |
| UAT-19 | Deduction short-pay | Process validated $100 deduction | Payment plus deduction clears invoice within configured limit |
| UAT-20 | Unknown reference | Process unmatched case | Cash remains unapplied and enters manual review |
| UAT-21 | High-value unmatched | Raise unmatched value above threshold | Exception routes to senior analyst |
| UAT-22 | Benchmark comparison | Compare current/future outputs | All seven KPI movements calculate; disclaimer remains visible |
| UAT-23 | Collection weighting | Increase broken-promise weight | Broken-promise items rank higher on rerun |
| UAT-24 | Agent handoff | Run offline agent control | Supervisor emits specialist handoff and structured recommendation |
| UAT-25 | Human control gate | Propose write-off/refund/post | Recommendation requires approval and executes no financial action |
| UAT-26 | MCP discovery | List server capabilities | Four tools, three resources and two prompts are discoverable |
| UAT-27 | Telemetry privacy | Inspect trace JSONL | Agent/tool/handoff spans exist; record content capture is false |
| UAT-28 | Go-live decision | Evaluate seed-42 evidence | DQ pass plus four unmet stretch KPIs produces CONDITIONAL_GO |

Exit criteria: all automated tests pass; UAT-01–28 signed by designated owner; no Severity-1 defects open; rollback assets verified; target exceptions accepted by Finance Operations.

