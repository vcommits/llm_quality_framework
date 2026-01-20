import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agentic_red_team.driver.playwright_driver import PlaywrightDriver
from agentic_red_team import config

# YOUR PATH
COMET_PATH = r"C:\Users\vmoor\AppData\Local\Perplexity\Comet\Application\comet.exe"


async def debug_comet():
    print(f"🕵️  DEBUGGING COMET APP: {COMET_PATH}")

    # Launch with stability flags
    driver = PlaywrightDriver(
        headless=False,
        executable_path=COMET_PATH,
        video_dir=config.VIDEO_DIR
    )

    try:
        await driver.start()
        print("   [App] Launched. Waiting 10s for UI to settle...")
        await asyncio.sleep(10)

        # 1. LIST ALL PAGES/WINDOWS
        # Sometimes apps have hidden background windows
        pages = driver.context.pages
        print(f"   [System] Found {len(pages)} active window(s).")

        for i, page in enumerate(pages):
            title = await page.title()
            url = page.url
            print(f"   --- Window {i + 1}: '{title}' ({url}) ---")

            # Save the HTML source of this window
            try:
                content = await page.content()
                filename = f"comet_dump_window_{i + 1}.html"
                filepath = os.path.join(config.EVIDENCE_DIR, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"      💾 HTML Saved to: {filepath}")

                # Take a screenshot to see what it looks like
                shot_path = os.path.join(config.EVIDENCE_DIR, f"comet_debug_{i + 1}.png")
                await page.screenshot(path=shot_path)
                print(f"      📸 Screenshot: {shot_path}")

            except Exception as e:
                print(f"      ⚠️ Could not dump window {i + 1}: {e}")

    except Exception as e:
        print(f"❌ Crash: {e}")
    finally:
        await driver.stop()


if __name__ == "__main__":
    asyncio.run(debug_comet())