import os
import paramiko
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [NODE C VALIDATOR]: %(message)s')
logger = logging.getLogger("AerialMuscle")

class CloudNodeValidator:
    """
    [ ☁️ AERIAL MUSCLE VALIDATOR ]
    Verifies the operational status of Node C (node-c-brain-spot) before 
    dispatching heavy inference workloads. Confirms NVIDIA driver health 
    and GPU availability over the Tailnet.
    """

    def __init__(self):
        # We rely on the Tailscale MagicDNS name or static Tailnet IP
        self.host = os.environ.get("NODE_C_HOST", "node-c-brain-spot")
        self.port = int(os.environ.get("NODE_C_PORT", 22))
        self.user = os.environ.get("NODE_C_USER")
        self.ssh_key_path = os.environ.get("NODE_C_SSH_KEY")
        
        if not self.user or not self.ssh_key_path:
            logger.warning("[WARNING] Node C SSH credentials not fully provisioned in environment variables.")

    def _execute_command(self, command: str) -> Tuple[int, str, str]:
        """Opens a secure SSH tunnel to Node C via Tailscale and executes a command."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # We assume key-based auth for cloud nodes
            client.connect(hostname=self.host, port=self.port, username=self.user, key_filename=self.ssh_key_path, timeout=5)
            
            logger.debug(f"Injecting Verification Command: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            return exit_status, out, err
            
        except Exception as e:
            logger.error(f"[FATAL] SSH Tunnel to Node C Failed. Instance may be preempted: {e}")
            return -1, "", str(e)
        finally:
            client.close()

    def verify_gpu_health(self) -> bool:
        """
        [ GPU VITALITY CHECK ]
        Executes nvidia-smi to confirm the T4/L4 GPU is active and drivers are loaded.
        """
        logger.info(f"Probing {self.host} for NVIDIA GPU vitality...")
        
        # We check if nvidia-smi runs successfully and grep for the GPU name
        command = "nvidia-smi --query-gpu=name --format=csv,noheader"
        status, out, err = self._execute_command(command)
        
        if status == 0 and out:
            logger.info(f"[GPU VERIFIED] Detected: {out}")
            return True
        else:
            logger.error(f"[GPU FAILURE] NVIDIA drivers offline or GPU missing. Err: {err}")
            return False

# Example Usage:
# if __name__ == "__main__":
#     validator = CloudNodeValidator()
#     if validator.verify_gpu_health():
#         print("Node C is ready for heavy workloads.")
#     else:
#         print("Node C is preempted or broken. Route to external APIs.")
