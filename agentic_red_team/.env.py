import os

# -----------------------------------------------------------------------------
# SAFE CONFIG: LOADS FROM ENVIRONMENT VARIABLES
# DO NOT PASTE REAL KEYS HERE. USE A SEPARATE .ENV FILE.
# -----------------------------------------------------------------------------

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHERAI_API_KEY = os.getenv("TOGETHERAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")