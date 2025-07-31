# File: llm_tests/test_evaluators.py
# Purpose: Contains functions that use libraries like deepeval and langtest
#          to programmatically "grade" the quality of LLM responses.

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, ToxicityMetric
from deepeval.test_case import LLMTestCase
from deepeval import assert_test  # Corrected import path for DeepEval 3.3.0
import logging
import os
import json  # ADDED: Import json module

# --- Install necessary libraries ---
# If you haven't already, install these:
# pip install deepeval
# pip install langtest[openai,transformers,huggingface]

# CRITICAL FIX: ADD THIS LINE to import Harness from langtest
from langtest import Harness
import pandas as pd  # Already present, but good to note its proximity

# Set up basic logging (optional, but good for seeing more details)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set pandas to display all columns in the terminal for better reporting
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# --- DeepEval Internal LLM Configuration (using an OpenAI model) ---
DEEPEVAL_EVAL_MODEL_NAME = os.getenv("DEEPEVAL_EVAL_MODEL", "gpt-4o-mini")
logging.info(f"DeepEval will attempt to use OpenAI model: '{DEEPEVAL_EVAL_MODEL_NAME}' for evaluations.")

# --- Enable DeepEval's Verbose Mode ---
os.environ["DEEPEVAL_VERBOSE_MODE"] = "True"
logging.info("DeepEval verbose mode is ENABLED.")


def evaluate_toxicity_deepeval(prompt: str, response_text: str, toxicity_threshold: float = 0.5) -> dict:
    """
    Evaluates a response for toxicity using the DeepEval library.
    """
    # Initialize metric and test_case to None to prevent UnboundLocalError
    metric = None
    test_case = None

    # Check for OPENAI_API_KEY for DeepEval's internal LLM
    if not os.getenv("OPENAI_API_KEY"):
        reason = "OPENAI_API_KEY environment variable not set. DeepEval evaluation will likely fail."
        logging.error(reason)
        return {"passed": False, "reason": reason, "score": None}

    logging.info(f"Evaluating toxicity for prompt: '{prompt[:50]}...' and response: '{response_text[:50]}...'")

    try:
        metric = ToxicityMetric(threshold=toxicity_threshold, model=DEEPEVAL_EVAL_MODEL_NAME)
        test_case = LLMTestCase(input=prompt, actual_output=response_text)

        # This function raises AssertionError if the metric fails its threshold
        assert_test(test_case, [metric])

        # --- NEW: Log metric.score and metric.reason immediately after assert_test ---
        logging.info(f"DeepEval Toxicity Metric Raw Score: {metric.score}")
        logging.info(f"DeepEval Toxicity Metric Raw Reason: {metric.reason}")

        # If assert_test does NOT raise an error, the test passed its threshold
        score = metric.score
        # Safely handle metric.reason potentially being None
        reason_text = metric.reason if metric.reason is not None else 'No reason provided.'
        # Safely handle score potentially being None for formatting
        score_display = f"{score:.2f}" if score is not None else "N/A"

        reason = f"DeepEval Toxicity score ({score_display}) is below threshold ({toxicity_threshold}). Reason: {reason_text}"
        logging.info(f"Toxicity evaluation complete. Passed: True, Score: {score_display}, Reason: {reason}")
        return {"passed": True, "reason": reason, "score": score}

    except AssertionError as e:
        # This block catches the AssertionError raised by assert_test
        # It means the metric was calculated, but failed its threshold.
        score = metric.score  # Retrieve the score even if it failed the assertion
        reason_detail = f"DeepEval metric failed threshold. Original error: {e}"
        # Safely handle score potentially being None for formatting
        score_display = f"{score:.2f}" if score is not None else "N/A"
        if score is not None:
            reason_detail += f" (Score: {score_display}, Threshold: {toxicity_threshold})"
        # Safely handle metric.reason potentially being None
        if metric and metric.reason:  # Check if metric is not None before accessing its reason
            reason_detail += f". DeepEval's internal reason: {metric.reason}"
        logging.error(f"Toxicity evaluation failed: {reason_detail}")
        return {"passed": False, "reason": reason_detail, "score": score}

    except Exception as e:
        # This catches any other unexpected errors during the evaluation process
        reason = f"An unexpected error occurred during DeepEval Toxicity evaluation: {e}"
        # Safely try to get the score and reason if metric object exists
        score_val = getattr(metric, 'score', None)
        reason_val = getattr(metric, 'reason', None)

        if score_val is None:
            reason += " (Score was None - potential service/input issue before calculation)."
        if reason_val is not None:
            reason += f" Internal reason: {reason_val}"

        logging.error(reason, exc_info=True)
        return {"passed": False, "reason": reason, "score": score_val}


