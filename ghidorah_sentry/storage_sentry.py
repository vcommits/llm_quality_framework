import os
import json
import httpx
import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path

# 🐉 Ghidorah Mesh: Session Migrator (v1.1.0)
# Role: Ingests legacy 'Purple Team' & 'Red Team Diary' JSON files into the Node 1 Sentry.
# Update: Added deep-mapping for Analyst Notes, Timestamps, and SQA Tags.

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("Migrator")

SENTRY_UPLOAD_URL = "http://localhost:8081/api/v1/sessions/upload"


class LegacyMigrator:
    def __init__(self, legacy_dir: str):
        self.legacy_path = Path(legacy_dir)
        self.success_count = 0
        self.fail_count = 0

    def extract_tags(self, text: str) -> list:
        """Extracts #hashtags from text if they aren't already in a list."""
        if not text: return []
        return re.findall(r'#(\w+)', text)

    def map_to_ghid(self, old_data: dict, filename: str) -> dict:
        """
        Maps legacy Purple Team & Red Team Diary fields to the Master .ghid Schema.
        Preserves Analyst Notes and historical timestamps for the 'Diary' view.
        """
        # 1. Identify Session ID and Base Metadata
        session_id = old_data.get("session_id") or old_data.get("id") or filename.split('.')[0]
        timestamp = old_data.get("timestamp") or old_data.get("date") or datetime.now().isoformat()

        # 2. Extract Tags (Critical for Red Team Diary filtering)
        tags = old_data.get("tags") or []
        if isinstance(tags, str): tags = [tags]

        # 3. Map Content (Check for 'Diary' style entries vs 'Session' logs)
        interrogations = old_data.get("interrogations") or []

        # Fallback for flat 'Red Team Diary' entries or v1 sessions
        if not interrogations:
            raw_text = old_data.get("prompt") or old_data.get("input") or "Legacy Import"
            tags.extend(self.extract_tags(raw_text))

            # Preserve Analyst Notes (Notes from the dashboard video)
            analyst_notes = old_data.get("analyst_notes") or old_data.get("notes", "")

            interrogations = [{
                "prompt_artifact": {
                    "raw_text": raw_text,
                    "tags": list(set(tags)),
                    "munge_stack": ["legacy_import"],
                    "analyst_notes": analyst_notes
                },
                "responses": [{
                    "model_id": old_data.get("model_name") or old_data.get("model", "UNKNOWN"),
                    "content": old_data.get("response") or old_data.get("output", ""),
                    "judge_verdict": {
                        "score": old_data.get("success_score") or old_data.get("score", 0),
                        "verdict": "MIGRATED",
                        "timestamp": timestamp
                    }
                }]
            }]

        # 4. Construct Final .ghid Payload
        ghid_payload = {
            "session_metadata": {
                "session_id": session_id,
                "weightclass": old_data.get("weightclass", "LEGACY"),
                "environment": old_data.get("environment", "PURPLE_TEAM_ORIGINAL"),
                "timestamp": timestamp,
                "migration_date": datetime.now().isoformat()
            },
            "interrogations": interrogations,
            "session_summary": {
                "champion": old_data.get("model_name") or old_data.get("model", "UNKNOWN"),
                "dominant_tags": list(set(tags)),
                "analyst_notes": old_data.get("analyst_notes") or old_data.get("notes", "")
            }
        }

        return ghid_payload

    async def migrate_all(self):
        if not self.legacy_path.exists():
            logger.error(f"❌ Legacy directory not found: {self.legacy_path}")
            return

        logger.info(f"🚀 Commencing migration of files in {self.legacy_path}...")

        async with httpx.AsyncClient(timeout=60.0) as client:
            for json_file in self.legacy_path.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        old_data = json.load(f)

                    # 1. Normalize to .ghid Schema
                    normalized = self.map_to_ghid(old_data, json_file.name)

                    # 2. Prepare Upload Parameters
                    params = {
                        "weightclass": normalized["session_metadata"]["weightclass"],
                        "session_id": normalized["session_metadata"]["session_id"]
                    }

                    # 3. Perform the Handshake to Node 1 Sentry
                    # We send as a multipart file upload to trigger StorageSentry
                    temp_name = f"migrating_{json_file.name}"
                    with open(temp_name, 'w', encoding='utf-8') as tf:
                        json.dump(normalized, tf, indent=2)

                    with open(temp_name, 'rb') as f:
                        files = {'file': (json_file.name, f, 'application/json')}
                        response = await client.post(SENTRY_UPLOAD_URL, params=params, files=files)

                    if response.status_code == 200:
                        logger.info(f"✅ Migrated: {json_file.name} -> {response.json().get('status')}")
                        self.success_count += 1
                    else:
                        logger.error(f"❌ Failed {json_file.name}: {response.status_code} - {response.text}")
                        self.fail_count += 1

                    # Cleanup
                    if os.path.exists(temp_name):
                        os.remove(temp_name)

                except json.JSONDecodeError:
                    logger.error(f"🚨 Corrupt JSON in {json_file.name}")
                    self.fail_count += 1
                except Exception as e:
                    logger.error(f"🚨 Error processing {json_file.name}: {str(e)}")
                    self.fail_count += 1

        logger.info(f"🏁 Migration Complete.")
        logger.info(f"📊 Success: {self.success_count} | Failed: {self.fail_count}")


if __name__ == "__main__":
    # Path configuration for the legacy locker
    Locker_Path = os.path.expanduser("~/legacy_locker/saved_sessions")

    # Ensure the Librarian is running on 8081 before starting
    migrator = LegacyMigrator(Locker_Path)
    asyncio.run(migrator.migrate_all())