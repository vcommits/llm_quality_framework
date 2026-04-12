import asyncio
from playwright.async_api import async_playwright

async def scout_the_range(target_url="http://192.168.1.1"):
    async with async_playwright() as p:
        # HEADFUL mode so you can see it in VNC
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"📡 Navigating to Node 0: {target_url}")
        await page.goto(target_url)
        await asyncio.sleep(5) # Let the Architect observe
        await page.screenshot(path="evidence/screenshots/router_scout.png")
        await browser.close()
        print("📸 Evidence captured.")

if __name__ == "__main__":
    asyncio.run(scout_the_range())