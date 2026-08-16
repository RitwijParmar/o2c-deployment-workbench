# Agent and observability design

The multi-agent layer is used where judgment is useful and where deterministic matching has intentionally stopped.

| Agent | Receives | Produces | Cannot do |
|---|---|---|---|
| Supervisor Agent | Routed exception | Specialist handoff | Financial posting |
| Cash Application Agent | Payment, match, remittance and residual evidence | Classification and next-action recommendation | Force ambiguous match, refund, write off |
| Data Quality Agent | Duplicate/invalid record evidence | Quarantine/steward recommendation | Change master data |
| Collections Agent | Open AR, aging, risk, promises and deductions | Prioritized outreach draft | Send external communication |
| Go Live Monitor Agent | DQ, KPIs and operational controls | GO/CONDITIONAL_GO/NO_GO with conditions | Override exit criteria |

The default run is a deterministic orchestration harness. It proves routing, structured decisions, approval gates, and traceability without an API key. The optional model path uses the same evidence boundary and structured recommendation contract.

OpenTelemetry spans cover ingestion, canonicalization, validation, matching, KPI calculation, agent invocation, and handoffs. Attributes include `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.agent.name`, and `gen_ai.tool.name`. Record content capture is off by default because prompts, tool arguments, and results can contain sensitive information in real implementations.

Evaluation lanes for a production extension:

- Cash exception classification precision/recall by route.
- Evidence-grounding rate: every recommendation cites available structured evidence.
- Human override rate by agent/action.
- Approval-bypass rate (must remain zero).
- Tool/handoff errors, latency, token usage and cost by case class.
- Auto-match precision sampled independently of the auto-match rate.

