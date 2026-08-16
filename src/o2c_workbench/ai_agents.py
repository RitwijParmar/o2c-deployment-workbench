from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pydantic import BaseModel, Field

from o2c_workbench.io_utils import read_csv, read_json, write_json


class AgentRecommendation(BaseModel):
    classification: str
    evidence: list[str]
    proposed_action: str
    confidence: float = Field(ge=0, le=1)
    human_approval_required: bool


def run_model_review(project_root: Path, case_id: str) -> AgentRecommendation:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for the optional model-backed review. The core demo runs offline without it.")
    from agents import Agent, Runner, function_tool

    exception_rows = read_csv(project_root / "output" / "exception_queue.csv")
    worklist_rows = read_csv(project_root / "output" / "collection_worklist.csv")

    @function_tool
    def get_exception(payment_id: str) -> str:
        """Return the synthetic exception evidence for one payment identifier."""
        return json.dumps(next((row for row in exception_rows if row["payment_id"] == payment_id), {}))

    @function_tool
    def get_collection_context(customer_id: str) -> str:
        """Return the highest-priority synthetic collection items for a customer."""
        return json.dumps([row for row in worklist_rows if row["customer_id"] == customer_id][:5])

    shared = "Use only supplied synthetic evidence. Never claim a real ERP action occurred. ERP posting, write-off, refund, and master-data changes always require human approval."
    cash_agent = Agent(name="Cash Application Agent", instructions=shared + " Investigate payment matching and remittance exceptions.", tools=[get_exception], output_type=AgentRecommendation)
    data_agent = Agent(name="Data Quality Agent", instructions=shared + " Investigate duplicates and invalid source records.", tools=[get_exception], output_type=AgentRecommendation)
    collections_agent = Agent(name="Collections Agent", instructions=shared + " Assess broken promises and collection priority.", tools=[get_collection_context], output_type=AgentRecommendation)
    triage = Agent(
        name="O2C Supervisor Agent",
        instructions=shared + " Triage the case to exactly one specialist and return its structured recommendation.",
        handoffs=[cash_agent, data_agent, collections_agent],
        model=os.getenv("O2C_AGENT_MODEL", "gpt-5.4-mini"),
    )
    result = Runner.run_sync(triage, f"Review synthetic O2C case {case_id}. Use evidence tools and do not execute financial changes.")
    recommendation = result.final_output
    if not isinstance(recommendation, AgentRecommendation):
        recommendation = AgentRecommendation.model_validate_json(str(recommendation))
    if recommendation.proposed_action in {"POST_TO_ERP", "WRITE_OFF", "REFUND", "CHANGE_CUSTOMER_MASTER"} and not recommendation.human_approval_required:
        raise ValueError("Guardrail failure: a controlled financial action was not marked for human approval")
    return recommendation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one optional model-backed multi-agent exception review.")
    parser.add_argument("case_id")
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args()
    root = Path(args.project_root)
    recommendation = run_model_review(root, args.case_id)
    destination = root / "output" / "model_agent_review.json"
    write_json(destination, recommendation.model_dump())
    print(destination)


if __name__ == "__main__":
    main()

