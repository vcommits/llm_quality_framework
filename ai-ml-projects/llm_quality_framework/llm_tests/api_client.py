# File: llm_tests/api_client.py
# Purpose: A factory for creating configured LangChain chat model objects for testing.

import logging
from llm_tests.providers import ProviderFactory

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Re-export MODEL_TIERS for backward compatibility if needed, 
# but ideally consumers should use the factory.
MODEL_TIERS = ProviderFactory.MODEL_TIERS

def get_llm_for_evaluation(provider: str, tier: str = 'lite'):
    """
    Factory function to get a configured LangChain chat model.
    Refactored to use the ProviderFactory.
    """
    try:
        provider_instance = ProviderFactory.get_provider(provider, tier, max_tokens=1024)
        return provider_instance.get_model()
    except Exception as e:
        logging.error(f"Failed to configure LLM for provider {provider}: {e}")
        raise

# --- Legacy API Call Functions (for backward compatibility with LLMKeywords.py) ---
# These will be deprecated in favor of direct model usage or a unified invoke method.

def call_openai_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    return _generic_api_call('openai', prompt, system_prompt, model, mock_mode, model_tier)

def call_anthropic_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    return _generic_api_call('anthropic', prompt, system_prompt, model, mock_mode, model_tier)

def call_gemini_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    return _generic_api_call('gemini', prompt, system_prompt, model, mock_mode, model_tier)

def call_grok_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    return _generic_api_call('grok', prompt, system_prompt, model, mock_mode, model_tier)

def _generic_api_call(provider, prompt, system_prompt, model, mock_mode, model_tier):
    if mock_mode:
        return f"Mock response from {provider} ({model})"
    
    # Note: 'model' argument is largely ignored here in favor of 'model_tier' 
    # because the factory handles model selection based on tier.
    # If specific model overrides are needed, the factory would need adjustment.
    
    llm = get_llm_for_evaluation(provider, model_tier)
    
    # LangChain models handle system prompts differently. 
    # For simplicity in this refactor, we'll prepend it if present, 
    # or use proper message construction if we want to be more robust.
    if system_prompt:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
    else:
        response = llm.invoke(prompt)
        
    return response.content
