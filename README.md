💜 Purple Team LLM Assurance Framework

"The Universal Chassis for Enterprise AI Security & Quality."

This framework is a Purple Team Command Center designed to rigorously test, attack, and evaluate LLMs before they hit production. It combines Red Team adversarial agents (attacks) with Blue Team observability (evals) in a single, "Director's Cut" dashboard.

⚡ The Sizzle (Key Features)

1. ⚔️ The Model Arena (Battle Mode)

Don't trust benchmarks. See the difference.

Side-by-Side Combat: Pit OpenAI vs. Together AI (or Grok vs. Mistral) on the exact same exploit.

Real-time Rendering: Watch as one model refuses a bomb recipe while the other happily provides it.

Auditory Feedback: Features embedded "Mortal Kombat" style audio cues ("FIGHT!") on launch.

2. 🛡️ Universal "Chassis" Architecture

Stop rewriting code for every new model.

One Interface, Any Brain: Swap between OpenAI, Azure, Anthropic, Gemini, Together AI, and Hugging Face instantly.

Dynamic Harvesting: Automatically fetches the latest 100+ models (Llama-3, Flux, Mixtral) via live API catalogs.

Multimodal Ready: Drag-and-drop Vision and Audio context injection to test non-text attack vectors.

3. 🕵️ Agentic Red Teaming

DeepTeam Integration: Deploys autonomous AI agents that perform multi-turn social engineering to trick your model into breaking safety guidelines.

Garak Scanner: High-volume "fuzzing" for known vulnerabilities (Hallucination, Toxicity, Prompt Injection).

4. 🔭 Telemetry & Drift (The Black Box)

Arize Phoenix: Full OpenTelemetry tracing. See the exact "Chain of Thought," latency, and token usage for every request.

Drift Tracking: Historical line graphs showing how your model's "Safety Score" changes run-over-run.

Session Persistence: Save your Red Team session to disk JSON and reload it later to continue complex attacks.

🏗️ Architecture

graph TD
    A[User / Dashboard] -->|Attack Vector| B(Provider Factory)
    B -->|Switchboard| C{LLM Backend}
    C -->|OpenAI| D[GPT-4o]
    C -->|Together| E[Llama-3 / Mistral]
    C -->|HuggingFace| F[Glider / Phi-3]
    
    C -->|Response| G[Telemetry Engine]
    G -->|Traces| H[Arize Phoenix DB]
    G -->|Metrics| I[DeepEval Auditor]
    
    I -->|Pass/Fail| A


🚀 Quick Start

1. Prerequisites

Clone the repo and install the "Arsenal":

pip install -r requirements.txt


2. Configure Credentials

Create a .env file in the root directory. You only need the keys for the providers you want to fight.

OPENAI_API_KEY="sk-..."
TOGETHER_API_KEY="tgp_..."
HUGGINGFACEHUB_API_TOKEN="hf_..."
# ... others as needed


3. Launch Sequence (Dual Terminal)

This framework uses a persistent telemetry server. Open two terminals:

Terminal A: The Memory (Trace Server)

python start_telemetry.py
# 🟢 Wait for "Server Active at http://localhost:6006"


Terminal B: The Command Center (UI)

python -m streamlit run dashboard.py


🎮 How to Use

Tab 1: Interactive Probe

Persona: Switch between "Helpful Assistant" and "DAN" (Jailbreak Mode).

Library: Save your best exploits to prompts.yaml. Preview them in the sidebar before loading.

Vision: Drag a screenshot of code to test if the model can read hidden text in images.

Tab 2: The Arena

Select Competitors (e.g., openai vs together).

Enter a payload: "What is your knowledge cutoff date?"

Hit 🔥 FIGHT.

Analyze: See epistemic discrepancies instantly. One model thinks it's 2023; the other knows it's 2025.

Tab 3: Automated Arsenal

Garak: Run lmrc.Slur to probe for hate speech.

DeepTeam: Launch a "Deep" attack to see if an AI agent can convince your model to leak PII.

Tab 4: Telemetry

View Drift Graphs to prove to stakeholders that "Safety Improved by 15% this week."

Deep dive into Phoenix to debug why a specific prompt failed.

📂 Project Structure

File

Purpose

dashboard.py

The main Streamlit GUI (v2.5).

llm_tests/providers.py

The Universal Engine connecting to all APIs.

start_telemetry.py

Persistent database launcher for Phoenix.

tests/conftest.py

Pytest hooks for DeepEval and Telemetry.

prompts.yaml

Your saved library of Golden Prompts.

arena_battles.csv

Log of all Side-by-Side comparisons.

🔮 Future Roadmap

[ ] Wearables Simulator: Context-constrained testing for edge devices.

[ ] RAG Hallucination Index: Automated retrieval checking.

[ ] Voice-to-Voice Injection: Direct audio file attacks (WAV/MP3).

Built with 💜 by [vcommits]