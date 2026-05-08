#!/usr/bin/env python3
"""Build 3 Stage 1 Google Forms via Forms API.

For each dim batch (R1.7, R1.4, R1.1):
  - Form title + description
  - Section 1: intro + agreement (consent checkbox + Prolific ID short text)
  - Sections 2..19: one section per package (18 ratings).
    Each rating section embeds the package content (delegation, artifact,
    agent output, anchor) as section description, then asks:
      - Score (multiple-choice 1.0/1.5/.../5.0)
      - Rationale (long answer)
      - Confidence (multiple-choice 0.0/0.1/.../1.0)
      - Blockers (short answer, optional)
  - Section 20: completion + Prolific completion code

Each form's responder URL is printed at the end.
"""

from __future__ import annotations

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
STAGE1_DIR = ROOT / "human_annotation/texts/stage1"
CALIBRATIONS_PATH = ROOT / "human_annotation/recruitment/stage1_calibrations.json"
OUT_PATH = ROOT / "human_annotation/recruitment/stage1_form_urls.json"

DIM_DESCRIPTIVE = {
    "R1.1": "Conceptual reconstruction",
    "R1.4": "Novelty assessment",
    "R1.7": "Citation and scholarship",
}

DIM_ANCHOR_TEXT = {
    "R1.1": ("s=1  Restates surface phrasing without changing the conceptual "
             "object. Adds no framing improvement.\n\n"
             "s=3  Identifies one conceptual issue and proposes a tighter "
             "framing, partially supported.\n\n"
             "s=5  Names the load-bearing concept, shows where the draft drifts "
             "from it, and proposes a reframing that survives prior-work contrast."),
    "R1.4": ("s=1  Asserts novelty without specific contrast.\n\n"
             "s=3  Names one prior work and articulates the delta.\n\n"
             "s=5  Maps against the nearest 3-5 works; identifies sharp vs "
             "rhetorical delta. Proposes positioning text."),
    "R1.7": ("s=1  No citation-level engagement.\n\n"
             "s=3  Flags one missing or wrong citation.\n\n"
             "s=5  Audits every load-bearing citation against the source. Flags "
             "missing key works in the relevant cluster. Suggests insertions "
             "with bibliographic precision."),
}

INTRO_DESCRIPTION_TMPL = """Welcome — please read fully before clicking Next.

WHAT YOU WILL DO

You will read 18 short outputs (~600 words each) produced by AI agents that were asked to review academic paper sections. For each output, you will assign a score on a single dimension — {dim_name} — on a 1.0 to 5.0 scale (in 0.5 increments).

Total time: ~90 minutes. Reward: see Prolific posting.

WHAT YOU MUST NOT DO

  - Do not share the texts, agent outputs, or rubric anchors outside this study (this is pre-publication internal research material).
  - Do not consult external sources to "look up" what the right answer should be. We need YOUR judgment based on the rubric anchors only.
  - Do not copy/paste the same rationale across ratings. Each rationale must specifically reference the agent output you are scoring.

DIMENSION YOU WILL SCORE: {dim_name}

Anchor (memorize the verbs):

{anchor}

Click Next to begin."""

SCORE_OPTIONS = [f"{v:.1f}" for v in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]]
CONFIDENCE_OPTIONS = [f"{v:.1f}" for v in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]


def get_creds() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"].strip(),
        client_id=os.environ["google_id"].strip(),
        client_secret=os.environ["google_secret"].strip(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=[
            "https://www.googleapis.com/auth/forms.body",
            "https://www.googleapis.com/auth/forms.responses.readonly",
            "https://www.googleapis.com/auth/drive.file",
        ],
    )


def parse_package(md_path: Path) -> dict:
    """Extract delegation/artifact/agent_output from package markdown."""
    text = md_path.read_text()
    pkg_id_match = re.search(r"package_id:\s*(\S+)", text)
    pkg_id = pkg_id_match.group(1) if pkg_id_match else md_path.stem

    def extract_section(label: str) -> str:
        m = re.search(rf"## {re.escape(label)}.*?\n```\n(.*?)\n```", text, re.DOTALL)
        return m.group(1).strip() if m else ""

    return {
        "pkg_id": pkg_id,
        "delegation": extract_section("A. Delegation (사용자가 agent에게 보낸 요청)"),
        "artifact": extract_section("B. Artifact (저자가 작성한 원본 — 평가 대상이 review한 텍스트)"),
        "agent_output": extract_section("C. Agent output (평가 대상)"),
    }


