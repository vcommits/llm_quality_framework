import asyncio
import os
from playwright.async_api import async_playwright
from agentic_red_team.driver.base_driver import BaseDriver


class PlaywrightDriver(BaseDriver):
    def __init__(self, headless=True, executable_path=None, video_dir=None, channel=None, debug_port=None):
        super().__init__()
        self.headless = headless
        self.executable_path = executable_path
        self.video_dir = video_dir
        self.channel = channel
        self.debug_port = debug_port
        self.playwright = None
        self.browser = None
        self.context = None
        self._page = None

    async def start(self, storage_state=None):
        self.playwright = await async_playwright().start()

        # --- MODE A: HIJACK (Connect to running App) ---
        if self.debug_port:
            print(f"[Driver] 🔌 Connecting to App on 127.0.0.1:{self.debug_port}...")
            try:
                # Force IPv4
                endpoint = f"http://127.0.0.1:{self.debug_port}"
                self.browser = await self.playwright.chromium.connect_over_cdp(endpoint)

                # SMART WINDOW SELECTION (Now with Ghost Protection)
                if self.browser.contexts:
                    self.context = self.browser.contexts[0]
                    pages = self.context.pages
                    print(f"[Driver] Found {len(pages)} active windows.")

                    candidate_page = None

                    if pages:
                        for i, p in enumerate(pages):
                            try:
                                # Safe Title Check: If it fails, it's a ghost window
                                title = await p.title()
                                url = p.url
                                print(f"   - Window {i}: '{title}' [{url}]")

                                # Heuristic: The main window usually has a title or specific URL
                                # If we haven't picked one yet, pick the first valid one
                                if not candidate_page:
                                    candidate_page = p

                            except Exception as e:
                                print(f"   - Window {i}: [Ghost/Closed] ({e})")

                        if candidate_page:
                            self._page = candidate_page
                            # Bring to front
                            try:
                                await self._page.bring_to_front()
                            except:
                                pass
                            print(f"[Driver] ✅ Attached to Window: '{await self._page.title()}'")
                        else:
                            print("[Driver] ⚠️ No stable windows found. Defaulting to first index.")
                            self._page = pages[0]

                return  # SUCCESS
            except Exception as e:
                print(f"[Driver] ❌ Connection Failed: {e}")
                raise e

        # --- MODE B: LAUNCH (Standard Web Browser) ---
        print(f"[Driver] 👻 Launching New Browser Session...")
        launch_args = {
            "headless": self.headless,
            "args": ["--start-maximized", "--disable-blink-features=AutomationControlled"]
        }

        if self.executable_path:
            launch_args["executable_path"] = self.executable_path
        elif self.channel:
            launch_args["channel"] = self.channel

        self.browser = await self.playwright.chromium.launch(**launch_args)

        context_args = {}
        if self.video_dir:
            context_args["record_video_dir"] = self.video_dir
            context_args["record_video_size"] = {"width": 1280, "height": 720}

        if storage_state and os.path.exists(storage_state):
            print(f"[Driver] 🍪 Injecting Auth State: {os.path.basename(storage_state)}")
            context_args["storage_state"] = storage_state

        self.context = await self.browser.new_context(**context_args)
        self._page = await self.context.new_page()

    async def stop(self):
        if self.debug_port and self.browser:
            await self.browser.close()
        elif self.context:
            await self.context.close()
            if self.browser: await self.browser.close()

        if self.playwright: await self.playwright.stop()
        print("[Driver] Engine Stopped.")

    async def navigate(self, url):
        if self._page and not self.debug_port:
            try:
                await self._page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                pass

    async def get_state(self):
        if not self._page: return "", ""
        try:
            content = await self._page.content()
            text = await self._page.inner_text("body")
            return content, text
        except Exception:
            return "", ""

    async def execute_actions(self, actions):
        print(f"[Driver] executing {len(actions)} actions")
        return {"status": "success"}