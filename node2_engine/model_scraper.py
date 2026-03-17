import httpx
import asyncio
import logging
from datetime import datetime
from harvester import SecretHarvester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelHarvester")

NODE_1_LIBRARIAN = "http://100.101.24.26:8000"

# Target Manifests
PROVIDER_APIS = {
    "openrouter": "https://openrouter.ai/api/v1/models",
    "together": "https://api.together.xyz/v1/models",
    "huggingface": "https://huggingface.co/api/models?pipeline_tag=text-generation&sort=downloads&direction=-1&limit=100"
}

harvester = SecretHarvester()


async def push_intel_to_librarian(client: httpx.AsyncClient, provider: str, payload: list):
    """Vaults the normalized intelligence back to Node 1."""
    try:
        await client.post(
            f"{NODE_1_LIBRARIAN}/api/v1/intel/update-manifest",
            json={"provider": provider, "data": payload}
        )
        logger.info(f"🟢 Successfully vaulted {len(payload)} models from {provider}.")
    except Exception as e:
        logger.error(f"Failed to push {provider} intel to Node 1: {e}")


# --- PROVIDER SPECIFIC HARVESTERS ---

async def harvest_openrouter(client: httpx.AsyncClient):
    logger.info("Syphoning OpenRouter manifest...")
    api_key = harvester.get_key("OPENROUTER_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    res = await client.get(PROVIDER_APIS["openrouter"], headers=headers, timeout=10.0)
    if res.status_code == 200:
        models = res.json().get("data", [])
        payload = [{
            "model_id": m["id"],
            "name": m["name"],
            "context_length": m.get("context_length", "Unknown"),
            "provider": "openrouter",
            "last_scraped": datetime.now().isoformat()
        } for m in models if "chat" in m.get("id", "").lower() or "chat" in m.get("description", "").lower()]
        await push_intel_to_librarian(client, "openrouter", payload)


async def harvest_together_ai(client: httpx.AsyncClient):
    logger.info("Syphoning Together AI manifest...")
    api_key = harvester.get_key("TOGETHER_AI_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    res = await client.get(PROVIDER_APIS["together"], headers=headers, timeout=10.0)
    if res.status_code == 200:
        models = res.json()
        payload = [{
            "model_id": m["id"],
            "name": m.get("display_name", m["id"]),
            "context_length": m.get("context_length", "Unknown"),
            "provider": "together",
            "last_scraped": datetime.now().isoformat()
        } for m in models if m.get("type") == "chat" or "chat" in m.get("id", "").lower()]
        await push_intel_to_librarian(client, "together", payload)


async def harvest_huggingface(client: httpx.AsyncClient):
    logger.info("Syphoning Hugging Face Top 100 Text-Gen models...")
    res = await client.get(PROVIDER_APIS["huggingface"], timeout=10.0)
    if res.status_code == 200:
        models = res.json()
        payload = [{
            "model_id": m["id"],
            "name": m["id"].split("/")[-1],  # Gets the clean name
            "context_length": "Variable (Local/Endpoint)",
            "provider": "huggingface",
            "last_scraped": datetime.now().isoformat()
        } for m in models]
        await push_intel_to_librarian(client, "huggingface", payload)


# --- THE DAEMON LOOP ---

async def run_harvester_daemon(interval_hours: int = 12):
    """The continuous background loop for Node 2's passive reconnaissance."""
    logger.info("🟢 Multi-Provider Intel Harvester Daemon Online.")

    async with httpx.AsyncClient() as client:
        while True:
            logger.info(f"--- Initiating Global Reconnaissance Sweep at {datetime.now()} ---")

            # Run all three syphons concurrently
            await asyncio.gather(
                harvest_openrouter(client),
                harvest_together_ai(client),
                harvest_huggingface(client)
            )

            logger.info(f"Sweep complete. Daemon sleeping for {interval_hours} hours.")
            await asyncio.sleep(interval_hours * 3600)


if __name__ == "__main__":
    try:
        asyncio.run(run_harvester_daemon())
    except KeyboardInterrupt:
        logger.info("Harvester Daemon terminated manually.")