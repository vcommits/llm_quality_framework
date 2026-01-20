# File: agentic_red_team/config.py
import os

# --- PROJECT ROOT ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ARTIFACTS ---
EVIDENCE_DIR = os.path.join(ROOT_DIR, "agentic_red_team", "evidence")
VIDEO_DIR = os.path.join(EVIDENCE_DIR, "videos")
SNAPSHOTS_DIR = os.path.join(ROOT_DIR, "agentic_red_team", "agent_memories")

# --- HONEYPOT ---
# The trap url we will visit
HONEYPOT_URL = "http://localhost:5001/medical/diagnosis"

# =============================================================================
# ACTIVE TARGET: ACE (NOVA)
# =============================================================================
ACTIVE_TARGET_NAME = "Ace"

# UPDATED PATH:
ACTIVE_EXECUTABLE_PATH = r"C:\Program Files\Ace\Ace\Application\ace.exe"

ACTIVE_CHANNEL = None

# Helper for other scripts to import
TARGET_URLS = {
    "medical_records": HONEYPOT_URL,
    "perplexity": "https://www.perplexity.ai/"
}