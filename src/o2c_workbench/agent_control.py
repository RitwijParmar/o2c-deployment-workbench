from __future__ import annotations

from typing import Any

from o2c_workbench.io_utils import write_csv, write_json
from o2c_workbench.observability import Telemetry


def _specialist(exception: dict[str, Any]) -> tuple[str, str, str, float]:
    code = exception["route_code"]
    if code == "DUPLICATE_PAYMENT":
        return "Data Quality Agent", "RECOMMEND_ROUTE", "Repeated bank transaction identifier; preserve the first record and recommend quarantine to the data steward.", 0.99
    if code == "OVERPAYMENT_RESIDUAL":
        return "Cash Application Agent", "RETAIN_CUSTOMER_CREDIT", "Referenced invoice was cleared and the residual must remain unapplied until a human selects credit or refund treatment.", 0.96
    if code == "HIGH_VALUE_UNMATCHED":
        return "Cash Application Agent", "RECOMMEND_ROUTE", "No deterministic invoice evidence and value exceeds the configured approval threshold; recommend senior-analyst escalation.", 0.98
    return "Cash Application Agent", "DRAFT_COLLECTION_ACTION", "No deterministic invoice evidence; draft a remittance request before any posting recommendation.", 0.94


def run_offline_agent_control(
    summary: dict[str, Any],
    exceptions: list[dict[str, Any]],
    worklist: list[dict[str, Any]],
    config: dict[str, Any],
    telemetry: Telemetry,
    output_root: Any,
) -> dict[str, Any]:
    """Deterministic reviewer-safe path; the optional LLM path lives in ai_agents.py."""
    limit = int(config["agentic_control"]["offline_case_limit"])
    decisions: list[dict[str, Any]] = []
    for exception in exceptions[:limit]:
        with telemetry.span(
            "invoke_agent Supervisor Agent",
            {
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.workflow.name": config["observability"]["workflow_name"],
                "gen_ai.agent.name": "Supervisor Agent",
                "o2c.case.type": exception["route_code"],
            },
        ):
            specialist, action, rationale, confidence = _specialist(exception)
            with telemetry.span(
                f"handoff Supervisor Agent to {specialist}",
                {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": f"transfer_to_{specialist.lower().replace(' ', '_')}"},
            ):
                with telemetry.span(
                    f"invoke_agent {specialist}",
                    {
                        "gen_ai.operation.name": "invoke_agent",
                        "gen_ai.workflow.name": config["observability"]["workflow_name"],
                        "gen_ai.agent.name": specialist,
                        "o2c.decision.confidence": confidence,
                    },
                ):
                    approval = action not in config["agentic_control"]["allowed_autonomous_actions"]
                    decisions.append(
                        {
                            "case_id": exception["payment_id"],
                            "supervisor": "Supervisor Agent",
                            "specialist": specialist,
                            "recommended_action": action,
                            "assigned_team": exception["assigned_team"],
                            "confidence": confidence,
                            "human_approval_required": approval,
                            "rationale": rationale,
                            "execution_status": "RECOMMENDATION_ONLY",
                        }
                    )

    with telemetry.span(
        "invoke_agent Collections Agent",
        {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.workflow.name": config["observability"]["workflow_name"],
            "gen_ai.agent.name": "Collections Agent",
            "o2c.worklist.records": len(worklist),
        },
    ):
        collection_brief = {
            "critical_accounts": sum(row["priority"] == "CRITICAL" for row in worklist),
            "broken_promises": sum(bool(row["broken_promise"]) for row in worklist),
            "highest_priority_action": "Call broken-promise accounts first, then work descending configured score.",
        }

    unmet = [row["label"] for row in summary["kpi_comparison"] if not row["target_met"]]
    with telemetry.span(
        "invoke_agent Go Live Monitor Agent",
        {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.workflow.name": config["observability"]["workflow_name"],
            "gen_ai.agent.name": "Go Live Monitor Agent",
            "o2c.kpi.targets_unmet": len(unmet),
            "o2c.data_quality.status": summary["data_quality"]["status"],
        },
    ):
        readiness = "CONDITIONAL_GO" if summary["data_quality"]["status"] == "PASS" and len(unmet) <= 4 else "NO_GO"
        go_live = {
            "recommendation": readiness,
            "unmet_targets": unmet,
            "conditions": ["Retain human approval for all ERP posting, write-off, refund, and master-data actions.", "Operate a hypercare queue for unapplied cash and residual overpayments."],
        }

    write_csv(output_root / "agent_decisions.csv", decisions)
    write_json(output_root / "agent_control_summary.json", {"mode": "offline_deterministic", "decision_count": len(decisions), "collection_brief": collection_brief, "go_live": go_live})
    return {"mode": "offline_deterministic", "decision_count": len(decisions), "collection_brief": collection_brief, "go_live": go_live}
