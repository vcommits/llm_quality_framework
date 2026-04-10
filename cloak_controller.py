import requests
import json
import time


class TacticalCloakController:
    """
    Node 3 (Control) RPC interface for Node 0 (GL.iNet AC1300).
    Manages WireGuard rotation and Kill-Switches via the router's local API.
    """

    def __init__(self, router_ip="192.168.8.1", password="admin"):
        self.base_url = f"http://{router_ip}/rpc"
        self.password = password
        self.token = self._authenticate()

    def _authenticate(self):
        """Logs into the GL.iNet API and retrieves an auth token."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": ["", "ui", "login", {"username": "root", "password": self.password}],
            "id": 1
        }
        try:
            res = requests.post(self.base_url, json=payload, timeout=5)
            if res.status_code == 200:
                return res.json().get('result', {}).get('token')
        except Exception as e:
            # Silently fail for UI rendering purposes if not on the local network yet
            pass
        return None

    def get_vpn_status(self):
        """Fetches the current WireGuard connection status."""
        if not self.token: return {"status": "Disconnected", "ip": "Unknown", "geo_profile": "None"}

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [self.token, "wireguard", "get_status", {}],
            "id": 1
        }
        try:
            res = requests.post(self.base_url, json=payload, timeout=5)
            data = res.json().get('result', {})
            return {
                "status": "Active" if data.get('status') == 'connected' else "Inactive",
                "ip": data.get('ip_address', 'Hidden'),
                "geo_profile": data.get('group_name', 'None')
            }
        except:
            return {"status": "Error", "ip": "Unknown", "geo_profile": "None"}

    def rotate_vpn(self, profile_name):
        """Commands the AC1300 to drop current VPN and connect to a new Geo-Profile."""
        if not self.token: return False

        # 1. Disconnect current
        stop_payload = {"jsonrpc": "2.0", "method": "call", "params": [self.token, "wireguard", "stop", {}], "id": 1}
        requests.post(self.base_url, json=stop_payload)
        time.sleep(2)  # Wait for tunnel collapse

        # 2. Connect to new profile
        start_payload = {
            "jsonrpc": "2.0", "method": "call",
            "params": [self.token, "wireguard", "start", {"group_name": profile_name}],
            "id": 1
        }
        res = requests.post(self.base_url, json=start_payload)

        if res.json().get('result', {}).get('code') == 0:
            return True
        return False

    def trigger_killswitch(self):
        """Emergency Network Sever (Drops WAN)."""
        if not self.token: return False
        payload = {"jsonrpc": "2.0", "method": "call",
                   "params": [self.token, "network", "disconnect", {"interface": "wan"}], "id": 1}
        requests.post(self.base_url, json=payload)
        return True