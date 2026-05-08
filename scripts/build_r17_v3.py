#!/usr/bin/env python3
"""R1.7 v3 — B-arm (protocol-read) co-annotation form.

Same 6 packages as v2, but framed as a re-pass for raters who have read
`rater_protocol_v1.md` separately before the rating session. Tests
whether the score-event decoupling observed in v2 (raters B and C) is
closed when the protocol doc is read offline first.

Q0 (NEW): "Did you read rater_protocol_v1.md before this session?"
  (Yes / No / Partially) — required, dropdown only.
Q1 (NEW): "Your re-pass role" (rater_B / rater_C / other) — explicit
  anonymized labels matching the v2 analysis doc.

Then 6 packages, identical to v2.

Output:
  - human_annotation/recruitment/r17_v3_coannotation_form_url.txt
"""

import json
import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv
load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data/pilot_v1.1/examples"
EXECUTION = ROOT / "data/pilot_v1.1/execution"
PKG_DIR = ROOT / "human_annotation/texts/stage1/R1_7_v2"
FORM_URL_PATH = ROOT / "human_annotation/recruitment/r17_v3_coannotation_form_url.txt"

# same 6 examples as v2
EIDS = ["ad_r1_026", "ad_r1_024", "ad_r1_046", "ad_r1_016", "ad_r1_009", "ad_r1_013"]
CONDITION = "projection_driven"
DIM_NAME = "Citation and scholarship"

ANCHOR_SHARP = """Score by counting CITATION ENGAGEMENT EVENTS in the agent output.
A "citation event" = the agent does ONE of:
  (a) flags a specific citation as missing, wrong, mis-attributed, or mis-classified
  (b) names a specific work the artifact omits and explains why it matters
  (c) audits a specific citation's venue/year/authorship against the source
  (d) suggests a specific insertion with bibliographic precision (author + year + venue)
NOT events:
  - "Please double-check your references" without naming a specific citation
  - Praise of the existing citations
  - Comments on writing, methods, claims, or evidence outside the citation layer

Score (Axis 1 — operational engagement):
  s=1: 0 events; s=2: 1 borderline; s=3: 1 clear; s=4: 2-3 clear; s=5: 4+ clear.

Critical: the score reflects CITATION engagement only. Excellent prose / claim /
method review with ZERO citation events = s=1, not s=4."""

INTRO = f"""R1.7 v3 — B-arm: protocol-read re-pass.

Context: this is a re-pass of the SAME 6 packages from the R1.7 v2 form
(the one you already filled out). The hypothesis being tested: if the rater
reads `rater_protocol_v1.md` SEPARATELY before this session (not just the
embedded anchor), does the score-event mapping become more anchor-aligned?

PREREQUISITE: please read `human_annotation/rater_protocol_v1.md` (sent with
this form link) BEFORE starting. The protocol document contains: counting
convention (cluster-as-1), 4 worked examples (esp. Example A pkg_04 zero-event
case), and a §3.2 list of 6 known-borderline cases with v1 defaults.

Total time: ~30-45 minutes (faster than v2 — same packages, you've seen them).

DIMENSION: {DIM_NAME}

Anchor (sharpened, also in protocol §4):

{ANCHOR_SHARP}

Click Next to begin."""


def parse_package(md_path: Path) -> dict:
    text = md_path.read_text()
    pkg_id = re.search(r"package_id:\s*(\S+)", text).group(1)
    def section(label):
        m = re.search(rf"## {re.escape(label)}.*?\n```\n(.*?)\n```", text, re.DOTALL)
        return m.group(1).strip() if m else ""
    return {
        "pkg_id": pkg_id,
        "delegation": section("A. Delegation (사용자가 agent에게 보낸 요청)"),
        "artifact": section("B. Artifact (저자가 작성한 원본 — 평가 대상이 review한 텍스트)"),
        "agent_output": section("C. Agent output (평가 대상)"),
    }


def get_creds() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"].strip(),
        client_id=os.environ["google_id"].strip(),
        client_secret=os.environ["google_secret"].strip(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/forms.body",
                "https://www.googleapis.com/auth/drive.file"],
    )


