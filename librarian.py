# librarian.py | Node: 1 (The Sentry)
# Purpose: Parses prompts for identity hashtags and injects the corresponding
# API key from Azure Key Vault for the execution node.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os

# Assume vault_auth.py is in the same directory or a discoverable path
# In a real deployment, vault_auth.py would handle Azure Key Vault access
# For this context, we'll mock it if it's not present.
try:
    from vault_auth import get_live_secret
except ImportError:
    logging.warning("vault_auth.py not found. Mocking get_live_secret for local testing.")
    def get_live_secret(secret_name: str) -> str:
        # Mock implementation for local testing without Azure Key Vault
        mock_secrets = {
            "PATRONUS-API-KEY": "mock-patronus-key",
            "MAILSLURP-API-KEY": "mock-mailslurp-key",
            "MANCER-API-KEY": "mock-mancer-key",
            "SOLAR-API-KEY": "mock-solar-key",
            "DEEPINFRA-API-KEY": "mock-deepinfra-key",
            "HUGGINGFACE-API-KEY": os.environ.get("HUGGINGFACE_API_KEY", "hf_mock_key"), # Use env var for HF
            "ANTHROPIC-API-KEY": os.environ.get("ANTHROPIC_API_KEY", "anthropic_mock_key"), # Use env var for Anthropic
        }
        return mock_secrets.get(secret_name, f"mock-secret-for-{secret_name}")


logging.basicConfig(level=logging.INFO, format='%(asctime)s [LIBRARIAN]: %(message)s')
app = FastAPI(title="Ghidorah Librarian API")

# --- CORS MIDDLEWARE ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "null", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IDENTITY MAP (SYNCHRONIZED WITH AZURE VAULT) ---
# Maps a hashtag found in a prompt to the dash-cased secret name in Azure Key Vault.
IDENTITY_MAP = {
    "#glider": "PATRONUS-API-KEY",
    "#auditor": "MAILSLURP-API-KEY",
    "#mancer": "MANCER-API-KEY",
    "#eval": "SOLAR-API-KEY",
    "#deepinfra": "DEEPINFRA-API-KEY",
    "#huggingface": "HUGGINGFACE-API-KEY", # New
    "#anthropic": "ANTHROPIC-API-KEY",     # New
}

class PromptRequest(BaseModel):
    prompt: str

class SecretResolveRequest(BaseModel):
    secret_name: str

@app.post("/inject-identity")
async def inject_identity(request: PromptRequest):
    logging.info(f"Scanning prompt for identity tags...")
    
    for tag, secret_name in IDENTITY_MAP.items():
        if tag in request.prompt:
            logging.info(f"Identity tag '{tag}' detected. Resolving secret '{secret_name}' from Azure Vault...")
            try:
                secret_value = get_live_secret(secret_name)
                if secret_value:
                    return {"identity": tag, "secret_name": secret_name, "key_injected": True}
                else:
                    raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found in vault.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve secret from Azure: {e}")

    logging.info("No known identity tags found in prompt.")
    return {"identity": "default", "key_injected": False}

@app.post("/secrets/resolve_by_name")
async def resolve_secret_by_name(request: SecretResolveRequest):
    """
    Directly resolves a secret from Azure Key Vault by its name.
    Used by other services (like Manifest Server) to get API keys.
    """
    logging.info(f"Direct request to resolve secret: {request.secret_name}")
    try:
        secret_value = get_live_secret(request.secret_name)
        if secret_value:
            return {"secret_name": request.secret_name, "value": secret_value}
        else:
            raise HTTPException(status_code=404, detail=f"Secret '{request.secret_name}' not found in vault.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve secret from Azure: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
