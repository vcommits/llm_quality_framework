# File: targets.py | Version: 2.3
# Added: Interaction 'Recipes' discovered in legacy framework mining.

import os
import platform


class KaijuTarget:
    def __init__(self, id, name, target_type, **kwargs):
        self.id = id
        self.name = name
        self.type = target_type
        self.paths = kwargs.get("paths", {})
        self.debug_port = kwargs.get("debug_port", 9222)
        self.url = kwargs.get("url", None)
        self.is_app = kwargs.get("is_app", True)

        # LEGACY INSIGHT: Specific interaction recipes for shadow DOMs
        self.selectors = kwargs.get("selectors", {"input": "textarea", "submit": "Enter"})
        self.use_pulse = kwargs.get("use_pulse", True)  # Space -> Backspace pulse

    def get_exe_path(self):
        current_os = platform.system()
        path = self.paths.get("Darwin" if current_os == "Darwin" else "Windows")
        return os.getenv(f"GHIDORAH_{self.id.upper()}_PATH", path)


class TargetRegistry:
    _REGISTRY = {
        "ace": KaijuTarget(
            id="ace", name="Ace Nova", target_type="agent",
            paths={"Windows": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ace\Ace.exe"), 
                   "Darwin": "/Applications/Ace.app/Contents/MacOS/Ace"},
            selectors={
                "input": "textarea[placeholder*='Ask'], input[placeholder*='Ask']",
                "submit": "img[alt='Send']"
            },
            use_pulse=True  # Ace requires 'Pulse' (Space/Backspace) to trigger React listeners
        ),
        "comet": KaijuTarget(
            id="comet", name="Perplexity Comet", target_type="agent",
            paths={"Windows": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Comet\Comet.exe"), 
                   "Darwin": "/Applications/Comet.app/Contents/MacOS/Comet"},
            selectors={
                "input": "textarea[placeholder*='Ask'], #ask-input",
                "submit": "button[aria-label='Submit'], .gap-x-sm"
            },
            use_pulse=False
        ),
        "edge": KaijuTarget(
            id="edge", name="Microsoft Edge", target_type="browser",
            paths={"Windows": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                   "Darwin": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"},
            url="https://www.bing.com/chat",
            selectors={"input": "textarea", "submit": "Enter"},
            is_app=False,
            use_pulse=True
        )
    }

    @classmethod
    def get_target(cls, key):
        t = cls._REGISTRY.get(key.lower())
        if not t: return None
        return {
            "name": t.name, "exe_path": t.get_exe_path(), "debug_port": t.debug_port,
            "selectors": t.selectors, "is_app": t.is_app, "url": t.url, "use_pulse": t.use_pulse
        }