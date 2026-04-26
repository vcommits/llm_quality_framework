import os, json, uvicorn, logging, httpx, asyncio, re
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# --- Architecture Constants ---
CLOAK_IP = "100.120.132.20"
ENGINE_TARGET = "100.107.125.52"
AERIAL_MUSCLE_TARGET = "node-c-brain-spot"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Sentry")


# --- Pydantic Data Models (v8.9.5) ---

class Pricing(BaseModel):
    input_cost: Optional[float] = Field(None, description="Cost per 1M input tokens")
    output_cost: Optional[float] = Field(None, description="Cost per 1M output tokens")
    unit: str = "tokens"


class UnifiedModel(BaseModel):
    provider: str
    model_id: str
    name: str
    type: Literal["functional", "image", "chat", "video", "audio", "rerank", "embedding", "coding", "vision"]
    deployment: Literal["serverless", "dedicated", "cloud_spot", "hosted"]
    pricing: Pricing
    context: int = 128000


class DispatchPayload(BaseModel):
    task_type: Literal["whisper_synthesis", "slm_inference", "garak_sweeps", "standard_api", "heavy_inference"]
    payload: Dict[str, Any]


# --- Vault & Discovery Logic ---

class ManifestManager:
    """The 'Vacuum Extractor' - Handles hydration and normalization."""

    VAULT_MAP = {
        'FIREWORKS-API-KEY01': 'fireworks', 'OPEN-ROUTER-API-KEY': 'openrouter',
        'MINSTRAL-API-KEY': 'mistral', 'GEMINI-API-KEY': 'google',
        'TOGETHER-AI-KEY': 'together', 'NVIDIA-NIM-API-KEY': 'nvidia',
        'GROK-API-KEY': 'grok', 'MANCER-API-KEY-01': 'mancer',
        'PATRONUS-API-KEY': 'patronus', 'SOLAR-API-KEY': 'solar',
        'CARTESIA-API-KEY': 'cartesia', 'XIAOMI-API-KEY': 'xiaomi',
        'ANTHROPIC-API-KEY': 'anthropic', 'HUGGINGFACE-API-KEY': 'huggingface'
    }

    def __init__(self):
        self.registry: List[UnifiedModel] = []

    def normalize(self, raw_id: str, provider: str, raw_obj=None) -> UnifiedModel:
        rid = str(raw_id).lower()
        m_type = "chat"

        # SQA Tagging Logic
        if any(x in rid for x in ["vision", "vl", "image", "pixtral"]):
            m_type = "vision"
        elif any(x in rid for x in ["code", "coder", "python", "sql", "gemini-1.5-pro", "claude-3-5"]):
            m_type = "coding"
        elif any(x in rid for x in ["audio", "speech", "tts", "voice", "sonic"]):
            m_type = "audio"
        elif any(x in rid for x in ["embedding", "vector", "similarity"]):
            m_type = "embedding"

        deployment = "serverless"
        if any(x in rid for x in ["spot", "local", "node-c"]):
            deployment = "cloud_spot"
        elif any(x in rid for x in ["dedicated", "azure"]):
            deployment = "dedicated"

        return UnifiedModel(
            provider=provider,
            model_id=raw_id,
            name=raw_id.split('/')[-1] if '/' in raw_id else raw_id,
            type=m_type,
            deployment=deployment,
            pricing=Pricing(input_cost=0.1, output_cost=0.1)
        )

    async def hydrate(self, api_keys: dict):
        """Dynamic Discovery Loop."""
        new_registry = []
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            # 1. Hardcoded Mesh Models
            for m in ["claude-3-5-sonnet", "claude-3-5-haiku", "patronus-lynx-8b", "milm-7b-v1"]:
                new_registry.append(self.normalize(m, "Mesh-Internal"))

            # 2. Aggregator Probes (Together, OpenRouter, HF)
            # This is where the 'Firehose' logic sits in production
            # ... API Fetch Logic ...

        self.registry = new_registry
        logger.info(f"✅ Hydrated {len(self.registry)} targets into the mesh registry.")


# --- API Application ---

manager = ManifestManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # In production, keys would be pulled from Vault here
    asyncio.create_task(manager.hydrate({}))
    yield


app = FastAPI(title="Ghidorah Sentry API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# --- Tactical Health Handshake ---

async def verify_health(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(url)
            return res.status_code == 200
    except:
        return False


@app.get("/ui/mesh-status", response_class=HTMLResponse)
async def get_mesh_status():
    cloak = await verify_health(f"http://{CLOAK_IP}/")
    muscle = await verify_health(f"http://{ENGINE_TARGET}:8000/health")
    aerial = await verify_health(f"http://{AERIAL_MUSCLE_TARGET}:8000/health")

    def pill(label, status, color):
        s_text = "ONLINE" if status else "OFFLINE"
        s_color = f"text-{color}-400" if status else "text-red-500"
        return f'<div class="flex items-center gap-1"><span class="text-gray-500">{label}:</span><span class="{s_color} font-bold px-1 py-0.5 bg-gray-900 border border-gray-700 rounded text-[9px]">{s_text}</span></div>'

    html = f"""
    <div class="flex gap-4 font-mono text-[10px] tracking-widest bg-black/60 p-2 rounded border border-gray-800 w-fit">
        {pill("CLOAK [N0]", cloak, "cyan")}
        {pill("MUSCLE [N2]", muscle, "purple")}
        {pill("AERIAL [NC]", aerial, "yellow")}
    </div>
    """
    return HTMLResponse(content=html)


@app.get("/api/v1/providers")
async def get_providers():
    return sorted(list(set([m.provider for m in manager.registry])))


@app.get("/api/v1/manifest/{provider}")
async def get_manifest(provider: str):
    models = [m for m in manager.registry if m.provider.lower() == provider.lower()]
    return {"provider": provider, "models": models}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)