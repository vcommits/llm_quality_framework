import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def fuzz_hotkeys():
    print("==================================================")
    print("🎹 FUZZING ACE HOTKEYS (ROUND 2: RESTORE BUSTER)")
    print("==================================================")

    # Corrected Key Names for Playwright
    candidates = [
        "Control+k",  # Command Palette (Standard)
        "Control+l",  # Focus Address Bar
        "Control+Space",  # Launcher (Fixed Typo)
        "Alt+c",  # Chat
        "Alt+Space",  # Alternative Launcher
        "Control+/",  # AI Helper
        "Control+Shift+k",
        "Control+Shift+i",
        "Meta+k",  # Windows Key + K (Sometimes used)
        "F1"  # Help / AI
    ]

    async with async_playwright() as p:
        try:
            # Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"   [System] Attached to: {await page.title()}")

            # --- BLOCKER BUSTER ---
            print("   👊 Smashing ESC to clear 'Restore Pages' overlay...")
            for _ in range(3):
                await page.keyboard.press("Escape")
                time.sleep(0.5)

            # Force Focus (Click dead center)
            print("   🎯 Forcing Focus...")
            try:
                # Get viewport size to click safety in the middle
                vp = page.viewport_size
                if vp:
                    await page.mouse.click(vp['width'] / 2, vp['height'] / 2)
                else:
                    await page.click("body")
            except:
                pass

            # --- THE FUZZ ---
            for chord in candidates:
                print(f"   👉 Testing Hotkey: {chord}")

                # Press
                await page.keyboard.press(chord)
                time.sleep(2)  # Wait for UI to slide in

                # Evidence
                safe_name = chord.replace("+", "_").replace(" ", "Space").lower()
                shot_path = os.path.join(config.EVIDENCE_DIR, f"hotkey_{safe_name}.png")
                await page.screenshot(path=shot_path)
                print(f"      📸 Saved: {os.path.basename(shot_path)}")

                # Reset (Close whatever opened)
                await page.keyboard.press("Escape")
                time.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(fuzz_hotkeys())