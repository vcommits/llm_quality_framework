from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List
import time
import os
import requests
import asyncio

from utils.payload_modifiers import PayloadMutator
from utils.model_harvester import ModelHarvester
from utils.payload_catalog import PayloadCatalog
from agentic_red_team.core.metrics import TelemetryEngine
from agentic_red_team.driver.playwright_driver import PlaywrightDriver

from litellm import completion

app = FastAPI(title="Ghidorah Node X API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mutator = PayloadMutator(node_tier="high")
honeypot_status = {"status": "ARMED", "last_hit": None}

# --- Pydantic Models ---
class MutateRequest(BaseModel):
    text: str
    methods: List[dict]

class TelemetryRequest(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int

class DispatchRequest(BaseModel):
    model: str
    payload: Any
    system_prompt: str = "You are a helpful assistant."

class BrowseRequest(BaseModel):
    url: str

# --- API Endpoints ---
@app.get("/")
def health_check():
    return {"status": "online", "node": "X"}

@app.post("/api/v1/honeypot_ping")
async def honeypot_ping():
    honeypot_status["status"] = "TRAP SPRUNG!"
    honeypot_status["last_hit"] = time.time()
    return {"status": "acknowledged"}

@app.get("/api/v1/honeypot_status")
def get_honeypot_status():
    # Reset status after a while to make the UI dynamic
    if honeypot_status["last_hit"] and (time.time() - honeypot_status["last_hit"] > 30):
        honeypot_status["status"] = "ARMED"
    return honeypot_status

@app.get("/api/v1/honeypot/payloads")
def list_honeypot_payloads():
    # This would ideally be a more robust discovery method, but for now, we'll hardcode
    # based on the known structure of the ghidorah-honeypot project.
    # In a real mesh, this might be a service discovery call.
    return {
        "payloads": [
            {"name": "World of Warcraft Injection", "id": "wow"},
            {"name": "Corporate Login Lure", "id": "corporate_login"},
        ],
        "base_url": "http://192.168.1.200/index.cgi" # Your Honeypot IP
    }

@app.post("/api/v1/mutate")
def mutate_payload(req: MutateRequest):
    result = req.text
    for m in req.methods:
        method_name = m.get("method")
        sev = m.get("severity", 0.5)
        if method_name == "translation_bypass":
            target_lang = m.get("target_lang", "ar")
            result = f"[REDIRECT_{target_lang.upper()}]: {result}"
        else:
            result = mutator.mutate(result, method_name, severity=sev)
    return {"original": req.text, "mutated": result}

@app.post("/api/v1/telemetry/burn")
def calculate_burn(req: TelemetryRequest):
    burn = TelemetryEngine.calculate_burn(req.model, req.prompt_tokens, req.completion_tokens)
    return burn

@app.post("/api/v1/dispatch")
async def live_dispatch(req: DispatchRequest):
    if "offline" in req.model.lower():
        time.sleep(1)
        mock_text = req.payload if isinstance(req.payload, str) else "[Multimodal Payload]"
        return {"response": f"[Offline Mode] Received: '{mock_text}'", "usage": {"prompt_tokens": 10, "completion_tokens": 20}, "latency_ms": 1000}
        
    try:
        start_time = time.time()
        messages = [{"role": "system", "content": req.system_prompt}, {"role": "user", "content": req.payload}]
        res = await completion(model=req.model, messages=messages)
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "response": res.choices[0].message.content,
            "usage": res.usage.model_dump() if hasattr(res, 'usage') and res.usage else {},
            "latency_ms": latency_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/browse")
async def browse_url(req: BrowseRequest):
    driver = PlaywrightDriver(headless=True)
    try:
        await driver.start()
        await driver.navigate(req.url)
        content, text = await driver.get_state()
        return {"url": req.url, "html_content": content, "text_content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse URL: {e}")
    finally:
        await driver.stop()

@app.get("/api/v1/catalog")
def get_catalog():
    return {
        "languages": PayloadCatalog.LANGUAGES,
        "tricky_payloads": PayloadCatalog.TRICKY_PAYLOADS,
        "extended_chars": PayloadCatalog.EXTENDED_CHARS,
        "emojis": PayloadCatalog.EMOJIS
    }

@app.get("/api/v1/models")
def list_models():
    try:
        hydrated_models = []
        if os.getenv("OPENAI_API_KEY"):
            hydrated_models.append({"id": "openai/gpt-4o", "name": "GPT-4o (Vision)", "provider": "openai", "capabilities": ["vision", "chat"], "type": "multimodal", "status": "online"})
        if os.getenv("ANTHROPIC_API_KEY"):
            hydrated_models.append({"id": "anthropic/claude-3-opus-20240229", "name": "Claude 3 Opus", "provider": "anthropic", "capabilities": ["chat"], "type": "language/chat", "status": "online"})
        
        if not hydrated_models:
            return {"models": [{"id": "offline/gpt-mock", "name": "Mock System", "provider": "offline", "capabilities": ["chat"], "type": "language/chat", "status": "offline"}]}
        
        return {"models": hydrated_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
