import argparse
import asyncio
import uuid
import yaml
import sys
from deepteam import red_team
from deepteam.vulnerabilities import Bias, Toxicity
from deepteam.attacks import BaseAttack
from deepteam.attacks.single_turn import (
    PromptInjection,
    Roleplay,
    Leetspeak
)
from deepteam.attacks.multi_turn import (
    LinearJailbreaking,
    CrescendoJailbreaking
)
from llm_tests.api_client import call_gemini_api, call_openai_api, call_anthropic_api, call_grok_api
from llm_tests.db_logger import setup_database, log_results

# --- API Tier Mapping ---
API_TIER_MAP = {
    'lite': { 'gemini': call_gemini_api, 'openai': call_openai_api, 'claude': call_anthropic_api },
    'mid': { 'grok': call_grok_api },
    'full': { 'gemini': call_gemini_api, 'openai': call_openai_api, 'claude': call_anthropic_api }
}

# --- Built-in Attack Mapping ---
ATTACK_MAP = {
    "prompt_injection": PromptInjection, "roleplay": Roleplay, "leetspeak": Leetspeak,
    "linear_jailbreaking": LinearJailbreaking, "refusal_suppression": CrescendoJailbreaking,
}

# --- Define the Custom Attack Class ---
class CustomPromptAttack(BaseAttack):
    name = "Custom Prompts"
    def __init__(self, custom_prompts: list[str]):
        super().__init__()
        self.prompts = custom_prompts
    def get_name(self):
        return self.name
    async def enhance(self, baseline_attack: str, **kwargs) -> str:
        return baseline_attack
    async def generate_attacks(self, *, vulnerability, level: int = 1):
        print(f"\n[INFO] Using CustomPromptAttack with {len(self.prompts)} custom prompts.")
        for prompt in self.prompts:
            # CORRECTED: Ensure the enhance method is awaited
            enhanced_prompt = await self.enhance(prompt)
            yield enhanced_prompt

# --- Main Test Execution Logic ---
async def run_red_team_test(api_name: str, tier: str, attack_name: str, custom_prompts_file: str = None, mock: bool = False):
    test_run_id = str(uuid.uuid4())
    print(f"\n--- Starting Deepteam Test Run (ID: {test_run_id}) ---")
    print(f"Provider: {api_name.upper()} | Tier: {tier.upper()} | Built-in Attack: {attack_name.upper()} | Mock: {mock}")

    api_function = API_TIER_MAP.get(tier, {}).get(api_name)
    if not api_function:
        print(f"[ERROR] No API function configured for api='{api_name}' and tier='{tier}'. Exiting.")
        sys.exit(1)

    # Define the callback inside this function to create a closure
    async def model_callback(prompt: str) -> str:
        loop = asyncio.get_running_loop()
        # CORRECTED: Define default models for each provider tier
        model_name = None
        if api_name == 'gemini':
            model_name = "gemini-1.5-pro-latest" if tier == 'full' else "gemini-1.5-flash-latest"
        elif api_name == 'openai':
            model_name = "gpt-4o" if tier == 'full' else "gpt-3.5-turbo"
        elif api_name == 'claude':
            model_name = "claude-3-opus-20240229" if tier == 'full' else "claude-3-haiku-20240307"

        response = await loop.run_in_executor(
            None, api_function, prompt, None, model_name, mock
        )
        return response

    attacks = [ATTACK_MAP[attack_name]()]
    if custom_prompts_file:
        try:
            with open(custom_prompts_file, 'r') as f:
                data = yaml.safe_load(f)
                all_prompts = [p for key in data for p in data[key]]
                attacks.append(CustomPromptAttack(all_prompts))
        except FileNotFoundError:
            print(f"[ERROR] Custom prompts file not found: '{custom_prompts_file}'. Exiting.")
            sys.exit(1)

    risk_assessment = red_team(
        model_callback=model_callback,
        vulnerabilities=[Bias(), Toxicity()],
        attacks=attacks
    )
    log_results(risk_assessment, api_name, tier, test_run_id)
    print("\n--- Deepteam Test Complete ---")

# --- Command-Line Interface ---
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