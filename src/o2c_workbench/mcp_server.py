from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from o2c_workbench.io_utils import load_yaml, read_csv, read_json
from o2c_workbench.pipeline import run_pipeline


ROOT = Path(os.getenv("O2C_PROJECT_ROOT", Path(__file__).resolve().parents[2]))
server = MCPServer(
    name="o2c-deployment-workbench",
    title="O2C Deployment Workbench",
    version="1.0.0",
    instructions="Read-only investigation tools over clearly synthetic ERP receivables evidence. Financial actions are recommendations only.",
)


@server.resource("o2c://configuration", mime_type="application/json")
def configuration_resource() -> str:
    return json.dumps(load_yaml(ROOT / "config" / "customer_implementation.yaml"), indent=2)


@server.resource("o2c://benchmark", mime_type="application/json")
def benchmark_resource() -> str:
    return json.dumps(read_json(ROOT / "output" / "benchmark_summary.json"), indent=2)


@server.resource("o2c://observability", mime_type="application/json")
def observability_resource() -> str:
    return json.dumps(read_json(ROOT / "output" / "telemetry" / "summary.json"), indent=2)


@server.tool()
def get_implementation_summary() -> dict[str, Any]:
    """Return controlled benchmark KPIs, data-quality status, disclaimers, and agent readiness."""
    return read_json(ROOT / "output" / "benchmark_summary.json")


@server.tool()
def investigate_payment(payment_id: str) -> dict[str, Any]:
    """Return matching evidence and exception routing for one synthetic payment."""
    matches = read_csv(ROOT / "output" / "future_matches.csv")
    exceptions = read_csv(ROOT / "output" / "exception_queue.csv")
    return {
        "match": next((row for row in matches if row["payment_id"] == payment_id), {}),
        "exception": next((row for row in exceptions if row["payment_id"] == payment_id), {}),
        "financial_action_executed": False,
    }


@server.tool()
def get_collection_priority(invoice_id: str) -> dict[str, Any]:
    """Return the configured collection score evidence for one synthetic invoice."""
    rows = read_csv(ROOT / "output" / "collection_worklist.csv")
    return next((row for row in rows if row["invoice_id"] == invoice_id), {})


@server.tool()
def run_controlled_benchmark(seed: int = 42) -> dict[str, Any]:
    """Regenerate synthetic source exports and controlled benchmark outputs; never connects to a genuine ERP."""
    return run_pipeline(ROOT, seed=seed)["summary"]


@server.prompt()
def investigate_cash_exception(payment_id: str) -> str:
    return f"Investigate synthetic payment {payment_id}. Read its evidence, classify the exception, recommend a route, and require human approval for any financial action."


@server.prompt()
def assess_go_live() -> str:
    return "Assess go-live readiness from the synthetic benchmark, data-quality controls, unmet KPI targets, and agent telemetry. Do not describe the KPI movement as real customer impact."


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve O2C workbench tools and resources over MCP.")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.transport == "stdio":
        server.run()
    else:
        server.run(transport="streamable-http", host=args.host, port=args.port, streamable_http_path="/mcp")


if __name__ == "__main__":
    main()
