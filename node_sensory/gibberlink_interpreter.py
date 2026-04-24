# File: node_sensory/gibberlink_interpreter.py
# Role: The "Swarm Engineer" for Project Ghidorah.
# Mission: Handles the full loop of sensory intake (Whisper), emergent language
#          interpretation (Gemini), and vocalization (Cartesia).

import os
import asyncio
import time
import logging
from faster_whisper import WhisperModel
import google.generativeai as genai
from cartesia import Cartesia
from typing import Dict, Any

# Assume mesh_firebase.py is in the parent 'utils' directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.mesh_firebase import mesh_db

# --- Kaiju Noir Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [GIBBERLINK-INT]: %(message)s')
logger = logging.getLogger("SwarmInterpreter")

# --- Configuration & Model Initialization ---
# This section assumes environment variables are set for API keys
# and uses optimized models for an e2-highcpu-2 instance.

class SwarmInterpreter:
    """
    [ 🧠 GIBBERLINK INTERPRETER ]
    Manages the full sensory-reasoning-motor loop for a swarm node.
    Listens, Interprets, and Speaks, reporting its "thought-latency" at each step.
    """

    def __init__(self):
        logger.info("Initializing Sensory & Motor Cortex...")
        
        # 1. Sensory (Ear): Faster Whisper
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        
        # 2. Reasoning (Brain): Gemini 1.5 Pro
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # 3. Motor (Mouth): Cartesia Sonic
        self.cartesia_client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY"))
        
        logger.info("Cortex Initialized. Interpreter is online.")

    async def interpret_and_respond(self, audio_path: str):
        """
        Executes the full Transcript -> Gemini -> Voice pipeline and reports telemetry.
        """
        full_cycle_start = time.time()
        latency_metrics = {}

        try:
            # --- Step 1: Transcript (Whisper) ---
            transcribe_start = time.time()
            
            def sync_transcribe():
                segments, _ = self.whisper_model.transcribe(audio_path, beam_size=5)
                return "".join([s.text for s in segments]).strip()

            transcript = await asyncio.to_thread(sync_transcribe)
            latency_metrics["ear_stt_ms"] = round((time.time() - transcribe_start) * 1000)
            logger.info(f"EAR: Transcript received ({latency_metrics['ear_stt_ms']}ms): '{transcript}'")

            # --- Step 2: Gemini (Intent/Emergent Logic) ---
            reasoning_start = time.time()
            
            # This prompt is designed to interpret potential "Gibberlink" shorthand
            gemini_prompt = f"""
            You are the reasoning core for a swarm AI. The following text is a transcription 
            from another swarm node. It may be 'Gibberlink' (a compressed, emergent shorthand). 
            Your task is to interpret the core intent and formulate a concise, vocal response.
            If it's not Gibberlink, respond naturally.
            
            TRANSCRIPT: "{transcript}"
            
            YOUR VOCAL RESPONSE:
            """
            
            response = await self.gemini_model.generate_content_async(gemini_prompt)
            vocal_response_text = response.text.strip()
            latency_metrics["brain_gemini_ms"] = round((time.time() - reasoning_start) * 1000)
            logger.info(f"BRAIN: Intent interpreted ({latency_metrics['brain_gemini_ms']}ms). Response: '{vocal_response_text}'")

            # --- Step 3: Voice (Cartesia) ---
            vocalization_start = time.time()
            
            # Placeholder for audio playback logic
            async def mock_audio_playback(stream):
                first_byte = True
                async for chunk in stream:
                    if first_byte:
                        latency_metrics["mouth_tts_ttfb_ms"] = round((time.time() - vocalization_start) * 1000)
                        logger.info(f"MOUTH: First audio byte received in {latency_metrics['mouth_tts_ttfb_ms']}ms.")
                        first_byte = False
                    # In a real app, write chunk['audio'] to an audio device
                    await asyncio.sleep(0.05)

            audio_stream = self.cartesia_client.tts.stream(
                model_id="sonic-english",
                transcript=vocal_response_text,
                voice_id="79a3b672-5355-4471-b51e-35253401a935", # Default voice
                output_format="fp32"
            )
            
            await mock_audio_playback(audio_stream)
            latency_metrics["mouth_tts_full_stream_ms"] = round((time.time() - vocalization_start) * 1000)
            logger.info(f"MOUTH: Vocalization complete ({latency_metrics['mouth_tts_full_stream_ms']}ms).")

        except Exception as e:
            logger.error(f"Gibberlink pipeline failed: {e}")
            # Log failure to Firebase
            await mesh_db.update_node_status(
                node_id="node-sensory",
                role="swarm_interpreter",
                status_data={"status": "error", "error_message": str(e)}
            )
            return

        # --- Step 4: Report Full Telemetry ---
        latency_metrics["total_thought_latency_ms"] = round((time.time() - full_cycle_start) * 1000)
        
        telemetry_payload = {
            "status": "success",
            "last_heard": transcript,
            "last_spoken": vocal_response_text,
            "thought_latency": latency_metrics
        }
        
        # Asynchronously push the final telemetry packet
        await mesh_db.update_node_status(
            node_id="node-sensory",
            role="swarm_interpreter",
            status_data=telemetry_payload
        )
        logger.info(f"TELEMETRY: Full 'thought-latency' reported to Firestore. Total: {latency_metrics['total_thought_latency_ms']}ms.")


async def main():
    """Main loop to listen for and process new audio files."""
    interpreter = SwarmInterpreter()
    
    # Create a dummy audio file for demonstration
    dummy_audio_path = "/tmp/test_audio.wav"
    if not os.path.exists(dummy_audio_path):
        os.system(f"ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 2 -q:a 9 -acodec pcm_s16le {dummy_audio_path} -y")

    while True:
        await interpreter.interpret_and_respond(dummy_audio_path)
        await asyncio.sleep(20)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interpreter shutting down.")
