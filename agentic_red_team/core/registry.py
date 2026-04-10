# File: agentic_red_team/core/registry.py
# Purpose: Single Source of Truth for Model Colors and Taxonomy ("Kaiju Noir")

class ColorRegistry:
    """Provides Cardinal Colors for model families based on 'Kaiju Noir' specs."""
    
    FAMILIES = {
        "openai": {"base": "#10a37f", "hue": "#2ea043", "kanji": "知"},
        "anthropic": {"base": "#d73a49", "hue": "#cb2431", "kanji": "安"},
        "google": {"base": "#1f6feb", "hue": "#58a6ff", "kanji": "星"},
        "meta": {"base": "#8957e5", "hue": "#a371f7", "kanji": "繋"},
        "mistral": {"base": "#e3b341", "hue": "#f2cc60", "kanji": "風"},
        "default": {"base": "#4CAF50", "hue": "#56d364", "kanji": "龍"}
    }

    @classmethod
    def get_theme(cls, model_id: str) -> dict:
        """Returns the specific cardinal color and hue for a given model string."""
        if not model_id:
            return cls.FAMILIES["default"]

        model_id = model_id.lower()
        if "gpt" in model_id or "openai" in model_id:
            return cls.FAMILIES["openai"]
        if "claude" in model_id or "anthropic" in model_id:
            return cls.FAMILIES["anthropic"]
        if "gemini" in model_id or "google" in model_id:
            return cls.FAMILIES["google"]
        if "llama" in model_id or "meta" in model_id:
            return cls.FAMILIES["meta"]
        if "mistral" in model_id or "mixtral" in model_id:
            return cls.FAMILIES["mistral"]
        return cls.FAMILIES["default"]
