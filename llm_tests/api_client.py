# File: llm_tests/api_client.py
# Purpose: Contains reusable functions to interact with various LLM APIs.

import os
import sys
import requests
import time
import argparse
import logging
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log
)

# --- Install necessary libraries ---
# If you haven't already, install these:
# pip install requests tenacity openai anthropic google-generativeai

# Configure logging to output to stderr, which Robot Framework captures well.
# Set level to INFO to see general progress, WARNING for issues, ERROR for critical failures.
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Model Tier Mapping ---
# This dictionary maps the user-friendly tier names to specific model IDs for each provider.
MODEL_TIERS = {
    'grok': {
        'lite': 'grok-3-mini',
        'full': 'grok-4'
    },
    'openai': {
        'lite': 'gpt-3.5-turbo',
        'mid': 'gpt-4o-mini',
        'full': 'gpt-4o'
    },
    'anthropic': {
        'lite': 'claude-3-haiku-20240307',
        'mid': 'claude-3.5-sonnet-20240620',
        'full': 'claude-3-opus-20240229'
    },
    'gemini': {
        'lite': 'gemini-1.5-flash-latest',
        'mid': 'gemini-1.5-pro-latest',
        'full': 'gemini-1.5-pro-latest'
    }
}

# --- Default Max Tokens for LLM Responses ---
# Adjust these based on typical expected response length and model limits.
# These values help prevent "length limit was reached" errors.
DEFAULT_MAX_TOKENS = {
    'grok': 1024,
    'openai': 1024,  # Can be increased for models like gpt-4o if longer responses are expected
    'anthropic': 1024,
    'gemini': 1024
}


def _get_mock_response(prompt):
    """A private helper function to generate a fake API response."""
    logging.info("--- MOCK MODE: Returning a fake response. No API call was made. ---")
    time.sleep(0.1)  # Simulate a small delay for mock calls
    if "pirate" in prompt.lower() or "password" in prompt.lower():
        return "Arrr, ye be needin' a new password? That be a tale for the captain, not a humble deckhand like me!"
    else:
        return f"This is a mocked response to your prompt: '{prompt}'"


# --- Common Retry Decorator for requests-based APIs (Grok, Gemini) ---
# This decorator will automatically retry API calls that fail due to transient issues
# like network errors (ConnectionError, Timeout) or HTTP 429/5xx status codes.
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),  # Wait 4s, 8s, 16s... up to 60s between retries
    stop=stop_after_attempt(5),  # Max 5 attempts (1 original + 4 retries)
    retry=retry_if_exception_type(requests.exceptions.ConnectionError) |
          retry_if_exception_type(requests.exceptions.Timeout) |
          retry_if_exception_type(requests.exceptions.HTTPError),  # Catch HTTP 4xx/5xx errors
    before_sleep=before_sleep_log(logging.getLogger(), logging.INFO),  # Log before sleeping
    reraise=True  # Re-raise the last exception if all retries fail
)
def _make_request_with_retry(method, url, headers, json_data, timeout=120):  # Increased timeout to 120 seconds
    """Helper to make an HTTP request with retry logic."""
    response = requests.request(method, url, headers=headers, json=json_data, timeout=timeout)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response


# --- API Client Functions with enhanced retry and error handling ---

def call_grok_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    """Sends a prompt to the Grok (xAI) API and returns the response."""
    if mock_mode:
        return _get_mock_response(prompt)

    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        logging.error("GROK_API_KEY environment variable not set. Cannot call Grok API.")
        return None

    # Determine the actual model to use based on provided model or tier
    actual_model = model if model else MODEL_TIERS['grok'].get(model_tier, MODEL_TIERS['grok']['lite'])
    logging.info(f"Calling Grok API with model: {actual_model}")

    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    data = {
        "model": actual_model,
        "messages": messages,
        "stream": False,
        "max_tokens": DEFAULT_MAX_TOKENS['grok']  # Set max_tokens to prevent length limit issues
    }

    try:
        response = _make_request_with_retry("POST", url, headers=headers, json_data=data)
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_detail = e.response.text
        if status_code == 429:
            logging.error(f"Grok API Rate Limit Exceeded (429) after retries. Details: {error_detail}")
        else:
            logging.error(f"Grok API Error ({status_code}) after retries. Details: {error_detail}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error calling Grok API: {e}", exc_info=True)
        return None


