import asyncio, sys
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

async def run():
    print("🚀 INIT CALLED"); sys.stdout.flush()
    u = "https://cosmos-ghidorah-registry.documents.azure.com:443/"
    k = "REDACTED_USE_ENV_VAR"
    
    try:
        async with CosmosClient(u, credential=k) as c:
            db = await c.create_database_if_not_exists(id="ghidorah_db")
            print("✅ DB OK"); sys.stdout.flush()
            await db.create_container_if_not_exists(id="sessions", partition_key=PartitionKey(path="/partition_key"))
            print("✨ REGISTRY TIER STABILIZED."); sys.stdout.flush()
    except Exception as e:
        print(f"🚨 AZURE ERROR: {e}"); sys.stdout.flush()

asyncio.run(run())
