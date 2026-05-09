import asyncio
import sys
import os
import time
import requests
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def get_targets():
    """Fetches the raw list of debuggable pages/views from Ace."""
    try:
        response = requests.get("http://127.0.0.1:9222/json/list")
        return {t['id']: t for t in response.json()}
    except:
        return {}


async def watch_for_spawns():
    print("==================================================")
    print("👀 WATCHING FOR NOVA SPAWNS (TARGET DIFF)")
    print("==================================================")

    # 1. Connect to the main window to drive the keyboard
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            main_page = browser.contexts[0].pages[0]
            print(f"   [System] Driving Main Window: {await main_page.title()}")

            # Hotkeys to test
            triggers = ["Control+k", "Control+Space", "Alt+c", "Control+i"]

            for chord in triggers:
                print(f"\n   👉 Pressing: {chord}")

                # Snapshot BEFORE
                before_targets = get_targets()

                # Action
                await main_page.keyboard.press(chord)
                time.sleep(2)  # Wait for spawn

                # Snapshot AFTER
                after_targets = get_targets()

                # Diff
                new_ids = set(after_targets.keys()) - set(before_targets.keys())

                if new_ids:
                    print(f"   🚨 BINGO! New Target Spawned!")
                    for new_id in new_ids:
                        t = after_targets[new_id]
                        print(f"      Title: {t.get('title')}")
                        print(f"      Type:  {t.get('type')}")
                        print(f"      URL:   {t.get('url')}")
                        print(f"      ID:    {new_id}")
                        print("      -----------------------------------")
                        print("      ✅ WE FOUND IT. Update targets.py with this info!")
                        return  # Stop hunting, we found the entry point.
                else:
                    print("      (No new targets appeared)")

                # Cleanup (Close overlay if it opened but wasn't a separate target)
                await main_page.keyboard.press("Escape")
                time.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(watch_for_spawns())