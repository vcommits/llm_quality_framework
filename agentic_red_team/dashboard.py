import streamlit as st
import subprocess
import os
import sys

# Add path to find our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentic_red_team.targets import TargetRegistry

# --- CONFIG ---
st.set_page_config(page_title="Red Team Console", page_icon="🕵️", layout="wide")

st.title("🕵️ AI Red Team Console")
st.markdown("### LLM Quality & Privacy Framework")

# --- SIDEBAR: TARGET SELECTION ---
st.sidebar.header("🎯 Mission Parameters")

# 1. Get Targets dynamically from targets.py
target_options = list(TargetRegistry.TARGETS.keys())
selected_target = st.sidebar.selectbox("Select Target System", target_options)

# 2. Select Mission
mission_options = {
    "Universal Privacy Check (Guest)": "agentic_red_team/campaigns/universal_privacy.py",
    "Authenticated Happy Path": "agentic_red_team/campaigns/authenticated_test.py",
    "Capture Auth Session (Login Helper)": "agentic_red_team/utils/capture_session.py"
}
selected_mission_name = st.sidebar.selectbox("Select Mission", list(mission_options.keys()))
selected_script = mission_options[selected_mission_name]

# --- MAIN DISPLAY ---
target_info = TargetRegistry.get_target(selected_target)

col1, col2 = st.columns(2)

with col1:
    st.info(f"**Target:** {target_info['name']}")
    st.text(f"URL: {target_info['url']}")

with col2:
    st.warning(f"**Mission:** {selected_mission_name}")
    st.text(f"Script: {selected_script}")

st.divider()

# --- EXECUTION ENGINE ---
if st.button("🚀 LAUNCH MISSION", type="primary", use_container_width=True):
    st.write("### 📜 Mission Logs")
    log_container = st.empty()

    # Construct command
    # We use the current python executable to ensure we use the right venv
    cmd = [sys.executable, selected_script, selected_target]

    try:
        # Run the script and stream output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Live log streaming
        logs = ""
        for line in process.stdout:
            logs += line
            # Clean ANSI codes if necessary, but raw is fine for now
            log_container.code(logs, language="bash")

        process.wait()

        if process.returncode == 0:
            st.success("✅ Mission Complete")

            # Show evidence if it exists
            if "Happy Path" in selected_mission_name:
                evidence_path = os.path.join("agentic_red_team", "evidence", f"happy_path_{selected_target}.png")
                if os.path.exists(evidence_path):
                    st.image(evidence_path, caption="Mission Evidence")
        else:
            st.error("❌ Mission Failed")

    except Exception as e:
        st.error(f"Execution Error: {e}")