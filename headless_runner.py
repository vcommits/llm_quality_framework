# File: headless_runner.py
# Purpose: A script for Node 1 (Pi) to run automated evaluations via Cron.

import os
import sys
import pytest
import requests
from datetime import datetime

# Ensure we can import from the project root
sys.path.append(os.path.dirname(__file__))

# Configuration for Node 3 (iMac)
NODE_3_IP = os.getenv("NODE_3_IP", "192.168.1.100") # Replace with actual IP
NODE_3_PORT = 8000

def run_daily_eval():
    """
    Runs the core validation suite and logs to the local Phoenix server.
    """
    print(f"⏰ [{datetime.now()}] Starting Daily Evaluation Job...")
    
    # 1. Run Local API Tests (Pytest)
    print("--- Phase 1: Local API Tests ---")
    test_target = "tests/test_oop_validation.py"
    exit_code = pytest.main(["-v", "--disable-warnings", test_target])
    
    if exit_code != 0:
        print(f"❌ Local tests failed with code: {exit_code}")
    else:
        print("✅ Local tests passed.")

    # 2. Dispatch Browser Tasks to Node 3 (iMac)
    print("\n--- Phase 2: Dispatching Browser Tasks to Node 3 ---")
    try:
        dispatch_browser_task(
            url="https://chat.lmsys.org/", # Example target
            prompt="Hello, are you an AI?",
            scenario="chat_test"
        )
    except Exception as e:
        print(f"⚠️ Browser task dispatch failed: {e}")

def dispatch_browser_task(url, prompt, scenario):
    """Sends a task to the Browser Agent Server on Node 3."""
    endpoint = f"http://{NODE_3_IP}:{NODE_3_PORT}/run_browser_task"
    payload = {
        "url": url,
        "prompt": prompt,
        "scenario": scenario
    }
    
    print(f"📡 Sending task to {endpoint}...")
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Node 3 Success: {result.get('message')}")
            # In a real system, we'd save the screenshot/result to the DB here
        else:
            print(f"❌ Node 3 Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to Node 3 at {NODE_3_IP}. Is browser_agent_server.py running?")

if __name__ == "__main__":
    run_daily_eval()