def build_rating_section(pkg: dict, anchor_text: str, dim_name: str, page_idx: int, total: int) -> list[dict]:
    """Returns a list of `requests` for one rating page (1 section + 4 questions)."""
    body_block = (
        f"Rating {page_idx} of {total}\n"
        f"package_id: {pkg['pkg_id']}\n\n"
        f"DELEGATION (request to the agent):\n{pkg['delegation']}\n\n"
        f"ARTIFACT (the paper section the agent reviewed):\n{pkg['artifact']}\n\n"
        f"AGENT OUTPUT (what you score):\n{pkg['agent_output']}\n\n"
        f"ANCHOR (re-read for every rating):\n{dim_name}\n{anchor_text}"
    )
    # Forms API has a 4096-char limit on description; truncate if needed.
    MAX_DESC = 4000
    if len(body_block) > MAX_DESC:
        body_block = body_block[:MAX_DESC] + "\n\n[... truncated; full content was here ...]"

    section_request = {
        "createItem": {
            "item": {
                "title": f"Rating {page_idx} of {total} — {pkg['pkg_id']}",
                "description": body_block,
                "pageBreakItem": {},
            },
            "location": {"index": page_idx * 4 - 4},  # rough; Forms API places at index
        }
    }
    score_request = {
        "createItem": {
            "item": {
                "title": f"[{pkg['pkg_id']}] Score (1.0 to 5.0, 0.5 increments)",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "DROP_DOWN",
                            "options": [{"value": v} for v in SCORE_OPTIONS],
                        },
                    }
                },
            },
            "location": {"index": page_idx * 4 - 3},
        }
    }
    rationale_request = {
        "createItem": {
            "item": {
                "title": f"[{pkg['pkg_id']}] Rationale (must quote or paraphrase the agent output, 12–600 chars)",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {"paragraph": True},
                    }
                },
            },
            "location": {"index": page_idx * 4 - 2},
        }
    }
    confidence_request = {
        "createItem": {
            "item": {
                "title": f"[{pkg['pkg_id']}] Confidence (0.0 to 1.0)",
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "DROP_DOWN",
                            "options": [{"value": v} for v in CONFIDENCE_OPTIONS],
                        },
                    }
                },
            },
            "location": {"index": page_idx * 4 - 1},
        }
    }
    return [section_request, score_request, rationale_request, confidence_request]


