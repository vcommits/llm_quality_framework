# manifest_server.py | Node: 1 (The Sentry)
# Purpose: Serves a unified JSON "Atlas" of all available models.

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import logging
import json
import os
import httpx # For making async HTTP requests
from huggingface_hub import HfApi, ModelFilter # For Hugging Face API

logging.basicConfig(level=logging.INFO, format='%(asctime)s [MANIFEST]: %(message)s')
app = FastAPI(title="Ghidorah Manifest Atlas")

# --- CORS MIDDLEWARE ---
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
    type: Literal["chat", "image", "code", "embedding", "audio", "video", "rerank", "functional"] # Expanded types
    deployment: Literal["serverless", "dedicated", "cloud_spot"] = "serverless" # Added deployment
    pricing: Dict[str, Any] = Field(default_factory=dict) # Added pricing

# --- Manifest Manager ---
class ManifestManager:
    def __init__(self):
        self.registry: Dict[str, List[ModelEntry]] = {}
        # _load_and_hydrate is now async and called on startup
        
    async def _get_secret_from_librarian(self, secret_name: str) -> Optional[str]:
        """Fetches an API key from the local Librarian service."""
        librarian_url = "http://100.101.24.26:8081/secrets/resolve_by_name" # Node 1's Librarian
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(librarian_url, json={"secret_name": secret_name})
                response.raise_for_status()
                return response.json().get("value")
        except httpx.RequestError as e:
            logging.error(f"Failed to get secret '{secret_name}' from Librarian: {e}")
            return None
        except HTTPException as e:
            logging.error(f"Librarian returned error for '{secret_name}': {e.detail}")
            return None

    async def _fetch_huggingface_models(self) -> List[ModelEntry]:
        """Fetches models from Hugging Face Hub using the API key from Librarian."""
        hf_token = await self._get_secret_from_librarian("HUGGINGFACE-API-KEY")
        if not hf_token:
            logging.warning("Hugging Face API key not available. Skipping HF model hydration.")
            return []

        hf_api = HfApi(token=hf_token)
        models: List[ModelEntry] = []
        try:
            # Fetch a diverse set of models. Adjust filters as needed for your use case.
            # This is a simplified example; real-world might involve pagination and more specific filters.
            
            # Chat models
            for model_info in hf_api.list_models(filter=ModelFilter(task="text-generation"), sort="downloads", direction=-1, limit=50):
                if model_info.pipeline_tag == "text-generation": # Ensure it's a chat-like model
                    models.append(ModelEntry(
                        model_id=model_info.modelId,
                        name=model_info.id.split('/')[-1],
                        provider="HuggingFace",
                        type="chat",
                        deployment="serverless", # Assuming most HF models are serverless deployments
                        pricing={"input_cost": 0.0, "output_cost": 0.0, "unit": "1M tokens"} # HF pricing varies, set to 0 for now
                    ))
            
            # Image models
            for model_info in hf_api.list_models(filter=ModelFilter(task="text-to-image"), sort="downloads", direction=-1, limit=20):
                 models.append(ModelEntry(
                    model_id=model_info.modelId,
                    name=model_info.id.split('/')[-1],
                    provider="HuggingFace",
                    type="image",
                    deployment="serverless",
                    pricing={"input_cost": 0.0, "output_cost": 0.0, "unit": "images"}
                ))

            logging.info(f"Hydrated {len(models)} models from Hugging Face.")
            return models
        except Exception as e:
            logging.error(f"Failed to fetch Hugging Face models: {e}")
            return []

    async def _fetch_anthropic_models(self) -> List[ModelEntry]:
        """Hardcodes Anthropic models as they don't have a public listing API."""
        anthropic_key = await self._get_secret_from_librarian("ANTHROPIC-API-KEY")
        if not anthropic_key:
            logging.warning("Anthropic API key not available. Skipping Anthropic model hydration.")
            return []
        
        # Anthropic models are typically fixed and known
        models = [
            ModelEntry(model_id="claude-3-opus-20240229", name="Claude 3 Opus", provider="Anthropic", type="chat", deployment="dedicated", pricing={"input_cost": 15.0, "output_cost": 75.0, "unit": "1M tokens"}),
            ModelEntry(model_id="claude-3-sonnet-20240229", name="Claude 3 Sonnet", provider="Anthropic", type="chat", deployment="dedicated", pricing={"input_cost": 3.0, "output_cost": 15.0, "unit": "1M tokens"}),
            ModelEntry(model_id="claude-3-haiku-20240307", name="Claude 3 Haiku", provider="Anthropic", type="chat", deployment="dedicated", pricing={"input_cost": 0.25, "output_cost": 1.25, "unit": "1M tokens"}),
        ]
        logging.info(f"Hydrated {len(models)} models from Anthropic.")
        return models

    async def _load_and_hydrate(self):
        """
        Asynchronously loads model data from various aggregators and providers.
        """
        self.registry = {} # Clear previous dummy data

        # Fetch from Hugging Face
        hf_models = await self._fetch_huggingface_models()
        if hf_models:
            self.registry["HuggingFace"] = hf_models
        
        # Fetch from Anthropic
        anthropic_models = await self._fetch_anthropic_models()
        if anthropic_models:
            self.registry["Anthropic"] = anthropic_models

        # Add other providers with minimal dummy data for now, or integrate their APIs later
        self.registry["Together"] = [
            ModelEntry(model_id="together/llama-3-8b", name="Llama 3 8B Instruct", provider="Together", type="chat")
        ]
        self.registry["Fireworks"] = [
            ModelEntry(model_id="fireworks/firefunction-v2", name="FireFunction V2", provider="Fireworks", type="code")
        ]
        self.registry["DeepInfra"] = [
            ModelEntry(model_id="deepinfra/Mixtral-8x7B-Instruct-v0.1", name="Mixtral 8x7B Instruct", provider="DeepInfra", type="chat")
        ]
        
        logging.info(f"Manifest Atlas fully hydrated with {sum(len(v) for v in self.registry.values())} models from real APIs and dummy data.")

    def get_manifest_for_provider(self, provider: str) -> List[ModelEntry]:
        """Returns all models for a specific provider (the 'Firehose')."""
        return self.registry.get(provider, [])

# --- API Endpoints ---
registry_manager = ManifestManager()

@app.on_event("startup")
async def startup_event():
    """Hydrate the manifest on application startup."""
    await registry_manager._load_and_hydrate()

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
