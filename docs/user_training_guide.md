# User training guide

## What users do

1. Confirm the banner says **synthetic controlled implementation benchmark**.
2. Review validation status before opening match results. Errors block the batch; duplicate-bank warnings create steward work.
3. Read match method, confidence, allocations, residual, reason, and exception route together.
4. Work exception queues by assigned team and collection queues by priority score.
5. Treat agent output as an evidence-backed recommendation, never as proof that an ERP action occurred.

## Common cases

- **Partial payment:** cash is applied to the referenced invoice and a balance remains.
- **Overpayment:** the invoice clears but residual cash remains as customer credit; refund/credit treatment requires approval.
- **Bulk remittance:** one payment creates multiple invoice allocations.
- **Split payment:** multiple payments reduce one invoice across successive allocations.
- **Deduction short-pay:** only a validated deduction within the configured limit supports automatic clearing.
- **Duplicate payment:** later bank-reference occurrence is quarantined; do not apply it again.
- **Unmatched cash:** request remittance or route for research; never force a match to improve the KPI.

## Agent and MCP safety

Agents may retrieve evidence, classify, route, and draft a next action. They cannot post, refund, write off, or change master data. If an optional model review proposes one of those actions, the guardrail requires human approval.

When using MCP, begin with the benchmark resource, then call the narrow payment or invoice tool. Do not paste genuine customer data into this synthetic demo.

