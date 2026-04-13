import os
import json
import asyncio
import aiofiles
import logging
import shutil
from datetime import datetime
from typing import Dict, Any

try:
    from azure.storage.blob.aio import BlobServiceClient
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    pass

BASE_DIR = os.path.expanduser("~/ghidorah_sentry")
SSD_PATH = os.path.join(BASE_DIR, "evidence_locker/sessions")
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("StorageSentry")

class StorageSentry:
    def __init__(self):
        self.azure_client = None
        if AZURE_CONNECTION_STRING:
            try:
                self.azure_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
            except Exception:
                pass

    async def save_session(self, session_id: str, weightclass: str, data: Dict[str, Any]):
        os.makedirs(SSD_PATH, exist_ok=True)
        filename = f"{weightclass.upper()}_{session_id}.json"
        filepath = os.path.join(SSD_PATH, filename)
        async with aiofiles.open(filepath, mode='w') as f:
            await f.write(json.dumps(data, indent=2))
        logger.info(f"💾 SSD COMMIT: {filename}")
        asyncio.create_task(self.archive_to_azure(filepath, filename))
        asyncio.create_task(self.archive_to_gdrive(filepath, filename))
        return {"status": "WARM_SAVED", "local_path": filepath}

    async def archive_to_azure(self, filepath: str, filename: str):
        if not self.azure_client: return
        try:
            blob_client = self.azure_client.get_blob_client(container="ghidorah-diary", blob=filename)
            async with aiofiles.open(filepath, mode='rb') as data:
                await blob_client.upload_blob(await data.read(), overwrite=True)
            logger.info(f"☁️ AZURE MIRROR: {filename}")
        except Exception as e:
            logger.error(f"🚨 Azure Fail: {e}")

    async def archive_to_gdrive(self, filepath: str, filename: str):
        if not os.path.exists(SERVICE_ACCOUNT_FILE): return
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sync_gdrive, filepath, filename)
            logger.info(f"📁 GDRIVE ARCHIVE: {filename}")
        except Exception:
            pass

    def _sync_gdrive(self, filepath: str, filename: str):
        scopes = ['[https://www.googleapis.com/auth/drive.file](https://www.googleapis.com/auth/drive.file)']
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(filepath, mimetype='application/json')
        service.files().create(body={'name': filename}, media_body=media).execute()

if __name__ == "__main__":
    sentry = StorageSentry()
    asyncio.run(sentry.save_session("HANDSHAKE", "BOOT", {"msg": "Node 1 Online"}))
