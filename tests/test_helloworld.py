# File: tests/test_hello_world.py
# Purpose: A simple "Hello World" test to ensure pytest is set up correctly
# and can call our API client module.

# --- NEW: Add project root to the Python path ---
# This is a standard pattern to ensure that the test runner can find
# the modules in your 'llm_tests' package, regardless of where you
# run pytest from. It tells Python to look one directory "up" from this file.
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ------------------------------------------------

# We must import the pytest library to use its features.
import pytest

# We import the specific function we want to test from our API client.
# This demonstrates how your test files will use your framework's core logic.
from llm_tests.api_client import call_grok_api


def test_grok_api_mock_call_returns_response():
    """
    This is our first test case.
    Pytest automatically discovers any function that starts with 'test_'.

    Goal: Verify that our call_grok_api function returns a valid string
    when run in mock mode.
    """
    # ARRANGE: Set up the inputs for our function call.
    print("\n--- Test: Hello World for Pytest ---")
    prompt = "This is a test prompt for mock mode."

    # ACT: Call the function we are testing.
    # We explicitly set mock_mode=True to ensure this test is fast,
    # predictable, and does not use real API credits.
    print("Calling call_grok_api in mock mode...")
    response = call_grok_api(prompt, mock_mode=True)

    # ASSERT: Check if the result is what we expect.
    # This is the most important part of any test.
    print(f"Asserting the response: '{response}'")

    # 1. Assert that the function actually returned something (it's not None).
    assert response is not None, "The function should return a response string, not None."

    # 2. Assert that the response is a string.
    assert isinstance(response, str), "The response should be a string."

    # 3. Assert that the response contains expected text from our mock function.
    assert "mocked response" in response.lower(), "The mock response should contain the expected text."

    print("--- Test Passed ---")

