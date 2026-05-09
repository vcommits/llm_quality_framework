import os
import json
import asyncio
import aiofiles
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Cloud & Auth Imports
try:
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos import PartitionKey
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    pass

# 🐉 Ghidorah Node 1: Storage Sentry (v1.4.3)
# Identity Pivot: OAuth 2.0 User Delegation (Personal Quota Access)

load_dotenv()
BASE_DIR = os.path.expanduser("~/ghidorah_sentry")
SSD_PATH = os.path.join(BASE_DIR, "evidence_locker/sessions")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# Environment Variables
COSMOS_URL = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_PRIMARY_KEY")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID") 

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("StorageSentry")

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class StorageSentry:
    def __init__(self):
        self.ssd_path = SSD_PATH
        os.makedirs(self.ssd_path, exist_ok=True)
        self.cosmos_url = COSMOS_URL
        self.cosmos_key = COSMOS_KEY
        self.token_file = TOKEN_FILE
        self.scopes = SCOPES
        self.gdrive_folder_id = GDRIVE_FOLDER_ID

    async def save_session(self, session_id: str, weightclass: str, data: Dict[str, Any]):
        """The 3-Tier Archival Chain."""
        filename = f"{weightclass.upper()}_{session_id}.json"
        filepath = os.path.join(self.ssd_path, filename)
        
        # 1. SSD COMMIT
        try:
            async with aiofiles.open(filepath, mode='w') as f:
                await f.write(json.dumps(data, indent=2))
            logger.info(f"💾 SSD COMMIT: {filename}")
        except Exception as e:
            logger.error(f"🚨 SSD Write Error: {e}")

        # 2. GDRIVE ARCHIVE (OAuth 2.0 Background Task)
        asyncio.create_task(self.archive_to_gdrive(filepath, filename))
        
        # 3. COSMOS REGISTRY (Background Task)
        if self.cosmos_url and self.cosmos_key:
            asyncio.create_task(self.register_metadata(session_id, weightclass, data))
        
        return {"status": "WARM_SAVED", "local_path": filepath}

    async def register_metadata(self, session_id: str, weightclass: str, data: Dict[str, Any]):
        """Indexes metadata in Azure Cosmos DB."""
        client = CosmosClient(self.cosmos_url, credential=self.cosmos_key)
        try:
            async with client:
                db = client.get_database_client("ghidorah_db")
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
            logger.info(f"🌌 COSMOS REGISTRY: {session_id} indexed.")
        except Exception as e:
            logger.error(f"🚨 Cosmos Registry Fail: {e}")

    async def archive_to_gdrive(self, filepath: str, filename: str):
        """Grandfather Tier: OAuth 2.0 User Delegated Archival."""
        if not os.path.exists(self.token_file):
            logger.warning("⚠️ token.json missing. GDrive archival skipped.")
            return

        try:
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 OAuth token expired. Executing silent refresh...")
                creds.refresh(Request())
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._execute_gdrive_upload, creds, filepath, filename)
            logger.info(f"📁 GRANDFATHER TIER (OAuth 2.0): {filename} secured.")

        except Exception as e:
            logger.error(f"🚨 GDrive Auth/Upload Failure: {e}")

    def _execute_gdrive_upload(self, creds, filepath: str, filename: str):
        """Synchronous Google API upload."""
        service = build('drive', 'v3', credentials=creds)
        body = {'name': filename}
        if self.gdrive_folder_id:
            body['parents'] = [self.gdrive_folder_id]
            
        media = MediaFileUpload(filepath, mimetype='application/json')
        service.files().create(body=body, media_body=media).execute()
