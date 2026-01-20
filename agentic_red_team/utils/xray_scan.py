import asyncio
import sys
import os
import time
from playwright.async_api import async_playwright

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


async def xray_scan():
    print("==================================================")
    print("💀 OPERATION X-RAY: SCANNING ACCESSIBILITY TREE")
    print("==================================================")

    async with async_playwright() as p:
        try:
            # 1. Connect
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            print(f"   [System] Driving: {await page.title()}")

            # 2. Go to "Neutral Ground" (Wikipedia)
            # Nova is likely disabled on the "New Tab" page
            print("   [Setup] Navigating to Wikipedia to wake up Nova...")
            await page.goto("https://www.wikipedia.org")
            time.sleep(5)  # Give the UI time to inject itself

            # 3. The Scan
            print("   [Scan] Dumping Accessibility Tree...")
            snapshot = await page.accessibility.snapshot()

            # Recursive printer to find the needle in the haystack
            def print_interesting_nodes(node, depth=0):
                indent = "   " * depth
                name = node.get("name", "Unnamed")
                role = node.get("role", "Unknown")

                # Filter: We only care about interactive things or "AI" words
                interesting_roles = ["button", "textbox", "searchbox", "menu", "tree", "dialog"]
                interesting_words = ["nova", "agent", "ai", "chat", "assistant", "sidebar", "ask", "personalize"]

                is_interesting = role in interesting_roles or any(w in name.lower() for w in interesting_words)

                if is_interesting:
                    # Clean output
                    print(f"{indent}🔹 [{role}] '{name}'")

                    if any(w in name.lower() for w in interesting_words):
                        print(f"{indent}   🔥🔥 POTENTIAL TARGET FOUND! 🔥🔥")

                # Dig deeper
                for child in node.get("children", []):
                    print_interesting_nodes(child, depth + 1)

            print_interesting_nodes(snapshot)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(xray_scan())