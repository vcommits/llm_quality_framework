import streamlit as st
import subprocess
import os
import sys
import json
import pandas as pd
import plotly.express as px
import glob
from datetime import datetime

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config

# --- CONFIG & BRANDING ---
st.set_page_config(page_title="Agentic Prism", page_icon="💎", layout="wide")

col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.write("# 💎")
with col_title:
    st.title("Agentic Prism")
    st.caption("Unified AI Security (Red) & Quality Assurance (Blue) Platform")


# --- DATA LOADER ---
@st.cache_data
def load_history():
    history_path = os.path.join(config.EVIDENCE_DIR, "run_history.json")
    if not os.path.exists(history_path):
        return []
    try:
        with open(history_path, "r") as f:
            return json.load(f)
    except:
        return []


history = load_history()

# --- TABS ---
tab_ops, tab_safety, tab_quality, tab_evidence = st.tabs([
    "🚀 Mission Control",
    "🛡️ Safety Analysis",
    "📊 Quality Metrics",
    "📹 Evidence Locker"
])

# ==============================================================================
# TAB 1: OPERATIONS
# ==============================================================================
with tab_ops:
    col_config, col_action = st.columns([1, 2])

    with col_config:
        st.subheader("🎯 Target Configuration")
        targets = TargetRegistry.TARGETS
        # Convert keys to list for selectbox
        target_keys = list(targets.keys())
        selected_target_key = st.selectbox("Active Agent", target_keys,
                                           format_func=lambda
                                               x: f"{targets[x]['name']} ({'Desktop' if targets[x].get('is_app') else 'Web'})")
        target_info = targets[selected_target_key]

        with st.container(border=True):
            st.markdown(f"**Target:** `{target_info['name']}`")
            st.markdown(f"**Port:** `{target_info.get('debug_port', 'Auto')}`")
            st.markdown(f"**Path:** `{target_info.get('exe_path', 'N/A')[-40:]}...`")

        st.divider()

        if st.button("🧹 Cleanse Ports (Kill Fleet)", use_container_width=True):
            with st.spinner("Terminating Zombie Processes..."):
                subprocess.run([sys.executable, "agentic_red_team/utils/kill_fleet.py"])
            st.success("Environment Clean.")

        if st.button(f"🚀 Launch App", type="primary", use_container_width=True):
            subprocess.Popen([sys.executable, "agentic_red_team/utils/launch.py", selected_target_key])
            st.toast(f"Launching {target_info['name']}...")

    with col_action:
        st.subheader("⚔️ Campaign Execution")

        mission_type = st.radio("Select Operation Type", [
            "🟢 Connection Test (Authenticated Happy Path)",
            "🧠 Persona Injection (Prime Memories)",
            "👻 Privacy Audit (Ghost User Persistence)",
            "⚖️  Ethics & Safety Benchmark (Standard)",
            "🧠 Psychological Safety Audit (High Risk)",
            "🤖 Swarm Simulation (Problem Pairing)",
            "🧨 Stress Testing (Jailbreak Fuzzer)"
        ], horizontal=True)

        # --- DYNAMIC CONFIGURATION PANEL ---
        st.divider()
        st.markdown("#### 🛠️ Mission Parameters")

        cmd_args = []
        script = ""

        # 1. HAPPY PATH CONFIG
        if "Happy Path" in mission_type:
            prompt = st.text_input("Injection Prompt", "Hello Nova, tell me a secret.")
            # FIX: Ensure prompt is never empty to prevent argparse crash
            if not prompt.strip(): prompt = "Hello Nova"
            cmd_args.extend(["--prompt", prompt])
            script = "agentic_red_team/campaigns/authenticated_test.py"

        # 2. EVALUATION CONFIG (Ethics/Psych)
        elif "Benchmark" in mission_type or "Psychological" in mission_type:
            c1, c2 = st.columns(2)
            with c1:
                judge = st.selectbox("Evaluator Model (Judge)",
                                     ["evaluator_judge_gpt4", "evaluator_judge_glider", "evaluator_judge_flow",
                                      "evaluator_judge_llama"])
            with c2:
                st.info("💡 Comparing judges (SLM vs Frontier) helps establish baselines.")

            script = "agentic_red_team/campaigns/run_ethics_eval.py" if "Ethics" in mission_type else "agentic_red_team/campaigns/run_psych_eval.py"
            cmd_args.extend(["--judge", judge])

        # 3. SWARM CONFIG
        elif "Swarm" in mission_type:
            st.info("🐝 Simulates a conversation between two AI agents.")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Agent A (Leader/Bad Actor)**")
                provider_a = st.selectbox("Provider A", ["together_ai", "huggingface", "openai", "google"], key="pa")
                model_a = st.text_input("Model A Name", "meta-llama/Llama-3-70b-chat-hf", key="ma")
            with col_b:
                st.markdown("**Agent B (Follower/Target)**")
                provider_b = st.selectbox("Provider B", ["together_ai", "huggingface", "openai", "google"], key="pb")
                model_b = st.text_input("Model B Name", "mistralai/Mistral-7B-Instruct-v0.2", key="mb")

            turns = st.slider("Turns", 1, 10, 3)
            script = "agentic_red_team/campaigns/multi_agent_sim.py"
            cmd_args.extend(
                ["--model-a", model_a, "--provider-a", provider_a, "--model-b", model_b, "--provider-b", provider_b,
                 "--turns", str(turns)])

        # 4. DEFAULT / OTHERS
        elif "Prime" in mission_type:
            script = f"agentic_red_team/campaigns/prime_{selected_target_key}.py"
        elif "Ghost" in mission_type:
            script = "agentic_red_team/campaigns/ghost_memory.py"
        elif "Fuzzer" in mission_type:
            script = "agentic_red_team/fuzzer.py"

        # --- EXECUTION BUTTON ---
        if st.button("🔥 INITIALIZE CAMPAIGN", type="primary", use_container_width=True):
            # Fallback for Primers
            if "Prime" in mission_type and not os.path.exists(script):
                st.warning(f"No specific primer found for {selected_target_key}. Using generic fallback.")
                script = "agentic_red_team/campaigns/authenticated_test.py"

                # Check if prompt arg is already present (it might be from above logic)
                has_prompt = False
                for arg in cmd_args:
                    if arg == "--prompt": has_prompt = True

                if not has_prompt:
                    cmd_args.extend(["--prompt", "Hello Agent (Priming Fallback)"])

            # Build Command
            cmd = [sys.executable, script]

            # Most scripts take target as first arg (except Swarm/Fuzzer handles differently)
            if "Swarm" not in mission_type and "Fuzzer" not in mission_type:
                cmd.append(selected_target_key)

            cmd.extend(cmd_args)

            # Fix for Windows Unicode Error: Force UTF-8 environment
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"

            with st.status(f"Executing: {mission_type}...", expanded=True):
                st.write(f"📜 Script: `{os.path.basename(script)}`")
                st.code(f"{' '.join(cmd)}", language="bash")

                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1, universal_newlines=True,
                    env=env, encoding="utf-8"
                )
                log_area = st.empty()
                logs = ""
                for line in process.stdout:
                    logs += line
                    log_area.code(logs[-3000:], language="bash")

                process.wait()
                if process.returncode == 0:
                    st.success("✅ Mission Complete.")
                    st.cache_data.clear()
                else:
                    st.error("❌ Mission Failed.")

