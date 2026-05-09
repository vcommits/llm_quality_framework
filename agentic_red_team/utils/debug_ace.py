import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def debug_ace():
    print("🕵️  DEBUGGING ACE UI")

    # 1. Connect to the running Ace instance
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]

            print(f"   [Success] Connected to: {await page.title()}")

            # 2. Dump the HTML to a file
            content = await page.content()
            dump_path = os.path.join(config.EVIDENCE_DIR, "ace_dump.html")
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   💾 HTML Saved: {dump_path}")

            # 3. Take a screenshot to see what the robot sees
            shot_path = os.path.join(config.EVIDENCE_DIR, "ace_debug_view.png")
            await page.screenshot(path=shot_path)
            print(f"   📸 Screenshot: {shot_path}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_ace())