# File: llm_tests/LLMKeywords.py
# Purpose: A library of custom keywords for Robot Framework to interact with our LLM API client.

from robot.api.deco import keyword
from robot.api import logger
import time
import sqlite3 # Import sqlite3 for database operations
import os # Import os for path manipulation
import uuid # Import uuid for generating unique IDs

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
        logger.error(f"Database error saving response for '{test_case_id}': {e}", exc_info=True)
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

        # Log the raw response for debugging, as suggested in previous steps
        logger.info(f"Raw Response from {provider.upper()} API: {response}")

        return response

    @keyword
    def evaluate_response_for_toxicity(self, test_case_id: str, provider: str, model: str, model_tier: str, test_type: str, prompt: str, system_prompt: str, response_text: str):
        """
        Takes a prompt and response, runs them through the deepeval toxicity evaluator,
        and saves the result to the database. Fails the test if toxicity is found.
        """
        logger.info("Evaluating response for toxicity (DeepEval)...")
        if response_text is None or not isinstance(response_text, str) or not response_text.strip():
            reason = f"Cannot evaluate toxicity: LLM response was invalid or empty. Response: '{response_text}'"
            logger.error(reason)
            # Save partial data to DB even if evaluation couldn't run
            _save_response_to_db(
                test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
                test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response_text,
                mock_mode=False, # Assuming not mock mode if we're evaluating
                evaluation_metric="Toxicity", evaluation_score=None, evaluation_reasoning=reason
            )
            raise AssertionError(reason)

        result = evaluate_toxicity_deepeval(prompt, response_text)

        # Save evaluation result to database
        _save_response_to_db(
            test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
            test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response_text,
            mock_mode=False, # Assuming not mock mode if we're evaluating
            evaluation_metric="Toxicity", evaluation_score=result["score"], evaluation_reasoning=result["reason"]
        )

        if not result["passed"]:
            raise AssertionError(f'Toxicity evaluation failed. Reason: {result["reason"]}')

        logger.info(f'Toxicity evaluation passed. Reason: {result["reason"]}')

    @keyword
    def evaluate_response_for_relevancy(self, test_case_id: str, provider: str, model: str, model_tier: str, test_type: str, prompt: str, system_prompt: str, response_text: str):
        """
        Takes a prompt and response, runs them through the deepeval relevancy evaluator,
        and saves the result to the database. Fails the test if the response is not relevant.
        """
        logger.info("Evaluating response for answer relevancy (DeepEval)...")
        if response_text is None or not isinstance(response_text, str) or not response_text.strip():
            reason = f"Cannot evaluate relevancy: LLM response was invalid or empty. Response: '{response_text}'"
            logger.error(reason)
            # Save partial data to DB even if evaluation couldn't run
            _save_response_to_db(
                test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
                test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response_text,
                mock_mode=False, # Assuming not mock mode if we're evaluating
                evaluation_metric="Relevancy", evaluation_score=None, evaluation_reasoning=reason
            )
            raise AssertionError(reason)

        result = evaluate_answer_relevancy_deepeval(prompt, response_text)

        # Save evaluation result to database
        _save_response_to_db(
            test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
            test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response_text,
            mock_mode=False, # Assuming not mock mode if we're evaluating
            evaluation_metric="Relevancy", evaluation_score=result["score"], evaluation_reasoning=result["reason"]
        )

        if not result["passed"]:
            raise AssertionError(f'Answer Relevancy evaluation failed. Reason: {result["reason"]}')

        logger.info(f'Answer Relevancy evaluation passed. Reason: {result["reason"]}')

    @keyword
    def run_langtest_harness_and_save_results(self, test_case_id: str, provider: str, model: str, model_tier: str, test_type: str, prompt: str, system_prompt: str, response: str, test_config: str, data: list):
        """
        Takes provider, tier, test config (JSON string), data, runs langtest harness,
        and saves the results to the database.
        """
        logger.info(f"Running LangTest Harness for {provider.upper()} ({model})...")

        try:
            # The actual call to run_langtest_harness in test_evaluators.py will parse the test_config string
            results_df = run_langtest_harness(provider, model, test_config, data)

            logger.info(f"LangTest Results:\n{results_df.to_string()}")

            # Assuming langtest results_df has 'test_type', 'pass_rate', 'perturbation_count' columns
            # We'll save the first row's results for simplicity for this test case
            if not results_df.empty:
                first_row = results_df.iloc[0]
                robustness_test_type = first_row.get('test_type', 'Unknown') # e.g., 'typo'
                pass_rate = first_row.get('pass_rate', None)
                perturbation_count = first_row.get('perturbation_count', None) # LangTest might not have this directly

                # Save LangTest results to database
                _save_response_to_db(
                    test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
                    test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response,
                    mock_mode=False, # Assuming not mock mode if running LangTest
                    robustness_test_type=robustness_test_type,
                    pass_rate=pass_rate,
                    perturbation_count=perturbation_count,
                    evaluation_metric="LangTest Robustness", # Indicate this is a LangTest eval
                    evaluation_score=pass_rate # Use pass_rate as evaluation_score for consistency
                )
            else:
                logger.warning(f"LangTest Harness for {test_case_id} returned an empty DataFrame.")
                _save_response_to_db(
                    test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
                    test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response,
                    mock_mode=False,
                    robustness_test_type="N/A", pass_rate=None, perturbation_count=None,
                    evaluation_metric="LangTest Robustness", evaluation_reasoning="Empty results from LangTest."
                )


            all_passed = (results_df['pass_rate'] >= results_df['min_pass_rate']).all()

            if not all_passed:
                failed_tests = results_df[results_df['pass_rate'] < results_df['min_pass_rate']]
                raise AssertionError(f"LangTest evaluation failed:\n{failed_tests.to_string()}")

            logger.info("All LangTest evaluations passed.")

        except Exception as e:
            reason = f"An unexpected error occurred during LangTest Harness execution: {e}"
            logger.error(reason, exc_info=True)
            _save_response_to_db(
                test_case_id=test_case_id, provider=provider, model=model, model_tier=model_tier,
                test_type=test_type, prompt=prompt, system_prompt=system_prompt, response=response,
                mock_mode=False,
                robustness_test_type="Error", pass_rate=None, perturbation_count=None,
                evaluation_metric="LangTest Robustness", evaluation_reasoning=reason
            )
            raise AssertionError(reason) # Fail the Robot test if LangTest execution itself fails
