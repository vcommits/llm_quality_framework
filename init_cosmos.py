import sys
import os

# 🐉 Ghidorah: Hard-Reset Initializer (v1.1.5)
print("🚀 [1] SCRIPT STARTED")
sys.stdout.flush()

try:
    import asyncio
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos import PartitionKey
    print("📦 [2] CORE LIBRARIES LOADED")
    sys.stdout.flush()
except Exception as e:
    print(f"🚨 [FAIL] Library Import Error: {e}")
    sys.stdout.flush()
    sys.exit(1)

async def run_diag():
    print("🧪 [3] ATTEMPTING .ENV LOAD...")
    sys.stdout.flush()
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ [4] DOTENV SUCCESS")
    except Exception as e:
        print(f"⚠️ [4] DOTENV FAILED (Falling back to manual): {e}")

    # Manual check of secrets
    url = os.getenv("COSMOS_URI")
    key = os.getenv("COSMOS_PRIMARY_KEY")
    
    print(f"📡 [5] URI FOUND: {bool(url)}")
    print(f"📡 [6] KEY FOUND: {bool(key)}")
    sys.stdout.flush()

    if not url or not key:
        print("❌ ABORTING: Missing secrets in .env")
        return

    print(f"🌌 [7] CONTACTING AZURE: {url}")
    try:
        async with CosmosClient(url, credential=key) as client:
            db = await client.create_database_if_not_exists(id="ghidorah_db")
            print("✅ [8] DB VERIFIED")
            await db.create_container_if_not_exists(id="sessions", partition_key=PartitionKey(path="/partition_key"))
            print("✅ [9] CONTAINER VERIFIED")
            print("\n✨ REGISTRY TIER STABILIZED.")
    except Exception as e:
        print(f"🚨 [FAIL] COSMOS ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_diag())
