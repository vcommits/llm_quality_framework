import asyncio
import sys
import os
import time

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agentic_red_team.driver.playwright_driver import PlaywrightDriver
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config


async def run_inspector(target_key):
    target = TargetRegistry.get_target(target_key)

    # Path to your saved session
    auth_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"../../scenarios/auth_states/{target_key}_state.json"))

    print("==================================================")
    print(f"🕵️  AUTH INSPECTOR: {target['name']}")
    print("==================================================")

    driver = PlaywrightDriver(headless=False, channel="chrome")

    # Load cookies!
    if os.path.exists(auth_path):
        print(f"[System] Loading authenticated session...")
        await driver.start(storage_state=auth_path)
    else:
        print(f"❌ Warning: No auth file found at {auth_path}")
        await driver.start()

    await driver.navigate(target['url'])

    print("\n❄️  BROWSER FROZEN! ❄️")
    print("-------------------------------------------------")
    print("1. Right-click the Search Bar (where you type prompts).")
    print("2. Select 'Inspect'.")
    print("3. Copy the 'class', 'id', or 'placeholder' attribute.")
    print("-------------------------------------------------")

    input("👉 Press ENTER here when you are done to close...")
    await driver.stop()


if __name__ == "__main__":
    asyncio.run(run_inspector("perplexity"))