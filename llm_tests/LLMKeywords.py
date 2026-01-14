# File: llm_tests/LLMKeywords.py
# Purpose: A library of custom keywords for Robot Framework to interact with our LLM API client.

from robot.api.deco import keyword
from robot.api import logger
import time
import sqlite3 # Import sqlite3 for database operations
import os # Import os for path manipulation
import uuid # Import uuid for generating unique IDs
import json # IMPORT json for langtest configuration

from llm_tests.api_client import (
    call_grok_api,
    call_openai_api,
    call_anthropic_api,
    call_gemini_api,
    MODEL_TIERS
)
from llm_tests.test_evaluators import (
    evaluate_toxicity_deepeval,
    evaluate_answer_relevancy_deepeval,
    run_langtest_harness
)

# --- Database Configuration ---
DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'llm_responses.db')

def _initialize_db():
    """Initializes the SQLite database and creates the responses table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            test_run_id TEXT NOT NULL,
            test_case_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            model_tier TEXT,
            test_type TEXT NOT NULL,
            prompt TEXT NOT NULL,
            system_prompt TEXT,
            response TEXT NOT NULL,
            mock_mode BOOLEAN NOT NULL,

            -- NEW COLUMNS FOR ADVANCED EVALUATION (DEEPEVAL)
            evaluation_metric TEXT,
            evaluation_score REAL,
            evaluation_reasoning TEXT,

            -- NEW COLUMNS FOR ROBUSTNESS TESTING (LANGTEST)
            robustness_test_type TEXT,
            perturbation_count INTEGER,
            pass_rate REAL
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f"Database '{DATABASE_FILE}' initialized successfully.")

# Initialize the database when the library is loaded
_initialize_db()

# Generate a unique test run ID for this execution
CURRENT_TEST_RUN_ID = str(uuid.uuid4())
logger.info(f"Current Test Run ID: {CURRENT_TEST_RUN_ID}")


def _save_response_to_db(
    test_case_id: str,
    provider: str,
    model: str,
    model_tier: str,
    test_type: str,
    prompt: str,
    system_prompt: str,
    response: str,
    mock_mode: bool,
    evaluation_metric: str = None,
    evaluation_score: float = None,
    evaluation_reasoning: str = None,
    robustness_test_type: str = None,
    perturbation_count: int = None,
    pass_rate: float = None
):
    """Saves a single LLM response and its evaluation results to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO responses (
                test_run_id, test_case_id, provider, model, model_tier, test_type,
                prompt, system_prompt, response, mock_mode,
                evaluation_metric, evaluation_score, evaluation_reasoning,
                robustness_test_type, perturbation_count, pass_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            CURRENT_TEST_RUN_ID, test_case_id, provider, model, model_tier, test_type,
            prompt, system_prompt, response, mock_mode,
            evaluation_metric, evaluation_score, evaluation_reasoning,
            robustness_test_type, perturbation_count, pass_rate
        ))
        conn.commit()
        logger.info(f"Saved response for test_case_id '{test_case_id}' to DB.")
    except sqlite3.Error as e:
        logger.error(f"Database error saving response for '{test_case_id}': {e}")
    finally:
        conn.close()


class LLMKeywords:
    """
    This class exposes our Python API client functions and evaluators as keywords that Robot Framework can use.
    """

    @keyword
    def run_test_against_provider_and_tier(self, provider, tier, prompt, system_prompt=None, mock_mode=False):
        """
        A single, powerful keyword that runs a test against a specific provider and tier.
        It now saves the initial response to the database before running evaluations.
        """
        logger.info(f"Executing test for Provider: {provider.upper()}, Tier: {tier}")

        api_function_map = {
            'grok': call_grok_api,
            'openai': call_openai_api,
            'anthropic': call_anthropic_api,
            'gemini': call_gemini_api
        }

        if provider not in api_function_map:
            raise ValueError(f"Provider '{provider}' is not supported.")

        try:
            model_to_use = MODEL_TIERS[provider][tier]
        except KeyError:
            error_message = f"Tier '{tier}' is not available for provider '{provider}'. Available tiers: {list(MODEL_TIERS[provider].keys())}"
            logger.error(error_message)
            raise ValueError(error_message)

        api_function = api_function_map[provider]

        response = api_function(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model_to_use,
            mock_mode=mock_mode,
            model_tier=tier
        )

        logger.info(f"Raw Response from {provider.upper()} API: {response}")

        # Save the initial response to the database before evaluations
        _save_response_to_db(
            test_case_id=f"{prompt[:50]}-{provider}",
            provider=provider,
            model=model_to_use,
            model_tier=tier,
            test_type="API_Response",
            prompt=prompt,
            system_prompt=system_prompt,
            response=response,
            mock_mode=mock_mode
        )

        return response

    @keyword
    def evaluate_response_for_toxicity(self, prompt: str, response_text: str):
        """
        Takes a prompt and response, runs them through the deepeval toxicity evaluator.
        This keyword will now FAIL the test if toxicity is found.
        """
        logger.info("Evaluating response for toxicity (DeepEval)...")
        if response_text is None or not isinstance(response_text, str) or not response_text.strip():
            raise AssertionError("Cannot evaluate toxicity: LLM response was invalid or empty.")

        # This function will now raise an AssertionError on failure, which will fail the Robot test.
        evaluate_toxicity_deepeval(prompt, response_text)

        logger.info("Toxicity evaluation passed.")

    @keyword
    def evaluate_response_for_relevancy(self, prompt: str, response_text: str):
        """
        Takes a prompt and response, runs them through the deepeval relevancy evaluator.
        This keyword will now FAIL the test if the response is not relevant.
        """
        logger.info("Evaluating response for answer relevancy (DeepEval)...")
        if response_text is None or not isinstance(response_text, str) or not response_text.strip():
            raise AssertionError("Cannot evaluate relevancy: LLM response was invalid or empty.")

        # This function will now raise an AssertionError on failure, which will fail the Robot test.
        evaluate_answer_relevancy_deepeval(prompt, response_text)

        logger.info("Answer Relevancy evaluation passed.")

    @keyword
    def run_robustness_test_with_langtest(self, provider: str, tier: str, prompt: str):
        """
        Performs a "typo" robustness test using LangTest. This will FAIL the test on low pass rate.
        """
        logger.info(f"\n--- Initializing LangTest Robustness Test for {provider.upper()} ({tier}) ---")

        try:
            model_to_use = MODEL_TIERS[provider][tier]
        except KeyError:
            raise ValueError(f"Tier '{tier}' is not available for provider '{provider}'.")

        data = [{'question': prompt, 'expected_response': None}]
        test_config = {
            "tests": {
                "defaults": {"min_pass_rate": 0.90},
                "robustness": {
                    "typo": {"min_pass_rate": 0.85}
                }
            }
        }

        # This function will now raise an AssertionError on failure.
        run_langtest_harness(
            provider=provider,
            model=model_to_use,
            test_config=json.dumps(test_config),
            data=data
        )

        logger.info("--- LangTest Robustness Test Passed ---")
