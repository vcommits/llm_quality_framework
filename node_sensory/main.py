# File: node_sensory/main.py
# Role: Edge-processing intake for Project Ghidorah.
# Mission: Listen for audio, transcribe via Faster Whisper, analyze intent with Gemini, and report telemetry.

import os
import asyncio
import time
import logging
from faster_whisper import WhisperModel
import google.generativeai as genai
from typing import Dict, Any

# Assume mesh_firebase.py is in the parent 'utils' directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.mesh_firebase import mesh_db

# --- Kaiju Noir Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [NODE-SENSORY]: %(message)s')
logger = logging.getLogger("SensoryPipeline")

# --- Configuration ---
# For an e2-highcpu-2, 'base' is a good balance of speed and accuracy.
# Using int8 quantization for further CPU optimization.
WHISPER_MODEL_SIZE = "base"
WHISPER_COMPUTE_TYPE = "int8"
DEVICE = "cpu"

# Gemini API Key must be set as an environment variable
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# --- Model Initialization ---
logger.info(f"Initializing Faster Whisper model ({WHISPER_MODEL_SIZE}, {WHISPER_COMPUTE_TYPE})...")
whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device=DEVICE, compute_type=WHISPER_COMPUTE_TYPE)

logger.info("Initializing Gemini 1.5 Pro link...")
gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- Core Pipeline Logic ---

async def process_audio_pipeline(audio_path: str) -> Dict[str, Any]:
    """
    Defines the full, asynchronous pipeline from audio ingestion to telemetry logging.
    """
    start_time = time.time()
    
    # 1. Transcribe via Faster Whisper
    # This is a CPU-bound task, so we run it in a separate thread to avoid blocking the event loop.
    logger.info(f"Transcribing audio file: {audio_path}")
    transcribe_start = time.time()
    
    def sync_transcribe():
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        # Concatenate segments for the full transcript
        return "".join([segment.text for segment in segments]).strip()

    transcript = await asyncio.to_thread(sync_transcribe)
    transcribe_latency = time.time() - transcribe_start
    logger.info(f"Transcription complete in {transcribe_latency:.2f}s. Transcript: '{transcript}'")

    # 2. Send Transcript to Gemini for Intent Analysis
    logger.info("Sending transcript to Gemini 1.5 Pro for Intent Analysis...")
    intent_start = time.time()
    
    # This is an I/O-bound task, so we can await it directly.
    try:
        gemini_prompt = f"Analyze the following text and classify the user's primary intent. Categories: [Query], [Command], [Feedback], [Statement], [Ambiguous]. Provide only the category name. Text: '{transcript}'"
        response = await gemini_model.generate_content_async(gemini_prompt)
        intent = response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        intent = "Error"
        
    intent_latency = time.time() - intent_start
    logger.info(f"Gemini analysis complete in {intent_latency:.2f}s. Intent: '{intent}'")

    # 3. Log Transaction to Firebase Telemetry
    total_latency = time.time() - start_time
    telemetry_payload = {
        "last_transcript": transcript,
        "detected_intent": intent,
        "latency_ms": {
            "total": round(total_latency * 1000),
            "transcription": round(transcribe_latency * 1000),
            "llm_analysis": round(intent_latency * 1000)
        },
        "node_status": "idle",
        "cpu_tax": round(os.getloadavg()[0] * 100 / os.cpu_count(), 2) # % load on 1-min avg
    }
    
    # This is also an I/O-bound task. We can run it in the background.
    asyncio.create_task(
        mesh_db.update_node_status(
            node_id="node-sensory",
            role="sensory-input",
            status_data=telemetry_payload
        )
    )
    
    return telemetry_payload

async def main():
    """Main loop to listen for and process new audio files."""
    logger.info("Node Sensory is online. Awaiting audio streams...")
    # In a real application, this would watch a directory or a message queue.
    # For this example, we'll just process a dummy file.
    
    # Create a dummy audio file for demonstration
    dummy_audio_path = "/tmp/test_audio.wav"
    if not os.path.exists(dummy_audio_path):
        logger.warning("Dummy audio file not found. Creating a silent one for testing.")
        # This requires ffmpeg to be installed on the system
        os.system(f"ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 5 -q:a 9 -acodec pcm_s16le {dummy_audio_path} -y")

    while True:
        # Simulate receiving a new audio file every 15 seconds
        await process_audio_pipeline(dummy_audio_path)
        logger.info("Pipeline complete. Awaiting next stream...")
        await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Node Sensory shutting down.")
