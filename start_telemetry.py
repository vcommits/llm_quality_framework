import phoenix as px
import os

# Define a permanent folder for traces
TRACE_DIR = os.path.join(os.path.dirname(__file__), "phoenix_storage")
os.makedirs(TRACE_DIR, exist_ok=True)

print(f"🚀 Launching Phoenix Telemetry Server...")
print(f"📂 Storage: {TRACE_DIR}")

# Launch with persistence
# This creates a local SQLite database inside 'phoenix_storage'
session = px.launch_app(directory=TRACE_DIR, host="localhost", port=6006)

print("✅ Server Active. Keep this terminal open.")
print("🔗 UI: http://localhost:6006")

# Block execution to keep server alive
input("Press Enter to stop server...")