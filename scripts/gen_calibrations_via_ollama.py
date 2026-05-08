#!/usr/bin/env python3
"""Generate 6 Stage 1 calibration packages via local Ollama (mistral-large-2).

Pattern (anti-correlated):
  - Cal A (expected s=1): LONG agent output (~400-600 words) that does NOT hit
    anchor verbs. Looks effortful but anchor-empty.
  - Cal B (expected s=5): SHORT agent output (~150-200 words) that hits ALL
    anchor verbs precisely. Looks minimal but anchor-saturated.

Why anti-correlated: prevents raters from passing calibration via the
length-heuristic ('long = good, short = bad') without engaging anchor verbs.

Output: human_annotation/recruitment/stage1_calibrations.json (overwrites).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _clients

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "human_annotation/recruitment/stage1_calibrations.json"

GENERATOR_MODEL = "mistral-large-2-2407"   # mid-tier Ollama, 123B params

DIM_INFO = {
    "R1.1": {
        "name": "Conceptual reconstruction",
        "anchor_s5_verbs": [
            "names the load-bearing concept",
            "shows where the draft drifts from it",
            "proposes a reframing that survives prior-work contrast",
        ],
        "calA_pivot": "long surface-level prose / structural / wording suggestions; never names a load-bearing concept or addresses framing drift",
        "calB_pivot": "short, names load-bearing concept, shows drift, proposes reframing — all in ~150 words",
        "domain_seed": "self-supervised representation learning OR LLM evaluation OR scientific machine learning",
    },
    "R1.4": {
        "name": "Novelty assessment",
        "anchor_s5_verbs": [
            "maps against the nearest 3-5 prior works",
            "identifies sharp vs rhetorical delta",
            "proposes positioning text",
        ],
        "calA_pivot": "long generic praise about how the contribution is 'meaningful', 'well-positioned'; never names any specific prior work and never articulates the delta",
        "calB_pivot": "short, names 4 specific prior works with author/year/venue, sharp delta, proposes positioning sentence — all in ~180 words",
        "domain_seed": "computer vision tracking OR vision-language prompt tuning OR graph neural networks",
    },
    "R1.7": {
        "name": "Citation and scholarship",
        "anchor_s5_verbs": [
            "audits every load-bearing citation against the source",
            "flags missing key works in the relevant cluster",
            "suggests insertions with bibliographic precision (full author/year/venue)",
        ],
        "calA_pivot": "long discussion of citation FORMATTING (commas, italics, en-dashes, bibliography ordering); never flags any missing or wrong substantive citation",
        "calB_pivot": "short, audits 3 specific load-bearing citations, flags 2-3 missing key works with full author/year/venue — all in ~150 words",
        "domain_seed": "neural compression OR molecular property prediction OR drug discovery ML",
    },
}

ARTIFACT_TEMPLATE = """You will produce a synthetic academic paper section (200-250 words) in the {domain} domain. The section should have plausible technical claims and at least 2-3 citations to (made-up) prior work in author-year format. The section MUST contain weaknesses that are detectable by a careful reviewer applying the {dim_name} rubric.

Output ONLY the artifact text, no preamble, no explanation."""

CAL_A_TEMPLATE = """You will produce a synthetic AI agent's review output for the artifact below. STRICT requirements:

  1. **EXACTLY 200-300 words** (concise but visibly effortful — DO NOT exceed 300 words).
  2. Stays on topic — about {dim_name}.
  3. CRITICALLY: must NOT hit any of these anchor verbs:
       - {anchor_verbs}
  4. Instead, focus on: {pivot}.
  5. Use direct review voice ("This section...", "The draft..."). No meta-talk.

The intent: fool a length-heuristic reader, while a rubric-faithful reader scores s=1 because anchor verbs are absent.

ARTIFACT:
---
{artifact}
---

Output ONLY the review text, 200-300 words. Begin directly."""

CAL_B_TEMPLATE = """You will produce a synthetic AI agent's review output for the artifact below. STRICT requirements:

  1. **EXACTLY 80-100 words** (very short — DO NOT exceed 100 words).
  2. Hits ALL of these anchor verbs explicitly:
       - {anchor_verbs}
  3. Specifically: {pivot}.
  4. Use direct review voice ("This claim cites...", "Missing: X et al..."). No meta-talk.
  5. Each sentence must do anchor work — no filler.