def evaluate_answer_relevancy_deepeval(prompt: str, response: str, relevancy_threshold: float = 0.7) -> dict:
    """
    Evaluates the relevancy of a response to a given prompt using the DeepEval library.
    """
    # Initialize metric and test_case to None to prevent UnboundLocalError
    metric = None
    test_case = None

    if not os.getenv("OPENAI_API_KEY"):
        reason = "OPENAI_API_KEY environment variable not set. DeepEval evaluation will likely fail."
        logging.error(reason)
        return {"passed": False, "reason": reason, "score": None}

    logging.info(f"Evaluating relevancy for prompt: '{prompt[:50]}...' and response: '{response[:50]}...'")

    try:
        metric = AnswerRelevancyMetric(threshold=relevancy_threshold, model=DEEPEVAL_EVAL_MODEL_NAME)
        test_case = LLMTestCase(input=prompt, actual_output=response)

        assert_test(test_case, [metric])

        score = metric.score
        # Safely handle metric.reason potentially being None
        reason_text = metric.reason if metric.reason is not None else 'No reason provided.'
        # Safely handle score potentially being None for formatting
        score_display = f"{score:.2f}" if score is not None else "N/A"

        reason = f"DeepEval Relevancy score ({score_display}) is above threshold ({relevancy_threshold}). Reason: {reason_text}"
        logging.info(f"Relevancy evaluation complete. Passed: True, Score: {score_display}, Reason: {reason}")
        return {"passed": True, "reason": reason, "score": score}

    except AssertionError as e:
        score = metric.score
        reason_detail = f"DeepEval metric failed threshold. Original error: {e}"
        # Safely handle score potentially being None for formatting
        score_display = f"{score:.2f}" if score is not None else "N/A"
        if score is not None:
            reason_detail += f" (Score: {score_display}, Threshold: {relevancy_threshold})"
        # Safely handle metric.reason potentially being None
        if metric and metric.reason:  # Check if metric is not None before accessing its reason
            reason_detail += f". DeepEval's internal reason: {metric.reason}"
        logging.error(f"Answer Relevancy evaluation failed: {reason_detail}")
        return {"passed": False, "reason": reason_detail, "score": score}

    except Exception as e:
        reason = f"An unexpected error occurred during DeepEval Answer Relevancy evaluation: {e}"
        score_val = getattr(metric, 'score', None)
        reason_val = getattr(metric, 'reason', None)

        if score_val is None:
            reason += " (Score was None - potential service/input issue before calculation)."
        if reason_val is not None:
            reason += f" Internal reason: {reason_val}"

        logging.error(reason, exc_info=True)
        return {"passed": False, "reason": reason, "score": score_val}


def run_langtest_harness(provider: str, model: str, test_config: str,
                         data: list) -> pd.DataFrame:  # Changed test_config type hint to str
    """
    Performs a suite of tests using the LangTest library based on a dynamic configuration.
    test_config is now expected as a JSON string.
    """
    logging.info(f"\n--- Initializing LangTest Harness for {provider.upper()} ({model}) ---")

    try:
        # Parse the JSON string into a Python dictionary
        parsed_test_config = json.loads(test_config)
    except json.JSONDecodeError as e:
        reason = f"Invalid JSON string provided for test_config: {e}"
        logging.error(reason)
        raise ValueError(reason)  # Raise a ValueError that Robot Framework can catch

    # CRITICAL CHANGE: Wrap the list of samples under "data_source" key for in-memory data
    harness = Harness(
        task="question-answering",
        model={"model": model, "hub": provider},
        data={"data_source": data}
    )
    harness.configure(parsed_test_config)  # Use the parsed dictionary
    logging.info("-> Generating test cases...")
    harness.generate()
    logging.info("-> Running tests...")
    harness.run()
    report_df = harness.report(format="dataframe")
    logging.info("--- LangTest Harness Run Complete ---")
    return report_df
