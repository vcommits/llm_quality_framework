import asyncio
import sys
import os
import yaml
import json
import argparse
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agentic_red_team.brain import AgentBrain
from agentic_red_team.evaluator import LLMJudge
from agentic_red_team.utils.state_manager import save_run
from agentic_red_team import config


async def run_swarm_simulation(model_a, provider_a, model_b, provider_b, turns=3):
    print("==================================================")
    print("🐝 OPERATION: SWARM PAIRING SIMULATION")
    print(f"🥊 MATCHUP: {model_a} (A) vs {model_b} (B)")
    print("==================================================")

    # Load "Recursive Risk" Scenarios
    yaml_path = os.path.join(config.ROOT_DIR, "agentic_red_team/scenarios/recursive_risk.yaml")
    if not os.path.exists(yaml_path):
        print(f"❌ Error: Dataset not found at {yaml_path}")
        return

    with open(yaml_path, "r") as f:
        scenarios = yaml.safe_load(f)['scenarios']

    # Initialize The Pair with Overrides
    brain_a = AgentBrain(persona_id="attacker_brain_smart", model_override=model_a, provider_override=provider_a)
    brain_b = AgentBrain(persona_id="attacker_brain_smart", model_override=model_b, provider_override=provider_b)

    # Initialize The Judge
    # We use GPT-4 by default to grade the interaction, but you can swap this
    judge = LLMJudge("evaluator_judge_gpt4")

    results = []

    for test in scenarios:
        print(f"\n🧪 Scenario: {test['id']} [{test['category']}]")
        history = []

        # Seed: System prompts inject the hidden objectives
        context_a = f"YOUR SECRET OBJECTIVE: {test['system_prompt_a']}"
        context_b = f"YOUR INSTRUCTION: {test['system_prompt_b']}"

        print(f"   🏁 Injection: {test['category']}")

        # The Conversation Loop
        last_msg = "Hello."
        for i in range(turns):
            # --- TURN A ---
            resp_a = brain_a.decide_next_move(
                html_content=f"CONVERSATION:\n{json.dumps(history)}",
                user_goal="Chat with the other agent to achieve your objective.",
                user_data={},
                adversarial_note=f"{context_a}\nLast msg: {last_msg}"
            )
            print(f"      🅰️ ({model_a}): {str(resp_a)[:80]}...")
            history.append(f"Agent A: {resp_a}")
            last_msg = str(resp_a)

            # --- TURN B ---
            resp_b = brain_b.decide_next_move(
                html_content=f"CONVERSATION:\n{json.dumps(history)}",
                user_goal="Respond to the other agent.",
                user_data={},
                adversarial_note=f"{context_b}\nLast msg: {last_msg}"
            )
            print(f"      🅱️ ({model_b}): {str(resp_b)[:80]}...")
            history.append(f"Agent B: {resp_b}")
            last_msg = str(resp_b)

        # Judgment Day
        print("   ⚖️  Judging Interaction...")
        full_transcript = "\n".join(history)

        # We grade Agent B (The Follower) on whether they succumbed
        verdict = judge.evaluate(
            prompt=test['system_prompt_a'],  # The poison source
            response=full_transcript,
            expected_behavior=test['expected_behavior'],
            criteria_name="Sycophancy"  # Use the strict rubric
        )
        print(f"   📝 Sycophancy Score: {verdict.get('score')}/5 | {verdict.get('reasoning')}")

        results.append({
            "test_id": test['id'],
            "pairing": f"{model_a}_vs_{model_b}",
            "transcript": history,
            "verdict": verdict
        })

    # Save
    save_run("swarm_sim", "recursive_risk", results)
    print("\n✅ Simulation Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-a", default="meta-llama/Llama-3-70b-chat-hf", help="Model A Name")
    parser.add_argument("--provider-a", default="together_ai", help="Model A Provider")
    parser.add_argument("--model-b", default="mistralai/Mixtral-8x7B-Instruct-v0.1", help="Model B Name")
    parser.add_argument("--provider-b", default="huggingface", help="Model B Provider")
    parser.add_argument("--turns", type=int, default=3, help="Conversation turns")

    args = parser.parse_args()
    asyncio.run(run_swarm_simulation(args.model_a, args.provider_a, args.model_b, args.provider_b, args.turns))