SCORE_OPTS = [f"{v:.1f}" for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]]
CONF_OPTS = [f"{v:.1f}" for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
EVENT_OPTS = [str(i) for i in range(0, 11)]
ROLE_OPTS = ["rater_B", "rater_C", "other_peer"]
PROTOCOL_READ_OPTS = ["Yes — read it fully before this session",
                      "Partially — skimmed §2-§4 only",
                      "No — relied on the form-embedded anchor only"]


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n\n[... truncated ...]"


def fmt_body(p: dict) -> str:
    return (f"package_id: {p['pkg_id']}\n\n"
            f"--- DELEGATION ---\n{p['delegation']}\n\n"
            f"--- ARTIFACT ---\n{p['artifact']}\n\n"
            f"--- AGENT OUTPUT (what you score) ---\n{p['agent_output']}\n\n"
            f"--- ANCHOR ({DIM_NAME}) ---\n{ANCHOR_SHARP}")


def main():
    pkg_files = sorted(PKG_DIR.glob("R1_7_v2_pkg_*.md"))
    packages = [parse_package(p) for p in pkg_files]
    print(f"loaded {len(packages)} packages from {PKG_DIR.name}")

    forms = build("forms", "v1", credentials=get_creds())
    title = "R1.7 v3 — B-arm protocol-read re-pass"
    f = forms.forms().create(body={"info": {"title": title}}).execute()
    fid = f["formId"]
    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "updateFormInfo": {"info": {"title": title, "description": INTRO},
                           "updateMask": "title,description"}}]}).execute()

    # Q0: protocol-read confirmation (REQUIRED, DROPDOWN)
    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "createItem": {"item": {
            "title": "Q0 — Did you read rater_protocol_v1.md before this session?",
            "questionItem": {"question": {"required": True,
                "choiceQuestion": {"type": "DROP_DOWN",
                    "options": [{"value": v} for v in PROTOCOL_READ_OPTS]}}}},
            "location": {"index": 0}}}]}).execute()

    # Q1: role (anonymized labels only, no free text option)
    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "createItem": {"item": {
            "title": "Q1 — Your re-pass role (must match your v2 role; if you didn't do v2, pick other_peer)",
            "questionItem": {"question": {"required": True,
                "choiceQuestion": {"type": "DROP_DOWN",
                    "options": [{"value": v} for v in ROLE_OPTS]}}}},
            "location": {"index": 1}}}]}).execute()

    cur = 2
    for i, p in enumerate(packages, 1):
        sb = {"createItem": {"item": {
                "title": f"Rating {i} of {len(packages)} - {p['pkg_id']}",
                "description": truncate(fmt_body(p), 4000),
                "pageBreakItem": {}},
            "location": {"index": cur}}}
        score = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Score (1.0-5.0, 0.5 step)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in SCORE_OPTS]}}}},
            "location": {"index": cur+1}}}
        rationale = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Rationale (quote/paraphrase, 12-600 chars)",
                "questionItem": {"question": {"required": True,
                    "textQuestion": {"paragraph": True}}}},
            "location": {"index": cur+2}}}
        conf = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Confidence (0.0-1.0)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in CONF_OPTS]}}}},
            "location": {"index": cur+3}}}
        events = {"createItem": {"item": {
                "title": f"[{p['pkg_id']}] Event count (your tally of a/b/c/d events; 0-10)",
                "questionItem": {"question": {"required": True,
                    "choiceQuestion": {"type": "DROP_DOWN",
                        "options": [{"value": v} for v in EVENT_OPTS]}}}},
            "location": {"index": cur+4}}}
        forms.forms().batchUpdate(formId=fid, body={"requests": [
            sb, score, rationale, conf, events]}).execute()
        cur += 5
        print(f"  added page {i}/{len(packages)}")

    forms.forms().batchUpdate(formId=fid, body={"requests": [{
        "createItem": {"item": {"title": "Completion",
            "description": "Thank you. Submit and close.",
            "pageBreakItem": {}},
            "location": {"index": cur}}}]}).execute()

    final = forms.forms().get(formId=fid).execute()
    out = {
        "form_id": fid,
        "responder_url": final.get("responderUri"),
        "edit_url": f"https://docs.google.com/forms/d/{fid}/edit",
        "n_packages": len(packages),
        "version": "R1.7_v3_B_arm",
    }
    FORM_URL_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nform meta -> {FORM_URL_PATH.relative_to(ROOT)}")
    print(f"\n=== R1.7 v3 (B-arm) form ===")
    print(f"  responder URL: {out['responder_url']}")
    print(f"  edit URL: {out['edit_url']}")


if __name__ == "__main__":
    main()
