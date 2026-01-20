import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def interactive_auth_setup():
    print("==================================================")
    print("🔐 INTERACTIVE AUTHENTICATION SETUP (V3: CLEAN BREAK)")
    print("==================================================")

    # PHASE 1: PRE-FLIGHT CHECK
    print("   [Phase 1] Pinging Ace...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("   [System] Port 9222 is active. Disconnecting for safety.")
            await browser.close()  # Clean break
        except Exception as e:
            print(f"❌ Error: Ace is not running! Run launch.py first. ({e})")
            return

    # PHASE 2: MANUAL INTERVENTION
    print("\n   🛑 ACTION REQUIRED: MANUAL LOGIN")
    print("   1. Go to the Ace window.")
    print("   2. Select your profile / Log in.")
    print("   3. WAIT for the Dashboard/New Tab to fully load.")
    print("   4. (Recommended) Open a new tab to 'wikipedia.org' so we have a clean target.")

    input("\n   👉 Press ENTER here once you are logged in and looking at the UI...")

    # PHASE 3: RE-CONNECTION (Fresh Start)
    print("\n   [Phase 3] Establishing Fresh Connection...")
    async with async_playwright() as p:
        try:
            # Connect to the NEW window
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            if not context.pages:
                print("   ❌ Error: Connected, but no pages found. Try clicking inside the Ace window.")
                return

            # Grab the active page
            page = context.pages[0]
            print(f"   [System] Successfully attached to: '{await page.title()}'")

            # PHASE 4: THE HUNT
            print("\n   [Scan] Searching for Nova/Agent controls...")
            snapshot = await page.accessibility.snapshot()

            def find_nova(node):
                name = node.get("name", "")
                role = node.get("role", "")
                # We are looking for the "logged in" features
                keywords = ["nova", "agent", "memory", "memories", "chat", "ask", "assistant", "profile"]
                if any(x in name.lower() for x in keywords):
                    print(f"   🔥 FOUND TARGET: [{role}] '{name}'")

                for child in node.get("children", []):
                    find_nova(child)

            find_nova(snapshot)

            # Evidence
            path = os.path.join(config.EVIDENCE_DIR, "ace_loggedin_state.png")
            await page.screenshot(path=path)
            print(f"   📸 Screenshot saved: {path}")

        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            print("   (Ensure Ace didn't crash during login)")


if __name__ == "__main__":
    asyncio.run(interactive_auth_setup())