# ==============================================================================
# TAB 2: SAFETY ANALYSIS
# ==============================================================================
with tab_safety:
    st.header("🛡️ Security & Ethics Report")

    if not history:
        st.info("No audit history found.")
    else:
        flat_data = []
        for run in history:
            # Handle Ethics/Psych/Swarm Data
            ts = pd.to_datetime(run['timestamp'])

            # Swarm Data
            if "swarm" in run.get('campaign', ''):
                for res in run['results']:
                    flat_data.append({
                        "Date": ts,
                        "Target": f"Swarm: {res.get('pairing', 'Unknown')}",
                        "Category": "Collusion/Sycophancy",
                        "Score": res['verdict'].get('score', 0),
                        "Test": res.get('test_id', 'Unknown')
                    })
            # Standard Benchmark Data
            elif "results" in run:
                for res in run['results']:
                    # FIX: Handle missing 'test' key in newer results by using direct 'category' key
                    # This logic handles both the old structure (nested in 'test') and new structure (flat)
                    cat = res.get('category', res.get('test', {}).get('category', 'Unknown'))

                    # Safely get score
                    score = 0
                    if 'verdict' in res and isinstance(res['verdict'], dict):
                        score = res['verdict'].get('score', 0)

                    # EXTRACT JUDGE
                    # Newer runs save it in 'judge_id' inside the result item
                    # Older/Other runs might have it at the top level 'judge_id' or not at all
                    judge = res.get('judge_id', run.get('judge_id', 'Unknown'))

                    flat_data.append({
                        "Date": ts,
                        "Target": run.get('target', 'Unknown'),
                        "Judge": judge,
                        "Category": cat,
                        "Score": score,
                        "Prompt": res.get('prompt', '')[:50]
                    })

        if flat_data:
            df = pd.DataFrame(flat_data)

            # --- CRITICAL FIX FOR PYARROW ---
            # PyArrow (Streamlit's backend) sometimes fails to infer object columns as datetimes.
            # We force conversion to ensure compatibility.
            df['Date'] = pd.to_datetime(df['Date'])

            # Scorecards
            avg_score = df['Score'].mean()

            m1, m2, m3 = st.columns(3)
            m1.metric("Current Safety Score", f"{avg_score:.1f}/5.0")
            m2.metric("Total Audits", len(df['Date'].unique()))
            m3.metric("Critical Failures", len(df[df['Score'] == 1]))

            # Visuals
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Safety Trend")
                if not df.empty:
                    # Group by Date and Judge to show if judges differ
                    fig = px.line(df.groupby(['Date', 'Target', 'Judge'])['Score'].mean().reset_index(),
                                  x='Date', y='Score', color='Judge', symbol='Target', markers=True, range_y=[0, 5.5])
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("Vulnerability Heatmap")
                if not df.empty:
                    fig2 = px.density_heatmap(df, x="Target", y="Category", z="Score",
                                              color_continuous_scale="RdYlGn", range_color=[1, 5])
                    st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 📋 Audit Log")
            st.dataframe(
                df[["Date", "Target", "Judge", "Category", "Score", "Prompt"]].sort_values("Date", ascending=False),
                use_container_width=True
            )
        else:
            st.info("No safety data points found in history.")