The intent: a length-heuristic reader undervalues this; a rubric-faithful reader scores s=5 because all anchor verbs satisfied.

ARTIFACT:
---
{artifact}
---

Output ONLY the review text, 80-100 words. Begin directly."""


def gen_artifact(dim: str) -> str:
    info = DIM_INFO[dim]
    sys_prompt = (
        "You are a synthetic academic paper section generator. "
        "Produce only the requested artifact text, with no meta-commentary."
    )
    user = ARTIFACT_TEMPLATE.format(domain=info["domain_seed"], dim_name=info["name"])
    r = _clients.call_ollama(GENERATOR_MODEL, sys_prompt, user, max_tokens=600, temperature=0.7)
    return r["raw"].strip()


def gen_cal_a(dim: str, artifact: str) -> str:
    info = DIM_INFO[dim]
    sys_prompt = (
        "You are a synthetic AI-agent-review generator. Follow the constraints "
        "EXACTLY. Output only the agent's review text."
    )
    user = CAL_A_TEMPLATE.format(
        dim_name=info["name"],
        anchor_verbs="\n       - ".join(info["anchor_s5_verbs"]),
        pivot=info["calA_pivot"],
        artifact=artifact,
    )
    r = _clients.call_ollama(GENERATOR_MODEL, sys_prompt, user, max_tokens=600, temperature=0.7)
    return r["raw"].strip()


def gen_cal_b(dim: str, artifact: str) -> str:
    info = DIM_INFO[dim]
    sys_prompt = (
        "You are a synthetic AI-agent-review generator. Follow the constraints "
        "EXACTLY. Output only the agent's review text."
    )
    user = CAL_B_TEMPLATE.format(
        dim_name=info["name"],
        anchor_verbs="\n       - ".join(info["anchor_s5_verbs"]),
        pivot=info["calB_pivot"],
        artifact=artifact,
    )
    r = _clients.call_ollama(GENERATOR_MODEL, sys_prompt, user, max_tokens=300, temperature=0.7)
    return r["raw"].strip()


def main() -> None:
    out = []
    for dim in ["R1.7", "R1.4", "R1.1"]:
        info = DIM_INFO[dim]
        print(f"\n=== {dim} ({info['name']}) ===")
        artifact_a = gen_artifact(dim)
        artifact_b = gen_artifact(dim)
        print(f"  artifact A: {len(artifact_a)} chars")
        print(f"  artifact B: {len(artifact_b)} chars")

        agent_a = gen_cal_a(dim, artifact_a)
        agent_b = gen_cal_b(dim, artifact_b)
        print(f"  agent A (long+miss): {len(agent_a)} chars")
        print(f"  agent B (short+hit): {len(agent_b)} chars")

        out.append({
            "dim": dim,
            "cal_id": "cal_A",
            "expected_score": 1,
            "label": "Calibration 1 of 2",
            "delegation": "Review this section.",
            "artifact": artifact_a,
            "agent_output": agent_a,
            "reasoning_for_target_score": (
                f"Long output ({len(agent_a)} chars) that does NOT hit any of: "
                f"{', '.join(info['anchor_s5_verbs'])}. Anchor-faithful reader scores s=1."
            ),
            "generated_by": GENERATOR_MODEL,
        })
        out.append({
            "dim": dim,
            "cal_id": "cal_B",
            "expected_score": 5,
            "label": "Calibration 2 of 2",
            "delegation": "Review this section.",
            "artifact": artifact_b,
            "agent_output": agent_b,
            "reasoning_for_target_score": (
                f"Short output ({len(agent_b)} chars) that hits ALL of: "
                f"{', '.join(info['anchor_s5_verbs'])}. Anchor-faithful reader scores s=5."
            ),
            "generated_by": GENERATOR_MODEL,
        })

    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\n✓ wrote 6 calibrations to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
