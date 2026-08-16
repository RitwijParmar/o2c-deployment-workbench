# Current-state process

Controlled baseline for Northstar Industrial Distribution (Synthetic), as of 2026-07-31.

```mermaid
flowchart TD
    A["Receive three differently shaped ERP files"] --> B["Analyst reformats spreadsheets"]
    B --> C{"Required data present?"}
    C -- No --> D["Email source-system owner"]
    D --> B
    C -- Yes --> E["Search payment reference manually"]
    E --> F{"Exact single invoice and amount?"}
    F -- Yes --> G["Apply cash"]
    F -- No --> H["Create manual research item"]
    H --> I["Search remittance, customer, currency and deduction evidence"]
    I --> J["Route by analyst judgment"]
    J --> K["Update collection spreadsheet separately"]
    G --> L["Reconcile totals"]
    K --> L
```

Baseline symptoms evidenced by the seed-42 benchmark:

- 90.3% manual-review rate and $2.19M unapplied cash.
- 69.5% of ending AR past due and 54 broken promises to pay.
- 18 intentional duplicate bank transactions found during control checks.
- 67.7 estimated processing hours under configured baseline handling assumptions.

These are synthetic current-state conditions for a controlled implementation benchmark.

