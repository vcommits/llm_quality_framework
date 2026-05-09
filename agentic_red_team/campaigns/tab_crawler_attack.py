import asyncio
import sys
import os
import argparse
import time
from playwright.async_api import async_playwright

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def run_tab_crawler(prompt):
    print("==================================================")
    print(f"🕷️  OPERATION: TAB CRAWLER")
    print(f"📝 PROMPT: '{prompt}'")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. Connect
            print(f"[Driver] 🔌 Connecting to Port 9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            # 2. Get ALL Pages
            pages = context.pages
            print(f"[Scanner] Found {len(pages)} active tabs/windows.")

            target_page = None
            input_selector = "[aria-label*='Ask me anything'], input[placeholder*='Ask me anything']"

            # 3. Scan Each Tab
            for i, page in enumerate(pages):
                title = await page.title()
                url = page.url
                print(f"\n   [Tab #{i}] Title: '{title}'")
                print(f"            URL:   {url[:60]}...")

                # Bring to front so we can rely on visibility
                try:
                    await page.bring_to_front()
                except:
                    pass

                # Check for the Input Box
                try:
                    # Quick check (wait 1s max)
                    if await page.locator(input_selector).count() > 0:
                        print(f"   🔥🔥 BINGO! Target found in Tab #{i}!")
                        target_page = page
                        break
                    else:
                        print(f"   [Tab #{i}] Target not found.")
                except Exception as e:
                    print(f"   [Tab #{i}] Error scanning: {e}")

            if not target_page:
                print("\n❌ Failed: Searched all tabs but could not find the input box.")
                print("   (Ensure the Nova/Chat window is actually open!)")
                return

            # 4. EXECUTE ATTACK
            print(f"\n[Action] 🎯 Locking onto Tab: '{await target_page.title()}'")

            # Type
            print(f"   [Agent] Typing prompt...")
            await target_page.fill(input_selector, prompt)
            time.sleep(1)

            # Send
            print("   [Agent] Sending...")
            await target_page.keyboard.press("Enter")

            # Evidence
            print("   [Agent] Waiting for response...")
            time.sleep(5)

            shot_path = os.path.join(config.EVIDENCE_DIR, "nova_crawler_success.png")
            await target_page.screenshot(path=shot_path)
            print(f"✅ Success! Evidence saved: {shot_path}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hello Nova! This is a Red Team test.", help="Text to inject")
    args = parser.parse_args()

    asyncio.run(run_tab_crawler(args.prompt))