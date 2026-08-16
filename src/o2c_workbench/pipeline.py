from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from o2c_workbench.agent_control import run_offline_agent_control
from o2c_workbench.adapters.netsuite import NetSuiteAdapter
from o2c_workbench.adapters.oracle import OracleFusionAdapter
from o2c_workbench.adapters.sap import SAPS4HANAAdapter
from o2c_workbench.collections import build_collection_worklist
from o2c_workbench.generator import generate_raw_exports
from o2c_workbench.io_utils import load_yaml, write_csv, write_json
from o2c_workbench.kpis import calculate_kpis, compare_kpis
from o2c_workbench.matching import run_matching
from o2c_workbench.observability import Telemetry
from o2c_workbench.validation import validate


ADAPTERS = {
    "SAP_S4HANA_SIM": SAPS4HANAAdapter,
    "ORACLE_FUSION_SIM": OracleFusionAdapter,
    "NETSUITE_SIM": NetSuiteAdapter,
}


def load_canonical(config: dict[str, Any], raw_root: Path) -> dict[str, list[dict[str, Any]]]:
    canonical = {entity: [] for entity in ["customers", "invoices", "payments", "remittances", "deductions", "promises_to_pay", "collection_activities"]}
    for source_code, source_config in config["sources"].items():
        adapter = ADAPTERS[source_code](source_code, source_config, raw_root)
        extracted = adapter.extract()
        for entity, rows in extracted.items():
            canonical[entity].extend(rows)
    return canonical


def _route_exceptions(matches: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    routes = config["exception_routing"]
    routed = []
    for row in matches:
        if not row["exception_code"]:
            continue
        route_code = row["exception_code"]
        if route_code == "UNMATCHED_CASH" and row["payment_amount_usd"] >= 10000:
            route_code = "HIGH_VALUE_UNMATCHED"
        routed.append({**row, "route_code": route_code, "assigned_team": routes[route_code]})
    return routed


def run_pipeline(project_root: str | Path, config_path: str | Path | None = None, seed: int = 42) -> dict[str, Any]:
    root = Path(project_root)
    config_path = Path(config_path) if config_path else root / "config" / "customer_implementation.yaml"
    config = load_yaml(config_path)
    raw_root = root / "data" / "raw"
    canonical_root = root / "data" / "canonical"
    output_root = root / "output"
    trace_path = root / config["observability"]["trace_file"]
    telemetry = Telemetry(trace_path, config["observability"]["service_name"])
    with telemetry.span("generate simulated ERP exports", {"o2c.synthetic.seed": seed, "o2c.erp.source_count": len(config["sources"])}):
        generated_counts = generate_raw_exports(config, raw_root, seed=seed)
    with telemetry.span("canonicalize receivables", {"o2c.entity.type.count": 7}):
        canonical = load_canonical(config, raw_root)
    for entity, rows in canonical.items():
        write_csv(canonical_root / f"{entity}.csv", rows)

    with telemetry.span("validate canonical controls", {"o2c.validation.check_count": len(config["validation_checks"])}):
        dq_report = validate(canonical, set(config["fx_to_usd"]))
    with telemetry.span("match baseline cash", {"o2c.benchmark.state": "current"}):
        baseline = run_matching(canonical, config, "baseline")
    with telemetry.span("match configured cash", {"o2c.benchmark.state": "future"}):
        future = run_matching(canonical, config, "future")
    with telemetry.span("calculate controlled KPIs", {"o2c.kpi.count": len(config["kpi_targets"])}):
        baseline_kpis = calculate_kpis(canonical, baseline, config, "baseline")
        future_kpis = calculate_kpis(canonical, future, config, "future")
    comparison = compare_kpis(baseline_kpis, future_kpis, config["kpi_targets"])
    worklist = build_collection_worklist(canonical, future["invoices"], config)
    exceptions = _route_exceptions(future["matches"], config)
    match_distribution = Counter(row["match_method"] for row in future["matches"])

    write_csv(output_root / "baseline_matches.csv", baseline["matches"])
    write_csv(output_root / "future_matches.csv", future["matches"])
    write_csv(output_root / "future_allocations.csv", future["allocations"])
    write_csv(output_root / "exception_queue.csv", exceptions)
    write_csv(output_root / "collection_worklist.csv", worklist)
    write_csv(output_root / "kpi_comparison.csv", comparison)
    write_json(output_root / "data_quality_report.json", dq_report)

    summary = {
        "implementation": config["implementation"],
        "generated_counts": generated_counts,
        "canonical_counts": {entity: len(rows) for entity, rows in canonical.items()},
        "data_quality": {key: value for key, value in dq_report.items() if key != "issues"},
        "baseline_kpis": baseline_kpis,
        "future_kpis": future_kpis,
        "kpi_comparison": comparison,
        "match_method_distribution": dict(match_distribution),
        "exception_count": len(exceptions),
        "collection_worklist_count": len(worklist),
        "disclaimers": [config["implementation"]["source_disclaimer"], config["implementation"]["benchmark_disclaimer"]],
    }
    agent_control = run_offline_agent_control(summary, exceptions, worklist, config, telemetry, output_root)
    telemetry_summary = telemetry.summarize()
    write_json(output_root / "telemetry" / "summary.json", telemetry_summary)
    summary["agentic_control"] = agent_control
    summary["observability"] = telemetry_summary
    write_json(output_root / "benchmark_summary.json", summary)
    return {"config": config, "canonical": canonical, "dq_report": dq_report, "baseline": baseline, "future": future, "exceptions": exceptions, "worklist": worklist, "agent_control": agent_control, "summary": summary}
