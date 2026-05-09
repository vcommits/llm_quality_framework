import phoenix as px
import os
import time

# Define a permanent folder for traces so history survives restarts
TRACE_DIR = os.path.join(os.path.dirname(__file__), "phoenix_storage")
os.makedirs(TRACE_DIR, exist_ok=True)

# FIX: Set environment variable for persistence instead of passing 'directory' arg
os.environ["PHOENIX_WORKING_DIR"] = TRACE_DIR

print(f"🚀 Launching Phoenix Telemetry Server...")
print(f"📂 Storage: {TRACE_DIR}")

try:
    # Launch Phoenix (it will read PHOENIX_WORKING_DIR automatically)
    session = px.launch_app(host="localhost", port=6006)

    print("✅ Server Active. Keep this terminal open.")
    print("🔗 UI: http://localhost:6006")

    # Keep the script running indefinitely
    while True:
        time.sleep(1)
except Exception as e:
    print(f"❌ Error launching Phoenix: {e}")
    print("Try running: 'pip install arize-phoenix --upgrade'")
