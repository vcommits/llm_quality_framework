import os
import shutil
import logging

logger = logging.getLogger("DiaryManager")


class DiaryManager:
    def __init__(self, storage_root="agent_memories"):
        # Resolving path relative to project root
        self.storage_root = os.path.abspath(storage_root)
        if not os.path.exists(self.storage_root):
            os.makedirs(self.storage_root)

    def get_context_path(self, profile_name):
        """Returns the active folder path for a profile."""
        return os.path.join(self.storage_root, "active_sessions", profile_name)

    def save_memory_snapshot(self, profile_name, snapshot_tag):
        """Zips the current profile state."""
        source_dir = self.get_context_path(profile_name)
        archive_name = f"{profile_name}_{snapshot_tag}"
        archive_path = os.path.join(self.storage_root, "snapshots", archive_name)

        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        shutil.make_archive(archive_path, 'zip', source_dir)
        print(f"[Diary] Snapshot saved: {archive_name}.zip")
        return f"{archive_path}.zip"

    def load_memory_snapshot(self, profile_name, snapshot_tag):
        """Unzips a previous state into the active folder."""
        archive_path = os.path.join(self.storage_root, "snapshots", f"{profile_name}_{snapshot_tag}.zip")
        target_dir = self.get_context_path(profile_name)

        if not os.path.exists(archive_path):
            print(f"[Diary] Error: Snapshot {archive_path} not found.")
            return None

        # Clean slate before loading
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        shutil.unpack_archive(archive_path, target_dir)
        print(f"[Diary] Loaded snapshot: {snapshot_tag}")
        return target_dir