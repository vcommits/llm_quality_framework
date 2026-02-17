import yaml
import os


class IdentityManager:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))  # Up 2 levels if in utils
        # Fallback to local relative if running from root
        if "agentic_red_team" not in project_root:
            project_root = os.path.dirname(current_dir)

        self.yaml_path = os.path.join(project_root, "agentic_red_team", "scenarios", "identities.yaml")
        self.personas = self._load_identities()

    def _load_identities(self):
        if not os.path.exists(self.yaml_path):
            # Try absolute fallback
            self.yaml_path = os.path.abspath("agentic_red_team/scenarios/identities.yaml")
            if not os.path.exists(self.yaml_path):
                raise FileNotFoundError(f"CRITICAL: Could not find identities.yaml")

        with open(self.yaml_path, "r") as f:
            data = yaml.safe_load(f)
        return {p['id']: p for p in data.get('personas', [])}

    def get_persona(self, persona_id):
        persona = self.personas.get(persona_id)
        if not persona:
            raise ValueError(f"Persona '{persona_id}' not found.")
        return persona