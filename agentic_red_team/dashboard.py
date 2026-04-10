import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import glob
from datetime import datetime
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config

st.set_page_config(page_title="Agentic Prism: Node X", page_icon="💎", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .metric-card { background: #111; border: 1px solid #333; padding: 20px; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADER ---
def load_telemetry():
    files = glob.glob(os.path.join(config.EVIDENCE_DIR, "telemetry_*.json"))
    all_data = []
    for f in files:
        with open(f, "r") as src:
            all_data.extend(json.load(src))
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

df = load_telemetry()

st.title("💎 Agentic Prism: Muscle Monitor")
st.caption("Node X Sentinel | Always-On Telemetry Feed")

tab_ops, tab_currency, tab_skunk, tab_evidence = st.tabs([
    "🚀 Mission Control",
    "💸 Data Currency",
    "🧪 Skunkworks Audit",
    "📹 Evidence Locker"
])

with tab_currency:
    st.header("💸 The Burn Report (Resource Currency)")
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Cost", f"${df['cost_usd'].sum():.4f}")
        c2.metric("Carbon Footprint", f"{df['co2_grams'].sum():.2f}g")
        c3.metric("Avg Latency", f"{df['duration_sec'].mean():.2f}s")
        c4.metric("Hardware Stress", f"{df['cpu_delta'].max():.1f}% CPU Spike")

        st.divider()
        st.subheader("Safety vs. Cost Correlation")
        fig = px.scatter(df, x="cost_usd", y="resilience_score", color="target",
                         size="duration_sec", hover_data=["prompt_id"],
                         title="High Cost / Low Resilience detection")
        st.plotly_chart(fig, use_container_width=True)

with tab_skunk:
    st.header("🧪 Skunkworks: Hidden Element Audit")
    if not df.empty:
        leeches = df[df['skunk_bites'] > 0]
        if not leeches.empty:
            st.warning(f"🚨 ALERT: {len(leeches)} Leeching attempts detected in latest missions.")
            st.table(leeches[["timestamp", "target", "prompt_id", "skunk_bites", "resilience_score"]])
        else:
            st.success("No hidden DOM interaction detected. Models are operating on visual layer only.")

# (Remaining Tab logic for Evidence and Ops remains consistent with provided files)