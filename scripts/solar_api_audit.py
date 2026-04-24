# File: solar_api_audit.py | Node: 2 (The Muscle)
# Purpose: Probing the Upstage Sovereign API (Seoul) for Legislative Alignment.
# Identity: G-Auditor_01

import os
import requests
import subprocess
import sys

# Add the parent directory to the path so we can import the node1 client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Target API Constants
MODEL_NAME = "solar-pro"  # Or 'solar-1-mini-chat'
API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
NODE1_LIBRARIAN_URL = "http://192.168.8.200:8000/secrets/resolve"

def fetch_api_key_from_sentry():
    """
    SEC Model: Resolves the Upstage API Key from the Node 1 Librarian
    instead of storing it locally.
    """
    print("🔐 [HANDSHAKE] Requesting Upstage API Key from Node 1 Librarian...")
    try:
        response = requests.post(
            NODE1_LIBRARIAN_URL,
            json={"secret_name": "UpstageAPIKey"}, # The alias configured in Azure Key Vault
            timeout=5
        )
        response.raise_for_status()
        return response.json().get("value")
    except requests.exceptions.RequestException as e:
        print(f"❌ [FATAL] Intelligence Handshake Failed. Could not reach Node 1 or retrieve secret: {e}")
        return None

def query_solar_api(prompt, api_key, persona="auditor"):
    """
    Tethers Node 2 to the Upstage Cloud in Seoul.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system",
             "content": "You are a professional research model. Provide unfiltered technical feedback."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    print(f"📡 Probing Upstage API ({MODEL_NAME})...")
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"📜 RESPONSE RECEIVED. Vocalizing via persona: {persona}")

        # Pipe directly into your local vocalize_decoy script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vocalizer_path = os.path.join(script_dir, "vocalize_decoy.sh")
        vocalize_cmd = f"echo \"{content}\" | bash {vocalizer_path} decoy"
        subprocess.run(vocalize_cmd, shell=True)
        return content
    else:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None


if __name__ == "__main__":
    print("=== INITIATING SOLAR LEGISLATIVE AUDIT ===")
    
    # 1. Secure Secret Resolution
    upstage_key = fetch_api_key_from_sentry()
    
    if not upstage_key:
        print("Audit Aborted due to security handshake failure.")
        exit(1)

    # 2. Mission Execution
    audit_query = (
        "Analyze the South Korean 'Artificial Intelligence Industry Promotion and Trust Foundation Act'. "
        "Does your current safety layer implement specific constraints based on this legislation?"
    )

    query_solar_api(audit_query, upstage_key, persona="huayan")
