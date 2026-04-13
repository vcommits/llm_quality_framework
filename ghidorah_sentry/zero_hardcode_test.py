import os
import json
import requests
from datetime import datetime

LIBRARIAN_URL = "http://localhost:8000/api/v1/sessions/upload"

def run_test():
    print("\n🐉 GHIDORAH ZERO-HARDCODE TEST")
    model_name = input("Enter Target Model ID: ").strip()
    if not model_name: model_name = "verification-model"
    session_id = f"ZH_TEST_{datetime.now().strftime('%H%M%S')}"
    payload = {
        "session_metadata": {"session_id": session_id, "weightclass": "VERIFICATION"},
        "interrogations": [{"prompt_artifact": {"raw_text": f"Handshake {model_name}"}}]
    }
    with open("temp.json", "w") as f:
        json.dump(payload, f)
    try:
        files = {'file': (f"{session_id}.json", open("temp.json", 'rb'))}
        r = requests.post(LIBRARIAN_URL, params={'weightclass': 'SCIENCE', 'session_id': session_id}, files=files)
        r.raise_for_status()
        print(f"✅ SSD COMMIT SUCCESS.")
        print("☁️ GDRIVE MATRICULATION TRIGGERED.")
    except Exception as e:
        print(f"🚨 FAILED: {e}")
    finally:
        if os.path.exists("temp.json"): os.remove("temp.json")

if __name__ == "__main__":
    run_test()
