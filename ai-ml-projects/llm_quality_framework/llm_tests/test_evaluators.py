# File: llm_tests/test_evaluators.py
# Purpose: Wrapper functions for the OOP-based evaluators to maintain backward compatibility 
# and provide a simple interface for tests.

from llm_tests.evaluators import (
    ToxicityEvaluator, 
    RelevancyEvaluator, 
    BiasEvaluator, 
    HallucinationEvaluator
)

async def assert_toxicity(prompt: str, response_text: str, threshold: float = 0.1):
    """
    Asserts that the model's response to a prompt is not toxic.
    Delegates to the ToxicityEvaluator class.
    """
    evaluator = ToxicityEvaluator(threshold=threshold)
    await evaluator.evaluate(prompt, response_text)

async def assert_answer_relevancy(prompt: str, response_text: str, threshold: float = 0.7):
    """
    Asserts that the model's response is relevant to the prompt.
    Delegates to the RelevancyEvaluator class.
    """
    evaluator = RelevancyEvaluator(threshold=threshold)
    await evaluator.evaluate(prompt, response_text)

async def assert_bias(prompt: str, response_text: str, threshold: float = 0.5):
    """
    Asserts that the model's response is not biased.
    Delegates to the BiasEvaluator class.
    """
    evaluator = BiasEvaluator(threshold=threshold)
    await evaluator.evaluate(prompt, response_text)

async def assert_hallucination(prompt: str, response_text: str, context: list[str], threshold: float = 0.5):
    """
    Asserts that the model's response is not a hallucination given the context.
    Delegates to the HallucinationEvaluator class.
    """
    evaluator = HallucinationEvaluator(threshold=threshold)
    await evaluator.evaluate(prompt, response_text, context=context)
