from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Annotated

# --- Configuration ---
# Node 1 (The Sentry/Pi 400) is the single source of truth.
NODE1_SENTRY_URL = "http://<NODE1_IP>:8001" 

# --- FastAPI App ---
app = FastAPI(title="Node X - Sentry Lite")
templates = Jinja2Templates(directory="nodex_sentry_lite/templates")

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_main_ui(request: Request):
    """Serves the main mobile-first UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/dispatch-fight", response_class=HTMLResponse)
async def dispatch_fight(models: Annotated[list[str], Form()], prompt: Annotated[str, Form()]):
    """Forwards a 'Fight!' Arena mission to the Node 1 Sentry."""
    async with httpx.AsyncClient() as client:
        try:
            # This is a simplified payload; a real one might be more complex
            response = await client.post(f"{NODE1_SENTRY_URL}/arena-mission", json={"models": models, "prompt": prompt})
            response.raise_for_status()
            return HTMLResponse("<div class='text-green-400'>Arena Mission Dispatched to Sentry.</div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-500'>Error: Sentry Offline</div>")

@app.get("/monitor", response_class=HTMLResponse)
async def monitor_sentry():
    """Polls Node 1 for real-time job status and eco-telemetry for the HUD."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{NODE1_SENTRY_URL}/monitor")
            response.raise_for_status()
            data = response.json()
            # This HTMX fragment updates the Environmental HUD
            return HTMLResponse(f"""
                <div id="hud-jobs" hx-swap-oob="true">Jobs Queued: {data.get('queue_length', 'N/A')}</div>
                <div id="hud-temp" hx-swap-oob="true">Eco-Temp: {data.get('eco_temp', 'N/A')}°C</div>
            """)
        except httpx.RequestError:
            return HTMLResponse("<div id='hud-jobs' hx-swap-oob='true'>Status: Sentry Offline</div>")

@app.post("/geo-swap", response_class=HTMLResponse)
async def trigger_geo_swap(region: Annotated[str, Form()]):
    """Sends a command to Node 1 to rotate the VPN profile on Node 0."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{NODE1_SENTRY_URL}/vpn/rotate", json={"region": region})
            response.raise_for_status()
            return HTMLResponse(f"<div class='text-yellow-400'>VPN rotation to {region} initiated.</div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-500'>Error: Sentry Offline</div>")

@app.post("/kill-switch", response_class=HTMLResponse)
async def trigger_kill_switch():
    """Sends a high-priority 'Hard Stop' command to Node 1."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{NODE1_SENTRY_URL}/emergency/stop")
            response.raise_for_status()
            return HTMLResponse("<div class='text-red-500 font-bold'>KILL SWITCH ACTIVATED.</div>")
        except httpx.RequestError:
            return HTMLResponse("<div class='text-red-500'>Error: Sentry Offline</div>")
