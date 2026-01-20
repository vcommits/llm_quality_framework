import asyncio
import sys
import os

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agentic_red_team.driver.playwright_driver import PlaywrightDriver
from agentic_red_team.targets import TargetRegistry
from agentic_red_team import config

# 🔴 CONFIGURATION: FULL PATH TO COMET.EXE
# We point to the "comet.exe" inside the "Application" folder as you confirmed.
COMET_PATH = r"C:\Users\vmoor\AppData\Local\Perplexity\Comet\Application\comet.exe"


async def run_comet_test():
    # 1. Verify Path
    if not os.path.exists(COMET_PATH):
        print(f"❌ Error: Executable not found at: {COMET_PATH}")
        print("   👉 Check the path in Windows Explorer and update this script.")
        return

    print("==================================================")
    print("🚀 LAUNCHING PERPLEXITY DESKTOP (COMET)")
    print("==================================================")

    # 2. Load Target Config
    target = TargetRegistry.get_target("comet_app")

    # 3. Initialize Driver with CUSTOM EXECUTABLE
    driver = PlaywrightDriver(
        headless=False,
        executable_path=COMET_PATH,
        video_dir=config.VIDEO_DIR
    )

    try:
        await driver.start()
        print("   [App] Application launched.")

        # Desktop apps need time to load the UI
        print("   [Agent] Waiting for App UI to load (8s)...")
        await asyncio.sleep(8)

        if driver._page:
            selectors = target["selectors"]
            print(f"   [Agent] Targeting Input: {selectors['input']}")

            # --- INTERACTION BLOCK ---
            try:
                # 1. Click Input
                await driver._page.click(selectors["input"], timeout=5000)

                # 2. Type Message
                await driver._page.keyboard.type("Hello Comet. This is an automated Red Team test.")
                await asyncio.sleep(1)

                # 3. Send
                print("   [Agent] Sending Message...")
                await driver._page.keyboard.press("Enter")

                print("   [Success] Message sent. Keeping window open for 10s...")
                await asyncio.sleep(10)

                # 4. Evidence
                shot_path = os.path.join(config.EVIDENCE_DIR, "comet_desktop_test.png")
                await driver._page.screenshot(path=shot_path)
                print(f"   📸 Evidence saved: {shot_path}")

            except Exception as e:
                print(f"   ⚠️ Interaction failed: {e}")
                # We usually expect some selector issues on Desktop apps initially

    except Exception as e:
        print(f"❌ Error during Comet execution: {e}")
    finally:
        await driver.stop()


if __name__ == "__main__":
    asyncio.run(run_comet_test())