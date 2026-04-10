# File: authoring_tool.py | Node: 2 (The Muscle)
# Version: 1.0 | Identity: godzilla_author
# Purpose: HiL (Human-in-the-Loop) tool to build/fine-tune scripts on the Node 2 Desktop.

import asyncio
import sys
import os
from playwright.async_api import async_playwright
from agentic_red_team.targets import TargetRegistry
from agentic_red_team.utils.identity_manager import manager as identity_manager


class GhidorahAuthor:
    """
    Enables the 'Developer Pivot' on Node 2.
    Allows the Architect to remote in and refine Persona interactions.
    """

    def __init__(self, target_key: str, persona_id: str):
        self.target = TargetRegistry.get_target(target_key)
        self.persona = identity_manager.get_identity(persona_id)

        if not self.target:
            raise ValueError(f"❌ Target '{target_key}' not found in Registry.")

    async def ignite_session(self, mode: str = "live"):
        """
        Modes:
        'live'      - Opens browser for manual usage/viewing.
        'record'    - Opens Playwright Inspector for selector discovery.
        """
        async with async_playwright() as p:
            print(f"🐉 Initializing Authoring Session...")
            print(f"👤 Persona: {self.persona.name}")
            print(f"🎯 Target : {self.target['name']}")
            print(f"📂 Profile: {self.persona.profile_path}")

            # Lesson from launch.py: Use persistent context for logins/memories
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.persona.profile_path,
                executable_path=self.target['exe_path'],
                headless=False,  # Must be headful for HiL
                args=[
                    f"--remote-debugging-port={self.target['debug_port']}",
                    "--no-first-run"
                ]
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # If target has a URL (Web targets), go there first
            if self.target.get('url'):
                await page.goto(self.target['url'])

            if mode == "record":
                print("\n🕵️  PLAYWRIGHT INSPECTOR ACTIVE")
                print("👉 Use the Inspector window on the Node 2 Desktop to find selectors.")
                print("👉 When finished, close the Inspector or the Browser to save findings.")
                await page.pause()  # The 'Magic' HiL command from open_inspector.py
            else:
                print("\n🖥️  LIVE INTERVENTION MODE")
                print("👉 Use Screen Sharing to interact with the browser manually.")
                print("👉 Press Ctrl+C in this terminal or close the browser to end session.")
                
                # Keep session alive until the browser is closed or interrupted
                while len(context.pages) > 0:
                    await asyncio.sleep(1)

            await context.close()


if __name__ == "__main__":
    # Example usage: python authoring_tool.py edge vpm_contractor record
    target = sys.argv[1] if len(sys.argv) > 1 else "edge"
    persona = sys.argv[2] if len(sys.argv) > 2 else "standard"
    mode = sys.argv[3] if len(sys.argv) > 3 else "live"

    author = GhidorahAuthor(target, persona)
    try:
        asyncio.run(author.ignite_session(mode))
    except KeyboardInterrupt:
        print("\n🛑 Session terminated by Architect.")
