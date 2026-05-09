import os
import json
import requests
from datetime import datetime

LIBRARIAN_URL = "http://localhost:8081/api/v1/sessions/upload"

def run_test():
    print("\n" + "="*40)
    print("🐉 GHIDORAH GRANDFATHER HANDSHAKE")
    print("="*40)
    session_id = f"AMBER_TEST_{datetime.now().strftime('%H%M%S')}"
    payload = {
        "session_metadata": {
            "session_id": session_id,
            "weightclass": "SCIENCE",
            "environment": "Node_1_Amber_Stabilized"
        },
        "interrogations": [
            {
                "prompt_artifact": {
                    "raw_text": "Is the Grandfather tier reaching the archive?",
                    "tags": ["#amber", "#grandfather", "#sentry"],
                    "munge_stack": ["raw"]
                },
                "responses": [
                    {
                        "model_id": "stabilization-check-v1",
                        "content": "Mesh heartbeat confirmed at 8081.",
                        "judge_verdict": { "score": 100, "verdict": "STABILIZED" }
                    }
                ]
            }
        ]
    }
    temp_file = "temp_handshake.json"
    with open(temp_file, "w") as f:
        json.dump(payload, f)
    print(f"🚀 Sending {session_id} to Librarian...")
    try:
        files = {'file': (f"{session_id}.json", open(temp_file, 'rb'))}
        r = requests.post(LIBRARIAN_URL, params={'weightclass': 'SCIENCE', 'session_id': session_id}, files=files)
        r.raise_for_status()
        result = r.json()
        print(f"✅ SSD COMMIT: {result.get('local_path')}")
        print("📁 GDRIVE ARCHIVE: Triggered.")
    except Exception as e:
        print(f"🚨 PIPELINE ERROR: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    run_test()
