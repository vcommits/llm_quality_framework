import httpx
import uuid
from typing import Dict, Any

from .identity_manager import get_active_hydra_persona

# Configuration
NODE1_SENTRY_URL = "http://<Node1_IP>:8000/api/v1/jobs" # IMPORTANT: Replace with Node 1's actual IP

async def dispatch_mission(target_url: str, browser_version: str) -> Dict[str, Any]:
    """
    Constructs a job payload and sends it to the Node 1 Sentry.
    """
    # 1. Fetch the active Hydra Persona
    active_persona = get_active_hydra_persona()

    # 2. Construct the Job Payload
    mission_id = str(uuid.uuid4())
    job_payload = {
        "mission_id": mission_id,
        "campaign_details": {
            "target_url": target_url,
            "persona_id": active_persona["persona_id"],
            "browser_version": browser_version,
            "user_agent": active_persona["user_agent"]
        }
    }

    # 3. Implement an async POST request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(NODE1_SENTRY_URL, json=job_payload)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            
            # 4. Return status for UI update
            return {
                "status": "success",
                "message": f"Mission {mission_id} Queued on Node 1.",
                "details": response.json()
            }
        except httpx.RequestError as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Node 1 Sentry: {e}"
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"Error response from Node 1 Sentry: {e.response.status_code}"
            }
