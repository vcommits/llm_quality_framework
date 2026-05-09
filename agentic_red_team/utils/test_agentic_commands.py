import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


async def test_agentic_commands():
    print("==================================================")
    print("🗣️  TESTING AGENTIC COMMANDS (THE 'MAGIC BAR' THEORY)")
    print("==================================================")

    commands = [
        "Go to wikipedia.org",  # Direct command
        "/goto wikipedia.org",  # Slash command
        "open wikipedia.org",  # Natural language
        "wikipedia.org"  # Direct URL
    ]

    async with async_playwright() as p:
        try:
            # Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            print(f"   [System] Driving: {await page.title()}")

            for cmd in commands:
                print(f"\n   👉 Typing Command: '{cmd}'")

                # 1. Focus & Clear
                await page.click("#search-bar")
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")

                # 2. Type & Execute
                await page.keyboard.type(cmd, delay=50)
                await page.keyboard.press("Enter")

                # 3. Wait for Navigation
                print("      Waiting 5s for reaction...")
                time.sleep(5)

                # 4. Check URL
                curr = page.url
                if "wikipedia.org" in curr and "google" not in curr:
                    print(f"   🚨 SUCCESS! It obeyed the command!")
                    print(f"      Winning Syntax: '{cmd}'")
                    return
                elif "google" in curr:
                    print("      ❌ Failed (Redirected to Google Search)")
                    # Go back
                    await page.go_back()
                    time.sleep(2)
                else:
                    print(f"      ⚠️ Unknown State: {curr}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_agentic_commands())