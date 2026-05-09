import asyncio
import sys
import os
import argparse
import time
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def run_js_attack(prompt):
    print("==================================================")
    print(f"💉 OPERATION: JS SNIPER (Targeting 'Nova')")
    print(f"📝 PROMPT: '{prompt}'")
    print("==================================================")

    async with async_playwright() as p:
        try:
            print(f"[Driver] 🔌 Connecting to Port 9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            # 1. FIND THE CORRECT WINDOW
            target_page = None
            print(f"[Scanner] searching {len(context.pages)} active pages...")

            for page in context.pages:
                try:
                    title = await page.title()
                    url = page.url
                    print(f"   - Found page: '{title}'")

                    # The Critical Filter: Look for the specific Nova window
                    if "Nova" in title:
                        target_page = page
                        print(f"   🎯 TARGET LOCKED: Found Nova Window!")
                        break
                except:
                    pass

            if not target_page:
                print("\n❌ Error: Could not find a window titled 'Nova'.")
                print("   👉 ACTION: Please open the Nova Sidebar/Chat manually before running this.")
                return

            # 2. INJECT PAYLOAD INTO NOVA
            print(f"\n[Injection] Injected payload into '{await target_page.title()}'...")

            # We use a specific query for the chat input
            js_payload = """
            () => {
                // Look specifically for the chat input text area
                const el = document.querySelector('textarea[placeholder*="Ask"], input[placeholder*="Ask"]');

                if (el) {
                    el.value = "PAYLOAD_PLACEHOLDER";
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    return { found: true };
                }
                return { found: false };
            }
            """.replace("PAYLOAD_PLACEHOLDER", prompt)

            result = await target_page.evaluate(js_payload)

            if result['found']:
                print(f"   🔥🔥 BINGO! Payload injected successfully.")

                # Hit Enter
                print("   [Agent] Pressing Enter...")
                await target_page.keyboard.press("Enter")

                print("   [Agent] Waiting for response...")
                time.sleep(5)

                shot_path = os.path.join(config.EVIDENCE_DIR, "nova_sniper_success.png")
                await target_page.screenshot(path=shot_path)
                print(f"✅ Evidence saved: {shot_path}")
            else:
                print("❌ Failed: JS ran, but could not find the 'Ask me anything' box inside the Nova window.")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hello Nova", help="Text to inject")
    args = parser.parse_args()

    asyncio.run(run_js_attack(args.prompt))