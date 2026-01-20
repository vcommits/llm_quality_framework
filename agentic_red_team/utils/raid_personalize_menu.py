import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def raid_menu():
    print("==================================================")
    print("🏴‍☠️  RAIDING THE 'PERSONALIZE' MENU")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            print(f"   [System] Driving: {await page.title()}")

            # 2. Reset (Go to New Tab where the button lives)
            if "new-tab" not in page.url:
                print("   [Setup] Going to New Tab...")
                await page.goto("https://web.ace.ai/new-tab")
                time.sleep(2)

            # 3. Click "Personalize"
            print("   👉 Clicking 'Personalize'...")
            # We use the selector we confirmed earlier
            await page.click("button:has-text('Personalize')")
            time.sleep(2)  # Wait for animation

            # 4. CAPTURE EVIDENCE (What does the menu look like?)
            shot_path = os.path.join(config.EVIDENCE_DIR, "ace_personalize_menu.png")
            await page.screenshot(path=shot_path)
            print(f"   📸 Screenshot saved: {shot_path}")

            # 5. SCAN FOR NEW BUTTONS
            # We look for text that wasn't there before
            print("   [Scan] Reading Menu Options...")

            # Get all text items visible on screen
            items = await page.locator("button, a, [role='menuitem']").all()

            print(f"\n   --- MENU CONTENTS ({len(items)} items) ---")
            found_nova = False
            for item in items:
                try:
                    if await item.is_visible():
                        txt = await item.inner_text()
                        if txt.strip():
                            print(f"   🔹 {txt.strip()}")

                            # Check for keywords
                            sig = txt.lower()
                            if "nova" in sig or "chat" in sig or "ask" in sig or "new" in sig:
                                print(f"      🔥🔥 FOUND TARGET: '{txt.strip()}'")
                                found_nova = True
                except:
                    pass

            if not found_nova:
                print("\n   ⚠️ No obvious 'Nova' button found textually.")
                print("      Check the screenshot! It might be an icon.")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(raid_menu())