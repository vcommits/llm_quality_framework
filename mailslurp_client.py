import mailslurp_client
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class MailSlurpClient:
    """
    Handles transient identity verification using MailSlurp.
    Fetches API key from Azure Key Vault at runtime.
    """
    def __init__(self, vault_url: str):
        self.credential = DefaultAzureCredential()
        self.vault_client = SecretClient(vault_url=vault_url, credential=self.credential)
        self.api_key = self.vault_client.get_secret("MailSlurpApiKey").value
        
        self.config = mailslurp_client.Configuration()
        self.config.api_key['x-api-key'] = self.api_key
        self.api_client = mailslurp_client.ApiClient(self.config)
        
    def create_inbox(self):
        """Generates a new temporary inbox for persona registration."""
        controller = mailslurp_client.InboxControllerApi(self.api_client)
        return controller.create_inbox()

    def wait_for_verification_code(self, inbox_id: str):
        """Polls for incoming emails to extract verification codes."""
        controller = mailslurp_client.WaitForControllerApi(self.api_client)
        email = controller.wait_for_latest_email(inbox_id=inbox_id, timeout=30000)
        return email.body