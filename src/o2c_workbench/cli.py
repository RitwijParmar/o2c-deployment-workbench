from __future__ import annotations

import argparse
from pathlib import Path

from o2c_workbench.dashboard import render_dashboard
from o2c_workbench.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic O2C customer implementation benchmark.")
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--config", default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_pipeline(args.project_root, args.config, args.seed)
    render_dashboard(result["summary"], result["exceptions"], result["worklist"], Path(args.project_root) / "output" / "dashboard.html")
    print(f"Implementation benchmark complete: {Path(args.project_root) / 'output' / 'dashboard.html'}")
    print(result["summary"]["implementation"]["benchmark_disclaimer"])


if __name__ == "__main__":
    main()

