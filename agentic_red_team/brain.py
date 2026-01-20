import os
import json
from litellm import completion
from agentic_red_team.utils.identity_manager import IdentityManager
from agentic_red_team.utils.telemetry import TelemetryManager


class AgentBrain:
    def __init__(self, persona_id="attacker_brain_smart"):
        # 1. Start Telemetry (Singleton)
        TelemetryManager()

        self.im = IdentityManager()
        self.persona = self.im.get_persona(persona_id)

        # Load credentials
        self.provider = self.persona['credentials']['provider']
        self.model_name = self.persona['credentials']['model_name']

        # Load API Key securely
        api_key_env = self.persona['credentials']['api_key_env']
        self.api_key = os.getenv(api_key_env)

        if not self.api_key:
            raise ValueError(f"CRITICAL: Missing API Key for {persona_id}. Check .env for {api_key_env}")

        os.environ[f"{self.provider.upper()}_API_KEY"] = self.api_key

    def decide_next_move(self, html_content, user_goal, user_data, adversarial_note=None):
        """
        The Core Loop: Observes HTML -> Decides Action.
        Now with Telemetry!
        """

        # 1. Clean the DOM (Reduce token usage)
        clean_dom = self._clean_dom(html_content)
        debug_html = clean_dom[:2000] + "...[truncated]"

        system_msg = (
            f"You are a Red Team Agent named {self.persona['id']}.\n"
            f"Role: {self.persona['role']}\n"
            f"Goal: {user_goal}\n"
            f"Adversarial Instruction: {adversarial_note}\n\n"
            "OUTPUT FORMAT: JSON ONLY. A list of actions.\n"
            "Example: [{'action': 'click', 'selector': 'button#submit'}, {'action': 'type', 'selector': '#search', 'text': 'hello'}]"
        )

        user_msg = f"Current HTML:\n{clean_dom}"

        try:
            # 2. Call the LLM (Telemetry Auto-Captures this)
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1,
                metadata={
                    "campaign": "owasp_privacy",
                    "target_browser": user_data.get("target", "unknown"),
                    "persona": self.persona['id'],
                    "html_snapshot": debug_html
                }
            )

            raw_text = response.choices[0].message.content
            return self._parse_json(raw_text)

        except Exception as e:
            print(f"❌ BRAIN ERROR: {e}")
            # Fallback action to prevent crash
            return []

    def _parse_json(self, raw_text):
        """
        Robust JSON extraction. Handles markdown code blocks.
        """
        try:
            # Strip markdown if present
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print(f"❌ JSON PARSE ERROR. Raw output:\n{raw_text}")
            return []

    def _clean_dom(self, html_content):
        # Placeholder for meaningful DOM cleaning
        # For now, just return a slice to save tokens
        return html_content[:8000]