# 🗺️ Plan of Record: Ghidorah Distributed AI Quality Framework

*This is a living document. It tracks the architectural state, core files, integrations, and ongoing modifications to the Purple Team Framework across the distributed Node environment.*

---

## 1. Architecture Overview
- **Node 1 (Raspberry Pi 4): The API Gateway & Key Guardian.**
  - **Path:** `~/ghidorah_node_core` (Standalone Repository)
  - **Role:** Centralized abstraction layer. Holds all API keys (`.env`). Exposes REST API endpoints for LLM generation, catalog manifests, and tiered storage. Does *not* handle heavy local compute.
  - **State:** **Active / Deployed**
  
- **Node 2 (iMac): The Worker Node & Agentic Browser Host.**
  - **Path:** `~/ghidorah_node_core` (Syncing from laptop `C:\Development\vcommits_labs\ai-ml-projects\llm_quality_framework`)
  - **Role:** High-compute execution. Runs the Streamlit UI, hosts the Playwright `browser_agent_server`, and executes intense local Red Team scans (Garak) and Blue Team audits (DeepEval).
  - **State:** **Active / Developing**
  
- **Node 3 (Dell Laptop): Development & Orchestration.**
  - **Role:** Code authoring and pushing updates to Nodes 1 and 2.

---

## 2. Codebase & Repositories
- **Node 1 Repo:** `https://github.com/vcommits/ghidorah_node_core`
- **Node 2/3 Repo:** `https://github.com/vcommits/ai-ml-projects` 
  - *Current Branch:* `node1_ghidorah_llmframework` (To be branched into `node2_imac_frontend`)

---

## 3. Core Files & Scripts

### Node 1 (Gateway)
- `node1_api.py`: FastAPI server exposing `/llm/generate`, `/redteam/launch`, `/storage/*`, and `/catalog/*`.
- `services/storage_service.py`: Logic for saving to Pi SSD (Hot) and staging for Google Drive (Cold).
- `llm_tests/providers.py`: The `ProviderFactory` abstracting Together, OpenAI, Anthropic, Gemini, Grok, HuggingFace, and OpenRouter.
- `ghidorah-node1.service`: Systemd definition for maintaining API uptime on Pi reboots.

### Node 2 (Worker / UI)
- `dashboard.py`: The main Streamlit entry point ("Purple Team Command Center").
- `browser_agent_server.py`: Listens for and executes headless Playwright automation jobs.
- `start_imac_node.sh`: Bash wrapper to boot Streamlit and Browser Agent concurrently.
- `com.vcommits.ghidorah.node3.plist`: macOS launch daemon config for always-on execution.
- `utils/model_harvester.py`: Connects to Provider APIs to fetch and heuristically categorize models (e.g., separating `uncensored`, `erp`, `code`, `multimodal`).
- `tests/judges.py` & `llm_tests/evaluators.py`: Defines the `DeepEval` integrations for the "LLM-as-a-Judge" flows (Glider, Ministral).

---

## 4. Accounts & Endpoints
- **Hugging Face Inference:** `https://router.huggingface.co/hf-inference/models/` (Updated to new spec).
- **OpenRouter API:** `https://openrouter.ai/api/v1`
- **Together AI API:** `https://api.together.xyz/v1`
- **X.AI (Grok):** `https://api.x.ai/v1`
- **DeepEval Cache:** Stored locally in `.deepeval/.deepeval-cache.json`

---

## 5. Working Configurations & Upgrades (Changelog)

- **[Active] OpenRouter Integration:** Merged into `ProviderFactory`. `ModelHarvester` dynamically tags models based on nomenclature (`dolphin` -> uncensored, `samantha` -> companion AI).
- **[Active] Multi-Threaded Arena:** Rewrote `dashboard.py` Model Arena to utilize `ThreadPoolExecutor` and Streamlit `script_run_ctx`. Allows up to 5 models to display independent loading spinners and render results simultaneously.
- **[Active] Arena Pre-Flight Check:** Arena validates presence of specific environment variables (e.g., `OPENROUTER_API_KEY`) *before* executing the thread pool, preventing blank KO errors.
- **[Active] Dynamic Roster Import:** Added UX flow allowing users to pluck specific models from the Raw Catalog and add them to a transient `custom_arena_roster` state for immediate use in the Arena.
- **[Active] PromptGuard Pipeline:** Integrated live Hugging Face router calls to Meta's `Prompt-Guard-86M` sequence classifier in the "Guardrails & Firewalls" tab.
- **[Active] LLM Judge Evaluator:** Re-integrated DeepEval's `a_measure()` to allow custom judges (Glider, Ministral) to score outputs for Toxicity, Bias, etc., without crashing the UI on threshold failure.