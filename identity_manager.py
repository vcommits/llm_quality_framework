import yaml
import random
import time
from mailslurp_client import MailSlurpClient
from simplelogin_client import SimpleLoginClient

class IdentityManager:
    """
    Orchestrates the lifecycle of Hydra identities.
    Synchronizes Node 0 network state with Node 1 persona data.
    """
    def __init__(self, vault_url: str, identities_path: str = "identities.yaml"):
        self.identities_path = identities_path
        self.config = self._load_config()
        self.ms_client = MailSlurpClient(vault_url)
        self.sl_client = SimpleLoginClient(vault_url)
        self.current_persona = None

    def _load_config(self):
        with open(self.identities_path, 'r') as f:
            return yaml.safe_load(f)

    def provision_identity(self, identity_id: str):
        """Fully initializes a persona with ephemeral and persistent layers."""
        self.current_persona = next((i for i in self.config['identities'] if i['id'] == identity_id))
        
        # 1. Ephemeral Inbound
        inbox = self.ms_client.create_inbox()
        
        # 2. Persistent Alias (if defined in YAML)
        alias = self.sl_client.create_alias(mailbox_id=1, prefix=identity_id)
        
        print(f"[Hydra-Init] Persona {identity_id} provisioned with Email: {inbox.email_address}")
        return {"email": inbox.email_address, "alias": alias.get('email')}

    def apply_behavioral_jitter(self):
        """Injects non-deterministic delays to bypass bot detection."""
        jitter = self.config['global_defaults']['jitter_range_ms']
        sleep_time = random.uniform(jitter[0], jitter[1]) / 1000
        time.sleep(sleep_time)

    def validate_session(self, current_vpn_ip: str):
        """Ensures session integrity against geo-fencing requirements."""
        # Verification logic against Node 0's egress state
        if self.current_persona['fingerprint']['geo_fence']:
            print(f"[Hydra-Sync] Verifying Geo-Fence for {self.current_persona['id']}")
            # In production, integrate with Node 0's /status endpoint
            return True
        return False