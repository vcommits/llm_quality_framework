import sys
import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

print("🚀 FORCE INIT STARTED...")
sys.stdout.flush()

async def main():
    print("📖 Reading .env manually (No dotenv library)...")
    sys.stdout.flush()
    uri = ""
    key = ""
    try:
        with open("/home/godzilla/ghidorah_sentry/.env", "r") as f:
            for line in f:
                if line.startswith("COSMOS_URI="):
                    uri = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("COSMOS_PRIMARY_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception as e:
        print(f"🚨 Failed to read .env: {e}")
        return

    if not uri or not key:
        print("🚨 Secrets missing. Check /home/godzilla/ghidorah_sentry/.env")
        return

    print(f"🌌 Connecting to: {uri}")
    sys.stdout.flush()
    
    try:
        async with CosmosClient(uri, credential=key) as client:
            print("📡 Creating Database 'ghidorah_db'...")
            sys.stdout.flush()
            db = await client.create_database_if_not_exists(id="ghidorah_db")
            
            print("📡 Creating Container 'sessions'...")
            sys.stdout.flush()
            await db.create_container_if_not_exists(
                id="sessions", 
                partition_key=PartitionKey(path="/partition_key")
            )
            
            print("\n✨ REGISTRY TIER STABILIZED.")
            sys.stdout.flush()
    except Exception as e:
        print(f"🚨 AZURE ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
