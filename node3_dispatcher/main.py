from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from typing import Annotated

from .mission_dispatcher import dispatch_mission

app = FastAPI(title="Node 3 Dispatcher")

@app.post("/dispatch", response_class=HTMLResponse)
async def dispatch_htmx(
    target_url: Annotated[str, Form()],
    browser_version: Annotated[str, Form()]
):
    """
    HTMX-compatible endpoint to dispatch a new mission.
    """
    if not target_url:
        raise HTTPException(status_code=400, detail="Target URL is required.")

    result = await dispatch_mission(target_url, browser_version)

    if result["status"] == "error":
        # Return an error message to be displayed in the UI
        return HTMLResponse(
            content=f"<div class='text-red-500 p-2 bg-red-900/50 rounded'>Error: {result['message']}</div>",
            status_code=500
        )

    # On success, return the "Mission Queued" status message
    return HTMLResponse(
        content=f"<div class='text-green-400 p-2 bg-green-900/50 rounded'>{result['message']}</div>"
    )

@app.get("/")
def root():
    return {"message": "Node 3 Dispatcher is online. POST to /dispatch."}
