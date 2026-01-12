# File: tests/test_wnba_scenarios.py
# Purpose: The primary Pytest test suite for evaluating WNBA-related scenarios.

import pytest
import yaml
from pathlib import Path
from llm_tests.api_client import get_llm_for_evaluation
from llm_tests.test_evaluators import assert_toxicity, assert_answer_relevancy

# --- Test Data Loading ---

def load_prompts():
    """Loads all WNBA prompts from the YAML configuration file."""
    config_path = Path(__file__).parent.parent / 'config' / 'wnba_prompts.yaml'
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    all_prompts = (
        data['wnba_fairness_prompts'] +
        data['wnba_accuracy_prompts'] +
        data['wnba_toxicity_prompts']
    )
    return all_prompts

# --- Test Suite Definition ---

PROVIDERS = ['openai', 'anthropic', 'gemini', 'grok']
PROMPTS = load_prompts()

@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("prompt", PROMPTS)
async def test_wnba_scenario(provider: str, prompt: str):
    """
    A single, data-driven test case that runs for each provider and prompt.
    It evaluates the LLM's response for toxicity and answer relevancy.
    """
    # 1. Get the configured LangChain model for the given provider and tier
    llm = get_llm_for_evaluation(provider, tier='lite')

    # 2. Get the response from the model
    # The entire run will be automatically traced by LangSmith
    response = await llm.ainvoke(prompt)
    response_text = response.content

    # 3. Run assertions on the response text.
    # If any assertion fails, Pytest will automatically mark this test case as FAILED.
    await assert_toxicity(prompt, response_text)
    await assert_answer_relevancy(prompt, response_text)
