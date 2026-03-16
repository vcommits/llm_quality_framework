# File: llm_tests/evaluators.py
# Purpose: OOP-based evaluator abstractions for DeepEval metrics.

from abc import ABC, abstractmethod
import os
import logging
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric, 
    ToxicityMetric, 
    BiasMetric, 
    HallucinationMetric, 
    BaseMetric
)
from deepeval.test_case import LLMTestCase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseEvaluator(ABC):
    """Abstract base class for all evaluators."""

    def __init__(self, judge_model=None, threshold: float = 0.5):
        self.threshold = threshold
        # If a custom DeepEvalBaseLLM judge is passed, use it. 
        # Otherwise, DeepEval defaults to GPT-4o-mini if keys are set.
        self.judge_model = judge_model 

    @abstractmethod
    def _get_metric(self) -> BaseMetric:
        """Factory method to return the specific DeepEval metric."""
        pass

    async def evaluate(self, prompt: str, response_text: str, context: list[str] = None):
        """
        Polymorphic method to run the evaluation.
        Common logic for creating the test case and asserting is handled here.
        """
        logging.info(f"Running {self.__class__.__name__} for prompt: '{prompt[:50]}...'")
        
        metric = self._get_metric()
        
        test_case = LLMTestCase(
            input=prompt, 
            actual_output=response_text,
            context=context
        )
        
        # Measure directly instead of using assert_test so we can return the score 
        # without throwing an exception if it fails the threshold.
        await metric.a_measure(test_case)
        
        return {
            "score": metric.score,
            "reason": metric.reason,
            "success": metric.is_successful(),
            "threshold": self.threshold
        }

class ToxicityEvaluator(BaseEvaluator):
    def _get_metric(self) -> BaseMetric:
        return ToxicityMetric(threshold=self.threshold, model=self.judge_model)

class RelevancyEvaluator(BaseEvaluator):
    def _get_metric(self) -> BaseMetric:
        return AnswerRelevancyMetric(threshold=self.threshold, model=self.judge_model)

class BiasEvaluator(BaseEvaluator):
    def _get_metric(self) -> BaseMetric:
        return BiasMetric(threshold=self.threshold, model=self.judge_model)

class HallucinationEvaluator(BaseEvaluator):
    def _get_metric(self) -> BaseMetric:
        return HallucinationMetric(threshold=self.threshold, model=self.judge_model)
