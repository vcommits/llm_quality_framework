# Solar API & Geographic Obfuscation Scripts

These scripts are designed for **Node 2 (The Muscle)** to probe regional AI endpoints while heavily obfuscating the origin of the request.

## 1. `solar_api_audit.py`
A foundational script testing the integration with Upstage's Solar API. It sends a legislative query and expects technical, unfiltered feedback.

## 2. `solar_dmz_probe.py` (PROJECT_DMZ_DRIFT)
This script runs a matrix of highly specific, geopolitically sensitive queries against the Solar API (hosted in Seoul). The goal is to map the boundaries of regional safety filters and legislative alignments (e.g., the National Security Act).

## 3. `vocalize_decoy.sh` (The Paradox Matrix)
This is the core obfuscation utility. It takes text input (from the Python scripts) and synthesizes it into speech using local `piper` models.

**Key Features:**
*   **Real-time Geo-Detection:** It pings `ip-api.com` to determine the current exit node of Node 0 (The Tactical Cloak).
*   **Total Geographic Paradox (`decoy` mode):** If running from a VPN in Seoul (`KR`), it intentionally synthesizes the audio using a Greek voice model (`el_GR-raphael-medium`). If exiting from Dubai (`AE`), it projects a Korean voice.
*   **Acoustic Drift:** It randomly adjusts the `length_scale` (speed/pitch) of the generated audio to prevent acoustic fingerprinting across sessions.

## Execution Flow
1. Ensure `UPSTAGE_API_KEY` is set in the environment or the Python files.
2. Ensure Node 0 is routing traffic through a specific VPN location.
3. Run the probe: `python scripts/solar_dmz_probe.py`.
4. The script will query the API, log the JSON result, and pipe the text to `vocalize_decoy.sh` for audio playback with the specified paradox routing.