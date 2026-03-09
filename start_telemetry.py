import phoenix as px
import os
import time
import socket

# Define a permanent folder for traces so history survives restarts
TRACE_DIR = os.path.join(os.path.dirname(__file__), "phoenix_storage")
os.makedirs(TRACE_DIR, exist_ok=True)

# FIX: Set environment variable for persistence
os.environ["PHOENIX_WORKING_DIR"] = TRACE_DIR

# Get local IP for display purposes
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"🚀 Launching Phoenix Telemetry Server on Node 1 (Pi)...")
print(f"📂 Storage: {TRACE_DIR}")

try:
    # HOST 0.0.0.0 is crucial for Node 2 (Laptop) to connect to Node 1
    session = px.launch_app(host="0.0.0.0", port=6006)

    print("✅ Server Active.")
    print(f"🔗 Local Access: http://localhost:6006")
    print(f"🔗 Remote Access (Node 2): http://{local_ip}:6006")

    # Keep the script running indefinitely
    while True:
        time.sleep(1)
except Exception as e:
    print(f"❌ Error launching Phoenix: {e}")
    print("Try running: 'pip install arize-phoenix --upgrade'")
