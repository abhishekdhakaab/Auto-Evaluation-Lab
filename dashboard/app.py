import json, os, glob
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="AutoEval Lab", layout="wide")

st.title("🧮 AutoEval Lab – Dashboard")

# --- Load index (fast) ---
INDEX_PATH = "experiments/index.json"
if not os.path.exists(INDEX_PATH):
    st.warning("No experiments/index.json found. Run a few evals or backfill first.")
    st.stop()

with open(INDEX_PATH) as f:
    runs = json.load(f)

if not runs:
    st.warning("Index is empty. Run a few evals first.")
    st.stop()

df = pd.DataFrame(runs).sort_values("run_id")
st.subheader("Runs Index")
st.dataframe(df, use_container_width=True)

# --- Filters ---
col1, col2 = st.columns(2)
with col1:
    model = st.selectbox("Filter by model", ["(all)"] + sorted(df["model"].unique()))
with col2:
    mode = st.selectbox(
    "Filter by mode/domain",
    ["(all)"] + sorted(df.get("mode", "(unknown)").fillna("(unknown)").unique())
    )

fdf = df.copy()
if model != "(all)":
    fdf = fdf[fdf["model"] == model]
if mode != "(all)":
    fdf = fdf[fdf["mode"] == mode]

st.subheader("Accuracy Trend")
if fdf.empty:
    st.info("No rows after filtering.")
else:
    fig, ax = plt.subplots()
    ax.plot(range(1, len(fdf)+1), fdf["accuracy"], marker="o")
    ax.set_title("Accuracy over runs")
    ax.set_xlabel("Run # (filtered)")
    ax.set_ylabel("Accuracy")
    ax.grid(True)
    st.pyplot(fig)

# --- Drill into a run ---
st.subheader("Inspect a Run")
choices = [r["run_id"] for r in runs]
sel = st.selectbox("Run ID", choices[::-1])  # newest first
report_path = f"experiments/{sel}_report.json"
records_path = f"experiments/{sel}_records.json"

if os.path.exists(report_path):
    with open(report_path) as f:
        rep = json.load(f)
    st.write("**Report:**", rep)

if os.path.exists(records_path) and st.checkbox("Show records (first 50)"):
    with open(records_path) as f:
        recs = json.load(f)
    st.dataframe(pd.DataFrame(recs[:50]), use_container_width=True)