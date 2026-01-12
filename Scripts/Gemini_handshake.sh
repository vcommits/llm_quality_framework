#!/bin/bash

# The above line tells the system to execute this script with Bash.

# Check if the GEMINI_API_KEY environment variable is set.
# The "-z" flag checks if the string is empty.
if [ -z "${GEMINI_API_KEY}" ]; then
  # If it's empty, print an error message to the standard error stream (&2) and exit.
  echo "Error: GEMINI_API_KEY environment variable not set." >&2
  exit 1
fi

# Print a status message to the user.
echo "Pinging Gemini API to validate key..."

# Execute the curl command.
# We add the '-s' flag to make curl run in "silent" mode, which hides the progress meter.
# We add the '--ssl-no-revoke' flag to bypass the Windows-specific SSL error.
curl -s --ssl-no-revoke "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}"

# The script will output the JSON response from the API if successful,
# or an error from curl if it fails.