#!/usr/bin/env python3
"""Standalone OAuth helper — RUN THIS ON YOUR LOCAL WINDOWS MACHINE.

Why local? The remote Linux server can't open a browser, and the manual
copy-paste flow is failing silently after consent. This local-server flow
captures the OAuth redirect automatically.

Setup (one-time, on Windows):
    1. Install Python 3.10+
    2. Open PowerShell, run:
         pip install google-auth-oauthlib
    3. Save this file somewhere
    4. Edit lines below — paste your CLIENT_ID and CLIENT_SECRET
       (from Google Cloud Console → Credentials → your Desktop OAuth client)

Run:
    python google_oauth_local.py

The script will:
    - Open your browser to the consent screen
    - Spin up a local server on http://localhost:6577 to receive the redirect
    - After you click Allow, automatically capture the code and exchange for tokens
    - Print the REFRESH_TOKEN to the console

Then paste that REFRESH_TOKEN here so I can save it on the remote server.
"""

# ============================================================
# PASTE YOUR DESKTOP OAUTH CLIENT CREDENTIALS BELOW:
CLIENT_ID = "877943064284-0g77u1gqkl00okpouttrc4t2lcodsrcb.apps.googleusercontent.com"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"
# ============================================================

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:6577"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
creds = flow.run_local_server(
    host="localhost",
    port=6577,
    authorization_prompt_message=(
        "\n>>> Browser will open. Click 'Allow' on the consent screen.\n"
        ">>> If browser does not open, copy this URL manually:\n  {url}\n"
    ),
    success_message="OAuth complete — you can close this browser tab.",
    open_browser=True,
)

print()
print("=" * 70)
print("SUCCESS — copy the line below and send it to Claude:")
print("=" * 70)
print()
print(f"GOOGLE_OAUTH_REFRESH_TOKEN={creds.refresh_token}")
print()
print("=" * 70)
