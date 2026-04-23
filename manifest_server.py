# manifest_server.py | Node: 1 (The Sentry)
# Purpose: Serves a unified JSON "Atlas" of all available models.

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [MANIFEST]: %(message)s')
app = FastAPI(title="Ghidorah Manifest Atlas")

# --- CORS MIDDLEWARE (CRITICAL FIX) ---
# Explicitly allow the local development server to make requests.
origins = [
    "http://localhost",
    "http://localhost:8000",
    "null", # Allow file:// origins for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ModelEntry(BaseModel):
    model_id: str
    name: str
    provider: str
    type: Literal["chat", "image", "code", "embedding"]

# --- Manifest Manager ---
class ManifestManager:
    def __init__(self):
        self.registry: Dict[str, List[ModelEntry]] = {}
        self._load_and_hydrate()

    def _load_and_hydrate(self):
        self.registry = {
            "Together": [
                ModelEntry(model_id="together/llama-3-8b", name="Llama 3 8B", provider="Together", type="chat")
            ],
            "Fireworks": [
                ModelEntry(model_id="fireworks/firefunction-v2", name="FireFunction V2", provider="Fireworks", type="code")
            ],
            "DeepInfra": [
                ModelEntry(model_id="deepinfra/Mixtral-8x7B-Instruct-v0.1", name="Mixtral 8x7B", provider="DeepInfra", type="chat")
            ],
            "Gemini": [], "Claude": [], "OpenAI": [], "Grok": []
        }
        logging.info("Manifest Atlas hydrated with all provider data.")

    def get_manifest_for_provider(self, provider: str) -> List[ModelEntry]:
        return self.registry.get(provider, [])

# --- API Endpoints ---
registry_manager = ManifestManager()

@app.get("/manifest/{provider}", response_model=List[ModelEntry])
async def get_provider_manifest(provider: str):
    logging.info(f"UI requested firehose for provider: {provider}")
    models = registry_manager.get_manifest_for_provider(provider)
    if not models and provider not in registry_manager.registry:
        raise HTTPException(status_code=404, detail="Provider not found in the Atlas.")
    return models

@app.get("/providers", response_model=List[str])
async def get_providers():
    return list(registry_manager.registry.keys())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
