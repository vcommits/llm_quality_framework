# File: llm_tests/LLMKeywords.py
# Purpose:  Acts as a bridge, exposing our Python API client functions
#           and evaluator functions as keywords that Robot Framework can understand.

from robot.api.deco import keyword
from robot.api import logger
from llm_tests.api_client import call_grok_api, call_openai_api, call_anthropic_api, call_gemini_api
from llm_tests.test_evaluators import evaluate_toxicity


class LLMKeywords:
    """
    This class contains all the custom keywords for interacting with LLM APIs
    and evaluating their responses.
    """

    @keyword(name="Call Grok API")
    def call_grok(self, prompt: str, system_prompt: str = None, model: str = "grok-3-mini", mock_mode: bool = False):
        """A Robot Framework keyword that calls the Grok API."""
        logger.info(f"Calling Grok with prompt: '{prompt[:50]}...'")
        response = call_grok_api(prompt=prompt, system_prompt=system_prompt, model=model, mock_mode=mock_mode)
        return response

    @keyword(name="Call OpenAI API")
    def call_openai(self, prompt: str, system_prompt: str = None, model: str = "gpt-3.5-turbo",
                    mock_mode: bool = False):
        """A Robot Framework keyword that calls the OpenAI API."""
        logger.info(f"Calling OpenAI with prompt: '{prompt[:50]}...'")
        response = call_openai_api(prompt=prompt, system_prompt=system_prompt, model=model, mock_mode=mock_mode)
        return response

    @keyword(name="Call Anthropic API")
    def call_anthropic(self, prompt: str, system_prompt: str = None, model: str = "claude-3-haiku-20240307",
                       mock_mode: bool = False):
        """A Robot Framework keyword that calls the Anthropic API."""
        logger.info(f"Calling Anthropic with prompt: '{prompt[:50]}...'")
        response = call_anthropic_api(prompt=prompt, system_prompt=system_prompt, model=model, mock_mode=mock_mode)
        return response

    @keyword(name="Call Gemini API")
    def call_gemini(self, prompt: str, system_prompt: str = None, model: str = "gemini-1.5-flash-latest",
                    mock_mode: bool = False):
        """A Robot Framework keyword that calls the Gemini API."""
        logger.info(f"Calling Gemini with prompt: '{prompt[:50]}...'")
        response = call_gemini_api(prompt=prompt, system_prompt=system_prompt, model=model, mock_mode=mock_mode)
        return response

    @keyword(name="Response Should Be Non-Toxic")
    def response_should_be_non_toxic(self, response_text: str):
        """
        Evaluates the LLM response for toxicity using our custom evaluator.
        Fails the test if toxic content is found.
        """
        logger.info(f"Evaluating for toxicity: '{response_text[:50]}...'")
        result = evaluate_toxicity(response_text)

        if not result["passed"]:
            # This will cause the Robot Framework test case to fail with a clear message.
            raise AssertionError(f"Toxicity test failed. Reason: {result['reason']}")

        logger.info(f"Toxicity Check Passed. Reason: {result['reason']}")

