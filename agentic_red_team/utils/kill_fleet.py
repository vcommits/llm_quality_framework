import os
import subprocess
import time


def kill_process(process_name):
    try:
        # /F = Force, /IM = Image Name
        result = subprocess.run(
            ["taskkill", "/F", "/IM", process_name],
            capture_output=True,
            text=True
        )
        if "SUCCESS" in result.stdout:
            print(f"   💀 Killed: {process_name}")
    except Exception:
        pass


def cleanse_environment():
    print("==================================================")
    print("🧹 CLEANING UP ZOMBIE PROCESSES (SAFE MODE)")
    print("==================================================")

    # The Hit List: ONLY the AI Agents.
    # REMOVED: chrome.exe, firefox.exe, msedge.exe to save your browser!
    targets = [
        "Perplexity.exe",
        "Comet.exe",
        "Ace.exe",
        "brave.exe",
        "Fellou.exe",
        "BrowserOS.exe",
        "Arc.exe"
    ]

    for target in targets:
        kill_process(target)

    print("   [System] Cleanup complete. Your browser is safe.")
    time.sleep(1)


if __name__ == "__main__":
    cleanse_environment()