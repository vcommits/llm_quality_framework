import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

logger = logging.getLogger("ColdStorage")

# The specific folder ID in your personal GDrive (e.g., "Ghidorah_Evidence_Locker")
GDRIVE_FOLDER_ID = "YOUR_GDRIVE_FOLDER_ID_HERE"


def get_gdrive_service(ram_credentials_dict: dict):
    """
    Authenticates directly from a dictionary held in RAM (syphoned from Node 1),
    bypassing the need for a local credentials.json file.
    """
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_info(
        ram_credentials_dict, scopes=scopes
    )
    service = build('drive', 'v3', credentials=creds)
    return service


def vault_artifact_to_cold_storage(service, file_path: str, file_name: str, mime_type: str):
    """
    Uploads a heavy artifact directly to your GDrive Cold Storage.
    """
    logger.info(f"Uploading {file_name} to Cold Storage (GDrive)...")

    file_metadata = {
        'name': file_name,
        'parents': [GDRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        logger.info(f"✅ Cold Storage Vaulting Complete: {file.get('webViewLink')}")
        return file.get('id'), file.get('webViewLink')

    except Exception as e:
        logger.error(f"Failed to vault to GDrive: {e}")
        return None, None