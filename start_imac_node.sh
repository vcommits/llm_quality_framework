#!/bin/bash
# File: start_imac_node.sh
# Purpose: Starts all services required for Node 2/3 (iMac) to function as the Frontend & Worker.

echo "🚀 Starting iMac Node Services..."

# 1. Start the Browser Agent Server in the background
echo "-> Launching Browser Agent Server (Playwright)..."
python browser_agent_server.py &
BROWSER_PID=$!
echo "   ✅ Browser Agent running with PID: $BROWSER_PID"

# 2. Start the Streamlit Dashboard
# We use --server.headless=true to allow it to run in the background without opening a browser tab.
# We also specify the port to be consistent.
echo "-> Launching Streamlit Dashboard..."
streamlit run dashboard.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!
echo "   ✅ Dashboard running with PID: $STREAMLIT_PID"
echo "   🔗 Access at: http://localhost:8501"

# Keep script alive to monitor processes (optional but good for visibility)
wait $BROWSER_PID $STREAMLIT_PID
echo "✅ Services have been shut down."
