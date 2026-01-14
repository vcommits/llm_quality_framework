# File: llm_tests/providers.py
# Purpose: OOP-based provider abstractions for creating LangChain chat models.

from abc import ABC, abstractmethod
import os
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_together import ChatTogether

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Returns a configured LangChain chat model."""
        pass

class OpenAIProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        return ChatOpenAI(model_name=self.model_name, **self.kwargs)

class AnthropicProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        return ChatAnthropic(model=self.model_name, **self.kwargs)

class GeminiProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            **self.kwargs
        )

class GrokProvider(LLMProvider):
    def get_model(self) -> BaseChatModel:
        # xAI's Grok API is OpenAI-compatible
        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=os.getenv("GROK_API_KEY"),
            openai_api_base="https://api.x.ai/v1",
            **self.kwargs
        )

class TogetherProvider(LLMProvider):
    """Provider for open-source models (Mistral, Llama, Falcon) via Together AI."""
    
    def get_model(self) -> BaseChatModel:
        return ChatTogether(
            model=self.model_name,
            together_api_key=os.getenv("TOGETHER_API_KEY"),
            **self.kwargs
        )

class ProviderFactory:
    """Factory class to instantiate the correct provider."""
    
    MODEL_TIERS = {
        'grok': {
            'lite': 'grok-2-mini',
            'full': 'grok-2'
        },
        'openai': {
            'lite': 'gpt-4o-mini',
            'mid': 'gpt-4o',
            'full': 'gpt-4o'
        },
        'anthropic': {
            'lite': 'claude-3-haiku-20240307',
            'mid': 'claude-3-5-sonnet-20240620',
            'full': 'claude-3-opus-20240229'
        },
        'gemini': {
            'lite': 'gemini-1.5-flash-latest',
            'mid': 'gemini-1.5-pro-latest',
            'full': 'gemini-1.5-pro-latest'
        },
        'together': {
            'lite': 'mistralai/Mistral-7B-Instruct-v0.2',  # Fast/Cheap
            'mid': 'mistralai/Mixtral-8x7B-Instruct-v0.1',  # Smart Open Source
            'full': 'meta-llama/Llama-3-70b-chat-hf',  # Powerful
            'code': 'mistralai/Codestral-22B-v0.1'  # Coding Specialist
        }
    }

    @staticmethod
    def get_provider(provider_name: str, tier: str = 'lite', **kwargs) -> LLMProvider:
        provider_name = provider_name.lower()
        
        if provider_name not in ProviderFactory.MODEL_TIERS:
            raise ValueError(f"Provider '{provider_name}' is not supported.")
            
        tiers = ProviderFactory.MODEL_TIERS[provider_name]
        if tier not in tiers:
             raise ValueError(f"Tier '{tier}' is not available for provider '{provider_name}'.")
             
        model_name = tiers[tier]
        logging.info(f"Configuring model for provider: {provider_name.upper()}, model: {model_name}")

        if provider_name == 'openai':
            return OpenAIProvider(model_name, **kwargs)
        elif provider_name == 'anthropic':
            return AnthropicProvider(model_name, **kwargs)
        elif provider_name == 'gemini':
            return GeminiProvider(model_name, **kwargs)
        elif provider_name == 'grok':
            return GrokProvider(model_name, **kwargs)
        elif provider_name == 'together':
            return TogetherProvider(model_name, **kwargs)
        else:
            raise ValueError(f"Provider class for '{provider_name}' not implemented.")
