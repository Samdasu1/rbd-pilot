#!/usr/bin/env python3
"""Build 9 Stage 1 sub-batch Forms + Prolific drafts (3 dims × 3 sub-batches × 6 ratings).

Sub-batch design (round-robin pairing, spaced cross-condition):
  - 9 examples per dim → 3 trios (1-3, 4-6, 7-9)
  - Each trio's 2 conditions split across 2 different sub-batches:
      sb1 : trio_A direct_naive + trio_C projection_driven
      sb2 : trio_A projection_driven + trio_B direct_naive
      sb3 : trio_B projection_driven + trio_C direct_naive
  - Each sub-batch = 6 packages = 3 direct + 3 projection (balanced)
  - Each example appears in exactly 2 sub-batches (one per condition)
  - Same artifact never repeats within a sub-batch (less cross-contamination)

Outputs:
  - human_annotation/recruitment/stage1_subbatch_form_urls.json (9 entries)
  - human_annotation/recruitment/stage1_subbatch_prolific_drafts.json (9 entries)
"""

from __future__ import annotations

import json
import os
import re
import secrets
import string
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path.home() / "research-harness" / ".env")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build as gbuild

ROOT = Path(__file__).resolve().parents[1]
SAMPLING_PATH = ROOT / "data/pilot_v1.1/_stage1_sampling.json"
STAGE1_DIR = ROOT / "human_annotation/texts/stage1"
FORMS_OUT = ROOT / "human_annotation/recruitment/stage1_subbatch_form_urls.json"
DRAFTS_OUT = ROOT / "human_annotation/recruitment/stage1_subbatch_prolific_drafts.json"

API = "https://api.prolific.com/api/v1"
TOKEN = os.environ["Prolific_api_key"].strip()
H = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
WORKSPACE_ID = "69f74242cd633552920d88dc"
PROJECT_ID = "69f7424cbd0704ff115d828a"

DIM_DESCRIPTIVE = {
    "R1.1": "Conceptual reconstruction",
    "R1.4": "Novelty assessment",
    "R1.7": "Citation and scholarship",
}
DIM_ANCHOR_TEXT = {
    "R1.1": ("s=1  Restates surface phrasing without changing the conceptual object.\n"
             "s=3  Identifies one conceptual issue and proposes a tighter framing, partially supported.\n"
             "s=5  Names the load-bearing concept, shows where the draft drifts from it, and proposes a reframing that survives prior-work contrast."),
    "R1.4": ("s=1  Asserts novelty without specific contrast.\n"
             "s=3  Names one prior work and articulates the delta.\n"
             "s=5  Maps against the nearest 3-5 works; identifies sharp vs rhetorical delta. Proposes positioning text."),
    "R1.7": ("s=1  No citation-level engagement.\n"
             "s=3  Flags one missing or wrong citation.\n"
             "s=5  Audits every load-bearing citation against the source. Flags missing key works in the relevant cluster. Suggests insertions with bibliographic precision."),
}

SCORE_OPTIONS = [f"{v:.1f}" for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]]
CONFIDENCE_OPTIONS = [f"{v:.1f}" for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]

INTRO_TMPL = """Welcome — please read fully before clicking Next.

WHAT YOU WILL DO

You will read 6 short outputs (~600 words each) produced by AI agents that were asked to review academic paper sections. For each output, you will assign a score on a single dimension — {dim_name} — on a 1.0 to 5.0 scale (in 0.5 increments), write a short rationale, and report your confidence.

Total time: ~30 minutes. Reward: see Prolific posting.

This is sub-batch {sb_idx} of 3 for the {dim_name} dimension. After completion, the same researcher may invite you to the next sub-batch.

WHAT YOU MUST NOT DO
  - Do not share the texts, agent outputs, or rubric anchors outside this study.
  - Do not consult external sources. We need YOUR judgment based on the rubric anchors only.
  - Do not copy/paste the same rationale across ratings. Each rationale must specifically reference the agent output you are scoring.

DIMENSION YOU WILL SCORE: {dim_name}

Anchor (re-read for every rating):

{anchor}

Click Next to begin."""

