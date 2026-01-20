import subprocess
import sys
import os
import time

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agentic_red_team.targets import TargetRegistry


def launch_app(target_key):
    target = TargetRegistry.get_target(target_key)

    if not target:
        print(f"❌ Error: Target '{target_key}' not found.")
        print("   Available targets: comet, ace, brave, fellou, browseros")
        return

    if not target.get("is_app"):
        print(f"❌ '{target_key}' is a website, not a desktop app. No need to launch it.")
        return

    exe_path = target.get("exe_path")
    port = target.get("debug_port", 9222)

    if not os.path.exists(exe_path):
        print(f"❌ Error: Executable not found at:")
        print(f"   {exe_path}")
        print("   -> Check the path in 'agentic_red_team/targets.py'")
        return

    print(f"🚀 Launching {target['name']}...")
    print(f"   Path: {exe_path}")
    print(f"   Port: {port}")

    # The Magic Command: Launch with Debug Port
    cmd = [exe_path, f"--remote-debugging-port={port}"]

    try:
        # Popen launches it without blocking the script
        subprocess.Popen(cmd)
        print("\n✅ Launch Successful!")
        print("   You can now run the test script:")
        print(f"   python agentic_red_team/campaigns/authenticated_test.py {target_key}")
    except Exception as e:
        print(f"❌ Failed to launch: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python launch.py [target_name]")
        print("Example: python launch.py ace")
    else:
        launch_app(sys.argv[1])