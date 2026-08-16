from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _fmt(row: dict[str, Any], key: str, value: float) -> str:
    unit = row["unit"]
    if unit == "currency":
        return f"${value:,.0f}"
    if unit == "percent":
        return f"{value:.1%}"
    if unit == "percent_points":
        return f"{value:.1f}%"
    if unit == "days":
        return f"{value:.1f} days"
    return f"{value:.1f} hrs"


def render_dashboard(summary: dict[str, Any], exceptions: list[dict[str, Any]], worklist: list[dict[str, Any]], output_path: str | Path) -> None:
    cards = []
    for row in summary["kpi_comparison"]:
        before = _fmt(row, "baseline", row["baseline"])
        after = _fmt(row, "future", row["future"])
        target = _fmt(row, "target", row["target"])
        status = "Target met" if row["target_met"] else "Below target"
        status_class = "good" if row["target_met"] else "warn"
        cards.append(f"<article class='card'><div class='eyebrow'>{html.escape(row['label'])}</div><div class='value'>{after}</div><div class='comparison'>Baseline {before}</div><div class='target {status_class}'>{status}: {target}</div></article>")

    distribution = summary["match_method_distribution"]
    max_count = max(distribution.values()) if distribution else 1
    bars = "".join(f"<div class='bar-row'><span>{html.escape(method.replace('_', ' ').title())}</span><div class='bar-track'><div class='bar' style='width:{count / max_count * 100:.1f}%'></div></div><b>{count}</b></div>" for method, count in sorted(distribution.items(), key=lambda item: -item[1]))
    exception_rows = "".join(f"<tr><td>{html.escape(row['payment_id'])}</td><td>{html.escape(row['route_code'])}</td><td>${row['payment_amount_usd']:,.2f}</td><td>{html.escape(row['assigned_team'])}</td><td>{html.escape(row['reason'])}</td></tr>" for row in exceptions[:12])
    worklist_rows = "".join(f"<tr><td>{html.escape(row['customer_name'])}</td><td>{html.escape(row['invoice_number'])}</td><td>${row['open_balance_usd']:,.2f}</td><td>{row['days_past_due']}</td><td><span class='pill {row['priority'].lower()}'>{row['priority']}</span></td><td>{row['priority_score']:.1f}</td></tr>" for row in worklist[:12])
    payload = html.escape(json.dumps(summary, indent=2))
    document = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>O2C Deployment Workbench</title>
<style>
:root{{--navy:#0b1f33;--blue:#1769aa;--cyan:#30b6c9;--paper:#f4f7fa;--ink:#17212b;--muted:#617181;--green:#177a55;--amber:#b56a00;--red:#a93c3c}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;color:var(--ink)}}
header{{background:linear-gradient(120deg,var(--navy),#123f63);color:white;padding:34px 5vw 28px}} header h1{{margin:5px 0 8px;font-size:34px;letter-spacing:-.03em}} header p{{margin:0;color:#c8d8e6;max-width:920px;line-height:1.5}} .tag{{display:inline-block;background:#1d567e;border:1px solid #4f86ab;padding:5px 10px;border-radius:99px;font-size:12px}}
main{{padding:28px 5vw 60px;max-width:1500px;margin:auto}} .notice{{background:#fff8e6;border-left:5px solid #e2a532;padding:13px 16px;margin-bottom:22px;border-radius:7px;line-height:1.4}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:14px}} .card{{background:white;border:1px solid #dce5ec;border-radius:12px;padding:18px;box-shadow:0 4px 16px #0b1f330d}} .eyebrow{{text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--muted);font-weight:700}} .value{{font-size:30px;font-weight:750;margin:9px 0 4px;color:var(--navy)}} .comparison{{font-size:13px;color:var(--muted)}} .target{{font-size:12px;margin-top:12px;font-weight:700}} .good{{color:var(--green)}} .warn{{color:var(--amber)}}
.two{{display:grid;grid-template-columns:1fr 1.35fr;gap:18px;margin-top:20px}} section{{background:white;border:1px solid #dce5ec;border-radius:12px;padding:20px}} h2{{font-size:18px;margin:0 0 16px}} .bar-row{{display:grid;grid-template-columns:190px 1fr 35px;gap:10px;align-items:center;font-size:13px;margin:9px 0}} .bar-track{{height:10px;background:#eaf0f4;border-radius:8px;overflow:hidden}} .bar{{height:100%;background:linear-gradient(90deg,var(--blue),var(--cyan));border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}} th{{text-align:left;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #dce5ec;padding:8px}} td{{border-bottom:1px solid #edf1f4;padding:9px 8px;vertical-align:top}} .pill{{font-size:10px;font-weight:800;border-radius:99px;padding:4px 7px}} .critical{{background:#fde7e7;color:#9e2828}} .high{{background:#fff0d5;color:#8a5200}} .medium{{background:#e6f0ff;color:#275d9b}} .low{{background:#e5f7ef;color:#1a6f50}} details{{margin-top:20px}} pre{{overflow:auto;background:#0b1f33;color:#d4e6f5;padding:16px;border-radius:8px}}
@media(max-width:1000px){{.grid{{grid-template-columns:repeat(2,1fr)}}.two{{grid-template-columns:1fr}}}} @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style></head>
<body><header><span class='tag'>Controlled implementation benchmark</span><h1>O2C Deployment Workbench</h1><p>{html.escape(summary['implementation']['customer_name'])} · as of {summary['implementation']['as_of_date']} · ERP receivables integration simulation</p></header>
<main><div class='notice'><strong>Synthetic-data notice.</strong> {html.escape(summary['disclaimers'][0])} {html.escape(summary['disclaimers'][1])}</div>
<div class='grid'>{''.join(cards)}</div>
<div class='two'><section><h2>Future-state match methods</h2>{bars}</section><section><h2>Priority collection worklist</h2><table><thead><tr><th>Customer</th><th>Invoice</th><th>Open</th><th>Days late</th><th>Priority</th><th>Score</th></tr></thead><tbody>{worklist_rows}</tbody></table></section></div>
<section style='margin-top:20px'><h2>Exception routing queue</h2><table><thead><tr><th>Payment</th><th>Exception</th><th>Amount</th><th>Assigned team</th><th>Reason</th></tr></thead><tbody>{exception_rows}</tbody></table></section>
<details><summary>Benchmark payload</summary><pre>{payload}</pre></details></main></body></html>"""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")

