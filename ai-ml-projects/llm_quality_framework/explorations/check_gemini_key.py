# File: check_key.py
# Purpose: Validates a Gemini API key by making a simple request.
# This script uses best practices by reading the key from an environment variable.

import requests
import os
import sys

# Get the API key from the environment variable.
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if the key exists. If not, print an error and exit.
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please follow the instructions in Part 3 of the guide to set it up.")
    sys.exit(1) # Exit the script with an error code.

# This is a simple endpoint that just lists available models.
# It's a great way to test if your key is valid without sending a full prompt.
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

print("Pinging Gemini API to validate key...")

try:
    # We use a simple GET request since we're just asking for information.
    response = requests.get(url)

    # A "200 OK" status code means the request was successful.
    if response.status_code == 200:
        print("\n🟢 Handshake Successful!")
        print("Your API key is valid and you are connected to the Gemini API.")
        # Optionally, print the models found
        # models = response.json().get('models', [])
        # for model in models:
        #     print(f"- Found model: {model['name']}")
    else:
        # If something went wrong, print the error.
        print("\n🚨 Handshake Failed.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print("\n🚨 Connection Error.")
    print(f"Could not connect to the API. Please check your internet connection. Error: {e}")
