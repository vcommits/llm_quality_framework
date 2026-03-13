# File: llm_tests/providers.py
from abc import ABC, abstractmethod
import os
import logging
from langchain_core.language_models.chat_models import BaseChatModel

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LLMProvider(ABC):
    """
    Abstract Base Class for all LLM Providers.
    Ensures every provider has a standard 'get_model()' method.
    """

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        pass


# --- CONCRETE IMPLEMENTATIONS ---

class OpenAIProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        # Check for specific environment variables if passed in kwargs, else default
        api_key = self.kwargs.pop("api_key", os.getenv("OPENAI_API_KEY"))
        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=api_key,
            **self.kwargs
        )


class AzureProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import AzureChatOpenAI
        # Azure requires strict deployment names and API versions
        # Support kwargs overrides for multiple resources
        api_version = self.kwargs.pop("api_version", os.getenv("AZURE_OPENAI_API_VERSION"))
        azure_endpoint = self.kwargs.pop("azure_endpoint", os.getenv("AZURE_OPENAI_ENDPOINT"))
        api_key = self.kwargs.pop("api_key", os.getenv("AZURE_OPENAI_API_KEY"))
        
        return AzureChatOpenAI(
            azure_deployment=self.model_name,  # Maps tier to deployment name
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            **self.kwargs
        )


class AnthropicProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic
        api_key = self.kwargs.pop("api_key", os.getenv("ANTHROPIC_API_KEY"))
        return ChatAnthropic(
            model=self.model_name,
            anthropic_api_key=api_key,
            **self.kwargs
        )


class GeminiProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = self.kwargs.pop("api_key", os.getenv("GEMINI_API_KEY"))
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            **self.kwargs
        )


class GrokProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        # Grok uses the OpenAI Client structure but points to X.AI
        api_key = self.kwargs.pop("api_key", os.getenv("GROK_API_KEY"))
        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=api_key,
            openai_api_base="https://api.x.ai/v1",
            **self.kwargs
        )


class TogetherProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        # FIX: Use ChatOpenAI instead of langchain_together to avoid Pydantic conflicts
        from langchain_openai import ChatOpenAI
        api_key = self.kwargs.pop("api_key", os.getenv("TOGETHER_API_KEY"))
        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=api_key,
            openai_api_base="https://api.together.xyz/v1",
            **self.kwargs
        )


class HuggingFaceProvider(LLMProvider):
    """
    Used primarily for the 'Glider' Judge model via Serverless Inference.
    """

    def get_model(self) -> BaseChatModel:
        from langchain_huggingface import HuggingFaceEndpoint
        api_key = self.kwargs.pop("api_key", os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        return HuggingFaceEndpoint(
            repo_id=self.model_name,
            task="text-generation",
            max_new_tokens=512,
            do_sample=True,
            temperature=0.1,  # Low temp for judges
            huggingfacehub_api_token=api_key,
            **self.kwargs
        )


# --- THE FACTORY (Switchboard) ---

class ProviderFactory:
    # Central Registry of Models
    MODEL_TIERS = {
        'openai': {
            'lite': 'gpt-4o-mini',
            'mid': 'gpt-4o',
            'full': 'gpt-4o',
            'vision': 'gpt-4o',  # Natively multimodal
            'judge': 'gpt-4o'  # The standard judge
        },
        'azure': {
            # NOTE: These must match your Azure Portal Deployment Names exactly!
            'lite': 'gpt-35-turbo',
            'mid': 'gpt-4',
            'full': 'gpt-4o',
            'vision': 'gpt-4o'
        },
        'anthropic': {
            'lite': 'claude-3-haiku-20240307',
            'mid': 'claude-3-5-sonnet-20240620',
            'full': 'claude-3-opus-20240229',
            'vision': 'claude-3-5-sonnet-20240620'
        },
        'gemini': {
            'lite': 'gemini-1.5-flash',
            'mid': 'gemini-1.5-pro',
            'full': 'gemini-1.5-pro',
            'vision': 'gemini-1.5-flash'  # Excellent video/audio handling
        },
        'grok': {
            'lite': 'grok-2-mini',
            'full': 'grok-2'
        },
        'together': {
            'lite': 'mistralai/Mistral-7B-Instruct-v0.2', # Reliable serverless model
            'mid': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'full': 'meta-llama/Llama-3-70b-chat-hf',
            'code': 'mistralai/Codestral-22B-v0.1',
            # The new Judge (Ministral 8B)
            'judge': 'mistralai/Ministral-8B-Instruct-2410',
            # The new Vision Model (Llama 3.2 11B)
            'vision': 'meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo'
        },
        'huggingface': {
            # The Specialized Judge (Patronus Glider)
            'judge': 'PatronusAI/glider',
            'lite': 'microsoft/Phi-3.5-mini-instruct'
        }
    }

    # Configuration map for custom keys/endpoints per model if needed
    # This allows overriding the default env vars for specific tiers
    MODEL_CONFIG = {
        # Example: 'azure': {'mid': {'api_key': 'AZURE_GPT4_KEY', 'azure_endpoint': '...'}}
    }

    @staticmethod
    def get_provider(provider_name: str, tier: str = 'lite', model_name_override: str = None, **kwargs) -> LLMProvider:
        """
        Factory method to instantiate the correct provider class.
        Accepts 'model_name_override' to bypass tiers and use raw model IDs (from Harvester).
        """
        provider_name = provider_name.lower()

        # Validation
        if provider_name not in ProviderFactory.MODEL_TIERS:
            raise ValueError(f"Provider '{provider_name}' is not supported.")

        if model_name_override:
            # Bypass tier lookup if we have a raw ID
            model_name = model_name_override
        else:
            # Standard Tier Logic
            tiers = ProviderFactory.MODEL_TIERS[provider_name]
            if tier not in tiers:
                # Fallback logic: If 'vision' is requested but not defined, try 'full'
                if tier == 'vision' and 'full' in tiers:
                    print(f"⚠️ Warning: Tier 'vision' not found for {provider_name}. Falling back to 'full'.")
                    tier = 'full'
                else:
                    raise ValueError(
                        f"Tier '{tier}' is not available for provider '{provider_name}'. Available: {list(tiers.keys())}")
            model_name = tiers[tier]
            
            # Check for specific config overrides
            if provider_name in ProviderFactory.MODEL_CONFIG and tier in ProviderFactory.MODEL_CONFIG[provider_name]:
                config = ProviderFactory.MODEL_CONFIG[provider_name][tier]
                # Resolve env vars in config
                for k, v in config.items():
                    if k.endswith("_key") or k.endswith("_token"):
                        val = os.getenv(v)
                        if val: kwargs[k] = val # Pass the actual key value, not the env var name

        # Dispatch
        if provider_name == 'openai':
            return OpenAIProvider(model_name, **kwargs)
        elif provider_name == 'azure':
            return AzureProvider(model_name, **kwargs)
        elif provider_name == 'anthropic':
            return AnthropicProvider(model_name, **kwargs)
        elif provider_name == 'gemini':
            return GeminiProvider(model_name, **kwargs)
        elif provider_name == 'grok':
            return GrokProvider(model_name, **kwargs)
        elif provider_name == 'together':
            return TogetherProvider(model_name, **kwargs)
        elif provider_name == 'huggingface':
            return HuggingFaceProvider(model_name, **kwargs)
        else:
            raise ValueError(f"Provider class for '{provider_name}' not implemented.")
