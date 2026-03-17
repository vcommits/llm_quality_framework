import os
import asyncio
from utils.gdrive_vault import get_gdrive_service, vault_artifact_to_cold_storage
from harvester import fetch_secrets_into_ram  # Our existing Zero-Trust fetcher


async def execute_evaluation_suite(mission: MissionParams):
    logger.info(f"Igniting Passive Engine for {mission.operation_type}...")

    # 1. Zero-Trust Syphon: Get OpenAI keys AND GDrive Service Account from Node 1
    secrets = await fetch_secrets_into_ram(mission.provider)
    gdrive_creds = secrets.get("gdrive_service_account_json")

    if not gdrive_creds:
        logger.error("Failed to syphon GDrive credentials. Aborting to prevent data loss.")
        return

    # 2. Run the heavy compute (e.g., PromptFoo)
    logger.info("Executing PromptFoo matrix...")
    report_path = "/tmp/ghidorah_evals/promptfoo_workspace/output.html"

    # Simulate the heavy subprocess running...
    await asyncio.sleep(10)

    if os.path.exists(report_path):
        # 3. Stream the massive HTML/JSON output directly to Cold Storage
        gdrive_service = get_gdrive_service(gdrive_creds)
        file_id, drive_link = vault_artifact_to_cold_storage(
            gdrive_service,
            file_path=report_path,
            file_name=f"PromptFoo_Report_{mission.dataset_id}.html",
            mime_type="text/html"
        )

        # 4. Notify Node 1 (Hot Storage) with just the lightweight metadata/link
        if drive_link:
            await push_metadata_to_librarian(
                mission_id=mission.dataset_id,
                status="COMPLETED",
                cold_storage_link=drive_link
            )

        # 5. Purge the local heavy file from the iMac's SSD
        os.remove(report_path)
        logger.info("Local artifact purged. Node 2 reset and awaiting next directive.")