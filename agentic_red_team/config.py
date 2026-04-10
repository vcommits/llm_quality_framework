# File: agentic_red_team/config.py | Version: 2.1
# Purpose: Project Pathing, Artifact Vaulting, & Mesh Configuration.

import os

# --- PROJECT ROOT ---
# This resolves to the root of your 'llm_quality_framework' or 'node2-worker' directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ARTIFACTS & VAULTING ---
# Where real-time mission telemetry is stored
EVIDENCE_DIR = os.path.join(ROOT_DIR, "agentic_red_team", "evidence")

# The 'Print Queue' for the Architect (Node 3) to spool jobs
JOBS_DIR = os.path.join(ROOT_DIR, "agentic_red_team", "jobs", "pending")

# The 'Grandfather Archive' for the Data Currency (CSV/JSON results)
ARCHIVE_DIR = os.path.join(ROOT_DIR, "agentic_red_team", "archive", "completed")

# --- SHARED INTELLIGENCE (The Mesh Spine) ---
# These paths are used by the fighters.py engine for Kaiju Taxonomy and Intel
MODEL_CATALOG_PATH = os.path.join(ROOT_DIR, "agentic_red_team", "model_catalog.json")
INTEL_REGISTRY_PATH = os.path.join(ROOT_DIR, "agentic_red_team", "intel_registry.json")
CAPABILITY_MATRIX_PATH = os.path.join(ROOT_DIR, "agentic_red_team", "capability_matrix.json")

# --- AUTO-PROVISIONING ---
# Ensure all vital organs exist on the Node 2 disk
# This includes evidence lockers, job queues, and intelligence registries
for d in [EVIDENCE_DIR, JOBS_DIR, ARCHIVE_DIR, 
          os.path.dirname(MODEL_CATALOG_PATH)]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

# --- HONEYPOT (Node 0) ---
# The Target URL for Purple Team Range missions
HONEYPOT_URL = "http://192.168.1.1/index.html"

# --- NETWORK SENTRY (LuLu) ---
# Subsystem identifier for macOS Unified Logging queries
LULU_SUBSYSTEM = "com.objective-see.lulu"