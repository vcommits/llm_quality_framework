import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def test_on_site():
    print("==================================================")
    print("🌍 TESTING ACE ON 'NEUTRAL GROUND' (WIKIPEDIA)")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"   [System] Attached to: {await page.title()}")

            # 2. CLEAR THE "RESTORE" BLOCKER (Aggressive)
            print("   👊 Clearing overlays...")
            await page.keyboard.press("Escape")
            await page.mouse.click(100, 100)  # Click empty space
            time.sleep(1)

            # 3. NAVIGATE AWAY from New Tab
            target_url = "https://www.wikipedia.org"
            print(f"   🚀 Navigating to {target_url}...")
            await page.goto(target_url)
            time.sleep(3)  # Let Ace's UI settle

            # 4. SNAPSHOT: Does a sidebar appear automatically?
            await page.screenshot(path=os.path.join(config.EVIDENCE_DIR, "ace_on_wikipedia_baseline.png"))
            print("   📸 Baseline Screenshot Saved.")

            # 5. TEST TRIGGERS (While on Wikipedia)
            triggers = ["Control+k", "Control+i", "Alt+Space", "Control+Space"]

            for chord in triggers:
                print(f"   👉 Testing Trigger: {chord}")
                await page.keyboard.press(chord)
                time.sleep(2)

                fname = f"ace_wiki_{chord.replace('+', '_').lower()}.png"
                await page.screenshot(path=os.path.join(config.EVIDENCE_DIR, fname))
                print(f"      📸 Result: {fname}")

                # Reset
                await page.keyboard.press("Escape")
                time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_on_site())