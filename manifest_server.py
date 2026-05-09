import os, uvicorn, asyncio, logging, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from vault_auth import get_live_secret
except ImportError:
    def get_live_secret(name): return None

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

app = FastAPI(title="Ghidorah Manifest Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ATLAS = {}

# Define standard endpoints for OpenAI-compatible providers
OAI_COMPATIBLE = {
    "together": "https://api.together.xyz/v1/models",
    "fireworks": "https://api.fireworks.ai/inference/v1/models",
    "deepinfra": "https://api.deepinfra.com/v1/models",
    "openai": "https://api.openai.com/v1/models"
}

async def fetch_live_models(provider: str, api_key: str):
    """Live Discovery via HTTPX using Azure Vault Keys"""
    if not api_key or "MISSING" in api_key:
        logging.warning(f"⚠️ No valid API key found for {provider}. Skipping live fetch.")
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
                        
                        # Auto-Categorize discovered models based on naming conventions
                        m_type = "chat"
                        if "vision" in m_id.lower() or "llava" in m_id.lower(): m_type = "vision"
                        elif "coder" in m_id.lower() or "python" in m_id.lower(): m_type = "coding"
                        elif "audio" in m_id.lower() or "tts" in m_id.lower(): m_type = "audio"
                        elif "embed" in m_id.lower(): m_type = "embedding"
                        
                        models.append({"model_id": m_id, "name": m_id, "type": m_type})
                        
            elif provider == "google":
                # Custom Google format handshake
                r = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if r.status_code == 200:
                    data = r.json().get("models", [])
                    for item in data:
                        m_id = item.get("name").replace("models/", "")
                        models.append({"model_id": m_id, "name": item.get("displayName", m_id), "type": "chat"})
                        
        except Exception as e:
            logging.error(f"🚨 Live fetch failed for {provider}: {e}")
            
    return models

async def hydrate():
    global ATLAS
    logging.info("🌊 Hydrating Master Firehose & Checking Vault Keys...")
    
    # We assign 'type' flags so the frontend knows if it's an aggregator or a maker
    ATLAS = {
        "together": {
            "type": "aggregator",
            "api_key": get_live_secret("TOGETHER-AI-KEY"),
            "models": [{"model_id": "together/llama-3.3-70b", "name": "Llama 3.3 70B", "type": "chat"}]
        },
        "fireworks": {
            "type": "aggregator",
            "api_key": get_live_secret("FIREWORKS-API-KEY"),
            "models": [{"model_id": "accounts/fireworks/models/llama-v3p1-405b-instruct", "name": "Llama 3.1 405B", "type": "chat"}]
        },
        "deepinfra": {
            "type": "aggregator",
            "api_key": get_live_secret("DEEPINFRA-API-KEY"),
            "models": [{"model_id": "deepinfra/meta-llama/Llama-3.1-405B-Instruct", "name": "Llama 3.1 405B", "type": "chat"}]
        },
        "anthropic": {
            "type": "maker",
            "api_key": get_live_secret("ANTHROPIC-API-KEY"),
            "models": [{"model_id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet", "type": "chat"}]
        },
        "google": {
            "type": "maker",
            "api_key": get_live_secret("GEMINI-API-KEY"),
            "models": [{"model_id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "type": "chat"}]
        },
        "openai": {
            "type": "maker",
            "api_key": get_live_secret("OPENAI-API-KEY"),
            "models": [{"model_id": "gpt-4o", "name": "GPT-4o", "type": "chat"}]
        },
        "grok": {
            "type": "maker",
            "api_key": get_live_secret("GROK-API-KEY"),
            "models": [{"model_id": "grok-beta", "name": "Grok Beta", "type": "chat"}]
        }
    }
    logging.info(f"✅ Master Hydration Complete. {len(ATLAS)} providers active.")

@app.on_event("startup")
async def startup():
    asyncio.create_task(hydrate())

@app.get("/api/v1/providers")
async def get_providers():
    return list(ATLAS.keys()) if ATLAS else ["together", "fireworks", "deepinfra", "anthropic", "google", "openai", "grok"]

@app.get("/api/v1/manifest/{provider}")
async def get_provider_manifest(provider: str, mode: str = "standard"):
    data = ATLAS.get(provider, {"type": "maker", "models": [], "api_key": None})
    
    # Live Discovery Edge Case
    if mode == "raw" and data.get("api_key"):
        logging.info(f"📡 {provider} live capability discovery engaged...")
        live_models = await fetch_live_models(provider, data["api_key"])
        if live_models:
            return {"provider": provider, "type": data["type"], "models": live_models}
            
    return {"provider": provider, "type": data["type"], "models": data["models"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
