import os, json, uvicorn, logging, httpx, asyncio
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Sentry")

# --- Forensic Noir Constants ---
CLOAK_IP = "100.120.132.20"
ENGINE_TARGET = "100.107.125.52"
AERIAL_MUSCLE_TARGET = "node-c-brain-spot" # Internal DNS or specific Tailscale IP of Node C

# --- Pydantic Data Models ---

class Pricing(BaseModel):
    input_cost: Optional[float] = Field(None, description="Cost per 1 million input tokens/units")
    output_cost: Optional[float] = Field(None, description="Cost per 1 million output tokens/units")
    unit: str = "tokens"

class UnifiedModel(BaseModel):
    provider: str
    model_id: str
    name: str
    type: Literal["functional", "image", "chat", "video", "audio", "rerank", "embedding"]
    deployment: Literal["serverless", "dedicated", "cloud_spot"]
    pricing: Pricing

class DispatchPayload(BaseModel):
    task_type: Literal["whisper_synthesis", "slm_inference", "garak_sweeps", "standard_api", "heavy_inference"]
    payload: Dict[str, Any]

# --- Cost Calculation Helper ---

def estimate_cost(model: UnifiedModel, tokens: int = 1000) -> float:
    """Estimates the cost of an injection attempt."""
    if not model.pricing or model.pricing.input_cost is None:
        return 0.0
    
    cost_per_token = model.pricing.input_cost / 1_000_000
    return cost_per_token * tokens

# --- Manifest Manager ---

class ManifestManager:
    def __init__(self):
        self.registry: List[UnifiedModel] = []
        self._load_and_hydrate()

    def _load_and_hydrate(self):
        dummy_data = [
            {"provider": "Together AI", "model_id": "togethercomputer/llama-3-8b-chat", "name": "Llama 3 8B (Together)", "type": "chat", "deployment": "serverless", "pricing": {"input_cost": 0.2, "output_cost": 0.2, "unit": "1M tokens"}},
            {"provider": "Fireworks AI", "model_id": "accounts/fireworks/models/llama-v3-8b-instruct", "name": "Llama 3 8B (Fireworks)", "type": "chat", "deployment": "serverless", "pricing": {"input_cost": 0.16, "output_cost": 0.16, "unit": "1M tokens"}},
            {"provider": "Azure", "model_id": "azure-gpt-4o", "name": "GPT-4o (Azure)", "type": "chat", "deployment": "dedicated", "pricing": {"input_cost": 5.0, "output_cost": 15.0, "unit": "1M tokens"}},
            {"provider": "Hugging Face", "model_id": "google/gemma-2-9b-it", "name": "Gemma 2 9B", "type": "chat", "deployment": "serverless", "pricing": {"input_cost": 0.1, "output_cost": 0.1, "unit": "1M tokens"}},
            {"provider": "Together AI", "model_id": "stabilityai/stable-diffusion-xl-base-1.0", "name": "SDXL 1.0", "type": "image", "deployment": "serverless", "pricing": {"input_cost": 0.8, "output_cost": 0.8, "unit": "images"}},
            # New Node C Models
            {"provider": "Ghidorah Node C", "model_id": "unsloth/llama-3-8b-Instruct-bnb-4bit", "name": "Llama 3 8B (Local T4)", "type": "chat", "deployment": "cloud_spot", "pricing": {"input_cost": 0.0, "output_cost": 0.0, "unit": "1M tokens"}},
            {"provider": "Ghidorah Node C", "model_id": "whisper-small", "name": "Whisper STT (Local T4)", "type": "audio", "deployment": "cloud_spot", "pricing": {"input_cost": 0.0, "output_cost": 0.0, "unit": "minutes"}},
        ]
        for item in dummy_data:
            self.registry.append(UnifiedModel(**item))
        logger.info(f"Hydrated {len(self.registry)} models into the registry.")

    def search(self, provider: Optional[str], type: Optional[str], deployment: Optional[str]) -> List[UnifiedModel]:
        results = self.registry
        if provider:
            results = [m for m in results if m.provider.lower() == provider.lower()]
        if type:
            results = [m for m in results if m.type.lower() == type.lower()]
        if deployment:
            results = [m for m in results if m.deployment.lower() == deployment.lower()]
        return results

# --- FastAPI Application ---

