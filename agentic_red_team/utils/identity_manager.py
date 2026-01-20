import yaml
import os


class IdentityManager:
    def __init__(self):
        # robust path finding:
        # go up one level from 'utils' to find 'scenarios'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.yaml_path = os.path.join(project_root, "scenarios", "identities.yaml")

        self.personas = self._load_identities()

    def _load_identities(self):
        """
        Reads the YAML file and converts the list of personas into a dictionary
        keyed by their ID for fast lookup.
        """
        if not os.path.exists(self.yaml_path):
            raise FileNotFoundError(f"CRITICAL: Could not find identities.yaml at {self.yaml_path}")

        with open(self.yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Convert list to dictionary: { 'persona_mom': {...data...} }
        return {p['id']: p for p in data.get('personas', [])}

    def get_persona(self, persona_id):
        """
        Returns the full persona dictionary for a given ID.
        """
        persona = self.personas.get(persona_id)
        if not persona:
            available_ids = list(self.personas.keys())
            raise ValueError(f"Persona '{persona_id}' not found. Available: {available_ids}")
        return persona