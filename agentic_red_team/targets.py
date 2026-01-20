# agentic_red_team/targets.py

class TargetRegistry:
    TARGETS = {
        # --- 1. NOVA (Ace Agent) ---
        "ace": {
            "name": "Ace Nova (Agent)",
            "is_app": True,
            "exe_path": r"C:\Program Files\Ace\Ace\Application\ace.exe",
            "debug_port": 9222,
            "selectors": {
                "input": "input[placeholder*='Ask me anything'], [aria-label*='Ask me anything']",
                "submit": "button[aria-label='Send']",
                "modal_close": None
            },
            "submit_key": "Enter"
        },

        # --- 2. COMET (Perplexity) ---
        "comet": {
            "name": "Perplexity Comet",
            "is_app": True,
            "exe_path": r"C:\Users\vmoor\AppData\Local\Perplexity\Comet\Application\comet.exe",
            "debug_port": 9222,
            "selectors": {
                "input": "#ask-input, textarea",
                "submit": ".right-toastHMargin > div > div > .gap-x-sm",
                "modal_close": "button[data-testid='floating-signup-close-button']"
            },
            "submit_key": "Enter"
        },

        # --- 3. FELLOU (Felo) ---
        "fellou": {
            "name": "Fellou AI",
            "is_app": True,
            "exe_path": r"D:\Docs\Fellou\Fellou.exe",
            "debug_port": 9222,
            "selectors": {
                "input": "textarea, input[placeholder*='Search']",
                "submit": "Enter",
                "modal_close": None
            },
            "submit_key": "Enter"
        },

        # --- 4. BRAVE LEO ---
        "brave": {
            "name": "Brave Browser (Leo)",
            "is_app": True,
            # CONFIRMED PATH
            "exe_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            "debug_port": 9222,
            "selectors": {
                # Leo lives in the sidebar. We cast a wide net for textareas.
                "input": "textarea[placeholder*='Ask'], input[placeholder*='Ask'], textarea",
                "submit": "div[role='button'][aria-label='Send']",
                "modal_close": None
            },
            "submit_key": "Enter"
        },

        # --- 5. BROWSEROS ---
        "browseros": {
            "name": "BrowserOS",
            "is_app": True,
            "exe_path": r"C:\Users\vmoor\AppData\Local\BrowserOS\BrowserOS\Application\chrome.exe",
            "debug_port": 9222,
            "selectors": {
                "input": "input[placeholder*='Ask'], input[placeholder*='Search'], input[placeholder*='Chat'], textarea",
                "submit": "Enter",
                "modal_close": None
            },
            "submit_key": "Enter"
        },

        # --- 6. CHATGPT (Web Mode) ---
        "chatgpt": {
            "name": "ChatGPT (OpenAI)",
            "is_app": False,
            "exe_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "debug_port": 9222,
            "url": "https://chatgpt.com",
            "selectors": {
                "input": "#prompt-textarea",
                "submit": "button[data-testid='send-button']",
                "modal_close": None
            },
            "submit_key": "Enter"
        }
    }

    @staticmethod
    def get_target(key):
        return TargetRegistry.TARGETS.get(key)