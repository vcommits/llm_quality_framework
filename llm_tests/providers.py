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
        # FIX: Provide fallback string to prevent "Sync client" async evaluation bugs in Langchain when key is None
        api_key = self.kwargs.pop("api_key", os.getenv("OPENAI_API_KEY")) or "MISSING_KEY"
        return ChatOpenAI(
            model_name=self.model_name,
            api_key=api_key,
            **self.kwargs
        )


class AzureProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import AzureChatOpenAI
        api_version = self.kwargs.pop("api_version", os.getenv("AZURE_OPENAI_API_VERSION")) or "2023-05-15"
        azure_endpoint = self.kwargs.pop("azure_endpoint", os.getenv("AZURE_OPENAI_ENDPOINT")) or "https://missing.endpoint/"
        api_key = self.kwargs.pop("api_key", os.getenv("AZURE_OPENAI_API_KEY")) or "MISSING_KEY"
        
        return AzureChatOpenAI(
            azure_deployment=self.model_name,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            **self.kwargs
        )


class AnthropicProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic
        api_key = self.kwargs.pop("api_key", os.getenv("ANTHROPIC_API_KEY")) or "MISSING_KEY"
        return ChatAnthropic(
            model=self.model_name,
            api_key=api_key,
            **self.kwargs
        )


class GeminiProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = self.kwargs.pop("api_key", os.getenv("GEMINI_API_KEY")) or "MISSING_KEY"
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            api_key=api_key,
            **self.kwargs
        )


class GrokProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        api_key = self.kwargs.pop("api_key", os.getenv("GROK_API_KEY")) or "MISSING_KEY"
        return ChatOpenAI(
            model_name=self.model_name,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            **self.kwargs
        )


class TogetherProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        api_key = self.kwargs.pop("api_key", os.getenv("TOGETHER_API_KEY")) or "MISSING_KEY"
        return ChatOpenAI(
            model_name=self.model_name,
            api_key=api_key,
            base_url="https://api.together.xyz/v1",
            **self.kwargs
        )

class MistralProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_mistralai import ChatMistralAI
        api_key = self.kwargs.pop("api_key", os.getenv("mistral_api_key") or os.getenv("MISTRAL_API_KEY")) or "MISSING_KEY"
        return ChatMistralAI(
            model=self.model_name, 
            api_key=api_key,
            **self.kwargs
        )

class OpenRouterProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        api_key = self.kwargs.pop("api_key", os.getenv("ghidorah_openrouter_api") or os.getenv("OPENROUTER_API_KEY")) or "MISSING_KEY"
        return ChatOpenAI(
            model_name=self.model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/vcommits/llm_quality_framework",
                "X-Title": "Agentic Prism Framework",
            },
            **self.kwargs
        )

class HuggingFaceProvider(LLMProvider):
    """
    Used primarily for the 'Glider' Judge model via Serverless Inference.
    """
    def get_model(self) -> BaseChatModel:
        from langchain_huggingface import HuggingFaceEndpoint
        api_key = self.kwargs.pop("api_key", os.getenv("HUGGINGFACEHUB_API_TOKEN")) or "MISSING_KEY"
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
        'mistral': {
            'lite': 'mistral-small-latest',
            'mid': 'mistral-medium-latest',
            'full': 'mistral-large-latest',
            'code': 'codestral-latest',
            'vision': 'pixtral-12b-2409'
        },
        'together': {
            'lite': 'mistralai/Mistral-7B-Instruct-v0.2',
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
        },
        'openrouter': {
            'lite': 'huggingfaceh4/zephyr-7b-beta',
            'mid': 'meta-llama/llama-3-70b-instruct',
            'uncensored': 'cognitivecomputations/dolphin-mixtral-8x7b', # Popular uncensored model
            'judge': 'meta-llama/llama-3-70b-instruct'
        }
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
        elif provider_name == 'mistral':
            return MistralProvider(model_name, **kwargs)
        elif provider_name == 'together':
            return TogetherProvider(model_name, **kwargs)
        elif provider_name == 'huggingface':
            return HuggingFaceProvider(model_name, **kwargs)
        elif provider_name == 'openrouter':
            return OpenRouterProvider(model_name, **kwargs)
        else:
            raise ValueError(f"Provider class for '{provider_name}' not implemented.")