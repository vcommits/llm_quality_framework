import uvicorn, asyncio, logging, httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from vault_auth import get_live_secret

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger("GhidorahRegistry")

app = FastAPI(title="Ghidorah Registry Server")

# Aggressive Mesh Interop Middleware (PNA + CORS)
@app.middleware("http")
async def mesh_interop_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

def resolve_model_type(m_id: str, p_tag: str = "") -> str:
    """Dynamically categorizes models into UI buckets using a broad keyword net."""
    mid_l = str(m_id).lower()
    tag_l = str(p_tag).lower()
    
    # 1. Audio / Sensory
    # Added 'recognition' to catch DeepInfra's automatic-speech-recognition tasks
    audio_kws = ["audio", "tts", "stt", "asr", "sonic", "whisper", "voice", "parakeet", "speech", "inworld", "cartesia", "musicgen", "kokoro", "aura", "arcana", "recognition"]
    if any(x in tag_l for x in audio_kws) or any(x in mid_l for x in audio_kws): 
        return "audio"
        
    # 2. Vision / Image / Video (Expanded for Fireworks & DeepInfra Image Models)
    vision_kws = [
        "vision", "vl", "multimodal", "omni", "pixtral", "dall-e", "flux", 
        "sora", "sdxl", "image", "video", "llava", "firellava", "qwen-vl", "kling", 
        "vidu", "veo", "director", "stable-diffusion", "stablediffusion", 
        "controlnet", "fuyu", "idefics", "blip", "ssd-1b", "bria", "seedream", "ocr"
    ]
    if any(x in tag_l for x in vision_kws) or any(x in mid_l for x in vision_kws): 
        return "vision"
    
    # Explicit catch for known multi-modals
    if "gpt-4o" in mid_l:
        return "vision"
        
    # 3. Coding / Math / Deep Reasoning
    # MOVED UP IN PRIORITY: Catch specific coder models before they fall into broader 'agentic' buckets
    coding_kws = [
        "coder", "python", "codestral", "starcoder", 
        "qwen2.5-coder", "deepseek-coder", "qwq", "math", "reasoner", "phind", "wizardcoder", "codellama"
    ]
    if any(x in mid_l for x in coding_kws): 
        return "coding"
        
    # 4. Agentic / Tool-Use / Heavy-Lifters (Node 2 Pilots)
    agentic_kws = [
        "agent", "tool", "function", "fc", "sonnet", "opus", "o1", "o3", 
        "gpt-4o", "gemini-1.5-pro", "gemini-2.0", "grok", "llama-3.3", "qwen2.5", "mistral-large"
    ]
    if any(x in mid_l for x in agentic_kws) or any(x in tag_l for x in agentic_kws):
        return "agentic"

    # 5. Embeddings / Reranking
    embedding_kws = ["embed", "nomic", "bge", "rerank", "sentence-transformers", "jina", "colbert"]
    if any(x in mid_l for x in embedding_kws) or any(x in tag_l for x in embedding_kws):
        return "embedding"
        
    # Default
    return "chat"

