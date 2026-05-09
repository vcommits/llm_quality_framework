#!/bin/bash
# cloud_node_bootstrap.sh - Run via SSH on node-c-brain after provisioning

echo "[Ghidorah] Starting Cloud Node Bootstrapper..."

# 1. Wait for GCP background NVIDIA driver installation to complete
echo "[Ghidorah] Checking for NVIDIA drivers..."
while ! command -v nvidia-smi &> /dev/null
do
    echo "Waiting for NVIDIA drivers to initialize..."
    sleep 10
done
nvidia-smi
echo "[Ghidorah] GPU verified."

# 2. Network Security: Lock down UFW to Tailscale ONLY
echo "[Ghidorah] Configuring UFW Firewall for Tailscale Isolation..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow in on tailscale0 to any port 8000
sudo ufw allow 22/tcp # Allow SSH just in case, though TS SSH is preferred
sudo ufw --force enable

# 3. Install Tailscale securely
echo "[Ghidorah] Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# 4. Authenticate Tailscale
# Replace $TAILSCALE_AUTH_KEY with an ephemeral/reusable key injected via GCP Startup Script metadata
echo "[Ghidorah] Connecting to Swarm Tailnet..."
sudo tailscale up --authkey=${TAILSCALE_AUTH_KEY} --exit-node=slate-ac1300-name --accept-dns=false

# 5. Setup Python Environment for Inference
echo "[Ghidorah] Setting up Virtual Environment..."
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip
python3 -m venv /home/$USER/ghidorah_env
source /home/$USER/ghidorah_env/bin/activate

# 6. Install Core ML/API Dependencies
# Added bitsandbytes for 4-bit quantization (critical for 8B models on 16GB T4)
echo "[Ghidorah] Installing ML dependencies..."
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate bitsandbytes fastapi uvicorn python-multipart "openai-whisper"

echo "[Ghidorah] Bootstrap complete. Virtual environment ready at ~/ghidorah_env."
