import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Configuration ---
NODE0_API_URL = "http://100.120.132.20/v1/audit/gate"
# In a real app, user/pass would come from a secure source
NODE0_USER = "root"
NODE0_PASS = "st3nn3ts"

# --- Pydantic Models ---
class GeoCloakRequest(BaseModel):
    profile_index: int

# --- FastAPI App ---
app = FastAPI(title="Node 3 - Command Center API")

# --- Node 0 API Client (OOP Approach) ---
class Node0Client:
    def __init__(self, base_url: str, user: str, pwd: str):
        self.base_url = base_url
        self.user = user
        self.pwd = pwd
        self.session_id = None
        self.client = httpx.AsyncClient()

    async def _login(self):
        """Authenticates with Node 0's JSON-RPC and stores the session ID."""
        rpc_payload = {
            "jsonrpc": "2.0", "id": 1, "method": "call",
            "params": ["session", "login", {"username": self.user, "password": self.pwd}]
        }
        try:
            response = await self.client.post(self.base_url, json=rpc_payload)
            response.raise_for_status()
            self.session_id = response.json()["result"][1]["ubus_rpc_session"]
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Node 0 login failed: {e}")

    async def call(self, namespace: str, method: str, params: dict = {}):
        """Makes an authenticated call to the Node 0 ubus API."""
        if not self.session_id:
            await self._login()
        
        rpc_payload = {
            "jsonrpc": "2.0", "id": 1, "method": "call",
            "params": [self.session_id, namespace, method, params]
        }
        try:
            response = await self.client.post(self.base_url, json=rpc_payload)
            response.raise_for_status()
            return response.json()["result"][1]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Node 0 API call failed: {e}")

# --- Dependency Injection ---
node0_client = Node0Client(NODE0_API_URL, NODE0_USER, NODE0_PASS)

# --- API Endpoints for UI ---
@app.post("/dashboard/toggle-honeypot")
async def toggle_honeypot(enable: bool):
    """Enables or disables the Nginx honeypot on Node 0."""
    # This is a simplified example. A real implementation would modify the nginx config via uci.
    # For now, we'll just log the intent.
    action = "enable" if enable else "disable"
    return {"status": f"Honeypot {action} command sent to Node 0."}

@app.post("/dashboard/geo-cloak")
async def set_geo_cloak(request: GeoCloakRequest):
    """Commands Node 0 to switch its VPN exit node."""
    # This calls the /hp/geo endpoint on the Honeypot service itself.
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"http://100.120.132.20/hp/geo", json={"profile_index": request.profile_index})
        return {"status": f"Geo-cloak rotation to profile {request.profile_index} initiated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger geo-cloak: {e}")

@app.post("/dashboard/pcap-stream/start")
async def start_pcap_stream():
    """Triggers tcpdump on Node 0."""
    # Using the ubus API bridge to run a command
    result = await node0_client.call('system', 'run', {'command': 'tcpdump -i any -w /tmp/ghidorah_capture.pcap -c 1000'})
    return {"status": "PCAP capture started on Node 0.", "details": result}

@app.get("/")
def root():
    return {"message": "Node 3 Command Center API is online."}
