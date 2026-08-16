# Source-to-target mapping

All source labels and files are simulated. The configuration file is the executable mapping authority; this document is the implementation summary.

| Canonical entity | SAP S/4HANA-style file | Oracle Fusion-style file | NetSuite-style file | Business key |
|---|---|---|---|---|
| customers | `KNA1_SIM.csv` | `HZ_CUST_ACCOUNTS_SIM.csv` | `customers_export_sim.csv` | `customer_id` |
| invoices | `BSID_SIM.csv` | `RA_CUSTOMER_TRX_ALL_SIM.csv` | `transactions_invoices_sim.csv` | `invoice_id` |
| payments | `FEBEP_SIM.csv` | `AR_CASH_RECEIPTS_ALL_SIM.csv` | `customer_payments_sim.csv` | `payment_id` |
| remittances | `REMADV_SIM.csv` | `AR_RECEIVABLE_APPLICATIONS_SIM.csv` | `payment_applications_sim.csv` | `remittance_id` |
| deductions | `DM_CASE_SIM.csv` | `AR_DEDUCTIONS_SIM.csv` | `credit_memos_deductions_sim.csv` | `deduction_id` |
| promises_to_pay | `PTP_SIM.csv` | `AR_PROMISES_SIM.csv` | `promises_to_pay_sim.csv` | `promise_id` |
| collection_activities | `DUNNING_LOG_SIM.csv` | `AR_COLLECTION_ACTIVITIES_SIM.csv` | `collection_notes_sim.csv` | `activity_id` |

Representative field mappings:

| Canonical field | SAP-style | Oracle-style | NetSuite-style | Transformation/control |
|---|---|---|---|---|
| customer_id | KUNNR | CUST_ACCOUNT_ID | internalid | Preserve source value; add `source_system` lineage |
| invoice_number | XBLNR | TRX_NUMBER | tranid | Trim; required for reference matching |
| invoice_date | BLDAT | TRX_DATE | trandate | ISO date; due date must not precede it |
| open_amount | DMBTR_OPEN | AMOUNT_DUE_REMAINING | amountremaining | Decimal; non-negative |
| payment_id | KUKEY | CASH_RECEIPT_ID | internalid | Required and unique |
| bank_txn_id | BANK_REF | BANK_REFERENCE | custbody_bank_reference | Duplicate control; warning and quarantine |
| invoice_refs | XBLNR_LIST | APPLIED_TRX_NUMBERS | applied_tranids | Normalize `|`, `;`, or `,` into a reference list |
| deduction reason | REASON | REASON_CODE | reasoncode | Used only when status is validated and within limit |
| promise status | PTP_STATUS | PROMISE_STATUS | promisestatus | Broken promises influence collection priority |

Every canonical row also carries `source_system`, `source_file`, and `ingested_at` lineage fields. Exact per-field mappings live in `config/customer_implementation.yaml`.

