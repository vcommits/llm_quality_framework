import uvicorn, re, logging
import httpx
import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# --- Google Cloud Translation Imports ---
try:
    from google.cloud import translate_v3 as translate
    from google.oauth2 import service_account
except ImportError:
    translate = None
    service_account = None
    logging.warning("Google Cloud Translation libraries not found. Translation endpoint will be disabled.")


# --- Vault Auth (Amber State) ---
try:
    from vault_auth import get_live_secret
except ImportError:
    logging.warning("vault_auth.py not found. Mocking get_live_secret for local testing.")
    def get_live_secret(secret_name: str) -> str:
        mock_secrets = {
            "PATRONUS-API-KEY": "mock-patronus-key",
            "MAILSLURP-API-KEY": "mock-mailslurp-key",
            "MANCER-API-KEY-01": "mock-mancer-key", # Updated to MANCER-API-KEY-01
            "SOLAR-API-KEY": "mock-solar-key",
            "GOOGLE-TRANSLATE-API": "mock-google-translate-key", # Added for future translation
            "MINSTRAL-API-KEY": "mock-mistral-key", # Updated to MINSTRAL-API-KEY
            "OPENAI-API-KEY": "mock-openai-key",
            "ANTHROPIC-API-KEY": "mock-anthropic-key",
            "TOGETHER-AI-KEY": "mock-together-key",
            "FIREWORKS-API-KEY01": "mock-fireworks-key", # Updated to FIREWORKS-API-KEY01
            "DEEPINFRA-API-KEY": "mock-deepinfra-key",
            "GEMINI-API-KEY": "mock-gemini-key",
            "GROK-API-KEY": "mock-grok-key",
            "HUGGINGFACE-API-KEY": "mock-huggingface-key",
        }
        return mock_secrets.get(secret_name, f"mock-secret-for-{secret_name}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("GhidorahLibrarian")

app = FastAPI(title="Ghidorah Librarian")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- IDENTITY MAP (Amber State) ---
IDENTITY_MAP = {
    "glider": "PATRONUS-API-KEY",
    "auditor": "MAILSLURP-API-KEY",
    "mancer": "MANCER-API-KEY-01", # Updated to MANCER-API-KEY-01
    "eval": "SOLAR-API-KEY",
    "translate": "GOOGLE-TRANSLATE-API",
    "mistral": "MINSTRAL-API-KEY", # Updated to MINSTRAL-API-KEY
    "openai": "OPENAI-API-KEY",
    "anthropic": "ANTHROPIC-API-KEY",
    "together": "TOGETHER-AI-KEY",
    "fireworks": "FIREWORKS-API-KEY01", # Updated to FIREWORKS-API-KEY01
    "deepinfra": "DEEPINFRA-API-KEY",
    "google": "GEMINI-API-KEY",
    "grok": "GROK-API-KEY",
    "huggingface": "HUGGINGFACE-API-KEY",
}

# --- Pydantic Models for Chat Completions ---
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    provider: str
    model_id: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False # We will always stream from the backend

# --- Pydantic Models for Translation ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str = "en" # Default to English
    source_language: Optional[str] = None # Auto-detect if not provided

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: Optional[str] = None
    target_language: str


# --- Provider Configuration for Routing ---
PROVIDER_CONFIG = {
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "api_key_name": "OPENAI-API-KEY",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "format_payload": lambda model, messages, temp, max_tok: {
            "model": model,
            "messages": [m.dict() for m in messages],
            "temperature": temp,
            "max_tokens": max_tok,
            "stream": True # Always request stream from provider
        }
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "api_key_name": "ANTHROPIC-API-KEY",
        "headers": lambda key: {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        "format_payload": lambda model, messages, temp, max_tok: {
            "model": model,
            "messages": [m.dict() for m in messages],
            "temperature": temp,
            "max_tokens": max_tok,
            "stream": True # Always request stream from provider
        }
    },
    "together": {
        "base_url": "https://api.together.ai/v1/chat/completions", # Together AI strictly uses api.together.ai
        "api_key_name": "TOGETHER-AI-KEY",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "format_payload": lambda model, messages, temp, max_tok: {
            "model": model,
            "messages": [m.dict() for m in messages],
            "temperature": temp,
            "max_tokens": max_tok,
            "stream": True
        }
    },
    "fireworks": { # Updated to FIREWORKS-API-KEY01
        "base_url": "https://api.fireworks.ai/inference/v1/chat/completions",
        "api_key_name": "FIREWORKS-API-KEY01",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "format_payload": lambda model, messages, temp, max_tok: {
            "model": model,
            "messages": [m.dict() for m in messages],
            "temperature": temp,
            "max_tokens": max_tok,
            "stream": True
        }
    },
    "deepinfra": {
        "base_url": "https://api.deepinfra.com/v1/openai/chat/completions",
        "api_key_name": "DEEPINFRA-API-KEY",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "format_payload": lambda model, messages, temp, max_tok: {
            "model": model,
            "messages": [m.dict() for m in messages],
            "temperature": temp,
            "max_tokens": max_tok,
            "stream": True
        }
    },
    "google": { # Assuming Gemini API is OpenAI-compatible for now, adjust if needed
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
        "api_key_name": "GEMINI-API-KEY",
        "headers": lambda key: {"Content-Type": "application/json"}, # Key is in URL
        "format_payload": lambda model, messages, temp, max_tok: {
            "contents": [{"role": m.role, "parts": [{"text": m.content}]} for m in messages],
            "generationConfig": {"temperature": temp, "maxOutputTokens": max_tok}
        },
        "response_parser": lambda chunk: chunk.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    },
    # Add other providers as needed, following their API specs
}


# --- Existing Identity Parsing (Amber State) ---
@app.post("/api/v1/sentry/parse")
async def parse(payload: dict):
    text = payload.get("text", "")
    tags = re.findall(r'#(\w+)', text)
    injections = {}
    for t in tags:
        secret_name = IDENTITY_MAP.get(t.lower())
        if secret_name:
            val = get_live_secret(secret_name)
            if val: injections[t] = f"{val[:5]}..."
    return {"text": text, "tags": tags, "injections": injections, "status": "READY"}


# --- Unified Chat Completions Endpoint ---
@app.post("/api/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, http_request: Request):
    provider_id = request.provider.lower()
    config = PROVIDER_CONFIG.get(provider_id)

    if not config:
        logger.error(f"❌ Unsupported provider: {provider_id}")
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider_id}")

    api_key = get_live_secret(config["api_key_name"])
    if not api_key:
        logger.error(f"❌ API key not found for {provider_id}")
        raise HTTPException(status_code=500, detail=f"API key not found for {provider_id}")

    # Format payload specific to the provider
    payload = config["format_payload"](
        request.model_id, request.messages, request.temperature, request.max_tokens
    )

    headers = config["headers"](api_key)
    
    # Special handling for Gemini API key in URL
    url = config["base_url"]
    if provider_id == "google":
        url = url.format(api_key=api_key)
        headers = {"Content-Type": "application/json"} # Override headers as key is in URL

    logger.info(f"🚀 Dispatching request to {provider_id} for model {request.model_id}")

    async def generate_stream():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload, stream=True)
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    # OpenAI-compatible streaming
                    if b"data:" in chunk:
                        try:
                            # Decode chunk, remove "data: " prefix, and parse JSON
                            decoded_chunk = chunk.decode('utf-8').strip()
                            if decoded_chunk.startswith("data: "):
                                decoded_chunk = decoded_chunk[len("data: "):]
                            if decoded_chunk == "[DONE]":
                                yield chunk # Pass DONE marker directly
                                continue

                            json_data = json.loads(decoded_chunk)
                            
                            # Extract content based on provider (OpenAI-like vs Anthropic vs Gemini)
                            if provider_id == "anthropic":
                                # Anthropic's streaming format is different
                                if json_data.get("type") == "content_block_delta":
                                    text_content = json_data.get("delta", {}).get("text", "")
                                    if text_content:
                                        # Re-wrap in OpenAI-like format for frontend consistency
                                        yield f"data: {json.dumps({'choices': [{'delta': {'content': text_content}}]})}\n\n".encode('utf-8')
                                elif json_data.get("type") == "message_start":
                                    # Optionally send message_start info
                                    pass
                                elif json_data.get("type") == "message_stop":
                                    yield b"data: [DONE]\n\n"
                            elif provider_id == "google":
                                # Gemini's streaming format
                                text_content = config["response_parser"](json_data)
                                if text_content:
                                    yield f"data: {json.dumps({'choices': [{'delta': {'content': text_content}}]})}\n\n".encode('utf-8')
                            else:
                                # Default to OpenAI-compatible parsing
                                yield chunk
                        except json.JSONDecodeError:
                            logger.warning(f"JSONDecodeError in chunk: {decoded_chunk[:100]}")
                            # If not valid JSON, yield raw chunk or skip
                            yield chunk
                        except Exception as e:
                            logger.error(f"Error processing stream chunk: {e} - Chunk: {chunk.decode('utf-8', errors='ignore')[:100]}")
                            yield chunk # Yield raw chunk on unexpected errors
                    else:
                        # For non-data: prefixed chunks (e.g., Anthropic's non-delta events, or raw errors)
                        yield chunk

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from {provider_id}: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Network error to {provider_id}: {e}")
            raise HTTPException(status_code=503, detail=f"Could not connect to {provider_id} API: {e}")
        except Exception as e:
            logger.error(f"Unhandled error in streaming for {provider_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


# --- NEW: Google Cloud Translation Endpoint ---
@app.post("/api/v1/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if not translate or not service_account:
        logger.error("Google Cloud Translation libraries are not available.")
        raise HTTPException(status_code=500, detail="Translation service not configured on server.")

    # --- Authentication ---
    # Option A: GOOGLE_APPLICATION_CREDENTIALS environment variable
    # This is the preferred method for service accounts in GCP environments
    credentials = None
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        logger.info("Using GOOGLE_APPLICATION_CREDENTIALS for Translation API.")
        # The client library will automatically pick this up
    else:
        # Option B: API Key from Librarian (Fallback)
        logger.info("GOOGLE_APPLICATION_CREDENTIALS not set. Attempting to use API key from Librarian.")
        api_key = get_live_secret("GOOGLE-TRANSLATE-API-KEY")
        if not api_key or api_key.startswith("mock-"):
            logger.error("GOOGLE-TRANSLATE-API-KEY not found or is mocked.")
            raise HTTPException(status_code=500, detail="Google Translate API key not available.")
        # Note: Google Cloud Translation client library typically uses service account JSON or default credentials.
        # Using a raw API key directly with the client library is less common for v3.
        # For simplicity in this context, we'll assume the client can be initialized with project_id if key is present.
        # A more robust solution might involve creating a temporary credentials object or using a different client.
        # For now, we'll rely on default credentials if available, or raise error if only API key is present and not usable.
        logger.warning("Direct API key usage with google-cloud-translate_v3 client is complex. Relying on default credentials if available.")
        # If only API key is available, we need a project ID. Let's assume it's also an env var.
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            logger.error("GCP_PROJECT_ID environment variable is required for API key based translation.")
            raise HTTPException(status_code=500, detail="Google Translate API key requires GCP_PROJECT_ID.")
        
        # Initialize client with project_id if using API key fallback
        client = translate.TranslationServiceClient(client_options={"api_key": api_key})


    try:
        # If GOOGLE_APPLICATION_CREDENTIALS is set, client will pick it up automatically
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            client = translate.TranslationServiceClient()
        
        # The `parent` parameter is required for v3. It's typically 'projects/PROJECT_ID'
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            logger.error("GCP_PROJECT_ID environment variable is required for Google Cloud Translation API.")
            raise HTTPException(status_code=500, detail="GCP_PROJECT_ID not set.")
        
        parent = f"projects/{project_id}"

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [request.text],
                "target_language_code": request.target_language,
                "source_language_code": request.source_language, # Optional
            }
        )

        translated_text = response.translations[0].translated_text
        detected_source_language = response.translations[0].detected_language_code

        logger.info(f"🌐 Translated '{request.text[:30]}...' from {detected_source_language} to {request.target_language}")
        return TranslationResponse(
            translated_text=translated_text,
            source_language=detected_source_language,
            target_language=request.target_language
        )

    except Exception as e:
        logger.error(f"Google Translate API error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