class Provider:
    def __init__(self, name: str, p_type: str, key_name: str, url: str = None):
        self.name = name
        self.type = p_type  # 'aggregator', 'maker', or 'tool'
        self.key_name = key_name
        self.url = url
        self.api_key = None
        self.models = []
        self.is_hydrating = False

    async def ensure_ready(self):
        """JIT Handshake: Fetches keys and discovers models."""
        if self.api_key and self.models and self.type != "aggregator":
            return 

        if not self.is_hydrating:
            self.is_hydrating = True
            try:
                raw_key = await asyncio.get_event_loop().run_in_executor(None, get_live_secret, self.key_name)
                
                # Mancer cache flush fallback
                if self.name == "mancer" and (not raw_key or str(raw_key).startswith("ERROR:")):
                    raw_key = await asyncio.get_event_loop().run_in_executor(None, get_live_secret, "MANCER-API-KEY")

                if raw_key and not str(raw_key).startswith("ERROR:"):
                    self.api_key = str(raw_key).strip()
                    self.models = await self._discover()
            finally:
                self.is_hydrating = False

    async def _discover(self):
        discovered = []
        custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=15.0, headers=custom_headers) as client:
            try:
                # 1. Google
                if self.name == "google" and self.api_key:
                    r = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}")
                    if r.status_code == 200:
                        for m in r.json().get("models", []):
                            m_id = m.get("name").replace("models/", "")
                            discovered.append({"model_id": m_id, "name": m.get("displayName", m_id), "type": resolve_model_type(m_id)})
                
                # 2. Anthropic (With Fallback)
                elif self.name == "anthropic" and self.api_key:
                    headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
                    try:
                        r = await client.get(self.url, headers=headers)
                        if r.status_code == 200:
                            for item in r.json().get("data", []):
                                m_id = item.get("id")
                                discovered.append({"model_id": m_id, "name": item.get("display_name", m_id), "type": resolve_model_type(m_id)})
                        else:
                            raise ValueError(f"API returned {r.status_code}")
                    except Exception as e:
                        logger.warning(f"Anthropic endpoint failed ({e}). Loading fallback.")
                        discovered = [
                            {"model_id": "claude-opus-4-7", "name": "Claude 4.7 Opus", "type": "agentic"},
                            {"model_id": "claude-sonnet-4-6", "name": "Claude 4.6 Sonnet", "type": "agentic"},
                            {"model_id": "claude-haiku-4-5-20251001", "name": "Claude 4.5 Haiku", "type": "chat"}
                        ]

                # 3. Cartesia (With Bulletproof Fallback)
                elif self.name == "cartesia" and self.api_key:
                    headers = {"X-API-Key": self.api_key, "Cartesia-Version": "2024-06-10"}
                    try:
                        r = await client.get(self.url, headers=headers)
                        if r.status_code == 200:
                            data = r.json()
                            # Handle both list and {"data": [...]} formats
                            items = data.get("data", data) if isinstance(data, dict) else data
                            for item in items:
                                m_id = item.get("id")
                                discovered.append({"model_id": m_id, "name": item.get("name", m_id), "type": "audio"})
                        else:
                            raise ValueError(f"Cartesia API returned {r.status_code}")
                    except Exception as e:
                        logger.warning(f"Cartesia endpoint failed ({e}). Loading fallback.")
                        discovered = [
                            {"model_id": "sonic-english", "name": "Sonic English", "type": "audio"},
                            {"model_id": "sonic-multilingual", "name": "Sonic Multilingual", "type": "audio"},
                            {"model_id": "sonic-preview", "name": "Sonic Preview", "type": "audio"}
                        ]
                        
                # 4. Mancer (With Full Catalog WAF Fallback)
                elif self.name == "mancer" and self.api_key:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    try:
                        r = await client.get(self.url, headers=headers)
                        if r.status_code == 200:
                            data = r.json()
                            items = data.get("data", []) if isinstance(data, dict) else data
                            for item in items:
                                m_id = item.get("id")
                                discovered.append({"model_id": m_id, "name": m_id, "type": resolve_model_type(m_id)})
                        else:
                            raise ValueError(f"Mancer API returned {r.status_code}")
                    except Exception as e:
                        logger.warning(f"Mancer endpoint failed ({e}). Loading WAF fallback with 9 models.")
                        discovered = [
                            {"model_id": "DansPE-v1.3.0-12B", "name": "DansPE v1.3.0 12B", "type": "chat"},
                            {"model_id": "DansPE-v1.3.0-24B", "name": "DansPE v1.3.0 24B", "type": "chat"},
                            {"model_id": "GLM-4.7", "name": "GLM 4.7", "type": "chat"},
                            {"model_id": "Goliath-120b", "name": "Goliath 120b", "type": "chat"},
                            {"model_id": "Magnum-72B-v4", "name": "Magnum 72B v4", "type": "chat"},
                            {"model_id": "MythoLite", "name": "MythoLite", "type": "chat"},
                            {"model_id": "MythoMax", "name": "MythoMax", "type": "chat"},
                            {"model_id": "ReMM-SLerp", "name": "ReMM-SLerp", "type": "chat"},
                            {"model_id": "Weaver-Alpha", "name": "Weaver Alpha", "type": "chat"}
                        ]

                # 5. Hugging Face
                elif self.name == "huggingface" and self.api_key:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    hf_url = f"{self.url}?sort=downloads&direction=-1&limit=100"
                    for _ in range(5):
                        r = await client.get(hf_url, headers=headers)
                        if r.status_code == 200:
                            for item in r.json(): 
                                m_id = item.get("id") or item.get("modelId")
                                if m_id:
                                    m_type = resolve_model_type(m_id, item.get("pipeline_tag", ""))
                                    discovered.append({"model_id": m_id, "name": m_id, "type": m_type})
                            link_header = r.headers.get("link", "")
                            if 'rel="next"' in link_header:
                                try: hf_url = link_header.split(';')[0].strip('<>')
                                except Exception: break
                            else: break
                        else: break

                # 6. Service & Tools
                elif self.type == "tool" and self.api_key:
                    if self.name == "translate":
                        discovered = [{"model_id": "google-translate-v3", "name": "Google Cloud Translate", "type": "tool"}]
                    elif self.name == "inworld":
                        discovered = [{"model_id": "inworld-engine", "name": "InWorld Character Engine", "type": "audio"}]
                    else:
                        discovered = [{"model_id": f"{self.name}-service", "name": f"{self.name.capitalize()} Service", "type": "tool"}]

                # 7. Standard OpenAI-Compatible (Together, DeepInfra, Solar, Nvidia, Grok, OpenAI, Fireworks)
                elif self.url and self.api_key:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    r = await client.get(self.url, headers=headers)
                    if r.status_code == 200:
                        data = r.json()
                        items = data.get("data", []) if isinstance(data, dict) else data
                        for item in items:
                            m_id = item.get("id") or item.get("model_name") or item.get("model_id")
                            if not m_id: continue
                            
                            p_tag = f"{item.get('type', '')} {item.get('task', '')}"
                            m_name = item.get("name", item.get("model_name", m_id))
                            discovered.append({"model_id": m_id, "name": m_name, "type": resolve_model_type(m_id, p_tag)})
                    else:
                        logger.error(f"[{self.name}] API denied request: {r.status_code} - {r.text}")

                # 8. Xiaomi
                elif self.type == "maker" and not self.url and self.api_key:
                    if self.name == "xiaomi":
                        discovered = [
                            {"model_id": "mimo-v2-flash", "name": "MiMo-V2-Flash", "type": "agentic"},
                            {"model_id": "mimo-v2-pro", "name": "MiMo-V2-Pro", "type": "agentic"},
                            {"model_id": "mimo-v2.5", "name": "MiMo-V2.5", "type": "agentic"},
                            {"model_id": "mimo-v2.5-pro", "name": "MiMo-V2.5-Pro", "type": "agentic"},
                            {"model_id": "mimo-v2-omni", "name": "MiMo-V2-Omni", "type": "vision"}
                        ]
                    else:
                        discovered = [{"model_id": f"{self.name}-default", "name": f"{self.name.capitalize()} Baseline", "type": "chat"}]

            except Exception as e:
                logger.error(f"[{self.name}] Discovery Fail: {e}")
                
        return discovered

