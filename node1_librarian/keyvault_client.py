import os
import asyncio
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

# --- Configuration ---
KEY_VAULT_NAME = os.environ.get("AZURE_KEY_VAULT_NAME", "ghidorah-vault")
VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net/"

# --- Singleton Client for Efficiency ---
# Use a single, cached credential object across the application
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)

async def get_secret(secret_name: str) -> str:
    """
    Asynchronously retrieves a secret from the specified Azure Key Vault.

    Args:
        secret_name: The alias of the secret to retrieve (e.g., "MailSlurpAPIKey").

    Returns:
        The value of the secret.

    Raises:
        ResourceNotFoundError: If the secret is not found.
        Exception: For any other authentication or connection errors.
    """
    print(f"Attempting to retrieve secret '{secret_name}' from vault '{KEY_VAULT_NAME}'...")
    try:
        retrieved_secret = await secret_client.get_secret(secret_name)
        print(f"Successfully retrieved secret '{secret_name}'.")
        return retrieved_secret.value
    except ResourceNotFoundError as e:
        print(f"ERROR: Secret '{secret_name}' not found in vault '{KEY_VAULT_NAME}'.")
        raise e
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while authenticating with Azure: {e}")
        raise e
