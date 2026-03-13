# File: services/storage_service.py
# Purpose: Manages Hot (SSD) and Cold (Cloud) storage interactions on Node 1.

import os
import json
import shutil
import logging
from datetime import datetime

logger = logging.getLogger("StorageService")

# CONFIGURATION
HOT_STORAGE_PATH = os.getenv("HOT_STORAGE_PATH", "./data/hot")
COLD_STORAGE_PATH = os.getenv("COLD_STORAGE_PATH", "./data/archive_staging") # Staging area for upload

os.makedirs(HOT_STORAGE_PATH, exist_ok=True)
os.makedirs(COLD_STORAGE_PATH, exist_ok=True)

class StorageService:
    
    @staticmethod
    def save_hot_session(session_id: str, data: dict):
        """
        Saves a live session to the Pi's fast SSD storage.
        """
        filename = f"session_{session_id}.json"
        filepath = os.path.join(HOT_STORAGE_PATH, filename)
        
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"🔥 Hot Save: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Hot Save Failed: {e}")
            raise

    @staticmethod
    def list_hot_sessions():
        """
        Returns list of sessions currently on the SSD.
        """
        files = [f for f in os.listdir(HOT_STORAGE_PATH) if f.endswith(".json")]
        return sorted(files, reverse=True)

    @staticmethod
    def archive_to_cold(session_id: str):
        """
        Moves a session from Hot storage to the Cold Staging area 
        and triggers Cloud Sync (e.g., Google Drive upload).
        """
        filename = f"session_{session_id}.json"
        src = os.path.join(HOT_STORAGE_PATH, filename)
        dst = os.path.join(COLD_STORAGE_PATH, filename)
        
        if not os.path.exists(src):
            raise FileNotFoundError(f"Session {session_id} not found in Hot Storage")
            
        try:
            shutil.copy2(src, dst)
            logger.info(f"❄️ Archived to Staging: {filename}")
            
            # TODO: Integrate Google Drive Upload Here
            # upload_to_gdrive(dst)
            
            return {"status": "archived", "local_path": dst, "cloud_synced": False}
        except Exception as e:
            logger.error(f"Archive Failed: {e}")
            raise

# --- Google Drive Stub (For Future Implementation) ---
def upload_to_gdrive(local_path):
    # Implement PyDrive2 or Google Client logic here
    pass
