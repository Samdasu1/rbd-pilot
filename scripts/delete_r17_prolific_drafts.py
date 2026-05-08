#!/usr/bin/env python3
"""Delete R1.7 sb1/sb2/sb3 Prolific drafts + matching Google Forms.

Per 2026-05-07 Stage 1 closure decision: R1.7 Prolific arm is dropped.
Only the v2 author/peer co-annotation form (separate, already in use) is kept.
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
PROLIFIC_TOKEN = os.environ["Prolific_api_key"].strip()
PROLIFIC_BASE = "https://api.prolific.com/api/v1"

drafts = json.load((ROOT / "human_annotation/recruitment/stage1_subbatch_prolific_drafts.json").open())
forms_meta = json.load((ROOT / "human_annotation/recruitment/stage1_subbatch_form_urls.json").open())

r17_studies = [d for d in drafts if d.get("dim") == "R1.7"]
r17_forms = [f for f in forms_meta if f.get("dim") == "R1.7"]

print(f"R1.7 Prolific studies to delete: {len(r17_studies)}")
print(f"R1.7 Google Forms to delete: {len(r17_forms)}")

# 1. Delete Prolific studies (DELETE /api/v1/studies/{id}/)
for s in r17_studies:
    sid = s["study_id"]
    url = f"{PROLIFIC_BASE}/studies/{sid}/"
    r = requests.delete(url, headers={"Authorization": f"Token {PROLIFIC_TOKEN}"})
    if r.status_code in (204, 200, 404):
        print(f"  prolific {sid} ({s['dim']} sb{s['sub_batch']}) deleted (status {r.status_code})")
    else:
        print(f"  prolific {sid} ERR {r.status_code}: {r.text[:200]}")

# 2. Delete Google Forms (Drive API)
creds = Credentials(
    token=None,
    refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"].strip(),
    client_id=os.environ["google_id"].strip(),
    client_secret=os.environ["google_secret"].strip(),
    token_uri="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/drive.file"],
)
drive = build("drive", "v3", credentials=creds)
for f in r17_forms:
    fid = f["form_id"]
    try:
        drive.files().delete(fileId=fid).execute()
        print(f"  drive form {fid} ({f['dim']} sb{f['sub_batch']}) deleted")
    except Exception as e:
        msg = str(e)[:200]
        print(f"  drive form {fid} ERR: {msg}")

# 3. Update local manifests — remove R1.7 entries
remaining_drafts = [d for d in drafts if d.get("dim") != "R1.7"]
remaining_forms = [f for f in forms_meta if f.get("dim") != "R1.7"]
(ROOT / "human_annotation/recruitment/stage1_subbatch_prolific_drafts.json").write_text(
    json.dumps(remaining_drafts, indent=2))
(ROOT / "human_annotation/recruitment/stage1_subbatch_form_urls.json").write_text(
    json.dumps(remaining_forms, indent=2))
print(f"\nlocal manifests updated. remaining drafts: {len(remaining_drafts)}, forms: {len(remaining_forms)}")
