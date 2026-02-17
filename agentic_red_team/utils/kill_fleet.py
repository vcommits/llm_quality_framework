import os
import subprocess
import time


def kill_process(process_name):
    try:
        result = subprocess.run(["taskkill", "/F", "/IM", process_name], capture_output=True, text=True)
        if "SUCCESS" in result.stdout:
            print(f"   💀 Killed: {process_name}")
    except Exception:
        pass


def cleanse_environment():
    print("==================================================")
    print("🧹🧟 CLEANING UP ZOMBIE PROCESSES")
    print("==================================================")

    # Only kill the Agent Apps, leave Chrome/Edge alone if possible
    targets = ["Perplexity.exe", "Comet.exe", "Ace.exe", "brave.exe", "Fellou.exe", "BrowserOS.exe"]

    for target in targets:
        kill_process(target)

    print("   [System] Cleanup complete.")
    time.sleep(1)


if __name__ == "__main__":
    cleanse_environment()