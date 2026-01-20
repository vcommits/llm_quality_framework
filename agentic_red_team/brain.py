import os
import json
from litellm import completion
from agentic_red_team.utils.identity_manager import IdentityManager
from agentic_red_team.utils.telemetry import TelemetryManager


class AgentBrain:
    def __init__(self, persona_id="attacker_brain_smart"):
        # 1. Start Telemetry
        TelemetryManager()

        self.im = IdentityManager()
        self.persona = self.im.get_persona(persona_id)

        # Load credentials
        self.provider = self.persona['credentials']['provider']
        self.raw_model_name = self.persona['credentials']['model_name']

        # 2. Universal Provider Routing (LiteLLM Format)
        if self.provider == "together_ai":
            self.model_name = f"together_ai/{self.raw_model_name}"
        elif self.provider == "huggingface":
            self.model_name = f"huggingface/{self.raw_model_name}"
        else:
            self.model_name = self.raw_model_name

            # Load API Key
        api_key_env = self.persona['credentials']['api_key_env']
        self.api_key = os.getenv(api_key_env)

        if self.api_key:
            # Set ENV for LiteLLM auto-discovery
            if self.provider == "together_ai":
                os.environ["TOGETHERAI_API_KEY"] = self.api_key
            elif self.provider == "huggingface":
                os.environ["HUGGINGFACE_API_KEY"] = self.api_key
            elif self.provider == "openai":
                os.environ["OPENAI_API_KEY"] = self.api_key
            elif self.provider == "google":
                os.environ["GEMINI_API_KEY"] = self.api_key

    def decide_next_move(self, html_content, user_goal, user_data, adversarial_note=None):
        """
        The Core Loop: Observes HTML -> Decides Action.
        """
        clean_dom = html_content[:15000]

        system_msg = (
            f"You are a Red Team Agent. Goal: {user_goal}\n"
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
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ BRAIN ERROR: {e}")
            return []

    def _parse_json(self, raw_text):
        try:
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except:
            return []