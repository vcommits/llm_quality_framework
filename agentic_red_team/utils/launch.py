import subprocess
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team.targets import TargetRegistry


def launch_app(target_key):
    target = TargetRegistry.get_target(target_key)
    if not target:
        print(f"❌ Error: Target '{target_key}' not found.")
        return

    if not target.get("is_app"):
        # For Web targets like ChatGPT, we assume we launch Chrome with a persistent profile
        exe_path = target.get("exe_path")
        port = target.get("debug_port", 9222)
        user_data = f"C:\\RedTeam_Profiles\\{target_key}_Profile"
        os.makedirs(user_data, exist_ok=True)

        cmd = [exe_path, f"--remote-debugging-port={port}", f"--user-data-dir={user_data}", target.get("url")]
    else:
        # For Desktop Apps
        exe_path = target.get("exe_path")
        port = target.get("debug_port", 9222)

        if not os.path.exists(exe_path):
            print(f"❌ Error: Executable not found at: {exe_path}")
            return

        cmd = [exe_path, f"--remote-debugging-port={port}"]

        # Optional: Add user data dir if we want to force a specific profile
        # cmd.append(f"--user-data-dir=C:\\Users\\...\\AppData\\Roaming\\{target_key}")

    print(f"🚀 Launching {target['name']}...")
    try:
        subprocess.Popen(cmd)
        print("✅ Launch Successful!")
    except Exception as e:
        print(f"❌ Failed to launch: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python launch.py [target_name]")
    else:
        launch_app(sys.argv[1])