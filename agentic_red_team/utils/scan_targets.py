import requests
import json


def scan_debug_targets(port=9222):
    print(f"📡 SCANNING RAW TARGETS ON PORT {port}...")

    try:
        # The 'json/list' endpoint shows EVERYTHING attached to the debugger
        response = requests.get(f"http://127.0.0.1:{port}/json/list")
        targets = response.json()

        print(f"   [System] Found {len(targets)} active targets.\n")

        for i, t in enumerate(targets):
            title = t.get("title", "No Title")
            url = t.get("url", "No URL")
            t_type = t.get("type", "Unknown")

            print(f"   --- TARGET {i} ---")
            print(f"   Type:  {t_type}")
            print(f"   Title: {title}")
            print(f"   URL:   {url[:60]}...")
            print(f"   ID:    {t.get('id')}\n")

    except Exception as e:
        print(f"❌ Error connecting to port {port}: {e}")
        print("   (Make sure Ace is running with --remote-debugging-port=9222)")


if __name__ == "__main__":
    scan_debug_targets()  # <--- FIXED NAME