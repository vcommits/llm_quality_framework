import uvicorn, re, logging, json, os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from storage_sentry import StorageSentry

# 🐉 Ghidorah Node 1: Master Librarian (v8.9.9)
# Role: Traffic Cop for Model Selection, Prompt Parsing, and Session Ingestion.
# Update: Enhanced /upload endpoint to support batch migrations and GDrive handshake.

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Librarian")

try:
    from vault_auth import get_live_secret
except ImportError:
    logger.warning("⚠️ vault_auth.py not found. Secret resolution will be disabled.")


    def get_live_secret(n):
        return None

app = FastAPI(title="Ghidorah Librarian")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
sentry = StorageSentry()

# --- IDENTITY MAP ---
# Maps hashtags to Azure Vault secrets or local system triggers.
IDENTITY_MAP = {
    "glider": "PATRONUS-API-KEY",  # Model Grading (Patronus)
    "auditor": "SIMPLE-LOGIN-KEY",  # Mail/Identity (SimpleLogin Aliases)
    "mancer": "MANCER-API-KEY",  # Unfiltered/Unconstitutional Models
    "eval": "GEMINI-API-KEY",  # Dogfooding: Using Gemini 1.5 Pro for judging
    "translate": "GOOGLE-TRANSLATE-KEY",  # Polyglot Interrogation
    "vault": "LOCAL-GDRIVE-JSON",  # TRIGGER: Uses local service_account.json
    "muscle": "AZURE-STORAGE-KEY"  # Father Tier / Blob Storage access
}


@app.post("/api/v1/sessions/upload")
async def upload(weightclass: str, session_id: str, file: UploadFile = File(...)):
    """
    Receives session JSON and commits to SSD (Son) and Cloud (Grandfather).
    Compatible with new sessions and the legacy session_migrator.py.
    """
    try:
        content = await file.read()
        data = json.loads(content)
        # StorageSentry handles the 3-tier save (SSD -> Azure -> GDrive)
        return await sentry.save_session(session_id, weightclass, data)
    except Exception as e:
        logger.error(f"🚨 Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sentry/parse")
async def parse(payload: dict):
    """
    Parses prompts for Sentry Syntax (#tags, /commands, !execs) for injection.
    """
    text = payload.get("text", "")
    tags = re.findall(r'#(\w+)', text)
    injections = {}

    for t in tags:
        tag_lower = t.lower()
        secret_name = IDENTITY_MAP.get(tag_lower)

        # --- SPECIAL CASE: LOCAL JSON AUTH FOR GDRIVE ---
        if tag_lower == "vault":
            # Verify if the service account file exists on Node 1 (Sentry)
            has_json = os.path.exists("/home/godzilla/ghidorah_sentry/service_account.json")
            injections[t] = {
                "auth_type": "SERVICE_ACCOUNT_JSON",
                "status": "LOCAL_TRIGGER" if has_json else "FILE_MISSING",
                "target_node": "Node 1"
            }
            continue

        # --- STANDARD VAULT SECRET RESOLUTION ---
        if secret_name:
            key = get_live_secret(secret_name)
            if key:
                # Masked for telemetry, raw key stays in RAM for Node 2/Node C consumption
                injections[t] = {
                    "mask": f"{key[:5]}...{key[-4:]}",
                    "id": secret_name,
                    "target_node": "Node 2" if tag_lower != "muscle" else "Node 1"
                }

    return {
        "text": re.sub(r'#\w+', '', text).strip(),
        "tags": tags,
        "injections": injections,
        "status": "READY"
    }


@app.get("/health")
async def health():
    return {"status": "ONLINE", "node": "NODE_1_LIBRARIAN", "version": "8.9.9"}


if __name__ == "__main__":
    # Librarian operates on Port 8081 to avoid conflict with Manifest Server (8080)
    uvicorn.run(app, host="0.0.0.0", port=8081)
