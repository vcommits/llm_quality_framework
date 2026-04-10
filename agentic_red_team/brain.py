import os
import json
from litellm import completion
from agentic_red_team.utils.identity_manager import IdentityManager


class AgentBrain:
    def __init__(self, persona_id="attacker_brain_smart"):
        self.im = IdentityManager()
        self.persona = self.im.get_persona(persona_id)

        # Load credentials
        self.provider = self.persona['credentials']['provider']
        self.raw_model_name = self.persona['credentials']['model_name']

        # LiteLLM Format Mapping
        provider_map = {
            "together_ai": "together_ai/",
            "huggingface": "huggingface/",
            "google": "gemini/",
            "openai": ""
        }
        self.model_name = f"{provider_map.get(self.provider, '')}{self.raw_model_name}"

        # Sync API Keys to Environment for LiteLLM
        api_key_env = self.persona['credentials']['api_key_env']
        self.api_key = os.getenv(api_key_env)

        env_key_map = {
            "together_ai": "TOGETHERAI_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GEMINI_API_KEY"
        }
        if self.api_key and self.provider in env_key_map:
            os.environ[env_key_map[self.provider]] = self.api_key

    def decide_next_move(self, html_content, user_goal, user_data=None, adversarial_note=None):
        """
        The Core Loop: Observes HTML -> Decides Action.
        Returns response + token telemetry.
        """
        clean_dom = html_content[:15000]

        system_msg = (
            f"You are a Red Team Agent. Goal: {user_goal}\n"
            f"USER_CONTEXT: {user_data}\n"
            "OUTPUT FORMAT: JSON ONLY. List of actions.\n"
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
                metadata={"persona": self.persona['id']}
            )

            raw_content = response.choices[0].message.content
            # Capture actual token usage if available via LiteLLM
            usage = getattr(response, 'usage', None)

            return {
                "actions": self._parse_json(raw_content),
                "raw_text": raw_content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0
                }
            }
        except Exception as e:
            print(f"❌ BRAIN ERROR: {e}")
            return {"actions": [], "raw_text": "", "usage": {"prompt_tokens": 0, "completion_tokens": 0}}

    def _parse_json(self, raw_text):
        """Extracts JSON list from model response, handling markdown blocks."""
        try:
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, TypeError):
            return []
