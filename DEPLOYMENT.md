# Deployment record

## Production showcase

- URL: https://o2c-deployment-workbench.ritwij.chatgpt.site
- Platform: OpenAI Sites
- Project: `appgprj_6a81f84b2e148191b8d7b99bb65b9591`
- Deployment: `appgdep_6a81f89823508191888b5394d8ea1f99`
- Status at handoff: succeeded

The production showcase is built from `site/`. It contains no live ERP connection, credentials, customer data, or model API key. All downloadable data and benchmark results are synthetic.

## Verification gates

- Python workbench: `pytest -q`
- Hosted dashboard: `cd site && npm ci && npm test`
- Production dependency audit: `cd site && npm audit --omit=dev`
- GitHub Actions: `.github/workflows/ci.yml`

## Release flow

1. Run the Python and hosted-dashboard verification gates.
2. Review changes to financial-control boundaries and synthetic-data labels.
3. Push the exact tested source state.
4. Save and publish a new Sites version from that commit.
5. Confirm the production deployment succeeds and recheck artifact downloads.

The deployment is a portfolio implementation simulator, not a production accounts-receivable service. A real rollout additionally requires authenticated connectors, secrets management, role-based access, customer-specific retention, segregation of duties, and formal approval workflows.
