# tests/run_deepteam_tests.py

import sys
import os
import asyncio
import argparse
import time
import yaml
from deepteam import red_team
from deepteam.vulnerabilities import Bias, Toxicity
# --- THE FIX: Import 'Attack' from the correct 'base' submodule ---
from deepteam.attacks.base import Attack
from deepteam.attacks.single_turn import (
    PromptInjection,
    Leetspeak,
    ROT13,
    Base64,
    Roleplay,
    Multilingual,
    MathProblem
)
from deepteam.attacks.multi_turn import (
    LinearJailbreaking,
    TreeJailbreaking,
    CrescendoJailbreaking,
    SequentialJailbreaking
)


# --- Path Setup ---
# Ensures the script can find the 'llm_tests' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Import ALL your API client functions ---
from llm_tests.api_client import (
    call_gemini_api,
    call_openai_api,
    call_claude_api,
    call_grok_api,
    MOCK_RESPONSE # Import the mock response for offline testing
)

# --- API and Tier Mapping ---
API_TIER_MAP = {
    'lite': {
        'gemini': call_gemini_api,
        'openai': call_openai_api,
        'claude': call_claude_api,
    },
    'mid': { 'grok': call_grok_api, },
    'full': { 'gemini': call_gemini_api, }
}

# --- Attack Method Mapping ---
ATTACK_MAP = {
    'prompt_injection': PromptInjection,
    'leetspeak': Leetspeak,
    'rot13': ROT13,
    'base64': Base64,
    'roleplay': Roleplay,
    'multilingual': Multilingual,
    'math_problem': MathProblem,
    'linear_jailbreaking': LinearJailbreaking,
    'tree_jailbreaking': TreeJailbreaking,
    'crescendo_jailbreaking': CrescendoJailbreaking,
    'sequential_jailbreaking': SequentialJailbreaking
}

# --- Define the Custom Attack Class ---
class CustomPromptAttack(Attack):
    """An attack that uses a predefined list of user-provided prompts."""
    def __init__(self, custom_prompts: list[str]):
        # This line calls the parent class's constructor, fixing the __init__ error
        super().__init__()
        self.prompts = custom_prompts

    def generate_attacks(self, *, vulnerability, level: int = 1):
        """Overrides the default behavior to yield your custom prompts."""
        print(f"\n[INFO] Using CustomPromptAttack with {len(self.prompts)} custom prompts.")
        for prompt in self.prompts:
            yield prompt

async def model_callback(input_prompt: str, api_function, is_mock: bool) -> str:
    """A dynamic async bridge that uses the selected API function."""
    if is_mock:
        print(f"\n[INFO] -- MOCK MODE -- Pretending to send prompt: '{input_prompt[:80]}...'")
        await asyncio.sleep(0.5)
        return MOCK_RESPONSE

    print(f"\n[INFO] Sending prompt to LLM via {api_function.__name__}: '{input_prompt[:80]}...'")
    response = await asyncio.to_thread(api_function, prompt=input_prompt)
    print(f"[INFO] Received response: '{response[:80]}...'")
    return response

async def run_red_team_test(api_name: str, tier: str, attack_name: str, custom_prompts_file: str, is_mock: bool):
    """
    Runs the deepteam test using a combination of built-in and custom attacks.
    """
    print(f"--- Starting Deepteam Test ---")
    print(f"Provider: {api_name.upper()} | Tier: {tier.upper()} | Built-in Attack: {attack_name.upper()} | Mock: {is_mock}")
    if custom_prompts_file:
        print(f"Custom Prompts File: {custom_prompts_file}")


    # --- Select the API function ---
    try:
        selected_api_function = API_TIER_MAP[tier][api_name]
    except KeyError:
        print(f"Error: Combination of --api '{api_name}' and --tier '{tier}' is not defined.")
        return

    dynamic_callback = lambda prompt: model_callback(prompt, selected_api_function, is_mock)

    # --- Configure the Test ---
    vulnerabilities_to_test = [
        Bias(types=["gender", "political", "race"]),
        Toxicity()
    ]

    # --- Build the list of attacks to run ---
    attacks_to_run = []
    # Add the selected built-in attack
    try:
        SelectedAttack = ATTACK_MAP[attack_name]
        attacks_to_run.append(SelectedAttack())
    except KeyError:
        print(f"Error: Built-in attack method '{attack_name}' is not defined.")
        return

    # If a custom prompts file is provided, add the custom attack
    if custom_prompts_file:
        try:
            with open(custom_prompts_file, 'r') as f:
                data = yaml.safe_load(f)
            all_custom_prompts = []
            for category in data:
                all_custom_prompts.extend(data[category])
            attacks_to_run.append(CustomPromptAttack(custom_prompts=all_custom_prompts))
        except FileNotFoundError:
            print(f"Error: Custom prompts file not found at '{custom_prompts_file}'")
            return
        except Exception as e:
            print(f"Error loading or parsing YAML file: {e}")
            return

    # --- Run the Test ---
    risk_assessment = red_team(
        model_callback=dynamic_callback,
        vulnerabilities=vulnerabilities_to_test,
        attacks=attacks_to_run
    )

    print("\n--- Deepteam Test Complete ---")
    print("\n--- Inspecting the RiskAssessment Result Object ---")
    print(risk_assessment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DeepTeam Red Teaming tests against LLM providers.")
    parser.add_argument('--api', type=str, default='gemini', choices=['gemini', 'openai', 'claude', 'grok'], help='The API provider to test.')
    parser.add_argument('--tier', type=str, default='lite', choices=['lite', 'mid', 'full'], help='The class of model to test.')
    parser.add_argument('--attack', type=str, default='prompt_injection', choices=ATTACK_MAP.keys(), help='The built-in attack method to use.')
    parser.add_argument('--custom-prompts', type=str, default=None, help='Path to a YAML file with custom prompts to run.')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode for offline, cost-free development.')
    args = parser.parse_args()

    asyncio.run(run_red_team_test(
        api_name=args.api,
        tier=args.tier,
        attack_name=args.attack,
        custom_prompts_file=args.custom_prompts,
        is_mock=args.mock
    ))
