# File: utils/payload_modifiers.py
import random
import requests
from urllib.parse import quote
from abc import ABC, abstractmethod

class PayloadModifier(ABC):
    """
    Abstract Strategy class for mutating text payloads.
    """
    @abstractmethod
    def modify(self, text: str, **kwargs) -> str:
        pass


class ZalgoModifier(PayloadModifier):
    def modify(self, text: str, intensity: int = 5, **kwargs) -> str:
        if intensity <= 0:
            return text
            
        # Unicode combining character ranges for Zalgo effects
        up_marks = [chr(i) for i in range(0x030D, 0x0315)] + [chr(i) for i in range(0x033D, 0x0344)]
        down_marks = [chr(i) for i in range(0x0316, 0x0333)]
        mid_marks = [chr(i) for i in range(0x0334, 0x033D)]
        
        zalgo_text = ""
        for char in text:
            if char.isalnum():
                zalgo_text += char
                for _ in range(intensity):
                    zalgo_text += random.choice(up_marks + down_marks + mid_marks)
            else:
                zalgo_text += char
        return zalgo_text


class RTLModifier(PayloadModifier):
    def modify(self, text: str, **kwargs) -> str:
        """
        Injects the Right-to-Left Override character (\u202E) at the start of every line.
        """
        if not text:
            return ""
        return '\n'.join([f"\u202E{line}" for line in text.split('\n')])


class TranslationModifier(PayloadModifier):
    def modify(self, text: str, target_lang: str = 'ar', **kwargs) -> str:
        """
        Uses the free Google Translate unofficial endpoint for rapid translation.
        """
        if not text:
            return ""
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={quote(text)}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                # The response is a nested array. [0] contains arrays of [translated_text, original_text]
                return "".join([s[0] for s in res.json()[0]])
            return f"API Error: {res.status_code}"
        except Exception as e:
            return f"Translation failed: {e}"


# --- FACTORY ---
class ModifierFactory:
    """
    Factory to instantiate payload modifiers cleanly.
    """
    @staticmethod
    def get_modifier(mod_type: str) -> PayloadModifier:
        mod_type = mod_type.lower()
        if mod_type == 'zalgo':
            return ZalgoModifier()
        elif mod_type == 'rtl':
            return RTLModifier()
        elif mod_type == 'translate':
            return TranslationModifier()
        else:
            raise ValueError(f"Unknown modifier type: {mod_type}")
