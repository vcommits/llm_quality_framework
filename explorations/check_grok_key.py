# File: check_grok_key.py
# Purpose:  Validates a Grok (xAI) API key by making a simple request.
# The script uses best practices by reading the key from an environment variable.
import os
import sys
import requests

# Get the API key from the environment variable.
# The standard for xAI is often XAI_API_KEY, but we will use what you set.
API_KEY = os.getenv("GROK_API_KEY")

# Check if the key exists.  If not, print an error and exit.
if not API_KEY:
    print("Error: GROK_API_KEY environment variable not set.")
    print("Please ensure the variable is named correctly and you have restarted your terminal/IDE.")
    sys.exit(1) # Exit the script with an error code.


# The specific endpoint for Grok's chat models.
url = "https://api.x.ai/v1/chat/completions"


# --- SYNTAX CORRECTION: HEADERS DICTIONARY ---
# Grok uses the "Bearer" token standard, similar to OpenAI.
# The headers dictionary must use "key": "value" pairs.
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# The JSON payload structure is very similar to OpenAI's.
# We will use a fast model for this simple handshake test.
data = {
    "model": "grok-3-mini",
    "messages": [
        {
            "role": "user",
            "content": "Say 'Handshake successful!'"
        }
    ],
    "stream": False
}


# Updated print statement to be specific to Grok.
print("Pinging Grok (xAI) API to validate key...")

try:
    response = requests.post(url, headers=headers, json=data)

    # Check for a successful response (200 OK).
    if response.status_code == 200:
        print("\n🤝 Handshake Successful!")

        # --- SYNTAX CORRECTION: RESPONSE PARSING ---
        # Grok's response structure is like OpenAI's.
        # The content is in the 'choices' list.
        response_data = response.json()
        message = response_data['choices'][0]['message']['content']
        print(f"Response from model: {message.strip()}")
    else:
        print("\n🙅 Handshake Failed.")
        print(f"Status Code: {response.status_code}")
        # The error message from xAI is usually very informative.
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"\n🙅 Connection Error: {e}")

