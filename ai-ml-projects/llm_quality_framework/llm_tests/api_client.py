# File: llm_tests/api_client.py
# Purpose: A factory for creating configured LangChain chat model objects for testing.

import logging
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Model Tier Mapping ---
MODEL_TIERS = {
    'grok': {
        'lite': 'grok-3-mini',
        'full': 'grok-4'
    },
    'openai': {
        'lite': 'gpt-4o-mini',
        'mid': 'gpt-4o',
        'full': 'gpt-4o'
    },
    'anthropic': {
        'lite': 'claude-3-haiku-20240307',
        'mid': 'claude-3.5-sonnet-20240620',
        'full': 'claude-3-opus-20240229'
    },
    'gemini': {
        'lite': 'gemini-1.5-flash-latest',
        'mid': 'gemini-1.5-pro-latest',
        'full': 'gemini-1.5-pro-latest'
    }
}

def get_llm_for_evaluation(provider: str, tier: str = 'lite'):
    """
    Factory function to get a configured LangChain chat model.
    """
    try:
        model_name = MODEL_TIERS[provider][tier]
        logging.info(f"Configuring model for provider: {provider.upper()}, model: {model_name}")

        match provider:
            case "openai":
                return ChatOpenAI(model_name=model_name, max_tokens=1024)
            case "anthropic":
                return ChatAnthropic(model=model_name, max_tokens=1024)
            case "gemini":
                # FIX: Explicitly pass the API key for Gemini
                return ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                    max_output_tokens=1024
                )
            case "grok":
                # xAI's Grok API is OpenAI-compatible. We use ChatOpenAI and point it to the xAI endpoint.
                return ChatOpenAI(
                    model_name=model_name,
                    openai_api_key=os.getenv("GROK_API_KEY"),
                    openai_api_base="https://api.x.ai/v1",
                    max_tokens=1024
                )
            case _:
                raise ValueError(f"Provider '{provider}' is not supported.")

    except KeyError:
        raise ValueError(f"Tier '{tier}' is not available for provider '{provider}'.")
    except Exception as e:
        logging.error(f"Failed to configure LLM for provider {provider}: {e}")
        raise
