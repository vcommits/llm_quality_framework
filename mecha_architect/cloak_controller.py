import os
import json
import logging
import paramiko
from typing import Dict, Any, Tuple

# --- Kaiju Noir Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [NODE 0 COMMAND LINK]: %(message)s')
logger = logging.getLogger("TacticalCloak")

class TacticalCloakController:
    """
    [ 💀 TACTICAL CLOAK CONTROLLER ]
    Orchestrates the dark-routing capabilities of Node 0 (The Edge Gateway).
    Forges the Tailscale Exit Node protocols, ensuring adversarial purity
    by routing Node 2's heavy strikes through Node 0's WireGuard disguises.
    """

    def __init__(self):
        """
        Initializes the cryptographic handshake parameters.
        Adheres to Adversarial Purity: Zero hardcoded credentials.
        """
        self.host = os.environ.get("NODE0_HOST", "100.120.132.20")
        self.port = int(os.environ.get("NODE0_PORT", 22))
        self.user = os.environ.get("NODE0_USER")
        self.password = os.environ.get("NODE0_PASS")
        self.ssh_key_path = os.environ.get("NODE0_SSH_KEY")
        
        if not self.user and not (self.password or self.ssh_key_path):
            logger.warning("[WARNING] Node 0 credentials not fully provisioned in environment.")

    def _execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Opens a secure SSH tunnel to Node 0, injects the command, and retreats.
        Returns exit_status, stdout, stderr.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if self.ssh_key_path:
                client.connect(hostname=self.host, port=self.port, username=self.user, key_filename=self.ssh_key_path)
            else:
                client.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)
                
            logger.info(f"Injecting Command: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            return exit_status, out, err
            
        except Exception as e:
            logger.error(f"[FATAL] SSH Tunnel Collapse: {e}")
            raise
        finally:
            client.close()

    def verify_wan_status(self) -> bool:
        """
        [ DIAGNOSTIC PROBE ]
        Interrogates the OpenWrt ubus bridge to ensure the WAN interface is active.
        We do not route traffic into a dead void.
        """
        logger.info("Probing ubus for WAN vitality...")
        command = "ubus call network.interface.wan status"
        status, out, err = self._execute_command(command)
        
        if status != 0:
            logger.error(f"ubus probe failed: {err}")
            return False
            
        try:
            wan_data = json.loads(out)
            is_up = wan_data.get("up", False)
            if is_up:
                logger.info("WAN is UP. The Cloak has internet access.")
            else:
                logger.warning("WAN is DOWN. The Cloak is isolated.")
            return is_up
        except json.JSONDecodeError:
            logger.error("Mangled JSON received from ubus bridge.")
            return False

    def enable_ip_forwarding(self) -> bool:
        """
        [ KERNEL MUTATION ]
        Forces the OpenWrt kernel to allow packet forwarding, transforming
        the hardware from a passive client into an active routing hub.
        """
        logger.info("Initiating Kernel Mutation (IPv4/IPv6 Forwarding)...")
        cmds = [
            "sysctl -w net.ipv4.ip_forward=1",
            "sysctl -w net.ipv6.conf.all.forwarding=1"
        ]
        
        for cmd in cmds:
            status, out, err = self._execute_command(cmd)
            if status != 0:
                logger.error(f"Kernel mutation failed on '{cmd}': {err}")
                return False
                
        logger.info("Kernel Mutation successful. Forwarding enabled.")
        return True

    def advertise_exit_node(self) -> bool:
        """
        [ TAILSCALE ADVERTISEMENT ]
        Broadcasts Node 0's availability as an Exit Node across the Ghidorah Mesh.
        """
        logger.info("Broadcasting Exit Node advertisement to the Tailnet...")
        # Note: Depending on existing tailscale state, this might require --reset or --accept-routes
        command = "tailscale up --advertise-exit-node"
        status, out, err = self._execute_command(command)
        
        if status != 0:
            logger.error(f"Tailscale advertisement failed: {err}")
            return False
            
        logger.info("Advertisement successful. Node 0 is now a routing hub.")
        return True

    def engage_cloak(self) -> bool:
        """
        [ MASTER OVERRIDE: ENGAGE CLOAK ]
        Executes the full sequence to turn Node 0 into a working Exit Node.
        """
        logger.info("=== INITIATING CLOAK ENGAGEMENT PROTOCOL ===")
        
        if not self.verify_wan_status():
            logger.error("Protocol Aborted: WAN is disconnected.")
            return False
            
        if not self.enable_ip_forwarding():
            logger.error("Protocol Aborted: Kernel mutation failed.")
            return False
            
        if not self.advertise_exit_node():
            logger.error("Protocol Aborted: Tailscale routing failure.")
            return False
            
        logger.info("=== CLOAK ENGAGED. NODE 0 AWAITING TRAFFIC. ===")
        return True

# Example Usage (To be called by FastAPI endpoints in Node 3):
# if __name__ == "__main__":
#     controller = TacticalCloakController()
#     controller.engage_cloak()
