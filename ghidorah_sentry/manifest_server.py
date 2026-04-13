import os, json, uvicorn, logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Import from all data sources
from .data_hugging import HUGGINGFACE_DATA
from .data_togetherai import TOGETHER_AI_DATA

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Sentry")

app = FastAPI(title="Ghidorah Sentry (Multi-Source Data Loader)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Pydantic Models ---
class RichModelManifest(BaseModel):
    model_id: str
    name: str
    provider: str
    category: Optional[str] = None
    # Add other fields as needed

class ManifestManager:
    def __init__(self, data_directory: str, hf_data: Dict, together_data: Dict):
        self.registry: List[RichModelManifest] = []
        self.data_directory = data_directory
        self.hf_data = hf_data
        self.together_data = together_data
        self._load_and_hydrate()

    def _load_and_hydrate(self):
        """Dynamically loads all data sources and hydrates the registry."""
        all_models = {}
        
        # 1. Load from JSON provider files
        for filename in os.listdir(self.data_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_directory, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    provider = data.get("provider", "Unknown")
                    for model_data in data.get("models", []):
                        model_data["provider"] = provider
                        all_models[model_data["model_id"]] = model_data
        
        # 2. Load from Hugging Face data module
        for category, model_list in self.hf_data.items():
            for model_data in model_list:
                model_data["provider"] = "Hugging Face"
                model_data["name"] = model_data["model_id"]
                model_data["category"] = category
                all_models[model_data["model_id"]] = model_data

        # 3. Load from Together AI data module
        for category, model_list in self.together_data.items():
            for model_data in model_list:
                model_data["provider"] = "Together AI"
                model_data["name"] = model_data["model_name"]
                model_data["category"] = category
                all_models[model_data["model_id"]] = model_data

        # 4. Hydrate into Pydantic models
        for model_id, model_data in all_models.items():
            try:
                manifest_entry = RichModelManifest(**model_data)
                self.registry.append(manifest_entry)
            except Exception as e:
                logger.error(f"Failed to parse model: {model_data.get('name')}. Error: {e}")

        logger.info(f"Successfully hydrated {len(self.registry)} unique models from all sources.")

    def get_manifest(self) -> List[RichModelManifest]:
        return self.registry

# --- FastAPI Application ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
registry_manager = ManifestManager(data_directory=DATA_DIR, hf_data=HUGGINGFACE_DATA, together_data=TOGETHER_AI_DATA)

@app.get("/api/v1/manifest")
async def get_manifest_endpoint():
    return {"models": [m.dict(by_alias=True, exclude_none=True) for m in registry_manager.get_manifest()]}

@app.get("/")
async def root():
    return {"message": "Ghidorah Sentry is online. GET /api/v1/manifest for model data."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
