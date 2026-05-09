import os, uvicorn, asyncio, logging, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🐉 Ghidorah Manifest Server (v1.5.2)
# Role: Global Microservice for Model Discovery

try:
    from vault_auth import get_live_secret
except ImportError:
    def get_live_secret(name): return None

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Manifest")

app = FastAPI(title="Ghidorah Manifest Server")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# 1. Global ATLAS with immediate static fallbacks to prevent "Empty Model" bug
ATLAS = {
    "together": {
        "type": "aggregator",
        "api_key": None,
        "models": [{"model_id": "together/llama-3.3-70b", "name": "Llama 3.3 70B", "type": "chat"}]
    },
    "fireworks": {
        "type": "aggregator",
        "api_key": None,
        "models": [{"model_id": "accounts/fireworks/models/llama-v3p1-405b-instruct", "name": "Llama 3.1 405B", "type": "chat"}]
    },
    "deepinfra": {
        "type": "aggregator",
        "api_key": None,
        "models": [{"model_id": "deepinfra/meta-llama/Llama-3.1-405B-Instruct", "name": "Llama 3.1 405B", "type": "chat"}]
    },
    "anthropic": {
        "type": "maker",
        "api_key": None,
        "models": [{"model_id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet", "type": "chat"}]
    },
    "google": {
        "type": "maker",
        "api_key": None,
        "models": [{"model_id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "type": "chat"}]
    },
    "openai": {
        "type": "maker",
        "api_key": None,
        "models": [{"model_id": "gpt-4o", "name": "GPT-4o", "type": "chat"}]
    },
    "grok": {
        "type": "maker",
        "api_key": None,
        "models": [{"model_id": "grok-beta", "name": "Grok Beta", "type": "chat"}]
    }
}

OAI_COMPATIBLE = {
    "together": "https://api.together.xyz/v1/models",
    "fireworks": "https://api.fireworks.ai/inference/v1/models",
    "deepinfra": "https://api.deepinfra.com/v1/models",
    "openai": "https://api.openai.com/v1/models"
}

async def fetch_live_models(provider: str, api_key: str):
    """Executes Requirement 3: Live Discovery via HTTPX using Vault Keys."""
    if not api_key or len(api_key) < 10:
        return []
        
    models = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            if provider in OAI_COMPATIBLE:
                headers = {"Authorization": f"Bearer {api_key}"}
                r = await client.get(OAI_COMPATIBLE[provider], headers=headers)
                if r.status_code == 200:
                    data = r.json().get("data", [])
                    for item in data:
                        m_id = item.get("id")
                        m_type = "chat"
                        if "vision" in m_id.lower(): m_type = "vision"
                        elif "coder" in m_id.lower(): m_type = "coding"
                        elif "audio" in m_id.lower(): m_type = "audio"
                        elif "embed" in m_id.lower(): m_type = "embedding"
                        models.append({"model_id": m_id, "name": m_id, "type": m_type})
            
            elif provider == "google":
                r = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if r.status_code == 200:
                    data = r.json().get("models", [])
                    for item in data:
                        m_id = item.get("name").replace("models/", "")
                        models.append({"model_id": m_id, "name": item.get("displayName", m_id), "type": "chat"})
                        
        except Exception as e:
            logger.error(f"🚨 Live fetch failed for {provider}: {e}")
            
    return models

async def hydrate():
    """Background task to resolve Azure Vault keys."""
    logger.info("🌊 Hydrating Master Firehose (Azure Handshake)...")
    keys_map = {
        "together": "TOGETHER-AI-KEY",
        "fireworks": "FIREWORKS-API-KEY",
        "deepinfra": "DEEPINFRA-API-KEY",
        "anthropic": "ANTHROPIC-API-KEY",
        "google": "GEMINI-API-KEY",
        "openai": "OPENAI-API-KEY",
        "grok": "GROK-API-KEY"
    }
    
    for provider, secret_name in keys_map.items():
        key = get_live_secret(secret_name)
        if key:
            ATLAS[provider]["api_key"] = key
            
    logger.info(f"✅ Vault Hydration Complete. Keys ready.")

@app.on_event("startup")
async def startup():
    asyncio.create_task(hydrate())

@app.get("/api/v1/providers")
async def get_providers():
    return list(ATLAS.keys())

@app.get("/api/v1/manifest/{provider}")
async def get_provider_manifest(provider: str, mode: str = "standard"):
    data = ATLAS.get(provider, {"type": "maker", "models": [], "api_key": None})
    
    if mode == "raw" and data.get("api_key"):
        logger.info(f"📡 {provider} live capability discovery engaged...")
        live_models = await fetch_live_models(provider, data["api_key"])
        if live_models:
            return {"provider": provider, "type": data["type"], "models": live_models}
            
    return {"provider": provider, "type": data["type"], "models": data["models"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