def call_openai_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    """Sends a prompt to the OpenAI API and returns the response."""
    if mock_mode:
        return _get_mock_response(prompt)

    # Using OpenAI's official Python client, which has built-in retry logic with exponential backoff
    # for transient errors like rate limits and server errors.
    # https://github.com/openai/openai-python/blob/main/openai/_base_client.py
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY environment variable not set. Cannot call OpenAI API.")
        return None

    # Determine the actual model to use based on provided model or tier
    actual_model = model if model else MODEL_TIERS['openai'].get(model_tier, MODEL_TIERS['openai']['lite'])
    logging.info(f"Calling OpenAI API with model: {actual_model}")

    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=actual_model,
            messages=messages,
            max_tokens=DEFAULT_MAX_TOKENS['openai']  # Set max_tokens to prevent length limit issues
        )
        return response.choices[0].message.content.strip()
    except openai.APIStatusError as e:
        status_code = e.status_code
        error_message = e.response.json().get('error', {}).get('message', 'No message provided.')
        if status_code == 429:
            logging.error(f"OpenAI API Rate Limit Exceeded (429). Message: {error_message}")
        elif status_code == 400 and "length limit was reached" in error_message:
            logging.error(
                f"OpenAI API: Response content length limit reached. Consider increasing max_tokens if this is expected. Message: {error_message}")
        else:
            logging.error(f"OpenAI API Error ({status_code}): {error_message}", exc_info=True)
        return None
    except openai.APITimeoutError as e:
        logging.error(f"OpenAI API Timeout Error: {e}", exc_info=True)
        return None
    except openai.APIConnectionError as e:
        logging.error(f"OpenAI API Connection Error: {e}", exc_info=True)
        return None
    except openai.AuthenticationError as e:
        logging.error(f"OpenAI API Authentication Error: {e}. Check your OPENAI_API_KEY.", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error calling OpenAI API: {e}", exc_info=True)
        return None


def call_anthropic_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    """Sends a prompt to the Anthropic API and returns the response."""
    if mock_mode:
        return _get_mock_response(prompt)

    # Using Anthropic's official Python client, which has built-in retry logic with exponential backoff
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("ANTHROPIC_API_KEY environment variable not set. Cannot call Anthropic API.")
        return None

    # Determine the actual model to use based on provided model or tier
    actual_model = model if model else MODEL_TIERS['anthropic'].get(model_tier, MODEL_TIERS['anthropic']['lite'])
    logging.info(f"Calling Anthropic API with model: {actual_model}")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        messages = [{"role": "user", "content": prompt}]

        # Anthropic's system prompt is a direct parameter to messages.create
        response = client.messages.create(
            model=actual_model,
            max_tokens=DEFAULT_MAX_TOKENS['anthropic'],  # Set max_tokens to prevent length limit issues
            messages=messages,
            system=system_prompt if system_prompt else anthropic.NOT_GIVEN  # Use NOT_GIVEN for optional params
        )
        return response.content[0].text.strip()
    except anthropic.APIStatusError as e:
        status_code = e.status_code
        error_message = e.response.json().get('error', {}).get('message', 'No message provided.')
        if status_code == 429:
            logging.error(f"Anthropic API Rate Limit Exceeded (429). Message: {error_message}")
        else:
            logging.error(f"Anthropic API Error ({status_code}): {error_message}", exc_info=True)
        return None
    except anthropic.APITimeoutError as e:
        logging.error(f"Anthropic API Timeout Error: {e}", exc_info=True)
        return None
    except anthropic.APIConnectionError as e:
        logging.error(f"Anthropic API Connection Error: {e}", exc_info=True)
        return None
    except anthropic.AuthenticationError as e:
        logging.error(f"Anthropic API Authentication Error: {e}. Check your ANTHROPIC_API_KEY.", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error calling Anthropic API: {e}", exc_info=True)
        return None


def call_gemini_api(prompt, system_prompt=None, model=None, mock_mode=False, model_tier='lite'):
    """Sends a prompt to the Google Gemini API and returns the response."""
    if mock_mode:
        return _get_mock_response(prompt)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set. Cannot call Gemini API.")
        return None

    # Determine the actual model to use based on provided model or tier
    actual_model = model if model else MODEL_TIERS['gemini'].get(model_tier, MODEL_TIERS['gemini']['lite'])
    logging.info(f"Calling Gemini API with model: {actual_model}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{actual_model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    contents = []
    if system_prompt:
        # Gemini system instruction is typically handled as a "user" role followed by a "model" response
        # to establish the persona/context, then the actual user prompt.
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "model", "parts": [{"text": "OK"}]})  # Model acknowledges system instruction
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    data = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": DEFAULT_MAX_TOKENS['gemini']  # Set max_tokens to prevent length limit issues
        }
    }

    try:
        response = _make_request_with_retry("POST", url, headers=headers, json_data=data)
        response_json = response.json()
        # Robustly check for the existence of keys before accessing them
        if 'candidates' in response_json and response_json['candidates']:
            candidate = response_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                return candidate['content']['parts'][0]['text'].strip()

        # If the expected structure is not found, log a warning and return None
        logging.warning(f"Gemini API: Unexpected response structure or empty content. Full response: {response.text}")
        return None
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_detail = e.response.text
        if status_code == 429:
            logging.error(f"Gemini API Rate Limit Exceeded (429) after retries. Details: {error_detail}")
        else:
            logging.error(f"Gemini API Error ({status_code}) after retries. Details: {error_detail}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Unexpected error calling Gemini API: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LLM API clients directly.")
    parser.add_argument('--api', type=str, default='grok', choices=['grok', 'openai', 'anthropic', 'gemini', 'all'],
                        help="Select the API to test, or 'all'.")
    parser.add_argument('--mock', action='store_true', help="Run in mock mode.")
    parser.add_argument('--model', type=str, help="Specify a model ID to override the tier selection.")
    parser.add_argument('--tier', type=str, default='lite', choices=['lite', 'mid', 'full'],
                        help="Select the model tier to use.")
    parser.add_argument('--system-prompt', type=str, default=None, help="Define the AI's persona.")
    parser.add_argument('--prompt', type=str, default="Explain what a unit test is in one sentence.",
                        help="The prompt to send to the API.")

    args = parser.parse_args()

    api_function_map = {
        'grok': call_grok_api,
        'openai': call_openai_api,
        'anthropic': call_anthropic_api,
        'gemini': call_gemini_api
    }

    if args.api == 'all':
        logging.info(f"--- Testing ALL providers in tier: '{args.tier}' ---")
        for provider_name, api_function in api_function_map.items():
            model_to_use = args.model
            if not model_to_use:
                try:
                    model_to_use = MODEL_TIERS[provider_name][args.tier]
                except KeyError:
                    logging.warning(f"\n--- Skipping {provider_name.upper()}: Tier '{args.tier}' not available. ---")
                    continue

            logging.info(f"\n--- Testing {provider_name.upper()} with model: {model_to_use} ---")
            response = api_function(args.prompt, system_prompt=args.system_prompt, model=model_to_use,
                                    mock_mode=args.mock,
                                    model_tier=args.tier)
            if response:
                logging.info(f"Response: {response}")
            else:
                logging.error("-> Test failed to get a response.")

            if not args.mock:
                # Add a small delay between *providers* to be nice to APIs, even with backoff
                # Backoff handles retries *within* a single API call, this is for calls across different providers
                time.sleep(5)

    else:
        # --- Existing logic for testing a single API ---
        model_to_use = args.model
        if not model_to_use:
            try:
                model_to_use = MODEL_TIERS[args.api][args.tier]
            except KeyError:
                logging.warning(
                    f"Warning: Tier '{args.tier}' not available for API '{args.api}'. Falling back to 'lite' tier.")
                model_to_use = MODEL_TIERS[args.api]['lite']

        api_function = api_function_map[args.api]
        logging.info(f"--- Testing {args.api.upper()} API with model: {model_to_use} (Tier: {args.tier}) ---")
        response = api_function(args.prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock,
                                model_tier=args.tier)

        if response:
            logging.info("\n--- API Response ---")
            logging.info(response)
            logging.info("--------------------")
        else:
            logging.error("\n--- Test failed to get a response ---")