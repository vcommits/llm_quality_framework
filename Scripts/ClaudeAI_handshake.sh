#!/bin/bash
# File: check_anthropic_key.sh
# Purpose: Validates an Anthropic API key using curl from a Bash script.
# This script reads the key from the ANTHROPIC_API_KEY environment variable.

# Check if the ANTHROPIC_API_KEY environment variable is set.
# The "-z" flag checks if the string is empty.
if [ -z "${ANTHROPIC_API_KEY}" ]; then
  # If it's empty, print an error message to the standard error stream (&2) and exit.
  echo "Error: ANTHROPIC_API_KEY environment variable not set." >&2
  exit 1
fi

# Print a status message to the user.
echo "Pinging Anthropic API to validate key..."

# Execute the curl command to make a POST request.
# The command is on a single line to ensure compatibility across different shells.
#
# -s : "silent" mode, hides the progress meter for a cleaner output.
# --ssl-no-revoke : Bypasses a common SSL certificate error on Windows systems.
# -X POST : Specifies that we are making a POST request to send data.
# -H "Header: Value" : Sets a request header. We need three for Anthropic.
# -d '{"json": "data"}' : The '-d' flag specifies the data (payload) to send.
#
curl -s --ssl-no-revoke -X POST "https://api.anthropic.com/v1/messages" -H "x-api-key: ${ANTHROPIC_API_KEY}" -H "anthropic-version: 2023-06-01" -H" "Content-Type: application/json" "-d '{"model": "claude-3-haiku-20240307", "max_tokens": 25, "messages": [{"role": "user", "content": "Say Handshake successful!"}]}'

# The script will output the JSON response from the API if successful,
# or an error from curl if it fails.