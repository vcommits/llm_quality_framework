import uvicorn, asyncio, logging, httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

try:
    from vault_auth import get_live_secret
except ImportError:
    logging.warning("vault_auth.py not found. Mocking get_live_secret for local testing.")
    def get_live_secret(n): return f"mock-key-for-{n}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [MANIFEST]: %(message)s')
app = FastAPI(title="Ghidorah Manifest Atlas - Phase 2")

# --- Enhanced CORS for Universal Mesh Access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LAYER 2: Provider Metadata (Type Flags) ---
PROVIDERS_META = [
    {"id": "together", "name": "Together AI", "type": "aggregator", "secret_name": "TOGETHER-AI-KEY"},
    {"id": "fireworks", "name": "Fireworks AI", "type": "aggregator", "secret_name": "FIREWORKS-API-KEY"},
    {"id": "deepinfra", "name": "DeepInfra", "type": "aggregator", "secret_name": "DEEPINFRA-API-KEY"},
    {"id": "huggingface", "name": "Hugging Face", "type": "aggregator", "secret_name": "HUGGINGFACE-API-KEY"},
    {"id": "anthropic", "name": "Anthropic", "type": "maker", "secret_name": "ANTHROPIC-API-KEY"},
    {"id": "google", "name": "Google", "type": "maker", "secret_name": "GEMINI-API-KEY"},
    {"id": "openai", "name": "OpenAI", "type": "maker", "secret_name": "OPENAI-API-KEY"},
    {"id": "grok", "name": "Grok", "type": "maker", "secret_name": "GROK-API-KEY"},
]

@app.get("/")
async def root():
    return {"message": "Ghidorah Sentry Layer 2 Online", "version": "9.0.0"}

# Requirement 1: Provider Metadata Refactoring
@app.get("/api/v1/providers")
async def get_providers():
    """Returns the list of providers including their type flag (aggregator vs maker)."""
    return [{"id": p["id"], "name": p["name"], "type": p["type"]} for p in PROVIDERS_META]

# Requirement 3: Live Capability Discovery Logic
async def perform_live_discovery(provider_id: str, api_key: str) -> List[Dict[str, Any]]:
    """Performs live HTTP requests to the provider's API to fetch available models."""
    models = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider_id == "together" and api_key:
                res = await client.get("https://api.together.xyz/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                if res.status_code == 200:
                    models = [{"model_id": m["id"], "name": m.get("display_name", m["id"]), "type": "chat"} for m in res.json()]
            elif provider_id == "openai" and api_key:
                res = await client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                if res.status_code == 200:
                    models = [{"model_id": m["id"], "name": m["id"], "type": "chat"} for m in res.json().get("data", [])]
            elif provider_id == "huggingface":
                # Unauthenticated Top-K fetch for demonstration
                res = await client.get("https://huggingface.co/api/models?pipeline_tag=text-generation&sort=downloads&direction=-1&limit=30")
                if res.status_code == 200:
                    models = [{"model_id": m["modelId"], "name": m["modelId"].split('/')[-1], "type": "chat"} for m in res.json()]
            else:
                # Fallback Discovery for providers not yet fully wired
                models = [
                    {"model_id": f"{provider_id}-live-alpha", "name": f"{provider_id.title()} Live Alpha", "type": "chat"},
                    {"model_id": f"{provider_id}-live-beta", "name": f"{provider_id.title()} Live Beta", "type": "image"}
                ]
    except Exception as e:
        logging.error(f"Live discovery failed for {provider_id}: {e}")
        
    return models

# Requirement 4: Layer 2 API Endpoint Design
@app.get("/api/v1/models/{provider}")
async def get_models(provider: str, mode: str = Query("raw")):
    """Dynamically fetches models based on live discovery and requested mode."""
    meta = next((p for p in PROVIDERS_META if p["id"] == provider), None)
    if not meta:
        raise HTTPException(status_code=404, detail="Provider not found in the Atlas.")
    
    api_key = get_live_secret(meta["secret_name"])
    
    # 1. Execute Live Discovery
    discovered_models = await perform_live_discovery(provider, api_key)
    
    # 2. Filter/Map based on Mode
    if mode == "standard" and meta["type"] == "maker":
        # Simulate mapping raw models to your standard dashboard tiers
        standard_models = [
            {"model_id": f"{provider}-lite", "name": f"{meta['name']} Standard Lite", "type": "chat"},
            {"model_id": f"{provider}-mid", "name": f"{meta['name']} Standard Mid", "type": "chat"},
            {"model_id": f"{provider}-vision", "name": f"{meta['name']} Standard Vision", "type": "vision"}
        ]
        return {"api_key": api_key, "models": standard_models, "mode": mode}
        
    # Return Unfiltered Raw Catalog
    return {"api_key": api_key, "models": discovered_models, "mode": "raw"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
