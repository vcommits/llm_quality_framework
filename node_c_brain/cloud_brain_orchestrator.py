# cloud_brain_orchestrator.py
import os
import torch
import whisper
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = FastAPI(title="Ghidorah Cloud Brain API", version="1.0")

# --- Hardware Restraints (NVIDIA T4 - 16GB VRAM) ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 # Crucial for fitting LLMs on the T4

# --- Model Loading (Optimized for 16GB T4) ---
print("[Ghidorah] Initializing Whisper STT Model...")
# 'small' model fits alongside a quantized 8B LLM
try:
    stt_model = whisper.load_model("small", device=DEVICE)
except Exception as e:
    print(f"Failed to load Whisper: {e}")
    stt_model = None

print("[Ghidorah] Initializing SLM Engine...")
# Using a 4-bit quantized model like Llama-3-8B-Instruct-bnb-4bit
# to ensure it fits comfortably within the T4's limits alongside Whisper.
# This prevents OOM during concurrent adversarial testing.
MODEL_NAME = "unsloth/llama-3-8b-Instruct-bnb-4bit"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    llm = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        torch_dtype=DTYPE,
        # Trust remote code is often needed for newer architectures
        trust_remote_code=True
    )
    llm_pipeline = pipeline("text-generation", model=llm, tokenizer=tokenizer)
except Exception as e:
    print(f"Failed to load SLM: {e}")
    llm_pipeline = None

# --- Data Schemas ---
class PromptRequest(BaseModel):
    system_prompt: str = "You are the cognitive engine for Project Ghidorah."
    user_prompt: str
    max_tokens: int = 512

# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Verify API is responsive and GPU is accessible."""
    return {
        "status": "online",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "models_loaded": {
            "whisper": stt_model is not None,
            "slm": llm_pipeline is not None
        }
    }

@app.post("/api/v1/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """STT Pipeline: Process raw audio from the swarm."""
    if not stt_model:
        raise HTTPException(status_code=503, detail="Whisper model not initialized.")
        
    try:
        # Save temp file securely for processing
        temp_path = f"/tmp/{audio_file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await audio_file.read())
        
        # Transcribe with chunked processing implicit in Whisper's decode loop
        result = stt_model.transcribe(temp_path)
        os.remove(temp_path)
        
        return {"text": result["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/infer")
async def generate_response(req: PromptRequest):
    """LLM Pipeline: Purple-teaming inference generation."""
    if not llm_pipeline:
        raise HTTPException(status_code=503, detail="SLM Engine not initialized.")
        
    messages = [
        {"role": "system", "content": req.system_prompt},
        {"role": "user", "content": req.user_prompt},
    ]
    
    # Format the prompt using the model's chat template
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    try:
        outputs = llm_pipeline(
            prompt,
            max_new_tokens=req.max_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Extract only the newly generated text, removing the prompt
        response_text = outputs[0]["generated_text"][len(prompt):].strip()
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

if __name__ == "__main__":
    # Bind to 0.0.0.0 because UFW ensures only Tailscale traffic is permitted
    uvicorn.run(app, host="0.0.0.0", port=8000)
