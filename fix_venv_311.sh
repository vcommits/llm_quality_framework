#!/bin/bash
# 🐉 Ghidorah Mesh: Python 3.11 Stabilization & Auto-Init (Trixie/Pi 4 Fix)
# Role: Installs Miniforge, hydrates dependencies, and safely runs the Azure Init.

echo "🛠️ Bootstrapping Miniforge for Python 3.11 (Overwriting existing)..."
cd ~

# Clean up previous download attempts to ensure we use the fresh installer
rm -f Miniforge3-Linux-aarch64.sh*

wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh

# Added -u (Update) flag to handle the existing /home/godzilla/miniforge directory
bash Miniforge3-Linux-aarch64.sh -b -u -p $HOME/miniforge

# Initialize and create the 3.11 island
source "$HOME/miniforge/etc/profile.d/conda.sh"
"$HOME/miniforge/bin/conda" create -n ghid_311 python=3.11 -y

# Hydrate with all necessary mesh libraries (Includes aiohttp for async Azure requests)
echo "📥 Hydrating 3.11 island..."
"$HOME/miniforge/bin/conda" run -n ghid_311 pip install fastapi uvicorn httpx pydantic aiofiles python-multipart requests python-dotenv azure-cosmos aiohttp google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Align the venv symlink for the Librarian and Manifest services
cd ~/ghidorah_sentry
rm -rf .venv
ln -s $HOME/miniforge/envs/ghid_311 .venv

echo "✨ 3.11 ISLAND STABILIZED."
./.venv/bin/python3 --version

# --- NATIVE COSMOS INITIALIZATION ---
# Written directly via bash to prevent SSH paste mangling
echo "🚀 Generating Sterile Python Initializer..."

cat << 'PY_EOF' > compact_init.py
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
PY_EOF

echo "⚡ Executing Azure Handshake (Unbuffered)..."
./.venv/bin/python3 -u compact_init.py

