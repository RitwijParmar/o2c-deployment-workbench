# Five-minute implementation demo script

## 0:00–0:35 — Customer problem and boundary

This is the O2C Deployment Workbench for Northstar Industrial Distribution, a fictional customer. Every ERP file and every KPI result shown here is synthetic. The goal is not to claim a production integration. It is to simulate the work an implementation team performs: configure source mappings, validate receivables data, handle difficult cash cases, measure a controlled future state, route exceptions, prepare users, and monitor go-live.

## 0:35–1:10 — Configuration and source onboarding

The implementation begins in one customer configuration file. It contains the three source layouts, matching tolerances, cross-currency rates, deduction limits, collection-priority weights, exception ownership, validation gates, KPI targets, agent permissions, and observability policy. The raw folder contains visibly labeled SAP S/4HANA-style, Oracle Fusion-style, and NetSuite-style exports. Their field names and delimiters differ, but mapping-driven adapters normalize them into seven canonical tables with source lineage.

## 1:10–1:45 — Validation and difficult cash cases

The seed-42 batch contains 1,908 canonical records. Seven controls check required identifiers, uniqueness, customer relationships, amounts, currencies, dates, and duplicate bank transactions. The batch passes with zero errors and eighteen intentional duplicate warnings. The matching engine then handles exact, partial, overpayment, one-to-many, many-to-one, missing remittance, currency tolerance, deduction short-pay, duplicate, and genuinely unmatched cases. It never forces ambiguous cash merely to improve the metric.

## 1:45–2:25 — Current and future benchmark

The current-state baseline only accepts an exact single invoice reference, currency, and amount. That produces a ten percent auto-match rate and a ninety-point-three percent manual-review rate. The configured future state reaches eighty-point-seven percent auto-match and twenty-one-point-nine percent manual review. Unapplied cash falls from about two-point-two million dollars to about five hundred fifty thousand. DSO, CEI, past-due AR, and modeled processing time also improve. These are controlled synthetic benchmark movements, not customer results.

## 2:25–3:05 — Exceptions and collections

Open the exception queue and each residual has an evidence trail, exception code, and configured owner. Repeated bank transactions go to a data steward. High-value unmatched cash goes to a senior cash application analyst. Overpayment residuals go to a customer-credit analyst. Separately, collections priority combines days past due, open balance, broken promises, credit risk, and active deductions. The result is an explainable worklist, not a black-box score.

## 3:05–3:50 — MCP and agents

The MCP server exposes four structured tools, three resources, and two investigation prompts. An AI client can retrieve the controlled benchmark, investigate one payment, or inspect one collection score without receiving a broad filesystem tool. When deterministic matching stops, a supervisor hands the case to a Cash Application, Data Quality, or Collections specialist. A Go Live Monitor evaluates the full control state. Agents can read, classify, route, and draft; posting, refund, write-off, and master-data changes require human approval and are not available as execution tools.

## 3:50–4:25 — Observability and evaluation

Every ingestion, validation, matching, KPI, agent, and handoff operation emits a local OpenTelemetry span. The trace uses GenAI-aligned workflow, agent, operation, and tool attributes. Sensitive record content capture is disabled. The monitoring plan tracks classification quality, grounding, overrides, approval bypass, tool errors, latency, token usage, and cost. This makes agent behavior auditable and creates a clear route from demo to production evaluation.

## 4:25–5:00 — Consulting deliverables and decision

The repository closes the implementation loop with current and future process diagrams, source-to-target mapping, data-quality evidence, KPI definitions, a traceability matrix, twenty-eight UAT scenarios, cutover and rollback steps, go-live monitoring, user training, and a formula-driven implementation workbook. The seed-42 result is a conditional go: data quality passes and three targets are met, while unapplied cash, DSO, CEI, and past-due AR need hypercare. That honest gap is the point. The project demonstrates how to deploy and govern an O2C capability, not just move finance data.