PROLIFIC_DESC_TMPL = """You will read 6 short outputs (~600 words each) produced by AI agents reviewing academic paper sections. For each, you assign a 1.0-5.0 score on the dimension {dim_name}, write a short rationale (12-600 chars), and report your confidence.

Total time: ~30 minutes.

This is sub-batch {sb_idx} of 3 for the {dim_name} dimension. The same researcher may invite you to the next sub-batch.

CONTEXT:
  - Do not share the texts, agent outputs, or rubric anchors outside this study.
  - Do not consult external sources. We need YOUR judgment based on the anchor only.
  - Each rationale must specifically reference the agent output you are scoring."""

REWARD_PER_SUBBATCH = {  # cents — 30 min × $12-14/hr × Prolific minimum
    "R1.7": 600,   # $6
    "R1.4": 600,   # $6
    "R1.1": 500,   # $5
}


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
                "https://www.googleapis.com/auth/forms.responses.readonly",
                "https://www.googleapis.com/auth/drive.file"],
    )


def gen_completion_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n\n[... truncated, see source package ...]"


def _format_body(pkg: dict, dim_name: str, anchor: str) -> str:
    return (f"package_id: {pkg['pkg_id']}\n\n"
            f"━━━ DELEGATION ━━━\n{pkg['delegation']}\n\n"
            f"━━━ ARTIFACT (the paper section the agent reviewed) ━━━\n{pkg['artifact']}\n\n"
            f"━━━ AGENT OUTPUT (what you score) ━━━\n{pkg['agent_output']}\n\n"
            f"━━━ ANCHOR — re-read every rating ━━━\n{dim_name}\n{anchor}")


def round_robin_subbatches(eids: list[str]) -> dict[int, list[tuple[str, str]]]:
    """Round-robin pairing of 9 examples × 2 conditions across 3 sub-batches.

    Returns: {sb_idx -> list of (eid, condition)}
    Each sub-batch: 6 (eid, cond) pairs = 3 direct_naive + 3 projection_driven.
    Each example appears in exactly 2 sub-batches (one per condition).
    """
    assert len(eids) == 9, f"expected 9 eids, got {len(eids)}"
    trio_A = eids[:3]   # in sb1 (direct) + sb2 (projection)
    trio_B = eids[3:6]  # in sb2 (direct) + sb3 (projection)
    trio_C = eids[6:9]  # in sb3 (direct) + sb1 (projection)

    sb1 = [(e, "direct_naive") for e in trio_A] + [(e, "projection_driven") for e in trio_C]
    sb2 = [(e, "projection_driven") for e in trio_A] + [(e, "direct_naive") for e in trio_B]
    sb3 = [(e, "direct_naive") for e in trio_C] + [(e, "projection_driven") for e in trio_B]
    return {1: sb1, 2: sb2, 3: sb3}


