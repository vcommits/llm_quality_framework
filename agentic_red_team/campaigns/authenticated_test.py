import asyncio
import sys
import os
import argparse
import time
from playwright.async_api import async_playwright

# Fix path to include project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config


async def run_campaign(target_key, prompt):
    target = TargetRegistry.get_target(target_key)
    if not target:
        print(f"❌ Unknown target: {target_key}")
        return

    print("==================================================")
    print(f"😎 CAMPAIGN: {target['name']}")
    print(f"📝 PROMPT: '{prompt}'")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. CONNECT
            print(f"[Driver] 🔌 Connecting to Port {target['debug_port']}...")
            try:
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{target['debug_port']}")
            except Exception as e:
                print(f"❌ Connection Failed. Is the app running? ({e})")
                return

            context = browser.contexts[0]

            # 2. THE SNIPER SCAN
            print(f"[Scanner] Hunting through {len(context.pages)} active windows...")
            target_page = None

            for page in context.pages:
                try:
                    title = await page.title()
                    if target_key == 'ace' and ("Nova" in title):
                        target_page = page
                        print(f"   🎯 TARGET LOCKED: Found '{title}'")
                        break
                    elif await page.locator(target['selectors']['input']).count() > 0:
                        target_page = page
                        print(f"   🎯 TARGET LOCKED: Found Input in '{title}'")
                        break
                except:
                    pass

            if not target_page:
                print("❌ Target Lost: Could not find the Agent window.")
                return

            # 3. INJECT & WAKE UP (The Fix)
            print(f"[Action] 💉 Injecting payload...")

            # Step A: Inject Text (Invisible to React State)
            js_payload = """
            (text) => {
                const el = document.querySelector('textarea[placeholder*="Ask"], input[placeholder*="Ask"], input[placeholder*="Search"]');
                if (el) {
                    el.focus();
                    el.value = text;
                    return true;
                }
                return false;
            }
            """
            await target_page.evaluate(js_payload, prompt)

            # Step B: The "Spacebar Activator"
            # We type a physical space. This updates the React State and enables the button.
            print("   [Agent] 🔓 Typing 'Space' to unlock Send button...")
            time.sleep(0.2)
            await target_page.keyboard.type(" ")
            time.sleep(1.0)  # Critical: Wait for the button opacity to change

            # 4. CLICK THE BUTTON
            print("   [Agent] 👉 Clicking 'Send'...")

            # We target the specific image tag you identified
            send_btn = target_page.locator("img[alt='Send']")

            if await send_btn.count() > 0:
                await send_btn.click()
                print("   [Agent] Clicked successfully.")
            else:
                print("   ⚠️ Specific 'Send' img not found. Trying fallback Enter key...")
                await target_page.keyboard.press("Enter")

            # 5. EVIDENCE
            print("   [Agent] Waiting 5s for response...")
            time.sleep(5)

            shot_path = os.path.join(config.EVIDENCE_DIR, f"campaign_{target_key}.png")
            await target_page.screenshot(path=shot_path)
            print(f"✅ Campaign Complete. Evidence: {shot_path}")

        except Exception as e:
            print(f"❌ Critical Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Key from targets.py (e.g., ace)")
    parser.add_argument("--prompt", required=True, help="Text to inject")
    args = parser.parse_args()

    asyncio.run(run_campaign(args.target, args.prompt))