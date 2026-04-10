# File: identity_manager.py | Node: 2 (The Muscle)
# Version: 6.0 | Identity: godzilla_persona_orchestrator
# Purpose: Professional OOP Identity Chassis (Abstraction, Inheritance, Encapsulation, Polymorphism)

import os
import json
import shutil
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from agentic_red_team import config
from harvester import SecretHarvester

logger = logging.getLogger("IdentityManager")


# =============================================================================
# 1. ABSTRACTION: The Base Identity Interface
# =============================================================================

class BaseIdentity(ABC):
    """
    Abstract Base Class for all entities in the Ghidorah Mesh.
    Encapsulates standard metadata and session isolation logic.
    """

    def __init__(self, identity_id: str, name: str, params: Optional[Dict[str, Any]] = None):
        self._id = identity_id.lower()
        self._name = name
        self._params = params or {}

        # ENCAPSULATION: Profile path is protected and initialized internally
        self._profile_path = self._ensure_context_isolation()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def profile_path(self) -> str:
        return self._profile_path

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Abstract method to be implemented by child classes."""
        pass

    def _ensure_context_isolation(self) -> str:
        """Encapsulated logic to create a dedicated, persistent folder."""
        safe_id = "".join([c if c.isalnum() else "_" for c in self._id])
        path = os.path.join(config.PERSONA_PROFILES_DIR, safe_id)
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"🎭 [MEM_INIT] Isolated context for '{self._name}' at {path}")
        return path

    def get_param(self, key: str, default: Any = None) -> Any:
        return self._params.get(key, default)

    def to_dict(self) -> Dict:
        """Serialization for registry persistence."""
        return {
            "id": self._id,
            "name": self._name,
            "params": self._params,
            "profile_path": self._profile_path,
            "class": self.__class__.__name__
        }


# =============================================================================
# 2. INHERITANCE: Concrete Implementations
# =============================================================================

class Persona(BaseIdentity):
    """
    Inherits from BaseIdentity.
    Specializes in human-like adversarial roleplay.
    """

    def __init__(self,
                 persona_id: str,
                 name: str,
                 system_prompt: str,
                 traits: Optional[List[str]] = None,
                 meta_params: Optional[Dict[str, Any]] = None):
        super().__init__(persona_id, name, meta_params)
        self._system_prompt = system_prompt
        self._traits = traits or []

    def get_system_prompt(self) -> str:
        """Implementation of the abstract requirement."""
        trait_str = f" Behavioral traits: {', '.join(self._traits)}." if self._traits else ""
        return f"{self._system_prompt}{trait_str}"

    def __getitem__(self, key):
        """Allows dict-like access to parameters or traits."""
        if key == "traits":
            return self._traits
        if key == "system_prompt":
            return self._system_prompt

        # Support for nested data access used in campaigns (e.g. payment_methods)
        # We return an empty dict for missing keys to prevent crashes on nested access
        val = self._params.get(key)
        if val is None:
            if key == "payment_methods":
                return {
                    "stripe_test_card": "None",
                    "stripe_exp": "00/00",
                    "stripe_cvc": "000",
                    "stripe_zip": "00000"
                }
            return {}
        return val

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "system_prompt": self._system_prompt,
            "traits": self._traits
        })
        return data


class SystemAuditor(BaseIdentity):
    """
    Inherits from BaseIdentity.
    Specializes in automated, non-persona-based security scans.
    """

    def __init__(self, auditor_id: str, name: str, params: Optional[Dict[str, Any]] = None):
        super().__init__(auditor_id, name, params)

    def get_system_prompt(self) -> str:
        return "You are an automated security auditor. Focus purely on technical vulnerability detection."


# =============================================================================
# 3. POLYMORPHISM & ENCAPSULATION: The Identity Registry
# =============================================================================

class IdentityRegistry:
    """
    The Orchestrator. Manages a polymorphic collection of BaseIdentity objects.
    Encapsulates secret retrieval (AKV) and disk persistence.
    """

    def __init__(self):
        # Polymorphic storage: can contain Personas or SystemAuditors
        self._identities: Dict[str, BaseIdentity] = {}
        self._harvester = SecretHarvester()
        self._load_registry()

    def _load_registry(self):
        """Hydrates the registry from JSON manifests."""
        if not os.path.exists(config.PERSONA_REGISTRY_DIR):
            os.makedirs(config.PERSONA_REGISTRY_DIR)
            return

        for filename in os.listdir(config.PERSONA_REGISTRY_DIR):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(config.PERSONA_REGISTRY_DIR, filename), 'r') as f:
                        data = json.load(f)
                        # Polymorphic instantiation based on 'class' metadata
                        if data.get("class") == "Persona":
                            obj = Persona(data['id'], data['name'], data['system_prompt'], data.get('traits'),
                                          data.get('params'))
                        else:
                            obj = SystemAuditor(data['id'], data['name'], data.get('params'))

                        self.register_identity(obj, save=False)
                except Exception as e:
                    logger.error(f"❌ Failed to hydrate {filename}: {e}")

    def register_identity(self, identity: BaseIdentity, save: bool = True):
        """Polymorphic registration: Accepts any BaseIdentity child."""
        self._identities[identity.id] = identity
        if save:
            save_path = os.path.join(config.PERSONA_REGISTRY_DIR, f"{identity.id}.json")
            with open(save_path, 'w') as f:
                json.dump(identity.to_dict(), f, indent=2)
        logger.info(f"✅ Identity Active: {identity.name} [{identity.__class__.__name__}]")

    def get_identity(self, identity_id: str) -> BaseIdentity:
        """Retrieves identity or returns the Encapsulated fallback."""
        return self._identities.get(identity_id, self._get_fallback())

    def _get_fallback(self) -> BaseIdentity:
        """Returns a safe fallback persona with empty structures for expected campaign keys."""
        return Persona(
            "fallback", 
            "Sentry Auditor", 
            "Default safety audit instructions.", 
            params={
                "payment_methods": {
                    "stripe_test_card": "None",
                    "stripe_exp": "00/00",
                    "stripe_cvc": "000",
                    "stripe_zip": "00000"
                }
            }
        )

    def get_credentials(self, identity_id: str) -> Dict[str, str]:
        """
        Encapsulates the Param Layer.
        Reaches into Azure Key Vault via Harvester.
        """
        identity = self.get_identity(identity_id)
        secret_id = identity.get_param("credential_secret_id")

        if secret_id:
            # Secure Syphon: Never hits Node 2 disk
            key = self._harvester.get_key(secret_id)
            return {"api_key": key}
        return {}

    def purge(self, identity_id: str):
        """Tear Down logic for session and metadata."""
        if identity_id in self._identities:
            obj = self._identities[identity_id]
            if os.path.exists(obj.profile_path):
                shutil.rmtree(obj.profile_path)

            reg_file = os.path.join(config.PERSONA_REGISTRY_DIR, f"{identity_id}.json")
            if os.path.exists(reg_file):
                os.remove(reg_file)

            del self._identities[identity_id]
            logger.info(f"🧹 Purged: {identity_id}")


class IdentityManager(IdentityRegistry):
    """
    Compatibility wrapper for the IdentityRegistry.
    Provides the specific API expected by red-team campaigns.
    Ensures singleton behavior when instantiated.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IdentityManager, cls).__new__(cls)
        return cls._instance

    def get_persona(self, persona_id: str) -> BaseIdentity:
        return self.get_identity(persona_id)


# Singleton Interface
manager = IdentityManager()