def build_form_for_subbatch(forms_service, dim: str, sb_idx: int,
                            packages: list[dict], anchor: str, dim_name: str) -> dict:
    title = f"rbd-pilot Stage 1 — {dim_name} sub-batch {sb_idx} of 3"
    form_obj = forms_service.forms().create(body={"info": {"title": title}}).execute()
    form_id = form_obj["formId"]

    # description
    forms_service.forms().batchUpdate(formId=form_id, body={"requests": [{
        "updateFormInfo": {
            "info": {"title": title, "description": INTRO_TMPL.format(
                dim_name=dim_name, sb_idx=sb_idx, anchor=anchor)},
            "updateMask": "title,description",
        }
    }]}).execute()

    # Prolific ID question first
    forms_service.forms().batchUpdate(formId=form_id, body={"requests": [{
        "createItem": {
            "item": {
                "title": "Your Prolific ID (24 chars; copy-paste from Prolific)",
                "questionItem": {"question": {"required": True, "textQuestion": {"paragraph": False}}},
            },
            "location": {"index": 0},
        }
    }]}).execute()

    # 6 rating sections + 3 questions each (section + score + rationale + confidence)
    cur_index = 1
    total = len(packages)
    for page_idx, pkg in enumerate(packages, 1):
        section_break = {
            "createItem": {
                "item": {
                    "title": f"Rating {page_idx} of {total} — {pkg['pkg_id']}",
                    "description": _truncate(_format_body(pkg, dim_name, anchor), 4000),
                    "pageBreakItem": {},
                },
                "location": {"index": cur_index},
            }
        }
        score = {"createItem": {
            "item": {"title": f"[{pkg['pkg_id']}] Score (1.0–5.0, 0.5 step)",
                     "questionItem": {"question": {"required": True,
                         "choiceQuestion": {"type": "DROP_DOWN",
                             "options": [{"value": v} for v in SCORE_OPTIONS]}}}},
            "location": {"index": cur_index + 1}}}
        rationale = {"createItem": {
            "item": {"title": f"[{pkg['pkg_id']}] Rationale (quote/paraphrase, 12–600 chars)",
                     "questionItem": {"question": {"required": True,
                         "textQuestion": {"paragraph": True}}}},
            "location": {"index": cur_index + 2}}}
        confidence = {"createItem": {
            "item": {"title": f"[{pkg['pkg_id']}] Confidence (0.0–1.0)",
                     "questionItem": {"question": {"required": True,
                         "choiceQuestion": {"type": "DROP_DOWN",
                             "options": [{"value": v} for v in CONFIDENCE_OPTIONS]}}}},
            "location": {"index": cur_index + 3}}}
        forms_service.forms().batchUpdate(formId=form_id, body={"requests": [
            section_break, score, rationale, confidence]}).execute()
        cur_index += 4

    # completion section
    forms_service.forms().batchUpdate(formId=form_id, body={"requests": [{
        "createItem": {
            "item": {
                "title": "Completion",
                "description": ("Thank you for completing this sub-batch.\n\nPlease return to "
                                "Prolific and submit using the completion code shown there."),
                "pageBreakItem": {},
            },
            "location": {"index": cur_index},
        }
    }]}).execute()

    final = forms_service.forms().get(formId=form_id).execute()
    return {
        "dim": dim,
        "sub_batch": sb_idx,
        "form_id": form_id,
        "responder_url": final.get("responderUri"),
        "edit_url": f"https://docs.google.com/forms/d/{form_id}/edit",
        "n_packages": total,
        "package_ids": [p["pkg_id"] for p in packages],
    }


def build_prolific_for_subbatch(dim: str, sb_idx: int, form_url: str) -> dict:
    dim_name = DIM_DESCRIPTIVE[dim]
    cc = gen_completion_code()
    sep = "&" if "?" in form_url else "?"
    external = f"{form_url}{sep}PROLIFIC_PID={{{{%PROLIFIC_PID%}}}}&STUDY_ID={{{{%STUDY_ID%}}}}&SESSION_ID={{{{%SESSION_ID%}}}}"
    payload = {
        "name": f"Stage 1 — {dim_name} sb{sb_idx}/3 (rbd pilot)",
        "internal_name": f"rbd-stage1-{dim.lower()}-sb{sb_idx}",
        "description": PROLIFIC_DESC_TMPL.format(dim_name=dim_name, sb_idx=sb_idx),
        "external_study_url": external,
        "prolific_id_option": "url_parameters",
        "completion_codes": [{"code": cc, "code_type": "COMPLETED",
                              "actions": [{"action": "AUTOMATICALLY_APPROVE"}]}],
        "completion_option": "url",
        "total_available_places": 5,
        "estimated_completion_time": 30,
        "reward": REWARD_PER_SUBBATCH[dim],
        "device_compatibility": ["desktop"],
        "peripheral_requirements": [],
        "filters": [],
        "naivety_distribution_rate": None,
        "project": PROJECT_ID,
        "workspace_id": WORKSPACE_ID,
    }
    r = requests.post(f"{API}/studies/", headers=H, json=payload, timeout=60)
    if not r.ok:
        print(f"  Prolific {dim} sb{sb_idx} ERROR {r.status_code}: {r.text[:300]}", file=sys.stderr)
        r.raise_for_status()
    study = r.json()
    return {
        "dim": dim, "sub_batch": sb_idx,
        "study_id": study["id"],
        "internal_name": study.get("internal_name"),
        "name": study.get("name"),
        "status": study.get("status"),
        "reward_cents": study.get("reward"),
        "completion_code": cc,
        "form_responder_url": form_url,
        "study_admin_url": f"https://app.prolific.com/researcher/workspaces/projects/{PROJECT_ID}/studies/{study['id']}",
    }


