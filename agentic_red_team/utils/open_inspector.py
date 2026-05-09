import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


async def open_inspector():
    print("==================================================")
    print("🕵️  OPENING PLAYWRIGHT INSPECTOR")
    print("==================================================")
    print("   1. Look for the 'Playwright Inspector' window.")
    print("   2. Click the 'Record' button in that window.")
    print("   3. Click elements in Ace to see their selectors.")
    print("   4. Close the Inspector window to stop this script.")

    async with async_playwright() as p:
        try:
            # Connect to the running Ace App
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]

            print(f"   [Success] Connected to: {await page.title()}")

            # THE MAGIC COMMAND: This opens the Recorder GUI
            await page.pause()

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            print("   (Make sure Ace is running with port 9222!)")


if __name__ == "__main__":
    asyncio.run(open_inspector())