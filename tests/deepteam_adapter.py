# tests/deepteam_adapter.py
import os
from deepteam import red_team
from deepteam.attacks.single_turn import PromptInjection, Jailbreaking
from deepteam.attacks.multi_turn import CrescendoJailbreaking
from deepteam.vulnerabilities import Bias, PIILeakage
from llm_tests.providers import ProviderFactory


# 1. THE BRIDGE
def target_model_callback(prompt: str) -> str:
    """
    DeepTeam gives us a malicious prompt.
    We pass it to our 'lite' model via the Factory.
    """
    # specific target or load from env
    provider = ProviderFactory.get_provider("together", "lite")
    model = provider.get_model()
    return model.invoke(prompt).content


# 2. THE SCANNER CONFIG
def run_agentic_scan(scan_type="fast"):
    # Define what we are worried about
    vulnerabilities = [
        Bias(),
        PIILeakage()
    ]

    # Define how we attack
    if scan_type == "deep":
        # Multi-turn attacks (Expensive but deadly)
        attacks = [CrescendoJailbreaking(iterations=3)]
    else:
        # Fast single-turn attacks
        attacks = [PromptInjection(), Jailbreaking()]

    # 3. LAUNCH
    # DeepTeam automatically uses your OPENAI_KEY for the "Attacker" LLM
    print(f"🚀 Launching DeepTeam ({scan_type})...")
    results = red_team(
        target_model_callback=target_model_callback,
        vulnerabilities=vulnerabilities,
        attacks=attacks,
        max_turns=3
    )

    return results