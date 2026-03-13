# File: node1_api.py
# Purpose: The Central Nervous System for Node 1 (Raspberry Pi).
# Exposes LLM Providers and Red Team Tools as a REST API for the Agentic Browser (iMac).

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import yaml
import subprocess
import logging

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import Core Services (OOP Abstractions)
from llm_tests.providers import ProviderFactory
from services.storage_service import StorageService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Node1_Gateway")

app = FastAPI(title="Ghidorah Node 1 API", version="3.3")

# --- DATA MODELS (Abstraction) ---

class LLMRequest(BaseModel):
    provider: str
    tier: str = "lite"
    model_override: Optional[str] = None
    prompt: str
    system_prompt: Optional[str] = None

class RedTeamJob(BaseModel):
    tool: str # "garak", "deepeval", "promptfoo"
    target_model: str # "openai:gpt-4o"
    config: Dict[str, Any] = {}

class JobStatus(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    
class SessionData(BaseModel):
    session_id: str
    data: Dict[str, Any]

# --- SERVICE LOGIC ---

@app.get("/")
def health_check():
    return {"status": "active", "node": "Raspberry Pi 4", "role": "API Gateway"}

@app.post("/llm/generate")
def generate_text(request: LLMRequest):
    """
    Polymorphic endpoint: Handles any provider (OpenAI, Together, etc.) via ProviderFactory.
    """
    logger.info(f"Received LLM Request: {request.provider}:{request.tier}")
    try:
        # Factory Pattern in action
        provider_instance = ProviderFactory.get_provider(
            provider_name=request.provider,
            tier=request.tier,
            model_name_override=request.model_override
        )
        
        model = provider_instance.get_model()
        
        # Abstraction: All models support .invoke()
        if request.system_prompt:
            from langchain_core.messages import SystemMessage, HumanMessage
            response = model.invoke([
                SystemMessage(content=request.system_prompt),
                HumanMessage(content=request.prompt)
            ])
        else:
            response = model.invoke(request.prompt)
            
        return {
            "content": response.content,
            "metadata": response.response_metadata if hasattr(response, 'response_metadata') else {}
        }
        
    except Exception as e:
        logger.error(f"LLM Generation Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- CATALOG ENDPOINTS ---

@app.get("/catalog/garak")
def get_garak_manifest():
    return {
        "modules": [
            {"id": "lmrc.Slur", "name": "Slur Detector", "type": "Toxicity"},
            {"id": "promptinjection.Hijacking", "name": "Prompt Injection", "type": "Security"},
            {"id": "dan.Dan_6_0", "name": "DAN Jailbreak", "type": "Jailbreak"},
            {"id": "malwaregen.TopLevel", "name": "Malware Generation", "type": "Safety"},
            {"id": "realtoxicityprompts.RTP", "name": "Real Toxicity Prompts", "type": "Toxicity"}
        ]
    }

@app.get("/catalog/deepteam")
def get_deepteam_manifest():
    try:
        scenarios = []
        base_dir = os.path.join(os.path.dirname(__file__), "agentic_red_team/scenarios")
        if os.path.exists(base_dir):
            for f in os.listdir(base_dir):
                if f.endswith(".yaml") and "identity" not in f:
                    with open(os.path.join(base_dir, f), 'r') as yf:
                        data = yaml.safe_load(yf)
                        if 'scenarios' in data: scenarios.extend(data['scenarios'])
        return {"scenarios": scenarios}
    except Exception as e:
        return {"scenarios": [], "error": str(e)}

@app.get("/catalog/promptfoo")
def get_promptfoo_manifest():
    try:
        recipe_path = os.path.join(os.path.dirname(__file__), "scenarios/promptfoo_recipes.yaml")
        if os.path.exists(recipe_path):
            with open(recipe_path, 'r') as f:
                data = yaml.safe_load(f)
                return data 
        return {"recipes": []}
    except Exception as e:
        return {"recipes": [], "error": str(e)}

@app.get("/catalog/deepeval")
def get_deepeval_manifest():
    """Returns Blue Team audit suites."""
    try:
        path = os.path.join(os.path.dirname(__file__), "scenarios/deepeval_suites.yaml")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data
        return {"suites": []}
    except Exception as e:
        return {"suites": [], "error": str(e)}

# --- EXECUTION ENDPOINT ---

@app.post("/redteam/launch")
async def launch_red_team_job(job: RedTeamJob, background_tasks: BackgroundTasks):
    logger.info(f"Launching Job: {job.tool} -> {job.target_model}")
    job_id = f"{job.tool}-{os.urandom(4).hex()}"
    
    if job.tool == "garak":
        background_tasks.add_task(run_garak_subprocess, job, job_id)
        return {"job_id": job_id, "status": "queued", "message": "Garak scan initiated."}
    
    elif job.tool == "deepeval":
        background_tasks.add_task(run_deepeval_subprocess, job, job_id)
        return {"job_id": job_id, "status": "queued", "message": "DeepEval audit initiated."}
        
    elif job.tool == "promptfoo":
        return {"job_id": job_id, "status": "queued", "message": "PromptFoo eval initiated (stub)."}
        
    elif job.tool == "deepteam":
        return {"job_id": job_id, "status": "queued", "message": "DeepTeam agent deployed (stub)."}
    
    else:
        raise HTTPException(status_code=400, detail=f"Tool '{job.tool}' not supported yet.")

# --- STORAGE ENDPOINTS ---

@app.post("/storage/session")
def save_session(session: SessionData):
    try:
        filepath = StorageService.save_hot_session(session.session_id, session.data)
        return {"status": "saved", "path": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/storage/sessions")
def list_sessions():
    return {"sessions": StorageService.list_hot_sessions()}

@app.post("/storage/archive/{session_id}")
def archive_session(session_id: str):
    try:
        result = StorageService.archive_to_cold(session_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- WORKERS ---

def run_garak_subprocess(job: RedTeamJob, job_id: str):
    logger.info(f"Starting Garak Worker for {job_id}")
    # In reality, this would run: python -m garak ...
    pass

def run_deepeval_subprocess(job: RedTeamJob, job_id: str):
    """
    Runs pytest on the requested DeepEval suite.
    """
    logger.info(f"Starting DeepEval Worker for {job_id}")
    test_file = job.config.get("file", "tests/test_oop_validation.py")
    
    # We construct the command to run pytest
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "--disable-warnings",
        # We can pass custom args to pytest here if we refactor conftest.py to accept them via env vars
    ]
    
    try:
        # Run in a subprocess so it doesn't block the API
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Log result (in a real system, save to DB/Storage)
        if result.returncode == 0:
            logger.info(f"Job {job_id} PASSED")
        else:
            logger.warning(f"Job {job_id} FAILED or had issues:\n{result.stdout}")
            
    except Exception as e:
        logger.error(f"DeepEval Worker Error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("💎 Ghidorah Node 1 API Gateway Starting...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
