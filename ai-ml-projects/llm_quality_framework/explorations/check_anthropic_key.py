# File: check_anthropic_key.py
# Purpose: Validates an Anthropic API key by making a simple request.
# This script uses best practices by reading the key from an environment variable.

import requests
import os
import sys

# Get the API key from the environment variable.
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Check if the key exists. If not, print an error and exit.
if not API_KEY:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    print("Please follow the instructions in the guide to set it up.")
    # sys.exit(1) exits the script with a status code of 1, indicating an error.
    sys.exit(1)

# The specific endpoint for Anthropic's Messages API.
url = "https://api.anthropic.com/v1/messages"

# --- SYNTAX CORRECTION: HEADERS DICTIONARY ---
# A Python dictionary requires "key": "value" pairs.
# Each key and value is a string, and each pair is separated by a comma.
headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# The JSON payload structure is very similar to OpenAI's.
# We use a fast, cost-effective model for this simple handshake test.
data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 25,
    "messages": [
        {"role": "user", "content": "Say 'Handshake successful!'"}
    ]
}

# Updated print statement to be specific to Anthropic.
print("Pinging Anthropic API to validate key...")

try:
    response = requests.post(url, headers=headers, json=data)

    # Check for a successful response (200 OK).
    if response.status_code == 200:
        print("\n🤝 Handshake Successful!")

        # --- SYNTAX CORRECTION: RESPONSE PARSING ---
        # Anthropic's response structure is different from OpenAI's.
        # The content is in a list, and the text is in a 'text' field.
        response_data = response.json()
        message = response_data['content'][0]['text']
        print(f"Response from model: {message.strip()}")
    else:
        print("\n🙅 Handshake Failed.")
        print(f"Status Code: {response.status_code}")
        # Updated comment to be specific to Anthropic.
        # The error message from Anthropic is usually very informative.
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"\n🙅 Connection Error: {e}")