def main() -> None:
    sampling = json.loads(SAMPLING_PATH.read_text())
    creds = get_creds()
    forms_service = gbuild("forms", "v1", credentials=creds)

    forms_meta = []
    drafts_meta = []
    for dim in ["R1.7", "R1.4", "R1.1"]:
        eids = sampling["batches"][dim]["selected_ids"]
        sb_assign = round_robin_subbatches(eids)
        anchor = DIM_ANCHOR_TEXT[dim]
        dim_name = DIM_DESCRIPTIVE[dim]

        # Build a quick lookup: (eid, condition) → package dict
        flat_pkgs = {}
        for p in sorted((STAGE1_DIR / dim).glob("*_pkg_*.md")):
            pkg = parse_package(p)
            # cross-ref via _mapping.csv for (eid, condition)
        mapping_path = STAGE1_DIR / "_mapping.csv"
        import csv
        with mapping_path.open() as f:
            for row in csv.DictReader(f):
                if row["batch"] != dim:
                    continue
                pkg_path = STAGE1_DIR / dim / f"{row['package_id']}.md"
                if pkg_path.exists():
                    flat_pkgs[(row["example_id"], row["condition"])] = parse_package(pkg_path)

        for sb_idx in [1, 2, 3]:
            pkg_keys = sb_assign[sb_idx]
            packages = [flat_pkgs[k] for k in pkg_keys if k in flat_pkgs]
            if len(packages) != 6:
                print(f"  WARN {dim} sb{sb_idx}: expected 6 packages, got {len(packages)}")
                continue
            print(f"\n=== {dim} sub-batch {sb_idx} ({len(packages)} packages) ===")
            form_meta = build_form_for_subbatch(forms_service, dim, sb_idx,
                                                packages, anchor, dim_name)
            forms_meta.append(form_meta)
            print(f"  ✓ form: {form_meta['responder_url']}")

            draft_meta = build_prolific_for_subbatch(dim, sb_idx, form_meta["responder_url"])
            drafts_meta.append(draft_meta)
            print(f"  ✓ Prolific draft: {draft_meta['study_id']}  reward=${REWARD_PER_SUBBATCH[dim]/100:.2f}  cc={draft_meta['completion_code']}")

    FORMS_OUT.write_text(json.dumps(forms_meta, indent=2))
    DRAFTS_OUT.write_text(json.dumps(drafts_meta, indent=2))
    print(f"\nWrote {FORMS_OUT.relative_to(ROOT)}")
    print(f"Wrote {DRAFTS_OUT.relative_to(ROOT)}")
    print()
    print("=" * 70)
    print("SUMMARY (9 sub-batches: 3 dims × 3 sb)")
    print("=" * 70)
    for f, d in zip(forms_meta, drafts_meta):
        print(f"  {f['dim']} sb{f['sub_batch']}: form={f['form_id'][:12]}... "
              f"study={d['study_id'][:12]}... reward=${REWARD_PER_SUBBATCH[f['dim']]/100:.2f} "
              f"cc={d['completion_code']}")


if __name__ == "__main__":
    main()
