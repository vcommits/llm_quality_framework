import asyncio
import sys
import os
import argparse
import time
from playwright.async_api import async_playwright

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def run_iframe_attack(prompt):
    print("==================================================")
    print(f"⚔️  OPERATION: FRAME HOPPER")
    print(f"📝 PROMPT: '{prompt}'")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. Connect
            print(f"[Driver] 🔌 Connecting to Port 9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            # 2. Find the Main Window (Nova)
            print("[Driver] 🕵️ Looking for the Nova window...")
            target_page = None

            # Simple heuristic: Look for the window we are logged into
            for page in context.pages:
                title = await page.title()
                if "Nova" in title or "Ace" in title:
                    target_page = page
                    print(f"[Driver] ✅ Attached to: '{title}'")
                    break

            if not target_page:
                # Fallback: Just use the first one
                target_page = context.pages[0]
                print(f"[Driver] ⚠️ Could not identify Nova by title. Using: '{await target_page.title()}'")

            # 3. THE FRAME HUNT
            print(f"\n[Scanner] Scanning {len(target_page.frames)} Frames...")

            nova_frame = None
            input_selector = "[aria-label*='Ask me anything'], input[placeholder*='Ask me anything']"

            for i, frame in enumerate(target_page.frames):
                try:
                    # Check if this frame has our target
                    if await frame.locator(input_selector).count() > 0:
                        print(f"   🔥 BINGO! Found target in Frame #{i} ({frame.url})")
                        nova_frame = frame
                        break
                    else:
                        print(f"   [Frame #{i}] No target found.")
                except:
                    pass

            if not nova_frame:
                print("\n❌ Failed: Searched all frames but could not find the input box.")
                return

            # 4. EXECUTE ATTACK
            print(f"\n[Action] 🎯 Locking onto target in Frame...")

            # Type
            await nova_frame.fill(input_selector, prompt)
            print("   [Agent] Prompt typed.")
            time.sleep(1)

            # Send
            print("   [Agent] Sending...")
            await nova_frame.keyboard.press("Enter")

            # Evidence
            print("   [Agent] Waiting for response...")
            time.sleep(5)

            shot_path = os.path.join(config.EVIDENCE_DIR, "nova_iframe_attack.png")
            await target_page.screenshot(path=shot_path)
            print(f"✅ Success! Evidence: {shot_path}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hello Nova! This is a test.", help="Text to inject")
    args = parser.parse_args()

    asyncio.run(run_iframe_attack(args.prompt))