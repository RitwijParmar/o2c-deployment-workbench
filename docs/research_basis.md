# Research basis

Primary sources used to keep the project aligned with common receivables and agent-platform behavior:

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — structured tools/resources/prompts and current SDK behavior.
- [MCP transport guidance](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/run/index.md) — `stdio` for local servers and Streamable HTTP for deployed servers; new work does not use legacy SSE.
- [MCP specification overview](https://modelcontextprotocol.io/specification/2025-06-18/basic/index) — client/server primitives and JSON-RPC foundation.
- [OpenTelemetry GenAI attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/) — agent, workflow, operation, tool and usage attribute naming; content fields can be sensitive.
- [SAP partial payments versus residual items](https://help.sap.com/docs/SAP_S4HANA_CLOUD/918bca53037f408f91a2295d04ac16bc/279bad94d6414e05aab0cacf42eb3803.html?locale=en-US) — partial-payment and residual-item behavior.
- [SAP payment differences](https://help.sap.com/docs/SAP_S4HANA_CLOUD/918bca53037f408f91a2295d04ac16bc/a8d0f49995394451882809d7a0171f6a.html) — tolerance, partial, residual, write-off and on-account options.
- [Oracle Fusion Receivables Credit to Cash](https://docs.oracle.com/en/cloud/saas/financials/26c/faofc/using-receivables-credit-to-cash.pdf) — receipts, remittance and receivables operating context.
- [NetSuite customer payments](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3667711.html) — customer payment and auto-apply considerations.
- [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model) — Responses API and current multi-agent/model guidance for the optional model-backed path.

The repository does not claim schema parity with vendor products. Field names and files are deliberately labeled “style” and “simulated”; they exist to demonstrate configuration-driven implementation work, not reverse-engineered integrations.

