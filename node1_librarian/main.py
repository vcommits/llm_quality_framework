import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import keyvault_client

class SecretRequest(BaseModel):
    secret_name: str

class SecretResponse(BaseModel):
    secret_name: str
    value: str

app = FastAPI(
    title="Node 1 - Librarian API",
    description="A secure proxy for secrets and other critical assets."
)
logging.basicConfig(level=logging.INFO)

@app.post("/secrets/resolve", response_model=SecretResponse)
async def resolve_secret_endpoint(request: SecretRequest):
    try:
        secret_value = await keyvault_client.get_secret(request.secret_name)
        return SecretResponse(secret_name=request.secret_name, value=secret_value)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Secret '{request.secret_name}' not found or could not be retrieved. Error: {e}"
        )

@app.get("/health")
def health_check():
    return {"status": "Librarian API is online"}
