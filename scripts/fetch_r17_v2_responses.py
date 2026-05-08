#!/usr/bin/env python3
"""Fetch responses from the R1.7 v2 co-annotation form."""
import json, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "human_annotation/recruitment/r17_v2_coannotation_form_url.txt").read_text())
FORM_ID = META["form_id"]

creds = Credentials(
    token=None,
    refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"].strip(),
    client_id=os.environ["google_id"].strip(),
    client_secret=os.environ["google_secret"].strip(),
    token_uri="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/forms.body",
            "https://www.googleapis.com/auth/forms.responses.readonly",
            "https://www.googleapis.com/auth/drive.file"],
)
forms = build("forms", "v1", credentials=creds)

form = forms.forms().get(formId=FORM_ID).execute()
qmap = {}
for item in form.get("items", []):
    qi = item.get("questionItem")
    if not qi: continue
    qid = qi["question"]["questionId"]
    qmap[qid] = item.get("title", "")

resp = forms.forms().responses().list(formId=FORM_ID).execute()
responses = resp.get("responses", [])
print(f"=== {len(responses)} response(s) ===\n")
out = []
for r in responses:
    rec = {"responseId": r.get("responseId"),
           "submittedAt": r.get("lastSubmittedTime"),
           "answers": {}}
    for qid, ans in r.get("answers", {}).items():
        title = qmap.get(qid, qid)
        text_ans = ans.get("textAnswers", {}).get("answers", [])
        rec["answers"][title] = " | ".join(a.get("value","") for a in text_ans)
    out.append(rec)

OUT = ROOT / "human_annotation/recruitment/r17_v2_coannotation_responses.json"
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(f"wrote {OUT.relative_to(ROOT)}")
print(json.dumps(out, indent=2, ensure_ascii=False))
