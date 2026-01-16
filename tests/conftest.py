import os
import json
import time
import pytest
import phoenix as px
from phoenix.trace.langchain import LangChainInstrumentor
from deepeval.events import on_test_run_end

# --- 1. PERSISTENT TELEMETRY SETUP ---

# Use the exact same path as start_telemetry.py
TRACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../phoenix_storage"))
os.makedirs(TRACE_DIR, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def setup_telemetry():
    """
    Initializes Arize Phoenix for the test session.
    It writes to the shared 'phoenix_storage' folder so your Dashboard 
    can see these test results in the 'Run over Run' history.
    """
    try:
        # Launch Phoenix. 
        # Note: If start_telemetry.py is already running on port 6006, 
        # this will auto-bind to a random port (like 6007) but STILL write 
        # to the correct TRACE_DIR database.
        px.launch_app(directory=TRACE_DIR)

        # Hook into LangChain to capture every LLM call made by Pytest
        LangChainInstrumentor().instrument()

        print(f"\n✅ Telemetry Active. Writing to: {TRACE_DIR}")

    except Exception as e:
        print(f"\n⚠️ Telemetry Initialization Warning: {e}")
        # We don't stop the tests, just warn


# --- 2. DEEPEVAL DRIFT LOGGING ---

def log_drift_score(test_case, metrics):
    """
    Custom hook to save DeepEval scores to a local JSON file
    so the Dashboard can graph 'Drift' over time in Tab 3.
    """
    history_file = os.path.join(os.path.dirname(__file__), "../drift_history.json")

    # Load existing history
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    else:
        history = []

    # Append new entry
    for metric in metrics:
        entry = {
            "timestamp": time.time(),
            "metric": metric.__class__.__name__,
            "score": metric.score,
            "passed": metric.is_successful(),
            "input": getattr(test_case, 'input', 'N/A'),
            "actual_output": getattr(test_case, 'actual_output', 'N/A')
        }
        history.append(entry)

    # Save
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

# Hook DeepEval's lifecycle to our logger
# Note: DeepEval's event system can be finicky; ensuring this runs requires
# passing the metric objects correctly in your test files.
# Alternatively, you can call log_drift_score() directly inside your test functions.