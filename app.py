from pathlib import Path

import streamlit as st

from o2c_workbench.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="O2C Deployment Workbench", page_icon="💳", layout="wide")
st.title("O2C Deployment Workbench")
st.caption("Synthetic ERP receivables integration and controlled implementation benchmark")

st.warning("All ERP files and KPI changes in this demo are synthetic. Results are controlled implementation benchmarks, not real customer outcomes.")

seed = st.sidebar.number_input("Synthetic data seed", min_value=1, max_value=9999, value=42)
if st.sidebar.button("Run implementation", type="primary") or "result" not in st.session_state:
    st.session_state.result = run_pipeline(ROOT, seed=int(seed))

result = st.session_state.result
summary = result["summary"]

st.subheader("Current state vs configured future state")
columns = st.columns(4)
for index, row in enumerate(summary["kpi_comparison"]):
    before, after = row["baseline"], row["future"]
    if row["unit"] == "currency":
        display, delta = f"${after:,.0f}", f"${after-before:,.0f}"
    elif row["unit"] in {"percent", "percent_points"}:
        scale = 100 if row["unit"] == "percent" else 1
        display, delta = f"{after*scale:.1f}%", f"{(after-before)*scale:+.1f} pp"
    else:
        display, delta = f"{after:.1f}", f"{after-before:+.1f}"
    columns[index % 4].metric(row["label"], display, delta, delta_color="normal" if row["direction"] == "higher" else "inverse")

left, right = st.columns([1, 1.35])
with left:
    st.subheader("Future-state match distribution")
    st.bar_chart(summary["match_method_distribution"])
with right:
    st.subheader("Highest collection priorities")
    st.dataframe(result["worklist"][:20], use_container_width=True, hide_index=True)

st.subheader("Routed exceptions")
st.dataframe(result["exceptions"], use_container_width=True, hide_index=True)

with st.expander("Data-quality controls"):
    st.json(result["dq_report"])

