# File: harvester.py | Node: 2 (The Muscle)
# Purpose: Fetches secrets from Node 1 Pi over the mesh into RAM.
# Logic: Zero-Trust (No keys stored on Node 2 disk).

import requests
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Harvester_Client")


class SecretHarvester:
    """Zero-Trust client: keys are held in RAM, never on the local disk."""

    def __init__(self, node1_ip: str = "100.101.24.26", port: int = 8000):
        self.librarian_url = f"http://{node1_ip}:{port}/api/v1/secret"

    def get_key(self, secret_name: str) -> Optional[str]:
        """
        Retrieves keys from the Node 1 Librarian.
        Implements exponential backoff for mesh reliability.
        """
        try:
            target = secret_name.upper().replace("-", "_")

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(f"{self.librarian_url}/{target}", timeout=5)
                    if response.status_code == 200:
                        return response.json().get("value")

                    if response.status_code == 404:
                        # If not found, try appending _KEY as a fallback for config names
                        fallback = f"{target}_KEY"
                        response = requests.get(f"{self.librarian_url}/{fallback}", timeout=5)
                        if response.status_code == 200:
                            return response.json().get("value")
                        # If fallback also 404s, we stop
                        return None

                    # For other status codes (e.g. 500), we allow retry logic to proceed
                except requests.exceptions.RequestException:
                    pass

                if attempt < max_retries - 1:
                    # Exponential backoff: 2, 4, 8...
                    time.sleep(2 ** (attempt + 1))

            return None
        except Exception as e:
            logger.error(f"🚨 Sentry Connection Error: {str(e)}")
            return None