app = FastAPI(title="Ghidorah Sentry API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
registry_manager = ManifestManager()

# --- Intelligence Handshake Utilities ---

async def verify_tactical_cloak() -> bool:
    """Pings Node 0 (Tactical Cloak) to confirm it is online before dispatching."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(f"http://{CLOAK_IP}/")
            return True
    except httpx.RequestError:
        logger.error(f"[TACTICAL CLOAK OFFLINE] Failed to reach {CLOAK_IP}")
        return False

async def verify_aerial_muscle() -> bool:
    """Pings Node C (Aerial Muscle) to confirm the Spot VM is active."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            # Assumes Node C is running the Orchestrator on port 8000
            response = await client.get(f"http://{AERIAL_MUSCLE_TARGET}:8000/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("gpu_available"):
                    return True
            return False
    except httpx.RequestError:
        logger.warning(f"[AERIAL MUSCLE OFFLINE] Spot instance {AERIAL_MUSCLE_TARGET} unreachable.")
        return False

# --- Core Endpoints ---

@app.post("/librarian/dispatch")
async def librarian_dispatch(request: DispatchPayload):
    """
    LIBRARIAN_DISPATCH: Routes requests dynamically.
    Lightweight tasks go to Node 2 (Engine).
    Heavy tasks go to Node C (Aerial Muscle).
    """
    local_engine_tasks = ["garak_sweeps"]
    cloud_engine_tasks = ["whisper_synthesis", "slm_inference", "heavy_inference"]
    
    if request.task_type in cloud_engine_tasks:
        logger.info(f"Cloud-class task detected: {request.task_type}. Checking Aerial Muscle availability.")

        node_c_active = await verify_aerial_muscle()
        if not node_c_active:
            raise HTTPException(status_code=503, detail="Dispatch Aborted: Aerial Muscle (Node C) is preempted or offline.")

        # Ensure Cloak is active even for Cloud routing if we're bouncing traffic through it
        cloak_active = await verify_tactical_cloak()
        if not cloak_active:
             raise HTTPException(status_code=503, detail="Dispatch Aborted: Tactical Cloak (Node 0) is offline.")

        logger.info(f"Routing heavy payload to Aerial Muscle at {AERIAL_MUSCLE_TARGET}.")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client: # Longer timeout for heavy inference
                # Assuming infer endpoint handles generic payloads
                endpoint = "/api/v1/infer" if request.task_type != "whisper_synthesis" else "/api/v1/transcribe"
                response = await client.post(f"http://{AERIAL_MUSCLE_TARGET}:8000{endpoint}", json=request.payload)
                response.raise_for_status()
                return {"status": "success", "engine_response": response.json(), "node": "Node C"}
        except httpx.RequestError as e:
             raise HTTPException(status_code=502, detail=f"Node C unreachable: {e}")

    elif request.task_type in local_engine_tasks:
        logger.info(f"Local Engine-class task detected: {request.task_type}. Commencing Intelligence Handshake.")
        
        cloak_active = await verify_tactical_cloak()
        if not cloak_active:
            raise HTTPException(status_code=503, detail="Dispatch Aborted: Tactical Cloak (Node 0) is offline or compromised.")
            
        logger.info(f"Tactical Cloak verified. Routing payload to Local Engine Target at {ENGINE_TARGET}.")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"http://{ENGINE_TARGET}:8000/execute", json=request.payload)
                response.raise_for_status()
                return {"status": "success", "engine_response": response.json(), "node": "Node 2"}
        except httpx.RequestError as e:
             raise HTTPException(status_code=502, detail=f"Local Engine Target unreachable: {e}")
             
    else:
        return {"status": "success", "message": "Standard API task executed locally or routed to external provider."}


@app.get("/ui/mesh-status", response_class=HTMLResponse)
async def get_mesh_status():
    """
    HTMX Endpoint returning the current Engine Health and Cloak Status
    using Kaiju Noir aesthetic (Cyan/Purple/Gold).
    """
    cloak_active = await verify_tactical_cloak()
    node_c_active = await verify_aerial_muscle()

    engine_active = False
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.get(f"http://{ENGINE_TARGET}:8000/health")
            engine_active = True
    except httpx.RequestError:
        pass
        
    cloak_color = "text-cyan-400" if cloak_active else "text-red-500"
    cloak_text = "ONLINE" if cloak_active else "OFFLINE"
    cloak_glow = "shadow-[0_0_10px_#00f0ff]" if cloak_active else "shadow-[0_0_10px_#ff0000]"
    
    engine_color = "text-purple-400" if engine_active else "text-red-500"
    engine_text = "ONLINE" if engine_active else "OFFLINE"
    engine_glow = "shadow-[0_0_10px_#b5179e]" if engine_active else "shadow-[0_0_10px_#ff0000]"

    node_c_color = "text-yellow-400" if node_c_active else "text-gray-500"
    node_c_text = "ONLINE (SPOT)" if node_c_active else "PREEMPTED/OFF"
    node_c_glow = "shadow-[0_0_10px_#facc15]" if node_c_active else "shadow-none"


    html = f"""
    <div class="flex gap-4 font-mono text-[10px] tracking-widest bg-black/60 p-2 rounded border border-gray-800 w-fit">
        <div class="flex items-center gap-1">
            <span class="text-gray-500">CLOAK [N0]:</span>
            <span class="{cloak_color} font-bold {cloak_glow} px-1 py-0.5 bg-gray-900 border border-gray-700 rounded transition-all">{cloak_text}</span>
        </div>
        <div class="flex items-center gap-1">
            <span class="text-gray-500">MUSCLE [N2]:</span>
            <span class="{engine_color} font-bold {engine_glow} px-1 py-0.5 bg-gray-900 border border-gray-700 rounded transition-all">{engine_text}</span>
        </div>
        <div class="flex items-center gap-1">
            <span class="text-gray-500">AERIAL [NC]:</span>
            <span class="{node_c_color} font-bold {node_c_glow} px-1 py-0.5 bg-gray-900 border border-gray-700 rounded transition-all">{node_c_text}</span>
        </div>
    </div>
    """
    return HTMLResponse(content=html)


@app.get("/registry/search", response_model=List[UnifiedModel])
async def search_registry(
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    type: Optional[str] = Query(None, description="Filter by model type"),
    deployment: Optional[str] = Query(None, description="Filter by deployment type")
):
    return registry_manager.search(provider=provider, type=type, deployment=deployment)


@app.get("/")
async def root():
    return {"message": "Ghidorah Sentry API is online."}
