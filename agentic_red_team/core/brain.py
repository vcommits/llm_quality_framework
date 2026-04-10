# File: agentic_red_team/core/brain.py | Version: 2.1
# Identity: godzilla_brain | Role: Intelligence Core
# Purpose: Telemetry-Aware AI decision engine with LiteLLM usage tracking.

import os
import json
import re
from litellm import completion
from agentic_red_team.utils.identity_manager import manager as identity_manager


class AgentBrain:
    """The 'Will' of the individual Agent. Returns actions + token telemetry."""

    def __init__(self, persona_id="attacker_brain_smart", model_override=None, provider_override=None):
        # Fetch the full BaseIdentity child (Persona or SystemAuditor)
        self.persona = identity_manager.get_identity(persona_id)

        # Provider Mapping
        params = self.persona.get_param("credentials", {})
        self.provider = provider_override or params.get("provider", "openai")
        self.raw_model = params.get("model_name", "gpt-4o")

        prefix_map = {
            "together_ai": "together_ai/",
            "huggingface": "huggingface/",
            "google": "gemini/",
            "openai": ""
        }
        
        # If model_override is provided, we assume it's the full string or needs the provider prefix
        if model_override:
            if "/" in model_override:
                self.model_name = model_override
            else:
                self.model_name = f"{prefix_map.get(self.provider, '')}{model_override}"
        else:
            self.model_name = f"{prefix_map.get(self.provider, '')}{self.raw_model}"

        # API Key Harvesting (RAM-only environment variables for LiteLLM)
        creds = identity_manager.get_credentials(persona_id)
        api_key = creds.get("api_key")

        if api_key:
            env_map = {
                "together_ai": "TOGETHER_AI_API_KEY",
                "huggingface": "HUGGINGFACE_API_KEY",
                "openai": "OPENAI_API_KEY",
                "google": "GEMINI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY"
            }
            env_var = env_map.get(self.provider)
            if env_var:
                os.environ[env_var] = api_key

    def decide_next_move(self, html_content, user_goal, user_data=None, adversarial_note=None):
        """Returns parsed JSON actions + LiteLLM usage stats for Data Currency."""
        clean_dom = html_content[:15000]  # Buffer guard

        system_msg = (
            f"{self.persona.get_system_prompt()}\n"
            f"GOAL: {user_goal}\n"
            "OUTPUT FORMAT: JSON ONLY. List of browser actions.\n"
            "Example: [{'action': 'click', 'selector': 'button#submit'}]"
        )
        if adversarial_note:
            system_msg += f"\nATTACK VECTOR: {adversarial_note}"

        try:
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"Context:\n{clean_dom}"}
                ],
                temperature=0.1,
                metadata={"persona_id": self.persona.id}
            )

            raw_content = response.choices[0].message.content
            usage = getattr(response, 'usage', None)

            return {
                "actions": self._parse_json(raw_content),
                "raw_text": raw_content,
                "usage": {
                    "model_id": self.model_name,
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0
                }
            }
        except Exception as e:
            print(f"❌ BRAIN ERROR [{self.persona.id}]: {e}")
            return {
                "actions": [], 
                "raw_text": "", 
                "usage": {
                    "model_id": self.model_name,
                    "prompt_tokens": 0, 
                    "completion_tokens": 0
                }
            }

    def _parse_json(self, raw_text):
        """Standardized JSON extractor for various model output styles."""
        if not raw_text:
            return None
        try:
            # 1. Clean markdown and whitespace
            clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw_text).strip()
            return json.loads(clean)
        except Exception:
            # 2. Try finding anything between curly or square brackets as a fallback
            try:
                match = re.search(r"(\{.*\}|\[.*\])", raw_text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except Exception:
                pass
        return None