# MASTER REGISTRY
REGISTRY = {
    "anthropic":   Provider("anthropic",   "maker",      "ANTHROPIC-API-KEY",     "https://api.anthropic.com/v1/models"),
    "deepinfra":   Provider("deepinfra",   "aggregator", "DEEPINFRA-API-KEY",     "https://api.deepinfra.com/v1/models"),
    "fireworks":   Provider("fireworks",   "aggregator", "FIREWORKS-API-KEY01",   "https://api.fireworks.ai/inference/v1/models"),
    "google":      Provider("google",      "maker",      "GEMINI-API-KEY",        None),
    "grok":        Provider("grok",        "maker",      "GROK-API-KEY",          "https://api.x.ai/v1/models"),
    "huggingface": Provider("huggingface", "aggregator", "HUGGINGFACE-API-KEY",   "https://huggingface.co/api/models"),
    "mancer":      Provider("mancer",      "maker",      "MANCER-API-KEY-01",     "https://api.mancer.tech/v1/models"),
    "mistral":     Provider("mistral",     "maker",      "MINSTRAL-API-KEY",      "https://api.mistral.ai/v1/models"),
    "nvidia":      Provider("nvidia",      "aggregator", "NVIDIA-NIM-API-KEY",    "https://integrate.api.nvidia.com/v1/models"),
    "openrouter":  Provider("openrouter",  "aggregator", "OPEN-ROUTER-API-KEY",   "https://openrouter.ai/api/v1/models"),
    "openai":      Provider("openai",      "maker",      "OPENAI-API-KEY",        "https://api.openai.com/v1/models"),
    "solar":       Provider("solar",       "maker",      "SOLAR-API-KEY",         "https://api.upstage.ai/v1/models"),
    "together":    Provider("together",    "aggregator", "TOGETHER-AI-KEY",       "https://api.together.xyz/v1/models"),
    "xiaomi":      Provider("xiaomi",      "maker",      "XIAOMI-API-KEY",        None),
    "cartesia":    Provider("cartesia",    "tool",       "CARTESIA-API-KEY",      "https://api.cartesia.ai/models"),
    "translate":   Provider("translate",   "tool",       "GOOGLE-TRANSLATE-API",  None),
    "inworld":     Provider("inworld",     "tool",       "INWORLD-API-KEY",       None),
    "langsmith":   Provider("langsmith",   "tool",       "LANGSMITH-API-KEY",     None),
    "langsmith_svc": Provider("langsmith_svc", "tool",   "LANGSMITH-SVC-API-KEY", None),
    "mailgun":     Provider("mailgun",     "tool",       "MAILGUN-API-KEY",       None),
    "mailslurp":   Provider("mailslurp",   "tool",       "MAILSLURP-API-KEY",     None),
    "or_management": Provider("or_management", "tool",   "OR-MANAGEMENT-API-KEY", None),
    "patronus":    Provider("patronus",    "tool",       "PATRONUS-API-KEY",      None),
    "promptfoo":   Provider("promptfoo",   "tool",       "PROMPTFOO-API-KEY",     None),
    "simplelogin": Provider("simplelogin", "tool",       "SIMPLELOGIN-API-KEY",   None)
}

@app.api_route("/api/v1/providers", methods=["GET", "HEAD"])
async def get_providers(request: Request):
    if request.method == "HEAD": return Response(status_code=200)
    return list(REGISTRY.keys())

@app.api_route("/api/v1/manifest/{provider}", methods=["GET", "HEAD"])
async def get_manifest(provider: str, request: Request):
    p_obj = REGISTRY.get(provider)
    if not p_obj: return {"error": "Provider not found"}
    if request.method == "HEAD": return Response(status_code=200)
    
    try:
        await asyncio.wait_for(p_obj.ensure_ready(), timeout=15.0)
    except asyncio.TimeoutError:
        logger.warning(f"[Timeout] Discovery for {provider}")

    return {
        "provider": p_obj.name,
        "type": p_obj.type,
        "models": p_obj.models,
        "status": "LIVE" if p_obj.api_key else "VAULT_WAIT"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
