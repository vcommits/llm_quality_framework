from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Annotated

app = FastAPI(title="Node 3 - Architect")
templates = Jinja2Templates(directory="node3_architect/templates")

SENTRY_URL = "http://localhost:8001" # Node 1

@app.get("/", response_class=HTMLResponse)
async def get_architect_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dispatch", response_class=HTMLResponse)
async def dispatch_mission(
    persona_id: Annotated[str, Form()],
    target_url: Annotated[str, Form()]
):
    async with httpx.AsyncClient() as client:
        try:
            # Use data= for form submission, not json=
            response = await client.post(f"{SENTRY_URL}/jobs", data={"persona_id": persona_id, "target_url": target_url})
            response.raise_for_status()
            return HTMLResponse("<div class='text-cyan-400'>Mission Queued</div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-500'>Error: Sentry Offline</div>")

@app.get("/diary-update", response_class=HTMLResponse)
async def update_diary():
    """HTMX endpoint to poll for completed jobs."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SENTRY_URL}/monitor")
            response.raise_for_status()
            data = response.json()
            # This is a simplified representation for the stub
            return HTMLResponse(f"""
                <p>Pending: {data['queue_length']}</p>
                <p>Completed: {data['completed_count']}</p>
            """)
        except httpx.RequestError:
            return HTMLResponse("<p>Status: Sentry Offline</p>")
