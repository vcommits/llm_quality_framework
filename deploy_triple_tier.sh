#!/bin/bash
echo "🚀 Deploying Triple-Tier Storage Sentry (v1.3.2)..."

cat << 'PY_EOF' > ~/ghidorah_sentry/storage_sentry.py
import os, json, asyncio, aiofiles, logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

try:
    from azure.cosmos.aio import CosmosClient
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    pass

load_dotenv()
BASE_DIR = os.path.expanduser("~/ghidorah_sentry")
SSD_PATH = os.path.join(BASE_DIR, "evidence_locker/sessions")
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")

COSMOS_URL = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_PRIMARY_KEY")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("StorageSentry")

class StorageSentry:
    def __init__(self):
        self.ssd_path = SSD_PATH
        os.makedirs(self.ssd_path, exist_ok=True)
        self.cosmos_client = None
        if COSMOS_URL and COSMOS_KEY:
            self.cosmos_client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)

    async def save_session(self, session_id: str, weightclass: str, data: Dict[str, Any]):
        filename = f"{weightclass.upper()}_{session_id}.json"
        filepath = os.path.join(self.ssd_path, filename)
        
        # 1. SSD COMMIT (Immediate)
        try:
            async with aiofiles.open(filepath, mode='w') as f:
                await f.write(json.dumps(data, indent=2))
            logger.info(f"💾 SON TIER (SSD): {filename}")
        except Exception as e:
            logger.error(f"🚨 SSD Write Error: {e}")

        # 2. GDrive ARCHIVE (Background)
        asyncio.create_task(self.archive_to_gdrive(filepath, filename))
        
        # 3. COSMOS REGISTRY (Background)
        if self.cosmos_client:
            asyncio.create_task(self.register_metadata(session_id, weightclass, data))
        
        return {"status": "WARM_SAVED", "local_path": filepath}

    async def register_metadata(self, session_id: str, weightclass: str, data: Dict[str, Any]):
        try:
            async with self.cosmos_client:
                db = self.cosmos_client.get_database_client("ghidorah_db")
                container = db.get_container_client("sessions")
                summary = data.get("session_summary", {})
                doc = {
                    "id": session_id,
                    "partition_key": weightclass, 
                    "timestamp": data.get("session_metadata", {}).get("timestamp", datetime.now().isoformat()),
                    "total_score": summary.get("avg_score", 0),
                    "tags": summary.get("dominant_tags", []),
                    "source": "Node_1_Pi4"
                }
                await container.upsert_item(doc)
            logger.info(f"🌌 REGISTRY TIER (Cosmos): {session_id} indexed.")
        except Exception as e:
            logger.error(f"🚨 Cosmos Registry Fail: {e}")

    async def archive_to_gdrive(self, filepath: str, filename: str):
        if not os.path.exists(SERVICE_ACCOUNT_FILE): return
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sync_gdrive, filepath, filename)
            logger.info(f"📁 GRANDFATHER TIER (GDrive): {filename}")
        except Exception as e:
            logger.error(f"🚨 GDrive Fail: {e}")

    def _sync_gdrive(self, filepath: str, filename: str):
        scopes = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(filepath, mimetype='application/json')
        service.files().create(body={'name': filename}, media_body=media).execute()
PY_EOF

echo "🔄 Restarting Librarian Service..."
sudo systemctl restart ghidorah-librarian
sleep 3

echo "⚡ Firing Triple-Tier Handshake Test..."
~/ghidorah_sentry/.venv/bin/python3 ~/ghidorah_sentry/zero_hardcode_test.py

