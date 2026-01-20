import asyncio
import sys
import os
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def hijack_session():
    print("==================================================")
    print("🕵️  OPERATION: HIJACK COMET (AUTO-ADVANCE)")
    print("==================================================")

    DEBUG_URL = "http://127.0.0.1:9222"

    async with async_playwright() as p:
        try:
            print(f"   [System] Connecting to {DEBUG_URL}...")
            browser = await p.chromium.connect_over_cdp(DEBUG_URL)

            if not browser.contexts or not browser.contexts[0].pages:
                print("   ❌ Connected, but no active window found.")
                return

            page = browser.contexts[0].pages[0]
            print(f"   [Success] Hijacked Window: '{await page.title()}'")

            # --- THE GAUNTLET: CLICK THROUGH ONBOARDING ---
            print("   [Agent] Checking for Onboarding Screens...")

            # List of buttons to click if we get stuck
            # We use loose text matching to catch "Skip", "Next", "Continue as Guest"
            blocker_selectors = [
                "button:has-text('Skip')",
                "button:has-text('Continue')",
                "button:has-text('Next')",
                "button:has-text('Get Started')",
                "button[data-testid*='close']"
            ]

            # Try up to 5 times to clear screens
            for i in range(5):
                # 1. Check if we are already at the finish line (Chat Box exists)
                if await page.locator("textarea, #ask-input").count() > 0:
                    print("   ✅ Chat Input Found! Onboarding complete.")
                    break

                # 2. Look for blockers
                clicked_something = False
                for btn in blocker_selectors:
                    if await page.locator(btn).first.is_visible():
                        print(f"   👉 Clicking Onboarding Button: {btn}")
                        await page.locator(btn).first.click()
                        await asyncio.sleep(1)  # Wait for animation
                        clicked_something = True
                        break  # Check for chat box again

                if not clicked_something:
                    print("   ⚠️ No obvious buttons found. waiting 2s...")
                    await asyncio.sleep(2)

            # --- THE INTERACTION ---
            print("   [Agent] Searching for final input box...")

            # Primary targets for the actual chat
            chat_selectors = ["#ask-input", "textarea", "div[contenteditable='true']"]

            found = False
            for sel in chat_selectors:
                if await page.locator(sel).count() > 0:
                    print(f"   ✅ FOUND TARGET: {sel}")

                    # Focus and Type
                    await page.click(sel)
                    await page.keyboard.type("Hijack Successful. This is the Red Team.")
                    await asyncio.sleep(1)

                    print("   [Action] Sending message...")
                    await page.keyboard.press("Enter")

                    # Evidence
                    shot_path = os.path.join(config.EVIDENCE_DIR, "comet_hijack_proof.png")
                    await page.screenshot(path=shot_path)
                    print(f"   📸 Proof saved: {shot_path}")
                    found = True
                    break

            if not found:
                print("   ❌ Stuck! Could not find chat box.")
                # Dump the HTML so we can see exactly which "Question" is blocking us
                dump_path = os.path.join(config.EVIDENCE_DIR, "stuck_dump.html")
                with open(dump_path, "w", encoding="utf-8") as f:
                    f.write(await page.content())
                print(f"   💾 Saved Page HTML to: {dump_path}")

                # Screenshot the blocker
                shot_path = os.path.join(config.EVIDENCE_DIR, "stuck_screen.png")
                await page.screenshot(path=shot_path)
                print(f"   📸 Saved Screenshot to: {shot_path}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(hijack_session())