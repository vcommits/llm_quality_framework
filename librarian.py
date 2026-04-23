# librarian.py | Node: 1 (The Sentry)
# Purpose: Parses prompts for identity hashtags and injects the corresponding
# API key from Azure Key Vault for the execution node.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Assume vault_auth.py is in the same directory or a discoverable path
from vault_auth import get_live_secret

logging.basicConfig(level=logging.INFO, format='%(asctime)s [LIBRARIAN]: %(message)s')
app = FastAPI(title="Ghidorah Librarian API")

# --- IDENTITY MAP (SYNCHRONIZED WITH AZURE VAULT) ---
# Maps a hashtag found in a prompt to the dash-cased secret name in Azure Key Vault.
IDENTITY_MAP = {
    "#glider": "PATRONUS-API-KEY",
    "#auditor": "MAILSLURP-API-KEY",
    "#mancer": "MANCER-API-KEY",
    "#eval": "SOLAR-API-KEY",
    # Adding a generic one for the new provider
    "#deepinfra": "DEEPINFRA-API-KEY"
}

class PromptRequest(BaseModel):
    prompt: str

@app.post("/inject-identity")
async def inject_identity(request: PromptRequest):
    """
    Scans prompt for a known identity hashtag and returns the corresponding secret.
    """
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
