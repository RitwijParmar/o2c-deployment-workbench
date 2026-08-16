from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from o2c_workbench.mcp_server import server
from o2c_workbench.pipeline import run_pipeline


@pytest.fixture(scope="module")
def result():
    return run_pipeline(Path(__file__).resolve().parents[1], seed=42)


def test_three_sources_and_seven_entities(result):
    assert len(result["config"]["sources"]) == 3
    assert set(result["canonical"]) == {"customers", "invoices", "payments", "remittances", "deductions", "promises_to_pay", "collection_activities"}
    assert sum(len(rows) for rows in result["canonical"].values()) == 1908


def test_data_quality_passes_with_intentional_duplicate_warnings(result):
    report = result["dq_report"]
    assert report["status"] == "PASS"
    assert report["error_count"] == 0
    assert report["warning_count"] == 18
    assert {issue["check_id"] for issue in report["issues"]} == {"VAL-007"}


def test_future_state_improves_every_required_kpi(result):
    for row in result["summary"]["kpi_comparison"]:
        if row["direction"] == "higher":
            assert row["future"] > row["baseline"], row["metric"]
        else:
            assert row["future"] < row["baseline"], row["metric"]


def test_difficult_cash_cases_are_evidenced(result):
    methods = {row["match_method"] for row in result["future"]["matches"]}
    assert {"REFERENCE", "PARTIAL_REFERENCE", "OVERPAYMENT_APPLY", "ONE_TO_MANY_REMITTANCE", "AMOUNT_INFERENCE", "DEDUCTION_SUPPORTED_SHORT_PAY", "DUPLICATE_DETECTED", "UNMATCHED"} <= methods
    bulk = next(row for row in result["future"]["matches"] if row["benchmark_case"] == "ONE_PAYMENT_MULTI_INVOICE")
    assert len(bulk["matched_invoice_ids"].split(";")) == 2
    split_allocations = [row for row in result["future"]["allocations"] if row["invoice_id"].endswith("-06")]
    assert len(split_allocations) == 108


def test_exception_routing_and_human_gate(result):
    routes = {row["route_code"] for row in result["exceptions"]}
    assert {"DUPLICATE_PAYMENT", "UNMATCHED_CASH", "OVERPAYMENT_RESIDUAL"} <= routes
    assert result["agent_control"]["go_live"]["recommendation"] == "CONDITIONAL_GO"
    decisions = result["agent_control"]["decision_count"]
    assert decisions == result["config"]["agentic_control"]["offline_case_limit"]


def test_mcp_capabilities_are_discoverable():
    tools = asyncio.run(server.list_tools())
    resources = asyncio.run(server.list_resources())
    prompts = asyncio.run(server.list_prompts())
    assert {tool.name for tool in tools} == {"get_implementation_summary", "investigate_payment", "get_collection_priority", "run_controlled_benchmark"}
    assert len(resources) == 3
    assert len(prompts) == 2


def test_observability_has_agent_spans_and_no_content_capture(result):
    telemetry = result["summary"]["observability"]
    assert telemetry["error_span_count"] == 0
    assert telemetry["agent_span_count"] >= 4
    assert telemetry["content_capture_enabled"] is False