# ==============================================================================
# TAB 3: QUALITY METRICS
# ==============================================================================
with tab_quality:
    st.header("📊 Quality Assurance Metrics")
    st.markdown("North Star Metrics: *Efficiency, Fluency, and Reliability*")

    if history:
        q_data = []
        for run in history:
            if "results" in run:
                ts = pd.to_datetime(run['timestamp'])
                for res in run['results']:
                    m = res.get('metrics', {})
                    # Safe access to nested metrics
                    q_data.append({
                        "Date": ts,
                        "Target": run.get('target', 'Unknown'),
                        "Latency (ms)": m.get('efficiency', {}).get('latency_ms', 0),
                        "Readability": m.get('language_quality', {}).get('readability_score', 0),
                        "Refusal": m.get('safety', {}).get('refusal_detected', False)
                    })

        if q_data:
            df_q = pd.DataFrame(q_data)

            # --- CRITICAL FIX FOR PYARROW (Again) ---
            df_q['Date'] = pd.to_datetime(df_q['Date'])

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("⏱️ Efficiency vs. Complexity")
                fig_scat = px.scatter(df_q, x="Latency (ms)", y="Readability", color="Target", size="Latency (ms)",
                                      title="Latency vs Readability (Top Right is Ideal)")
                st.plotly_chart(fig_scat, use_container_width=True)

            with c2:
                st.subheader("Refusal Rate")
                if not df_q.empty:
                    refusal_rate = df_q.groupby('Target')['Refusal'].mean() * 100
                    st.bar_chart(refusal_rate)

            st.subheader("Metric Distribution")
            st.dataframe(df_q.describe())

# ==============================================================================
# TAB 4: EVIDENCE
# ==============================================================================
with tab_evidence:
    st.header("📹 Evidence Locker")
    files = sorted(glob.glob(os.path.join(config.EVIDENCE_DIR, "*.*")), key=os.path.getmtime, reverse=True)
    if files:
        selected_file = st.selectbox("Select Artifact", [os.path.basename(f) for f in files])
        full_path = os.path.join(config.EVIDENCE_DIR, selected_file)

        if selected_file.endswith(".png"):
            st.image(full_path, caption=selected_file)
        elif selected_file.endswith(".webm"):
            st.video(full_path)
        elif selected_file.endswith(".json"):
            with open(full_path, "r") as f:
                st.json(json.load(f))
        elif selected_file.endswith(".html"):
            with open(full_path, "r", encoding="utf-8") as f:
                st.code(f.read(), language="html")
    else:
        st.info("No evidence found yet.")