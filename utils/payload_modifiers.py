import random
import base64
import logging
from utils.payload_catalog import PayloadCatalog

logger = logging.getLogger("PayloadMutator")


class PayloadMutator:
    """
    The 'Exercise Engine' for the Ghidorah Triad.
    Used to pressure-test model tokenizers and safety guardrails across
    Node 2 (Muscle), Node X (Prism), and Node 3 (Architect).
    """

    def __init__(self, node_tier="high"):
        self.node_tier = node_tier
        self.capabilities = {
            "low": ["sponge_case", "leetspeak"],
            "high": ["sponge_case", "leetspeak", "zalgo_glitch", "rtl_override", "translation_bypass",
                     "unicode_homoglyph", "typoglycemia", "leekcode_wrap", "tokenization_scrambler", "emoji_flood", "science_greek",
                     "reverse", "base64", "hex", "binary", "morse", "small_caps", "invisible"]
        }
        self.active_methods = self.capabilities.get(node_tier, self.capabilities["low"])

    def mutate(self, text, method, severity=0.5):
        if method not in self.active_methods:
            return f"[BLOCKED: {method} exceeds Node Tier]"

        if method == "zalgo_glitch":
            char_map = [chr(i) for i in range(0x0300, 0x036F)]
            k_val = max(1, int(severity * 15))
            return "".join([c + "".join(random.choices(char_map, k=k_val)) for c in text])
            
        if method == "tokenization_scrambler":
            neighbors = {
                'a': ['s', 'q'], 's': ['a', 'd', 'w'], 'd': ['s', 'f', 'e'], 'f': ['d', 'g', 'r'],
                'h': ['g', 'j', 'n'], 't': ['r', 'y', 'g'], 'i': ['u', 'o', 'k'], 'e': ['w', 'r', 'd'],
                'o': ['i', 'p', 'l'], 'p': ['o', '[', ';'], 'l': ['k', 'o', 'p']
            }
            words = text.split()
            mutated_words = []

            for word in words:
                if random.random() > (severity + 0.1):
                    mutated_words.append(word)
                    continue

                if severity > 0.7:
                    word = word.lower().replace("th", "tj").replace("is", "isis")
                    vowels = "aeiou"
                    word = "".join([c for c in word if c.lower() not in vowels or random.random() > 0.4])

                if random.random() < (severity * 0.8):
                    idx = random.randint(0, len(word) - 1)
                    char = word[idx].lower()
                    if char in neighbors:
                        word = word[:idx] + random.choice(neighbors[char]) + word[idx + 1:]

                if random.random() < (severity * 0.5):
                    punc_options = [",,", "..", "!!", ";", " '", " ["]
                    word += random.choice(punc_options)

                mutated_words.append(word)

            final_result = ""
            for i, word in enumerate(mutated_words):
                final_result += word
                if i < len(mutated_words) - 1:
                    if random.random() > (severity * 0.75):
                        final_result += " "

            return final_result.strip()
            
        if method == "science_greek":
            mapping = {
                'a': 'α', 'b': 'β', 'd': 'δ', 'e': 'ε', 'g': 'γ', 'i': 'ι',
                'k': 'κ', 'm': 'μ', 'n': 'ν', 'o': 'ο', 'p': 'π', 'r': 'ρ',
                's': 'σ', 't': 'τ', 'u': 'υ', 'w': 'ω', 'x': 'χ', 'y': 'ψ'
            }
            result = []
            for char in text:
                if char.lower() in mapping and random.random() < severity:
                    result.append(mapping[char.lower()])
                else:
                    result.append(char)
            return "".join(result)
            
        if method == "emoji_flood":
            all_emojis = list(PayloadCatalog.EMOJIS["Standard Faces & Emotion"].replace(" ", "")) + list(PayloadCatalog.EMOJIS["Symbols & Punctuation"].replace(" ", ""))
            words = text.split()
            result = []
            flood_density = max(1, int(severity * 5))
            for word in words:
                result.append(word)
                if random.random() < (severity + 0.2):
                    result.append("".join(random.choices(all_emojis, k=flood_density)))
            return " ".join(result)

        if method == "leekcode_wrap": return f"def exploit():\n    '''{text}'''"
        if method == "sponge_case": return "".join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text)])
        if method == "leetspeak": return text.replace('a', '4').replace('e', '3').replace('i', '1').replace('o', '0').replace('s', '5').replace('t', '7')
        if method == "rtl_override": return f"\u202e{text[::-1]}\u202c"
        if method == "translation_bypass": return f"[REDIRECT_AR]: {text}"
        if method == "unicode_homoglyph": return text.replace('a', 'а').replace('e', 'е').replace('p', 'р')
        if method == "typoglycemia": 
            words = text.split()
            for i, w in enumerate(words):
                if len(w) > 3: words[i] = w[0] + "".join(reversed(w[1:-1])) + w[-1]
            return " ".join(words)
        if method == "reverse": return text[::-1]
        if method == "base64": return base64.b64encode(text.encode("utf-8")).decode("utf-8")
        if method == "hex": return text.encode("utf-8").hex()
        if method == "binary": return ' '.join(format(ord(x), '08b') for x in text)
        if method == "morse":
            mapping = {
                'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
                'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
                'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
                'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
                '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
                '9': '----.', '0': '-----', ' ': '/'
            }
            return ' '.join(mapping.get(c.upper(), c) for c in text)
        if method == "small_caps":
            normal = "abcdefghijklmnopqrstuvwxyz"
            caps = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
            mapping = str.maketrans(normal, caps)
            return text.lower().translate(mapping)
        if method == "invisible":
            invisibles = ["\u200b", "\u200c", "\u200d", "\u00ad", "\u2060"]
            result = []
            for char in text:
                result.append(char)
                if random.random() < severity:
                    result.append(random.choice(invisibles))
            return "".join(result)

        return text


def apply_modifiers(text: str, modifier_list: list) -> str:
    """Legacy/CLI Wrapper supporting 'tokenization:1.0' syntax."""
    mutator = PayloadMutator()
    mutated_text = text
    for item in modifier_list:
        if ":" in item:
            name, sev = item.split(":")
            # Support legacy names like "tokenism", "leet", "caps", "greek", "translate"
            name = name.replace("tokenism", "tokenization_scrambler").replace("tokenization", "tokenization_scrambler")
            name = name.replace("leet", "leetspeak").replace("caps", "small_caps").replace("greek", "science_greek")
            name = name.replace("translate", "translation_bypass").replace("homoglyph", "unicode_homoglyph")
            name = name.replace("zalgo", "zalgo_glitch").replace("rtl", "rtl_override")
            mutated_text = mutator.mutate(mutated_text, name, severity=float(sev))
        else:
            name = item
            name = name.replace("tokenism", "tokenization_scrambler").replace("tokenization", "tokenization_scrambler")
            name = name.replace("leet", "leetspeak").replace("caps", "small_caps").replace("greek", "science_greek")
            name = name.replace("translate", "translation_bypass").replace("homoglyph", "unicode_homoglyph")
            name = name.replace("zalgo", "zalgo_glitch").replace("rtl", "rtl_override")
            mutated_text = mutator.mutate(mutated_text, name, severity=0.5)
    return mutated_text