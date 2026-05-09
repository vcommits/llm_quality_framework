#!/bin/bash
# 🐉 Ghidorah Mesh: Path & Venv Alignment (v1.2.6)

echo "🛠️ Aligning Ghidorah Mesh to ~/ghidorah_sentry..."

# 1. Update the Manifest Service
sudo tee /etc/systemd/system/ghidorah-manifest.service << S_EOF
[Unit]
Description=Ghidorah Manifest Server
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/ghidorah_sentry
ExecStart=$HOME/ghidorah_sentry/.venv/bin/python3 manifest_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
S_EOF

# 2. Update the Librarian Service
sudo tee /etc/systemd/system/ghidorah-librarian.service << S_EOF
[Unit]
Description=Ghidorah Librarian API
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/ghidorah_sentry
ExecStart=$HOME/ghidorah_sentry/.venv/bin/python3 librarian.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
S_EOF

# 3. Synchronize Dependencies
cd ~/ghidorah_sentry
cat << 'R_EOF' > requirements.txt
fastapi
uvicorn
httpx
pydantic
aiofiles
python-multipart
requests
azure-identity
azure-storage-blob
azure-cosmos
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
R_EOF

# 4. Rebuild & Populate Virtual Environment
echo "📦 Building the Virtual Environment..."
rm -rf .venv
python3 -m venv .venv

echo "📥 Installing Full Dependency Stack..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

# 5. Reload and Restart Services
echo "🔄 Reloading systemd and engaging services..."
sudo systemctl daemon-reload
sudo systemctl enable ghidorah-manifest ghidorah-librarian
sudo systemctl restart ghidorah-manifest ghidorah-librarian

echo "✨ MESH STABILIZED."
echo "🔗 Manifest: http://$(hostname -I | awk '{print $1}'):8080/health"
echo "🔗 Librarian: http://$(hostname -I | awk '{print $1}'):8081/health"
