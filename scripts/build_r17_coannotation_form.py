#!/usr/bin/env python3
"""Build R1.7 author + peer co-annotation Form (18 packages, no Prolific).

Single form, no sub-batching. First question identifies annotator role
(author / peer1 / peer2). Then 18 R1.7 packages with score/rationale/confidence.

Output: human_annotation/recruitment/r17_coannotation_form_url.txt
"""

import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
STAGE1_DIR = ROOT / "human_annotation/texts/stage1/R1.7"
OUT_PATH = ROOT / "human_annotation/recruitment/r17_coannotation_form_url.txt"

DIM = "R1.7"
DIM_NAME = "Citation and scholarship"
ANCHOR = ("s=1  No citation-level engagement.\n"
          "s=3  Flags one missing or wrong citation.\n"
          "s=5  Audits every load-bearing citation against the source. Flags "
          "missing key works in the relevant cluster. Suggests insertions with "
          "bibliographic precision.")

SCORE_OPTIONS = [f"{v:.1f}" for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]]
CONFIDENCE_OPTIONS = [f"{v:.1f}" for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]

INTRO = f"""Author + peer co-annotation for R1.7 (Citation and scholarship).

This is an internal evaluation conducted by the paper's author and 1-2 peers (collaborators), in parallel with the Prolific human-eval pilot. Your ratings will form the "expert" arm of a 3-tier qualitative comparison (Prolific allowlist + author + peer) for the paper's Stage 1 anchor on R1.7.

You will see 18 packages = 9 examples × 2 conditions (direct_naive / projection_driven). Each rating: score (1.0-5.0, 0.5 step), rationale (short, must reference agent output), confidence (0.0-1.0).

Total time: ~75-90 minutes.

DIMENSION: {DIM_NAME}

Anchor (re-read on every rating):

{ANCHOR}

Important:
  - Score the AGENT OUTPUT, not the artifact (paper section).
  - Quote/paraphrase agent phrasing in your rationale.
  - For peers: please do not consult the author or other peer until all 18 are submitted.

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


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n\n[... truncated, see source package ...]"


def _format_body(pkg: dict) -> str:
    return (f"package_id: {pkg['pkg_id']}\n\n"
            f"━━━ DELEGATION ━━━\n{pkg['delegation']}\n\n"
            f"━━━ ARTIFACT (the paper section the agent reviewed) ━━━\n{pkg['artifact']}\n\n"
            f"━━━ AGENT OUTPUT (what you score) ━━━\n{pkg['agent_output']}\n\n"
            f"━━━ ANCHOR ({DIM_NAME}) ━━━\n{ANCHOR}")


def main():
    forms = build("forms", "v1", credentials=get_creds())
    title = "R1.7 — Author + Peer Co-annotation (rbd pilot)"
    form_obj = forms.forms().create(body={"info": {"title": title}}).execute()
    fid = form_obj["formId"]

    forms.forms().batchUpdate(formId=fid, body={"requests":[{
        "updateFormInfo": {"info":{"title": title, "description": INTRO},
                           "updateMask":"title,description"}}]}).execute()

    # Annotator role question
    forms.forms().batchUpdate(formId=fid, body={"requests":[{
        "createItem":{"item":{
            "title":"Your role (select one)",
            "questionItem":{"question":{"required":True,
                "choiceQuestion":{"type":"DROP_DOWN",
                    "options":[{"value":v} for v in ["author","peer1","peer2"]]}}}},
            "location":{"index":0}}}]}).execute()

    # Load 18 packages, sorted by example_id then condition
    pkg_files = sorted(STAGE1_DIR.glob("R1_7_pkg_*.md"))
    packages = [parse_package(p) for p in pkg_files]
    print(f"loaded {len(packages)} packages from {STAGE1_DIR.name}")

    cur = 1
    for i, pkg in enumerate(packages, 1):
        section_break = {"createItem":{
            "item":{"title": f"Rating {i} of {len(packages)} — {pkg['pkg_id']}",
                    "description": _truncate(_format_body(pkg), 4000),
                    "pageBreakItem":{}},
            "location":{"index": cur}}}
        score = {"createItem":{
            "item":{"title": f"[{pkg['pkg_id']}] Score (1.0–5.0, 0.5 step)",
                    "questionItem":{"question":{"required":True,
                        "choiceQuestion":{"type":"DROP_DOWN",
                            "options":[{"value":v} for v in SCORE_OPTIONS]}}}},
            "location":{"index": cur+1}}}
        rationale = {"createItem":{
            "item":{"title": f"[{pkg['pkg_id']}] Rationale (quote/paraphrase, 12–600 chars)",
                    "questionItem":{"question":{"required":True,
                        "textQuestion":{"paragraph":True}}}},
            "location":{"index": cur+2}}}
        confidence = {"createItem":{
            "item":{"title": f"[{pkg['pkg_id']}] Confidence (0.0–1.0)",
                    "questionItem":{"question":{"required":True,
                        "choiceQuestion":{"type":"DROP_DOWN",
                            "options":[{"value":v} for v in CONFIDENCE_OPTIONS]}}}},
            "location":{"index": cur+3}}}
        forms.forms().batchUpdate(formId=fid, body={"requests":[
            section_break, score, rationale, confidence]}).execute()
        cur += 4
        if i % 5 == 0:
            print(f"  {i}/{len(packages)} pages added")

    forms.forms().batchUpdate(formId=fid, body={"requests":[{
        "createItem":{"item":{"title":"Completion",
            "description":"Thank you. Submit and close — the response is auto-saved.",
            "pageBreakItem":{}},
            "location":{"index": cur}}}]}).execute()

    final = forms.forms().get(formId=fid).execute()
    out = {
        "form_id": fid,
        "responder_url": final.get("responderUri"),
        "edit_url": f"https://docs.google.com/forms/d/{fid}/edit",
        "n_packages": len(packages),
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\n✓ wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"\n=== R1.7 author+peer co-annotation form ===")
    print(f"  responder URL: {out['responder_url']}")
    print(f"  edit URL: {out['edit_url']}")


if __name__ == "__main__":
    main()
