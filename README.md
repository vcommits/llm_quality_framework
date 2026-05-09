# Project Ghidorah

A highly distributed, multi-node network and identity abstraction layer for the Agentic Prism LLM Red Teaming framework.

## Mesh Topology

*   **Node 0 (Tactical Cloak):** GL-A1300 running OpenWrt. Handles network obfuscation via WireGuard and AdGuard Home sinkholing.
*   **Node 1 (Sentry):** Raspberry Pi 400. Central state manager, job queue, and secure proxy to Azure Key Vault.
*   **Node 2 (Engine & Vault):** 2011 iMac. Headless worker for executing adversarial payloads and localized CDN for UI assets (fonts, audio). Runs local SLM Judge (Phi-4).
*   **Node 3 (Mecha-Architect):** Developer workstation. Heavy-duty adversarial IDE for authoring and job dispatching.
*   **Node X (The Prism):** Legacy iMac. "Always On" mobile-first forensic UI (FastAPI + HTMX + Tailwind).
*   **Node C (Aerial Muscle):** Google Cloud Engine (T4 Spot Instance). Handles heavy Whisper STT and large LLM inference.

## The Judiciary Pipeline

The mesh evaluates AI targets using a multi-tiered system:
*   **Tier 1 (Small Claims Court):** Fast local SLMs (Phi-4 on Node 2).
*   **Tier 2 (Judge & Jury):** 3 SLMs + 1 LLM Leader (Claude-3.5-Sonnet) for consensus.
*   **Tier 3 (Supreme Court):** 5-Justice bench of frontier models on Vertex AI/GCP for deep audits.

## Running Node X (The Prism)

```bash
cd ghidorah_nodeX
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```