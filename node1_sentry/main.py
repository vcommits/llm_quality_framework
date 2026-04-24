from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

# --- In-Memory Queues ---
MISSION_QUEUE = []
COMPLETED_MISSIONS = []

# --- Pydantic Models ---
class Mission(BaseModel):
    mission_id: str
    persona_id: str
    target_url: str
    status: str = "queued"

# --- FastAPI App ---
app = FastAPI(title="Node 1 - Sentry")

@app.post("/jobs", status_code=201)
def create_job(persona_id: str, target_url: str):
    mission_id = str(uuid.uuid4())
    mission = Mission(mission_id=mission_id, persona_id=persona_id, target_url=target_url)
    MISSION_QUEUE.append(mission)
    return mission

@app.get("/jobs/next", response_model=Optional[Mission])
def get_next_job():
    if MISSION_QUEUE:
        mission = MISSION_QUEUE.pop(0)
        mission.status = "claimed"
        return mission
    return None

@app.post("/jobs/complete/{mission_id}")
def complete_job(mission_id: str):
    # In a real app, you'd verify the job existed and was claimed
    COMPLETED_MISSIONS.append(mission_id)
    return {"status": "completed", "mission_id": mission_id}

@app.get("/monitor")
def monitor_queue():
    return {"queue_length": len(MISSION_QUEUE), "completed_count": len(COMPLETED_MISSIONS)}
