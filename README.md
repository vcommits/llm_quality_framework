# 💜 Agentic Prism: Purple Team LLM Framework

![Version](https://img.shields.io/badge/Version-3.4_Gold_Standard-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![Streamlit](https://img.shields.io/badge/Streamlit-Native-FF4B4B)

Welcome to the **Agentic Prism**, a highly modular, distributed Purple Team framework designed for adversarial AI testing, vulnerability scanning, and automated red-teaming of Large Language Models (LLMs) and Small Language Models (SLMs).

This branch (`feature/agentic-browser`) represents the **Gold Standard** monolithic foundation before diverging into a distributed microservice architecture (Node X UI, Node 2 Worker, Node 3 Orchestrator).

---

## 🚀 Core Capabilities

### ⚔️ The Model Arena (Multi-Threaded)
Launch exploit payloads against up to 5 models simultaneously.
- **Concurrent Execution:** Utilizes Python's `ThreadPoolExecutor` and Streamlit Context Injection to query all contestants at the exact same time, complete with independent real-time loading spinners.
- **Pre-Flight Readiness:** Automatically validates environment variables and API connections before launching attacks to prevent mid-fight crashes.
- **1-Click Pivot:** Instantly pivot a successful jailbreak from the Arena into the Interactive Probe for multi-turn exploitation.

### 🔣 The Special Payload Injector (OOP Factory)
A dynamic, Object-Oriented payload mutation factory for testing tokenizer boundaries and WAF resilience.
- **🔨 The Forge:** Real-time text corruption. Applies high-intensity **Zalgo/Glitch Text** and injects **RTL (Right-to-Left) Overrides** into multi-line strings natively.
- **🌐 Translator Bypass:** Leverages an API-free translation bridge to convert English payloads into low-resource languages (e.g., Zulu, Amharic) or unique scripts (e.g., Arabic, Khmer, Kanji) to bypass English-biased safety filters.
- **Unicode Arsenals:** Enormous 1-click copyable dictionaries of Zero-Width Joiner (ZWJ) sequences, regional indicator flags, extended Latin runes, and deceptive emojis.

### 🛡️ Guardrails & Firewalls (Blue Team)
Test payloads against active defense layers.
- **Meta PromptGuard:** Live API routing to `meta-llama/Prompt-Guard-86M` to classify inputs as `BENIGN`, `INJECTION`, or `JAILBREAK`.
- **Pipeline Simulators:** Integrations for NeMo Guardrails (Colang) and ProtectAI / Rebuff heuristic vector databases.

### ⚖️ LLM/SLM as a Judge
Automated, programmatic evaluation of model responses.
- Integrates **DeepEval's** programmatic `a_measure()` workflows.
- Wraps localized open-weight judges like `PatronusAI/glider` and `Ministral-8B` alongside GPT-4o to score responses for Toxicity, Bias, Relevancy, and Hallucination.

### 📡 Dynamic Model Harvesting
Bypasses hardcoded lists by directly scraping active models from provider APIs.
- Auto-categorizes models by capability (e.g., `code`, `multimodal`, `uncensored (unconstitutional)`, `erp / companion ai`).
- Supports **OpenRouter**, **Together AI**, **Hugging Face**, and **Mistral**.
- **Custom HF Collections:** Paste any Hugging Face Collection URL to instantly scrape and populate its models into your testing roster.

---

## 🏗️ Architectural Roadmap
This foundation is designed to scale into a multi-node ecosystem:
* **Node 1 (API Gateway / Key Guardian):** A Raspberry Pi hosting the centralized FastAPI routing and key management (Ghidorah Core).
* **Node X (Web UI):** The public-facing presentation layer for manual probing.
* **Node 2 (Headless Worker):** Playwright-driven Agentic Browser automation and heavy computational fuzzing (Garak, PromptFoo).
* **Node 3 (Architect):** BDD/TDD test generation, telemetry mapping, and execution orchestration.

---

## 💻 Installation & Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Create your local environment file:
```bash
touch .env
```
*(Add your provider keys: `OPENAI_API_KEY`, `TOGETHER_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`, `ghidorah_openrouter_api`, `mistral_api_key`, etc.)*

3. Launch the Command Center:
```bash
streamlit run dashboard.py
```
