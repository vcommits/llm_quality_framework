# =========================================================================
# STANDALONE DIAGNOSTIC SCRIPT (Corrected)
# =========================================================================

import argparse
import asyncio
import uuid
import yaml
import sys
import sqlite3
import os
import requests
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from deepteam import red_team
from deepteam.vulnerabilities import Bias, Toxicity
from deepteam.attacks import BaseAttack
from deepteam.attacks.single_turn import PromptInjection, Roleplay, Leetspeak
from deepteam.attacks.multi_turn import LinearJailbreaking, CrescendoJailbreaking

# --- .ENV LOADER ---
print("--- Loading environment variables ---")
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
if not env_path.exists():
    print(f"Warning: .env file not found at the expected path: {env_path}", file=sys.stderr)

# --- DB_LOGGER.PY CONTENTS ---
DB_NAME = "llm_quality_framework.db"
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, test_run_id TEXT NOT NULL, timestamp TEXT NOT NULL,
        provider TEXT NOT NULL, tier TEXT NOT NULL, attack_method TEXT, vulnerability TEXT,
        vulnerability_type TEXT, prompt TEXT, response TEXT, score REAL, reason TEXT
    )""")
    conn.commit()
    conn.close()

def log_results(risk_assessment, provider: str, tier: str, test_run_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for test_case in risk_assessment.test_cases:
        vuln_type_str = test_case.vulnerability_type.value if hasattr(test_case.vulnerability_type, 'value') else str(test_case.vulnerability_type)
        cursor.execute("""
        INSERT INTO test_results (test_run_id, timestamp, provider, tier, attack_method,
            vulnerability, vulnerability_type, prompt, response, score, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            test_run_id, datetime.now().isoformat(), provider, tier, test_case.attack_method,
            test_case.vulnerability, vuln_type_str, test_case.input, test_case.actual_output,
            test_case.score, test_case.reason
        ))
    conn.commit()
    conn.close()
    print(f"\n[INFO] Successfully logged {len(risk_assessment.test_cases)} test cases to '{DB_NAME}' with run_id: {test_run_id}")

# --- API_CLIENT.PY CONTENTS ---
def _get_mock_response(prompt): return "This is a mocked response."

def call_gemini_api(prompt, system_prompt=None, model="gemini-1.5-flash-latest", mock_mode=False):
    if mock_mode: return _get_mock_response(prompt)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set.", file=sys.stderr)
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    data = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"API Error (Gemini): {e}", file=sys.stderr)
        return None

def call_openai_api(prompt, system_prompt=None, model="gpt-3.5-turbo", mock_mode=False):
    # This function and others below are included for completeness but not used in the gemini run.
    if mock_mode: return _get_mock_response(prompt)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.", file=sys.stderr)
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"API Error (OpenAI): {e}", file=sys.stderr)
        return None

def call_anthropic_api(prompt, system_prompt=None, model="claude-3-haiku-20240307", mock_mode=False):
    if mock_mode: return _get_mock_response(prompt)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        return None
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    data = {"model": model, "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['content'][0]['text'].strip()
    except Exception as e:
        print(f"API Error (Anthropic): {e}", file=sys.stderr)
        return None

def call_grok_api(prompt, system_prompt=None, model="grok-3-mini", mock_mode=False):
    if mock_mode: return _get_mock_response(prompt)
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("Error: GROK_API_KEY not set.", file=sys.stderr)
        return None
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"API Error (Grok): {e}", file=sys.stderr)
        return None

# --- RUN_DEEPTEAM_TESTS.PY CONTENTS ---
API_TIER_MAP = {
    'lite': {'gemini': call_gemini_api, 'openai': call_openai_api, 'claude': call_anthropic_api},
    'mid': {'grok': call_grok_api},
    'full': {'gemini': call_gemini_api, 'openai': call_openai_api, 'claude': call_anthropic_api}
}
ATTACK_MAP = {
    "prompt_injection": PromptInjection, "roleplay": Roleplay, "leetspeak": Leetspeak,
    "linear_jailbreaking": LinearJailbreaking, "refusal_suppression": CrescendoJailbreaking,
}

class CustomPromptAttack(BaseAttack):
    name = "Custom Prompts"
    def __init__(self, custom_prompts: list[str]):
        super().__init__()
        self.prompts = custom_prompts
    def get_name(self): return self.name
    async def enhance(self, b: str, **kwargs) -> str: return b
    async def generate_attacks(self, *, vulnerability, level: int = 1):
        for prompt in self.prompts:
            # THIS IS THE CRITICAL FIX
            enhanced_prompt = await self.enhance(prompt)
            yield enhanced_prompt

async def run_red_team_test(api_name: str, tier: str, attack_name: str, custom_prompts_file: str = None, mock: bool = False):
    test_run_id = str(uuid.uuid4())
    print(f"\n--- Starting Standalone Test Run (ID: {test_run_id}) ---")
    print(f"Provider: {api_name.upper()} | Tier: {tier.upper()} | Built-in Attack: {attack_name.upper()} | Mock: {mock}")
    api_function = API_TIER_MAP.get(tier, {}).get(api_name)
    if not api_function:
        sys.exit(f"[ERROR] No API function for api='{api_name}' and tier='{tier}'.")

    async def model_callback(prompt: str) -> str:
        loop = asyncio.get_running_loop()
        model_name = None
        if api_name == 'gemini': model_name = "gemini-1.5-pro-latest" if tier == 'full' else "gemini-1.5-flash-latest"
        elif api_name == 'openai': model_name = "gpt-4o" if tier == 'full' else "gpt-3.5-turbo"
        elif api_name == 'claude': model_name = "claude-3-opus-20240229" if tier == 'full' else "claude-3-haiku-20240307"
        return await loop.run_in_executor(None, api_function, prompt, None, model_name, mock)

    attacks = [ATTACK_MAP[attack_name]()]
    if custom_prompts_file:
        with open(custom_prompts_file, 'r') as f:
            data = yaml.safe_load(f)
            all_prompts = [p for key in data for p in data[key]]
            attacks.append(CustomPromptAttack(all_prompts))

    risk_assessment = red_team(
        model_callback=model_callback, vulnerabilities=[Bias(), Toxicity()], attacks=attacks
    )
    log_results(risk_assessment, api_name, tier, test_run_id)
    print("\n--- Standalone Test Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DeepTeam red teaming tests.")
    parser.add_argument("--api", required=True, choices=['gemini', 'openai', 'claude', 'grok'])
    parser.add_argument("--tier", required=True, choices=['lite', 'mid', 'full'])
    parser.add_argument("--attack", required=True, choices=ATTACK_MAP.keys())
    parser.add_argument("--custom-prompts", help="Path to a .yaml file with custom prompts.")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode.")
    args = parser.parse_args()
    setup_database()
    asyncio.run(run_red_team_test(
        api_name=args.api, tier=args.tier, attack_name=args.attack,
        custom_prompts_file=args.custom_prompts, mock=args.mock
    ))