def build_form(forms_service, dim: str, packages: list[dict]) -> dict:
    """Create one form for one dim batch and return its metadata."""
    title = f"rbd-pilot Stage 1 — {DIM_DESCRIPTIVE[dim]} (batch {dim})"
    # Step 1: Create form (title + document title only at creation time).
    form_obj = forms_service.forms().create(body={"info": {"title": title}}).execute()
    form_id = form_obj["formId"]
    print(f"  created form id={form_id}")

    # Step 2: Update form description (must use updateFormInfo with description).
    desc_request = {
        "updateFormInfo": {
            "info": {
                "title": title,
                "description": INTRO_DESCRIPTION_TMPL.format(
                    dim_name=DIM_DESCRIPTIVE[dim],
                    anchor=DIM_ANCHOR_TEXT[dim],
                ),
            },
            "updateMask": "title,description",
        }
    }
    forms_service.forms().batchUpdate(
        formId=form_id, body={"requests": [desc_request]}
    ).execute()

    # Step 3: Add an initial Prolific-ID short-answer question, then per-package sections.
    prolific_id_q = {
        "createItem": {
            "item": {
                "title": "Your Prolific ID (24 chars; copy-paste from Prolific)",
                "questionItem": {
                    "question": {
                        "required": True,
                        "textQuestion": {"paragraph": False},
                    }
                },
            },
            "location": {"index": 0},
        }
    }
    forms_service.forms().batchUpdate(
        formId=form_id, body={"requests": [prolific_id_q]}
    ).execute()

    # Calibration sections REMOVED per user decision (multi-rater α + Prolific
    # time-on-task + rationale spot-check are sufficient quality signals).
    anchor_text = DIM_ANCHOR_TEXT[dim]
    dim_name = DIM_DESCRIPTIVE[dim]
    cur_index = 1  # already used index 0 for prolific id

    cals = []   # disabled — kept loop structure for minimal diff
    for cal in cals:
        cal_pkg = {
            "pkg_id": f"{dim.replace('.', '_')}_{cal['cal_id']}",
            "delegation": cal["delegation"],
            "artifact": cal["artifact"],
            "agent_output": cal["agent_output"],
        }
        cal_section = {
            "createItem": {
                "item": {
                    "title": f"{cal['label']} — {cal_pkg['pkg_id']} (calibration)",
                    "description": _truncate(_format_package_body(cal_pkg, dim_name, anchor_text), 4000),
                    "pageBreakItem": {},
                },
                "location": {"index": cur_index},
            }
        }
        cal_score = {
            "createItem": {
                "item": {
                    "title": f"[{cal_pkg['pkg_id']}] Score (1.0–5.0, 0.5 step)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [{"value": v} for v in SCORE_OPTIONS],
                            },
                        }
                    },
                },
                "location": {"index": cur_index + 1},
            }
        }
        cal_rationale = {
            "createItem": {
                "item": {
                    "title": f"[{cal_pkg['pkg_id']}] Rationale (quote/paraphrase, 12–600 chars)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {"paragraph": True},
                        }
                    },
                },
                "location": {"index": cur_index + 2},
            }
        }
        cal_confidence = {
            "createItem": {
                "item": {
                    "title": f"[{cal_pkg['pkg_id']}] Confidence (0.0–1.0)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [{"value": v} for v in CONFIDENCE_OPTIONS],
                            },
                        }
                    },
                },
                "location": {"index": cur_index + 3},
            }
        }
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": [cal_section, cal_score]},
        ).execute()
        cur_index += 2
        print(f"    [{dim}] calibration {cal['cal_id']} added (expected ≈ {cal['expected_score']})")

    # Then 18 main rating sections + 3 questions each (section + score + rationale + confidence).
    total = len(packages)
    for page_idx, pkg in enumerate(packages, 1):
        section_break = {
            "createItem": {
                "item": {
                    "title": f"Rating {page_idx} of {total} — {pkg['pkg_id']}",
                    "description": _truncate(_format_package_body(pkg, dim_name, anchor_text), 4000),
                    "pageBreakItem": {},
                },
                "location": {"index": cur_index},
            }
        }
        score = {
            "createItem": {
                "item": {
                    "title": f"[{pkg['pkg_id']}] Score (1.0–5.0, 0.5 step)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [{"value": v} for v in SCORE_OPTIONS],
                            },
                        }
                    },
                },
                "location": {"index": cur_index + 1},
            }
        }
        rationale = {
            "createItem": {
                "item": {
                    "title": f"[{pkg['pkg_id']}] Rationale (quote/paraphrase, 12–600 chars)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {"paragraph": True},
                        }
                    },
                },
                "location": {"index": cur_index + 2},
            }
        }
        confidence = {
            "createItem": {
                "item": {
                    "title": f"[{pkg['pkg_id']}] Confidence (0.0–1.0)",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "DROP_DOWN",
                                "options": [{"value": v} for v in CONFIDENCE_OPTIONS],
                            },
                        }
                    },
                },
                "location": {"index": cur_index + 3},
            }
        }
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": [section_break, score, rationale, confidence]},
        ).execute()
        cur_index += 4
        if page_idx % 5 == 0:
            print(f"    [{dim}] {page_idx}/{total} pages added")

    # Final completion section
    completion = {
        "createItem": {
            "item": {
                "title": "Completion",
                "description": (
                    "Thank you for completing the study.\n\n"
                    "Please return to Prolific and submit using the completion code shown there."
                ),
                "pageBreakItem": {},
            },
            "location": {"index": cur_index},
        }
    }
    forms_service.forms().batchUpdate(
        formId=form_id, body={"requests": [completion]}
    ).execute()

    # Re-fetch form metadata to get responderUri
    final = forms_service.forms().get(formId=form_id).execute()
    return {
        "dim": dim,
        "form_id": form_id,
        "responder_url": final.get("responderUri"),
        "edit_url": f"https://docs.google.com/forms/d/{form_id}/edit",
        "n_packages": total,
    }


def load_calibrations() -> list[dict]:
    return json.loads(CALIBRATIONS_PATH.read_text())


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n\n[... truncated, see source package ...]"


def _format_package_body(pkg: dict, dim_name: str, anchor_text: str) -> str:
    return (
        f"package_id: {pkg['pkg_id']}\n\n"
        f"━━━ DELEGATION (request to the agent) ━━━\n{pkg['delegation']}\n\n"
        f"━━━ ARTIFACT (the paper section the agent reviewed) ━━━\n{pkg['artifact']}\n\n"
        f"━━━ AGENT OUTPUT (what you score) ━━━\n{pkg['agent_output']}\n\n"
        f"━━━ ANCHOR — re-read every rating ━━━\n{dim_name}\n{anchor_text}"
    )


def main() -> None:
    creds = get_creds()
    forms_service = build("forms", "v1", credentials=creds)

    out_meta = []
    for dim in ["R1.7", "R1.4", "R1.1"]:
        batch_dir = STAGE1_DIR / dim
        pkg_files = sorted(batch_dir.glob(f"{dim.replace('.', '_')}_pkg_*.md"))
        if not pkg_files:
            print(f"  WARN no packages for {dim}; skipping")
            continue
        packages = [parse_package(p) for p in pkg_files]
        print(f"\n=== Building form for {dim} ({len(packages)} packages) ===")
        meta = build_form(forms_service, dim, packages)
        out_meta.append(meta)
        print(f"  ✓ {dim} done. responder URL: {meta['responder_url']}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out_meta, indent=2))
    print(f"\nWrote form metadata: {OUT_PATH.relative_to(ROOT)}")
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for m in out_meta:
        print(f"  {m['dim']:6s}  packages={m['n_packages']}  edit={m['edit_url']}")
        print(f"          responder={m['responder_url']}")


if __name__ == "__main__":
    main()
