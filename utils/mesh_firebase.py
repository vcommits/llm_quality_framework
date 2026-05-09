import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# --- Kaiju Noir Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [MESH TELEMETRY]: %(message)s')
logger = logging.getLogger("FirebaseLink")

class GhidorahFirebaseManager:
    """
    [ 📡 MESH TELEMETRY LINK ]
    A singleton manager to handle low-latency C2 state updates and 60FPS UI 
    telemetry streaming to Firestore (Native Mode) in us-east1 for the Ghidorah Mesh.
    """
    
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GhidorahFirebaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes the firebase-admin SDK using the service account certificate."""
        
        # Per the Technical Context, the key file is deployed to ~/
        # We try to find it there, or allow an environment variable override for flexibility
        home_dir = os.path.expanduser("~")
        default_key_path = os.path.join(home_dir, "ghidorah-mesh-key.json")
        key_path = os.environ.get("FIREBASE_CREDENTIALS", default_key_path)

        if not os.path.exists(key_path):
            logger.error(f"[FATAL] Firebase credentials missing at {key_path}. Telemetry Link Offline.")
            # In a production script, you might want to raise an exception here.
            # We fail gracefully here to allow the app to boot without telemetry if needed.
            return

        try:
            # Check if already initialized to prevent errors on hot-reloads
            if not firebase_admin._apps:
                logger.info(f"Authenticating Mesh Link using certificate: {key_path}")
                cred = credentials.Certificate(key_path)
                # Ensure we target the correct project ID as defined in the context
                firebase_admin.initialize_app(cred, {
                    'projectId': 'ghidorah-archive',
                })
            
            self._db = firestore.client()
            logger.info("✅ Firebase Admin SDK Initialized. Connected to 'ghidorah-archive' (us-east1).")
        except Exception as e:
            logger.error(f"[FATAL] Failed to initialize Firebase: {e}")

    def get_db(self):
        """Returns the active Firestore client."""
        if not self._db:
             logger.warning("Attempted to access Firestore before initialization.")
        return self._db

    async def update_node_status(self, node_id: str, role: str, status_data: dict):
        """
        [ STATE OVERRIDE ]
        Updates the real-time telemetry document for a specific node.
        
        Args:
            node_id: e.g., 'node-c-brain-spot' or 'node-sensory'
            role: e.g., 'brain' or 'sensory-input'
            status_data: A dictionary of metrics (e.g., {"cpu": 45, "state": "inferring"})
        """
        if not self._db:
            return

        try:
            # Target the specific collection and document as per the Technical Context
            doc_ref = self._db.collection('mesh_status').document(node_id)
            
            # Ensure the base role is always present, then merge the new status data
            payload = {
                "role": role,
                "last_updated": firestore.SERVER_TIMESTAMP,
                **status_data
            }
            
            # Use merge=True to update specific fields without overwriting the whole document
            doc_ref.set(payload, merge=True)
            logger.debug(f"Updated status for {node_id}: {status_data}")
        except Exception as e:
            logger.error(f"Failed to update node status for {node_id}: {e}")

# Provide a ready-to-use instance for the rest of the application
mesh_db = GhidorahFirebaseManager()

# Example Usage:
# if __name__ == "__main__":
#     db_manager = GhidorahFirebaseManager()
#     import asyncio
#     asyncio.run(db_manager.update_node_status(
#         node_id="node-c-brain-spot", 
#         role="brain", 
#         status_data={"gpu_utilization": 88, "current_task": "whisper_stt"}
#     ))
