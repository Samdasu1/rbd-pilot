#!/usr/bin/env python3
"""One-time Google OAuth helper.

Generates an authorization URL using GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET
from `~/research-harness/.env`. After the user clicks the URL, signs in, and
grants consent, Google redirects to a (non-running) loopback URL containing
`?code=...`. The user pastes the entire URL back here, and we exchange the
code for a refresh token, then append it to .env.

Scopes requested:
  - forms.body          (create/edit Google Forms)
  - forms.responses     (read responses)
  - drive.file          (manage form files in Drive)

Usage:
    1) python google_oauth_helper.py --start
       → prints auth URL. Open in browser, grant consent.

    2) python google_oauth_helper.py --finish "<full redirect URL>"
       → extracts code, exchanges for refresh token, appends to .env.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

ENV_PATH = Path.home() / "research-harness" / ".env"
load_dotenv(ENV_PATH)

REDIRECT_URI = "http://localhost:6577"

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def _flow() -> Flow:
    # Desktop app credentials (.env lines 35/36, lowercase google_id/google_secret).
    cid = (os.environ.get("google_id") or "").strip()
    csec = (os.environ.get("google_secret") or "").strip()
    if not cid or not csec:
        sys.exit("Desktop app credentials missing in .env (expected google_id and google_secret)")
    client_config = {
        "installed": {
            "client_id": cid,
            "client_secret": csec,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


def start() -> None:
    flow = _flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    print()
    print("=" * 70)
    print("STEP 1: open this URL in your browser:")
    print("=" * 70)
    print()
    print(auth_url)
    print()
    print("=" * 70)
    print("STEP 2: After clicking 'Allow', your browser will fail to connect")
    print("        to 127.0.0.1:8765 (that's expected — no server running).")
    print("        Copy the ENTIRE URL from your browser's address bar")
    print("        (it contains '?code=...&state=...&scope=...') and run:")
    print()
    print('   python scripts/google_oauth_helper.py --finish "<paste-the-url>"')
    print("=" * 70)


def finish(redirect_url: str) -> None:
    parsed = urlparse(redirect_url)
    qs = parse_qs(parsed.query)
    code = qs.get("code", [None])[0]
    if not code:
        sys.exit(f"no `code` parameter found in URL: {redirect_url!r}")

    flow = _flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    if not creds.refresh_token:
        sys.exit("Google did not return a refresh_token. Re-run --start with prompt=consent.")

    # Append to .env if not already there; replace if there
    env_text = ENV_PATH.read_text()
    new_line = f"GOOGLE_OAUTH_REFRESH_TOKEN={creds.refresh_token}"
    lines = env_text.splitlines()
    written = False
    for i, line in enumerate(lines):
        if line.startswith("GOOGLE_OAUTH_REFRESH_TOKEN="):
            lines[i] = new_line
            written = True
            break
    if not written:
        lines.append(new_line)
    ENV_PATH.write_text("\n".join(lines) + "\n")

    print()
    print("✓ refresh_token saved to .env (GOOGLE_OAUTH_REFRESH_TOKEN)")
    print(f"  scopes: {creds.scopes}")
    print(f"  expires (access_token): {creds.expiry}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", action="store_true", help="Print the consent URL.")
    ap.add_argument("--finish", type=str, help="The full redirect URL after consent.")
    args = ap.parse_args()

    if args.start:
        start()
    elif args.finish:
        finish(args.finish)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
