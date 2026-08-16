# Cutover and rollback checklist

## Entry criteria

- [ ] Finance owner approves mappings, tolerance policy, deduction limit, routing, KPI targets, and agent action boundary.
- [ ] UAT-01–28 are signed; Severity-1 defects are zero.
- [ ] Source counts, control totals, currencies, and bank-reference uniqueness reconcile.
- [ ] Service accounts, least-privilege access, secrets rotation, and audit retention are approved for a real deployment.
- [ ] MCP exposure is restricted to approved clients; Streamable HTTP authentication is configured before leaving localhost.
- [ ] Trace content capture remains disabled; retention and access controls are confirmed.

## Cutover sequence

- [ ] Freeze configuration and tag release candidate.
- [ ] Export source snapshots and record file hashes/control totals.
- [ ] Run canonicalization and validation; stop on validation errors.
- [ ] Run benchmark smoke cases for exact, partial, bulk, FX, duplicate, deduction, and unmatched cash.
- [ ] Reconcile payment count, cash total, applied total, residual total, and ending AR.
- [ ] Enable recommendation-only agents and MCP read tools.
- [ ] Confirm all financial actions still require human approval.
- [ ] Publish dashboards; start hypercare ownership rota.

## Rollback triggers

- Validation errors after source freeze.
- Cash or AR control-total mismatch.
- Duplicate leakage into valid cash.
- Exception routing failure or trace loss above agreed threshold.
- Any agent-produced controlled action without human approval.

## Rollback actions

- [ ] Disable agent/MCP access and stop new batches.
- [ ] Restore the prior configuration tag and prior canonical snapshot.
- [ ] Revoke unapproved allocation proposals; no direct ERP postings exist in this demo.
- [ ] Reconcile source, canonical, match, allocation, and exception totals.
- [ ] Open incident record with trace IDs and affected batch ID.
- [ ] Obtain Finance/Technology approval before restart.

