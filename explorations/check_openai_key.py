# File: check_key.py
# Purpose:  Validates an OpenAI API key by making a simple request
# The script uses best practices by reading the key from an environment variable.
import os
import sys
import requests

# Get the API key from the environment variable.
API_KEY = os.getenv("OPENAI_API_KEY")

# Check if the key exists.  If not, print an error and exit.
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please follow the instructions in Part 3 of the guide to set it up.")
    sys.exit(1) # Exit the script without an error.


# The specific endpoint for OpenAI's chat models.
url = "https://api.openai.com/v1/chat/completions"

# --- KEY DIFFERENCE 1: AUTHENTICATION HEADER ---
# OpenAI expects the key in an "Authorization" header with the "Bearer" prefix.
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# --- KEY DIFFERENCE 2: PAYLOAD STRUCTURE ---
# The JSON payload has a different structure, specifying the model and a "messages" array.
data = {
    "model": "gpt-3.5-turbo",  # A fast and common model for testing
    "messages": [
        {"role": "user", "content": "Say 'Handshake successful!'"}
    ],
    "max_tokens": 10  # We can limit the response length for a simple test.
}

print("Pinging OpenAI API to validate key...")

try:
    response = requests.post(url, headers=headers, json=data)

    # Check for a successful response (200 OK).
    if response.status_code == 200:
        print("\n🤝 Handshake Successful!")
        # --- KEY DIFFERENCE 3: RESPONSE PARSING ---
        # The response structure is also different.
        response_data = response.json()
        message = response_data['choices'][0]['message']['content']
        print(f"Response from model: {message.strip()}")
    else:
        print("\n🙅 Handshake Failed.")
        print(f"Status Code: {response.status_code}")
        # The error message from OpenAI is usually very informative.
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"\n🙅 Connection Error: {e}")