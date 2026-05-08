#!/usr/bin/env python3
"""Build 3 Stage 1 Prolific study drafts via API.

For each dim batch (R1.7, R1.4, R1.1):
  - Title: 'Stage 1 — {dim_name} review (rbd pilot)'
  - External study URL: the dim's Google Form responder URL with PROLIFIC_PID parameter
  - 5 participants, 90 min estimated, baseline reward (user adjusts)
  - Pre-screens: English native, Master's+, ≥95% approval, ≥50 studies
  - Completion code generated unique per batch
  - Status: DRAFT (not submitted) — user reviews + submits manually

Outputs:
  - human_annotation/recruitment/stage1_prolific_drafts.json
"""

from __future__ import annotations

import json
import os
import secrets
import string
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path.home() / "research-harness" / ".env")

ROOT = Path(__file__).resolve().parents[1]
FORMS_PATH = ROOT / "human_annotation/recruitment/stage1_form_urls.json"
OUT_PATH = ROOT / "human_annotation/recruitment/stage1_prolific_drafts.json"

API = "https://api.prolific.com/api/v1"
TOKEN = os.environ["Prolific_api_key"].strip()
HEADERS = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

# Use existing workspace + project
WORKSPACE_ID = "69f74242cd633552920d88dc"     # 'studies'
PROJECT_ID = "69f7424cbd0704ff115d828a"        # existing 'Score AI agent...' project

DIM_DESCRIPTIVE = {
    "R1.1": "Conceptual reconstruction",
    "R1.4": "Novelty assessment",
    "R1.7": "Citation and scholarship",
}

# Baseline rewards in CENTS (Prolific uses minor units). User adjusts at submission.
# Suggested per-batch difficulty: R1.7 high (citation recall), R1.4 mid-high (novelty), R1.1 mid.
BASELINE_REWARD_CENTS = {
    "R1.7": 2100,  # ~$21
    "R1.4": 1800,  # ~$18
    "R1.1": 1500,  # ~$15
}

DESCRIPTION_TMPL = """You will read 18 short outputs (~600 words each) produced by AI agents that were asked to review academic paper sections. For each, you assign a 1.0-5.0 score on the dimension {dim_name}, write a short rationale (12-600 chars), and report your confidence (0.0-1.0).

Before the main 18 ratings, you will complete 2 short calibration tasks (~10 min) so we can verify the rubric is being interpreted consistently. If your calibration scores are too far off, the study ends with partial payment.

Total time: ~90 minutes.

The full anchor text and rubric details are inside the form. Each rating page contains the agent output you score and the anchor (s=1, s=3, s=5) for {dim_name}.

CONTEXT (please read):
- Do not share the texts, agent outputs, or rubric anchors outside this study.
- Do not consult external sources. We need YOUR judgment based on the anchor only.
- Each rationale must specifically reference the agent output you are scoring (no generic praise)."""


def gen_completion_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def build_filters() -> list[dict]:
    """Pre-screen filters using current Prolific API `filters` field.

    NOTE: filter IDs change occasionally; if this stops working, leave empty
    and add filters via Prolific web UI after drafts are created.
    """
    return [
        # Approval rate ≥ 95
        {
            "filter_id": "approval_rate",
            "selected_range": {"lower": 95, "upper": 100},
        },
        # Total studies completed ≥ 50
        {
            "filter_id": "total_approvals",
            "selected_range": {"lower": 50, "upper": 1_000_000},
        },
    ]


def build_study_payload(dim: str, form_url: str, completion_code: str) -> dict:
    dim_name = DIM_DESCRIPTIVE[dim]
    name = f"Stage 1 — {dim_name} (rbd pilot)"
    # Append PROLIFIC_PID parameter to form URL (Prolific replaces token at runtime)
    sep = "&" if "?" in form_url else "?"
    external_url = f"{form_url}{sep}PROLIFIC_PID={{{{%PROLIFIC_PID%}}}}&STUDY_ID={{{{%STUDY_ID%}}}}&SESSION_ID={{{{%SESSION_ID%}}}}"
    return {
        "name": name,
        "internal_name": f"rbd-stage1-{dim.lower()}",
        "description": DESCRIPTION_TMPL.format(dim_name=dim_name),
        "external_study_url": external_url,
        "prolific_id_option": "url_parameters",
        "completion_codes": [
            {
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "AUTOMATICALLY_APPROVE"}],
            }
        ],
        "completion_option": "url",
        "total_available_places": 5,
        "estimated_completion_time": 90,
        "reward": BASELINE_REWARD_CENTS[dim],
        "device_compatibility": ["desktop"],
        "peripheral_requirements": [],
        "filters": [],   # add via web UI: approval_rate ≥ 95, total studies ≥ 50, English first language, Master's+
        "naivety_distribution_rate": None,
        "project": PROJECT_ID,
        "workspace_id": WORKSPACE_ID,
    }


def create_draft(payload: dict) -> dict:
    r = requests.post(f"{API}/studies/", headers=HEADERS, json=payload, timeout=60)
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:500]}", file=sys.stderr)
        r.raise_for_status()
    return r.json()


def main() -> None:
    forms_meta = json.loads(FORMS_PATH.read_text())
    forms_by_dim = {m["dim"]: m for m in forms_meta}

    out = []
    for dim in ["R1.7", "R1.4", "R1.1"]:
        f = forms_by_dim[dim]
        cc = gen_completion_code()
        payload = build_study_payload(dim, f["responder_url"], cc)
        print(f"=== {dim} ({DIM_DESCRIPTIVE[dim]}) ===")
        print(f"  reward: ${BASELINE_REWARD_CENTS[dim]/100:.2f}")
        print(f"  completion code: {cc}")
        print(f"  form URL: {f['responder_url']}")
        try:
            study = create_draft(payload)
            out.append({
                "dim": dim,
                "study_id": study["id"],
                "internal_name": study.get("internal_name"),
                "name": study.get("name"),
                "status": study.get("status"),
                "reward_cents": study.get("reward"),
                "completion_code": cc,
                "form_responder_url": f["responder_url"],
                "form_edit_url": f["edit_url"],
                "study_admin_url": f"https://app.prolific.com/researcher/workspaces/projects/{PROJECT_ID}/studies/{study['id']}",
            })
            print(f"  ✓ draft created. study_id={study['id']}  status={study.get('status')}")
        except Exception as e:
            print(f"  FAIL: {e}", file=sys.stderr)
            out.append({"dim": dim, "error": str(e), "completion_code": cc})

    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nWrote draft metadata: {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
