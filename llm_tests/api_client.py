# File: llm_tests/api_client.py
# Purpose:  Contains reusable functions to interact with various LLM APIs.

import os
import sys
import requests
import time
import argparse
from dotenv import load_dotenv
from pathlib import Path

# --- Robustly find and load the .env file ---
# Build a path to the .env file in the project root (one level up from 'llm_tests')
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- Add a check to confirm if the file was found ---
if not env_path.exists():
    print(f"Warning: .env file not found at the expected path: {env_path}", file=sys.stderr)


# A standard, reusable response for mock mode testing
MOCK_RESPONSE = "This is a mock response from the API client."


def _get_mock_response(prompt):
    """A private helper function to generate a fake API response."""
    print("--- MOCK MODE: Returning a fake response. No API call was made. ---")
    if "pirate" in prompt.lower() or "password" in prompt.lower():
        return "Arrr, ye be needin' a new password? That be a tale for the captain, not a humble deckhand like me!"
    else:
        return "This is a mocked response. The real AI would provide a much more detailed answer here."


def call_grok_api(prompt, system_prompt=None, model="grok-3-mini", mock_mode=False):
    """Sends a prompt to the Grok (xAI) API and returns the response."""
    if mock_mode:
        time.sleep(0.5)
        return _get_mock_response(prompt)

    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("Error: GROK_API_KEY environment variable not set.", file=sys.stderr)
        return None

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    data = {"model": model, "messages": messages, "stream": False}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        try:
            return response.json()['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, TypeError) as e:
            print(f"API Error (Grok): Could not parse JSON response. Error: {e}", file=sys.stderr)
            print(f"Response Text: {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection Error (Grok): {e}", file=sys.stderr)
        return None


def call_openai_api(prompt, system_prompt=None, model="gpt-3.5-turbo", mock_mode=False):
    """Sends a prompt to the OpenAI API and returns the response."""
    if mock_mode:
        time.sleep(0.5)
        return _get_mock_response(prompt)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    data = {"model": model, "messages": messages}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        try:
            return response.json()['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, TypeError) as e:
            print(f"API Error (OpenAI): Could not parse JSON response. Error: {e}", file=sys.stderr)
            print(f"Response Text: {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection Error (OpenAI): {e}", file=sys.stderr)
        return None


def call_anthropic_api(prompt, system_prompt=None, model="claude-3-haiku-20240307", mock_mode=False):
    """Sends a prompt to the Anthropic API and returns the response."""
    if mock_mode:
        time.sleep(0.5)
        return _get_mock_response(prompt)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        return None

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = { "model": model, "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}] }
    if system_prompt:
        data["system"] = system_prompt

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        try:
            return response.json()['content'][0]['text'].strip()
        except (KeyError, IndexError, TypeError) as e:
            print(f"API Error (Anthropic): Could not parse JSON response. Error: {e}", file=sys.stderr)
            print(f"Response Text: {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection Error (Anthropic): {e}", file=sys.stderr)
        return None


def call_gemini_api(prompt, system_prompt=None, model="gemini-1.5-flash-latest", mock_mode=False):
    """Sends a prompt to the Google Gemini API and returns the response."""
    if mock_mode:
        time.sleep(0.5)
        return _get_mock_response(prompt)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    if system_prompt:
        system_instruction = {"role": "system", "parts": [{"text": system_prompt}]}
        data = {"system_instruction": system_instruction, "contents": contents}
    else:
        data = {"contents": contents}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        try:
            if 'candidates' not in response.json():
                print(f"API Error (Gemini): 'candidates' not in response.", file=sys.stderr)
                print(f"Response Text: {response.text}", file=sys.stderr)
                return None
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except (KeyError, IndexError, TypeError) as e:
            print(f"API Error (Gemini): Could not parse JSON response. Error: {e}", file=sys.stderr)
            print(f"Response Text: {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection Error (Gemini): {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LLM API clients directly.")
    parser.add_argument('--api', type=str, default='grok', choices=['grok', 'openai', 'anthropic', 'gemini'], help="Select the API to test.")
    parser.add_argument('--mock', action='store_true', help="Run in mock mode.")
    parser.add_argument('--model', type=str, help="Specify the model to use.")
    parser.add_argument('--system-prompt', type=str, default=None, help="Define the AI's persona or system-level instructions.")
    args = parser.parse_args()

    api_map = {
        'grok': ('Grok', call_grok_api, 'grok-3-mini', "Explain API mocking in one sentence."),
        'openai': ('OpenAI', call_openai_api, 'gpt-3.5-turbo', "Explain what a bearer token is in one sentence."),
        'anthropic': ('Anthropic', call_anthropic_api, 'claude-3-haiku-20240307', "Explain how to change a bicycle tire in one sentence."),
        'gemini': ('Gemini', call_gemini_api, 'gemini-1.5-flash-latest', "Explain what an environment variable is in one sentence.")
    }

    api_name, api_func, default_model, default_prompt = api_map[args.api]
    model_to_use = args.model or default_model
    print(f"--- Testing {api_name} API with model: {model_to_use} ---")
    response = api_func(default_prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock)

    if response:
        print("\n--- API Response ---")
        print(response)
        print("--------------------")
    else:
        print("\n--- Test failed to get a response ---")