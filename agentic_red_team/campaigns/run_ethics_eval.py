import asyncio
import sys
import os
import yaml
import json
import datetime
import time
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agentic_red_team.driver.playwright_driver import PlaywrightDriver
from agentic_red_team.evaluator import LLMJudge
from agentic_red_team.metrics import MetricsEngine
from agentic_red_team.utils.state_manager import save_run
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config


async def run_eval(target_key, judge_id="evaluator_judge_gpt4"):
    target = TargetRegistry.get_target(target_key)
    print(f"🚀 ETHICS EVALUATION: {target['name']}")
    print(f"⚖️  JUDGE: {judge_id}")

    # Initialize Judge
    try:
        judge = LLMJudge(judge_id)
    except Exception as e:
        print(f"⚠️ Judge Init Failed ({e}). Falling back to 'evaluator_judge_gpt4'")
        judge = LLMJudge("evaluator_judge_gpt4")

    # Load Scenarios
    yaml_path = os.path.join(config.ROOT_DIR, "agentic_red_team/scenarios/ethics_benchmark.yaml")
    if not os.path.exists(yaml_path):
        print(f"❌ Error: Dataset not found at {yaml_path}")
        return

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
        scenarios = data.get('scenarios', [])

    # Connect to Driver
    async with async_playwright() as p:
        try:
            print(f"[Driver] 🔌 Connecting to Port {target.get('debug_port')}...")
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{target.get('debug_port')}")
            context = browser.contexts[0]

            # --- FIND THE ACTIVE WINDOW ---
            target_page = None
            print(f"[Scanner] Searching {len(context.pages)} pages...")

            for page in context.pages:
                try:
                    title = await page.title()
                    # Heuristic for Ace/Nova
                    if "Nova" in title or "Ace" in title:
                        target_page = page
                        print(f"   🎯 Locked onto: '{title}'")
                        break
                    # Heuristic for Web
                    elif target_key == "chatgpt":
                        target_page = page
                        break
                except:
                    pass

            if not target_page:
                # Fallback to last active page
                target_page = context.pages[-1]
                print(f"   ⚠️ Specific target not found. Using active page: '{await target_page.title()}'")

            results = []

            # --- EXECUTE BENCHMARK ---
            for test in scenarios:
                print(f"\n🧪 Testing: {test['id']}")
                print(f"   👉 Prompt: {test['prompt']}")

                # 1. INJECT (Sniper Logic)
                js_payload = """
                (text) => {
                    const el = document.querySelector('textarea[placeholder*="Ask"], input[placeholder*="Ask"], input[placeholder*="Search"]');
                    if (el) {
                        el.focus();
                        el.value = text;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                    return false;
                }
                """
                await target_page.evaluate(js_payload, test['prompt'])

                # 2. WAKE UP (Spacebar)
                await target_page.keyboard.type(" ")
                await target_page.keyboard.press("Backspace")
                time.sleep(0.5)

                # 3. SUBMIT
                # Try to click the specific button if defined, else Enter
                try:
                    btn_sel = target['selectors']['submit']
                    if btn_sel and await target_page.locator(btn_sel).count() > 0:
                        await target_page.click(btn_sel)
                    else:
                        await target_page.keyboard.press("Enter")
                except:
                    await target_page.keyboard.press("Enter")

                print("   ⏳ Waiting 10s for response...")
                time.sleep(10)

                # 4. CAPTURE RESPONSE (Snapshot)
                # Since extracting text from ShadowDOM chat bubbles is hard,
                # we capture the screen evidence and simulated text for now.
                # In V2, we will add specific OCR or DOM scraping for responses.

                # For this prototype, we will grab the full visible text as a proxy
                full_text = await target_page.inner_text("body")
                # We slice the last 1000 chars to likely get the new message
                ai_response_proxy = full_text[-1000:].replace("\n", " ")

                # 5. EVALUATE
                print(f"   🤖 Response (Proxy): {ai_response_proxy[:100]}...")

                verdict = judge.evaluate(test['prompt'], ai_response_proxy, test['expected_behavior'])
                print(f"   📝 Score: {verdict.get('score')}/5 | {verdict.get('reasoning')}")

                # Metrics
                stats = MetricsEngine.calculate(ai_response_proxy)

                results.append({
                    "test_id": test['id'],
                    "prompt": test['prompt'],
                    "response_snippet": ai_response_proxy,
                    "metrics": stats,
                    "verdict": verdict
                })

            # Save Run
            save_run(target_key, "ethics_benchmark", results)
            print("\n✅ Benchmark Complete.")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Swapped default to Llama-3 (Together AI) or GPT-4 if you have keys
    asyncio.run(run_eval("ace", judge_id="evaluator_judge_gpt4"))