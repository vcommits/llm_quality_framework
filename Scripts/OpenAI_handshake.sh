#!/bin/bash
# File: check_openai_key.sh
# Purpose: Validates an OpenAI API key using curl from a Bash script.
# This script reads the key from the OPENAI_API_KEY environment variable.

# Check if the OPENAI_API_KEY environment variable is set.
# The "-z" flag checks if the string is empty.
if [ -z "${OPENAI_API_KEY}" ]; then
  # If it's empty, print an error message to the standard error stream (&2) and exit.
  echo "Error: OPENAI_API_KEY environment variable not set." >&2
  exit 1
fi

# Print a status message to the user.
echo "Pinging OpenAI API to validate key..."

# Execute the curl command to make a POST request.
#
# -s : "silent" mode, hides the progress meter for a cleaner output.
# --ssl-no-revoke : Bypasses a common SSL certificate error on Windows systems.
# -X POST : Specifies that we are making a POST request to send data.
# -H "Header: Value" : Sets a request header. We need two:
#   - "Content-Type: application/json" tells the server we are sending JSON data.
#   - "Authorization: Bearer $OPENAI_API_KEY" is the required authentication method.
# -d '{"json": "data"}' : The '-d' flag specifies the data (payload) to send.
#
curl -s --ssl-no-revoke "https://api.openai.com/v1/chat/completions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Say Handshake successful!"
      }
    ],
    "max_tokens": 10
  }'

# The script will output the JSON response from the API if successful,
# or an error from curl if it fails.