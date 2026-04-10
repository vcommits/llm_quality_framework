# File: discovery.py | Node: 2 (The Muscle)
# Version: 1.1 | Identity: godzilla_discovery_sentry
# Purpose: Consolidates map_ace_ui.py, scan_targets.py, and accessibility checks.

import asyncio
import logging
import json
import requests
import time
from typing import List, Dict, Optional
from playwright.async_api import Page, Frame

logger = logging.getLogger("DiscoveryEngine")


class DiscoveryEngine:
    """
    Deep-probes the UI layer of Agentic Browsers.
    Used for 'Handshake' verification and iFrame mapping.
    """

    @staticmethod
    async def crawl_frames(page: Page, keyword: str = "nova") -> List[Dict]:
        """
        Mined from map_ace_ui.py: Recursively searches all iFrames
        for an LLM interface keyword. Returns metadata for hits.
        """
        hits = []
        frames = page.frames
        logger.info(f"🔍 Scanning {len(frames)} frames for '{keyword}'...")

        for i, frame in enumerate(frames):
            try:
                # Some frames might be cross-origin and restricted
                content = await frame.content()
                if keyword.lower() in content.lower():
                    logger.info(f"🎯 HIT: Found '{keyword}' in frame[{i}] ({frame.name})")
                    hits.append({
                        "index": i,
                        "name": frame.name,
                        "url": frame.url,
                        "frame_obj": frame
                    })
            except Exception:
                continue
        return hits

    @staticmethod
    def get_debug_targets(port: int = 9222) -> List[Dict]:
        """
        Mined from scan_targets.py: Returns raw CDP targets from the port.
        Useful for verifying if an app is truly running in debug mode.
        """
        try:
            res = requests.get(f"http://127.0.0.1:{port}/json/list", timeout=2)
            return res.json()
        except Exception:
            return []

    @staticmethod
    async def wait_for_target(port: int, timeout: int = 30) -> bool:
        """Polls the debug port until a valid target response is received."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            targets = DiscoveryEngine.get_debug_targets(port)
            if targets:
                logger.info(f"✅ Debug Port {port} is active with {len(targets)} targets.")
                return True
            await asyncio.sleep(2)
        logger.error(f"❌ Timeout waiting for debug port {port}")
        return False

    @staticmethod
    async def verify_identity_signature(page: Page, keywords: Optional[List[str]] = None) -> bool:
        """
        Uses accessibility snapshots to detect if a Persona is logged in.
        Inherits logic from setup_auth.py.
        """
        keywords = keywords or ["profile", "account", "logout", "ask", "chat", "settings"]
        try:
            snapshot = await page.accessibility.snapshot()
            if not snapshot:
                return False

            def check_node(node):
                name = str(node.get("name", "")).lower()
                # Check current node
                if any(k in name for k in keywords):
                    return True
                # Recursive check children
                for child in node.get("children", []):
                    if check_node(child):
                        return True
                return False

            found = check_node(snapshot)
            if found:
                logger.info("👤 Identity Signature Verified via Accessibility Tree.")
            return found
        except Exception as e:
            logger.error(f"⚠️ Accessibility probe failed: {e}")
            return False

    @staticmethod
    async def get_element_state(page: Page, selector: str) -> Dict:
        """Returns the readiness state of a specific UI element."""
        try:
            locator = page.locator(selector).first
            if await locator.count() == 0:
                return {"exists": False}
            
            return {
                "exists": True,
                "visible": await locator.is_visible(),
                "enabled": await locator.is_enabled(),
                "editable": await locator.is_editable()
            }
        except Exception:
            return {"exists": False, "error": "State probe failed"}
