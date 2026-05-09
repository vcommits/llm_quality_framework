import os, sys
from google_auth_oauthlib.flow import InstalledAppFlow

print("OAUTH BOOTSTRAP INITIATED...")

cred_file = os.path.expanduser("~/ghidorah_sentry/credentials.json")
token_file = os.path.expanduser("~/ghidorah_sentry/token.json")

if not os.path.exists(cred_file):
    print("ERROR: Missing credentials.json")
    sys.exit(1)

scopes = ['https://www.googleapis.com/auth/drive.file']
flow = InstalledAppFlow.from_client_secrets_file(cred_file, scopes)

print("Generating URL... DO NOT CLOSE TERMINAL.")

creds = flow.run_local_server(port=0, open_browser=False)

with open(token_file, 'w') as f:
    f.write(creds.to_json())

print("SUCCESS: Saved to token.json")