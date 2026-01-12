# LLM Quality Framework

This framework is designed for evaluating and red-teaming Large Language Models (LLMs). It provides a modular architecture for interacting with various LLM providers (OpenAI, Anthropic, Gemini, Grok) and running evaluations using DeepEval and LangTest.

## Key Components

*   **`llm_tests/providers.py`**:  Abstracts LLM provider interactions (OpenAI, Anthropic, Gemini, Grok).
*   **`llm_tests/api_client.py`**:  Factory for creating configured LangChain chat models.
*   **`llm_tests/database.py`**:  Manages SQLite database for storing responses and evaluation results.
*   **`llm_tests/test_evaluators.py`**:  Contains evaluation logic using DeepEval.
*   **`tests/`**:  Contains Pytest-based test suites (e.g., `test_wnba_scenarios.py`).

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set environment variables for your API keys:
    *   `OPENAI_API_KEY`
    *   `ANTHROPIC_API_KEY`
    *   `GEMINI_API_KEY`
    *   `GROK_API_KEY`
    *   `DEEPEVAL_EVAL_MODEL` (optional, defaults to gpt-4o-mini)

## Running Tests

Use `pytest` to run the test suite:

```bash
pytest tests/test_wnba_scenarios.py
```

## Future Direction

The framework is currently being refactored to move away from Robot Framework and focus on a more flexible, Python-centric approach for orchestration and evaluation.
