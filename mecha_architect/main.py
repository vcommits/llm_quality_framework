from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import httpx
from typing import Annotated

from . import database

# --- App Initialization ---
app = FastAPI(title="Node 3 - Mecha-Architect")
database.init_db() # Create DB tables on startup

templates = Jinja2Templates(directory="mecha_architect/templates")

# --- Dependency ---
def get_db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Main UI Endpoint ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main Intelligence Hub UI."""
    return templates.TemplateResponse("index.html", {"request": request})

# --- Mission Dispatcher Endpoint ---
@app.post("/dispatch-mission", response_class=HTMLResponse)
async def dispatch_mission(
    request: Request,
    target_url: Annotated[str, Form()],
    persona: Annotated[str, Form()],
    browser: Annotated[str, Form()]
):
    """
    Receives mission details from the UI and POSTs to the Node 1 Sentry.
    """
    node1_url = "http://<NODE1_IP>:8000/api/v1/jobs" # Replace with actual Node 1 IP
    payload = {
        "target_url": target_url,
        "persona_id": persona,
        "browser_version": browser
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(node1_url, json=payload)
            response.raise_for_status()
            # On success, return a confirmation message to the UI
            return HTMLResponse("<div class='text-green-400'>Mission Queued on Node 1 Sentry.</div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-400'>Error: Could not connect to Node 1 Sentry.</div>")
        except httpx.HTTPStatusError as e:
            return HTMLResponse(f"<div class='text-red-400'>Error: {e.response.text}</div>")

# --- 1-on-1 Interrogation Mode Endpoint ---
@app.post("/interrogate", response_class=HTMLResponse)
async def interrogate_node2(prompt: Annotated[str, Form()]):
    """
    Acts as a thin client to send a direct prompt to Node 2's Ollama stable.
    """
    node2_url = "http://<NODE2_IP>:11434/api/generate" # Standard Ollama API endpoint
    payload = {
        "model": "llava", # Example model, could be configurable
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(node2_url, json=payload)
            response.raise_for_status()
            api_response = response.json()
            # Return just the response text to be swapped into the chat history
            return HTMLResponse(f"<div><p class='text-cyan-300'>{api_response.get('response', 'No content.')}</p></div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-400'>Error: Could not connect to Node 2 Engine.</div>")
        except Exception as e:
            return HTMLResponse(f"<div class='text-red-400'>Error: {str(e)}</div>")


# --- Data Viz Layer (Placeholders) ---
@app.get("/safety-analytics")
def get_safety_analytics():
    # In a real app, this would query the diary DB and return aggregated data
    return {"placeholder": "Safety Analytics Data (e.g., Garak Scores Over Time)"}

@app.get("/quality-metrics")
def get_quality_metrics():
    # In a real app, this would query the diary DB and return aggregated data
    return {"placeholder": "Quality Metrics Data (e.g., Hallucination Rates)"}
