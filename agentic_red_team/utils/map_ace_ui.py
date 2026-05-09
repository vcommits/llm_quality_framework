import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team import config


async def map_ace_ui():
    print("==================================================")
    print("🗺️  MAPPING ACE BROWSER UI LAYERS")
    print("==================================================")

    # 1. Connect
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            print(f"   [System] Found {len(context.pages)} main pages (tabs).")

            # 2. Iterate through every page (Tab)
            for i, page in enumerate(context.pages):
                title = await page.title()
                print(f"\n   --- 📄 Page {i}: '{title}' ---")

                # 3. Iterate through every FRAME inside that page
                # (Sidebars and UI panels are often IFrames)
                frames = page.frames
                print(f"       Found {len(frames)} internal frames.")

                for j, frame in enumerate(frames):
                    try:
                        frame_name = frame.name if frame.name else f"frame_{j}"
                        frame_url = frame.url
                        print(f"       [Frame {j}] Name: '{frame_name}' | URL: {frame_url[:50]}...")

                        # 4. Dump HTML to find 'Nova'
                        content = await frame.content()
                        if "Nova" in content or "nova" in content:
                            print(f"       🎯 HIT! Found keyword 'Nova' in this frame!")

                        # 5. Save Evidence
                        filename = f"ace_page{i}_frame{j}.html"
                        filepath = os.path.join(config.EVIDENCE_DIR, filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    except Exception as e:
                        print(f"       ⚠️ Could not read Frame {j}: {e}")

        except Exception as e:
            print(f"❌ Connection Error: {e}")


if __name__ == "__main__":
    asyncio.run(map_ace_ui())