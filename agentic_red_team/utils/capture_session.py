import asyncio
import os
import sys

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from playwright.async_api import async_playwright
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config


async def login_and_capture(target_key):
    target = TargetRegistry.get_target(target_key)
    if not target:
        print(f"❌ Target '{target_key}' not found.")
        return

    print("==================================================")
    print(f"🔐 AUTH CAPTURE: {target['name']}")
    print("==================================================")
    print("1. Browser will open.")
    print("2. You have 60 seconds to LOG IN manually.")
    print("3. Once logged in, the script will save your cookies.")
    print("==================================================")

    async with async_playwright() as p:
        # Use Real Chrome so Google Login works
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(target['url'])

        # Wait for user to do their thing
        print("\n⏳ WAITING FOR MANUAL LOGIN...")
        print("👉 Go to the browser. Log in. Handle 2FA.")
        print("👉 When you see your profile icon/dashboard, come back here.")

        input("👉 PRESS ENTER HERE WHEN YOU ARE LOGGED IN...")

        # Save the session state (cookies + local storage)
        # We create a specific folder for these credentials
        auth_dir = os.path.join(os.path.dirname(__file__), "../../scenarios/auth_states")
        os.makedirs(auth_dir, exist_ok=True)

        auth_path = os.path.join(auth_dir, f"{target_key}_state.json")
        await context.storage_state(path=auth_path)

        print(f"\n✅ SUCCESS! Session saved to:")
        print(f"   📂 {auth_path}")
        print("   (Future scripts can now use this file to skip login)")

        await browser.close()


if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "perplexity"
    asyncio.run(login_and_capture(target_arg))