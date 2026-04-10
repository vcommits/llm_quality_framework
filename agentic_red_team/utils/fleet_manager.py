# File: fleet_manager.py | Node: 2 (The Muscle)
# Version: 1.0 | Identity: godzilla_fleet_admiral
# Purpose: Consolidates launch.py and kill_fleet.py into an OOP controller.

import subprocess
import os
import platform
import logging
import time
from typing import List, Optional
from agentic_red_team.core.targets import TargetRegistry, KaijuTarget
from agentic_red_team.utils.identity_manager import manager as identity_manager

logger = logging.getLogger("FleetManager")


class FleetManager:
    """
    Manages the lifecycle of AI Agent applications on Node 2 and Node 3.
    Enforces Encapsulation of platform-specific terminal commands.
    """

    def __init__(self):
        self.is_mac = platform.system() == "Darwin"
        # Actual process names for pkill/taskkill
        self.zombie_targets = ["Ace", "Comet", "Perplexity", "BrowserOS", "Brave", "msedge", "chrome"]

    def cleanse(self):
        """Neutralizes all active agent processes to ensure a clean mission start."""
        logger.info("🧹 Cleansing Node Fleet...")
        for process in self.zombie_targets:
            try:
                if self.is_mac:
                    subprocess.run(["pkill", "-9", "-f", process], capture_output=True)
                else:
                    # Try with and without .exe extension for Windows
                    subprocess.run(["taskkill", "/F", "/IM", f"{process}.exe", "/T"], capture_output=True)
                    subprocess.run(["taskkill", "/F", "/IM", process, "/T"], capture_output=True)
            except Exception:
                pass
        time.sleep(1)

    def launch(self, target_id: str, persona_id: Optional[str] = None) -> bool:
        """
        Launches a specific target with remote debugging and persistent context.
        If persona_id is provided, it resolves the isolated profile path.
        """
        target_info = TargetRegistry.get_target(target_id)
        if not target_info:
            logger.error(f"❌ Target {target_id} not found in Registry.")
            return False

        exe_path = target_info['exe_path']
        port = target_info['debug_port']

        if not os.path.exists(exe_path):
            logger.error(f"❌ Executable not found: {exe_path}")
            return False

        # Build Command
        cmd = [exe_path, f"--remote-debugging-port={port}", "--no-first-run"]

        # Inject Persona Persistence if provided
        if persona_id:
            persona = identity_manager.get_identity(persona_id)
            profile_path = persona.profile_path
            cmd.append(f"--user-data-dir={profile_path}")

        # Handle Web vs Desktop App mode
        if not target_info.get('is_app') and target_info.get('url'):
            cmd.append(target_info['url'])

        try:
            logger.info(f"🚀 Firing Engine: {target_info['name']} on port {port}")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.error(f"❌ Launch failed: {e}")
            return False


if __name__ == "__main__":
    import sys

    fm = FleetManager()
    if "--clean" in sys.argv:
        fm.cleanse()
    
    # Allow: python fleet_manager.py ace attacker_brain_smart
    target = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None
    persona = sys.argv[2] if len(sys.argv) > 2 else None

    if target:
        fm.launch(target, persona)
