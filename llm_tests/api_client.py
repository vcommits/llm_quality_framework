# File: llm_tests/api_client.py
# Purpose:  Contains reusable functions to interact with various LLM APIs.

import os
import sys
import requests
import time
import argparse


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
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"API Error (Grok): {response.status_code} - {response.text}", file=sys.stderr)
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
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"API Error (OpenAI): {response.status_code} - {response.text}", file=sys.stderr)
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
    # Anthropic's API structure is slightly different for the payload
    data = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    # Anthropic handles system prompts as a top-level parameter
    if system_prompt:
        data["system"] = system_prompt

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['content'][0]['text'].strip()
        else:
            print(f"API Error (Anthropic): {response.status_code} - {response.text}", file=sys.stderr)
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
        # Gemini uses a specific structure for system instructions
        system_instruction = {"role": "system", "parts": [{"text": system_prompt}]}
        contents.insert(0, system_instruction)

    data = {"contents": contents}

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"API Error (Gemini): {response.status_code} - {response.text}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection Error (Gemini): {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LLM API clients directly.")
    parser.add_argument(
        '--api',
        type=str,
        default='grok',
        choices=['grok', 'openai', 'anthropic', 'gemini'],
        help="Select the API to test."
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help="Run in mock mode."
    )
    parser.add_argument(
        '--model',
        type=str,
        help="Specify the model to use."
    )
    parser.add_argument(
        '--system-prompt',
        type=str,
        default=None,
        help="Define the AI's persona or system-level instructions."
    )
    args = parser.parse_args()

    # --- Select which function to call based on the '--api' flag ---
    if args.api == 'grok':
        model_to_use = args.model or 'grok-3-mini'
        print(f"--- Testing Grok API with model: {model_to_use} ---")
        prompt = "Explain API mocking in one sentence."
        response = call_grok_api(prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock)

    elif args.api == 'openai':
        model_to_use = args.model or 'gpt-3.5-turbo'
        print(f"--- Testing OpenAI API with model: {model_to_use} ---")
        prompt = "Explain what a bearer token is in one sentence."
        response = call_openai_api(prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock)

    elif args.api == 'anthropic':
        model_to_use = args.model or 'claude-3-haiku-20240307'
        print(f"--- Testing Anthropic API with model: {model_to_use} ---")
        prompt = "Explain how to change a bicycle tire in one sentence."
        response = call_anthropic_api(prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock)

    elif args.api == 'gemini':
        model_to_use = args.model or 'gemini-1.5-flash-latest'
        print(f"--- Testing Gemini API with model: {model_to_use} ---")
        prompt = "Explain what an environment variable is in one sentence."
        response = call_gemini_api(prompt, system_prompt=args.system_prompt, model=model_to_use, mock_mode=args.mock)

    # --- Display the result ---
    if response:
        print("\n--- API Response ---")
        print(response)
        print("--------------------")
    else:
        print("\n--- Test failed to get a response ---")
