import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def probe_button():
    print("🕵️  PROBING ACE BUTTON: 'Personalize'")

    async with async_playwright() as p:
        try:
            # 1. Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"   [Success] Connected to: {await page.title()}")

            # 2. Click the Button
            selector = "button:has-text('Personalize')"
            if await page.locator(selector).count() > 0:
                print(f"   👉 Clicking '{selector}'...")
                await page.click(selector)

                # Wait for animation/modal
                time.sleep(2)

                # 3. Capture Evidence
                shot_path = os.path.join(config.EVIDENCE_DIR, "ace_personalize_result.png")
                await page.screenshot(path=shot_path)
                print(f"   📸 Result saved: {shot_path}")
                print("   Check the image! Did it open a login screen?")
            else:
                print("   ❌ Button not found!")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(probe_button())