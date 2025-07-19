# File: llm_tests/LLMKeywords.py
# Purpose: This file acts as a Robot Framework library, exposing our api_client functions as keywords.

# We import the functions we already built and tested.
from llm_tests.api_client import call_grok_api, call_openai_api, call_anthropic_api, call_gemini_api

class LLMKeywords:
    """
    A library of keywords for interacting with various LLM APIs in Robot Framework.
    """

    def call_grok_api(self, prompt, system_prompt=None, model="grok-3-mini", mock_mode=False):
        """
        A Robot Framework keyword to call the Grok API.
        See the api_client.py file for full documentation.
        """
        print(f"\n-- Executing Keyword: Call Grok API --")
        return call_grok_api(prompt, system_prompt, model, mock_mode)

    def call_openai_api(self, prompt, system_prompt=None, model="gpt-3.5-turbo", mock_mode=False):
        """
        A Robot Framework keyword to call the OpenAI API.
        """
        print(f"\n-- Executing Keyword: Call OpenAI API --")
        return call_openai_api(prompt, system_prompt, model, mock_mode)

    def call_anthropic_api(self, prompt, system_prompt=None, model="claude-3-haiku-20240307", mock_mode=False):
        """
        A Robot Framework keyword to call the Anthropic API.
        """
        print(f"\n-- Executing Keyword: Call Anthropic API --")
        return call_anthropic_api(prompt, system_prompt, model, mock_mode)

    def call_gemini_api(self, prompt, system_prompt=None, model="gemini-1.5-flash-latest", mock_mode=False):
        """
        A Robot Framework keyword to call the Gemini API.
        """
        print(f"\n-- Executing Keyword: Call Gemini API --")
        return call_gemini_api(prompt, system_prompt, model, mock_mode)

