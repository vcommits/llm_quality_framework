# File: agentic_red_team/core/providers.py
# Purpose: Polymorphic Dispatching for Model Backends

from abc import ABC, abstractmethod
from typing import Any, Dict
from litellm import completion

class BaseProvider(ABC):
    """Abstract interface for executing model payloads and harvesting raw telemetry."""

    @abstractmethod
    def execute(self, model_id: str, messages: list[dict], **kwargs) -> Any:
        """Executes the request against the provider."""
        pass

    @abstractmethod
    def harvest_metadata(self, raw_response: Any) -> Dict[str, Any]:
        """Standardizes metadata for the Glassdesk Postman tab."""
        pass

class GenericLitellmProvider(BaseProvider):
    """Fallback provider capable of hitting any generic endpoint via litellm."""

    def execute(self, model_id: str, messages: list[dict], **kwargs) -> Any:
        # Pass raw messages (strings or multimodal arrays) directly to LiteLLM
        return completion(model=model_id, messages=messages, **kwargs)

    def harvest_metadata(self, raw_response: Any) -> Dict[str, Any]:
        usage = getattr(raw_response, 'usage', None)
        
        return {
            "fingerprint": getattr(raw_response, 'system_fingerprint', 'UNKNOWN'),
            "model_version": getattr(raw_response, 'model', 'UNKNOWN'),
            "finish_reason": raw_response.choices[0].finish_reason if hasattr(raw_response, 'choices') else 'stop',
            "token_burn": {
                "prompt": usage.prompt_tokens if usage else 0,
                "completion": usage.completion_tokens if usage else 0,
                "total": usage.total_tokens if usage else 0
            }
        }
