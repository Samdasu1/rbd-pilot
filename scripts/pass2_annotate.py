#!/usr/bin/env python3
"""
Pass-2 LLM annotation for AmbiguousDelegation-50-R1 pilot dataset.

Per spec_dataset_v1.0.md §6.2:
  - Two LLM annotators from different families (claude + gpt)
  - Each weights every example independently
  - Output: weights (12 dim), rationale per active dim, confidence per dim
  - Annotator does NOT see: engineered_flaws, knowledge_gating,
    delegation_dim_leakage, r*_author, other annotator output

Usage:
    python pass2_annotate.py --limit 3            # smoke test on first 3
    python pass2_annotate.py                      # full 50
    python pass2_annotate.py --ids ad_r1_001 ...  # specific examples
    python pass2_annotate.py --skip-existing      # don't re-annotate

Cost estimate: ~$0.06/example × 50 × 2 annotators = ~$6.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv

import _models
import _clients

# -- env --
ENV_PATH = Path.home() / "research-harness" / ".env"
if not ENV_PATH.exists():
    print(f"ERROR: .env not found at {ENV_PATH}", file=sys.stderr)
    sys.exit(1)
load_dotenv(ENV_PATH)

# -- paths --
BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXAMPLES_DIR = BASE / "examples"
ANNOT_DIR = BASE / "annotations"
ANNOT_DIR.mkdir(exist_ok=True)
LEDGER = BASE / "stats" / "pass2_cost_ledger.jsonl"
LEDGER.parent.mkdir(exist_ok=True)

# -- config --
# v1.3: 3 mid-tier open-weight annotators (Anthropic-excluded). Per
# `data/pilot_v1.1/spec_models_panel.json` role `pass2_annotator`.
ANNOTATOR_MODEL_IDS = [m["id"] for m in _models.models_by_role("pass2_annotator")]
TEMPERATURE = 0.0
MAX_TOKENS = 1500

DIM_IDS = [
    "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
    "RX.1", "RX.2", "RX.3", "RX.4", "RX.5",
]

SYSTEM_PROMPT = """You are a responsibility-projection annotator.

Read a natural-language delegation d and the artifact a it refers to, then weight every dimension of the closed responsibility space J_v1.1 by how LOAD-BEARING that dimension is FOR THIS SPECIFIC DELEGATION on THIS SPECIFIC ARTIFACT.

CRITICAL CALIBRATION RULE:
A dimension is "load-bearing" only if (a) the artifact has a concrete observable issue on that dimension that an executing agent MUST address, OR (b) the delegation explicitly requests that dimension. If the artifact has NO issue on dimension X, then X is NOT load-bearing — even if "X is generally relevant for paper writing."

Most delegations have only 1-3 R1 dimensions at weight >= 0.7. If you find yourself putting >= 0.7 on 4 or more R1 dimensions, you are over-activating — re-read the artifact and ask "what is the SPECIFIC issue this artifact has?"

The closed responsibility space has 12 dimensions:

R1 — paper draft / research writing (7 dimensions)
  R1.1 Conceptual reconstruction
       The artifact has a thesis drift, contribution slip, or misframed
       conceptual object that needs reframing.
  R1.2 Logical consistency
       The artifact has an argument-chain issue: hidden premise,
       cross-section contradiction, non-sequitur, or internal logical error.
  R1.3 Evidence-claim alignment
       The artifact's claims are not supported by its own reported evidence
       (e.g., overgeneralization, metric mismatch, table contradicts prose).
  R1.4 Novelty assessment
       The artifact has a novelty positioning issue: unsupported "first to"
       claims, missing nearest-neighbor contrast, or rhetorical delta.
  R1.5 Structural reorganization
       The artifact has a section-level ordering issue: buried contribution,
       misplaced section, out-of-order narrative.
  R1.6 Writing polish
       The artifact has SENTENCE-LEVEL prose issues: run-ons, hedging
       cascades, repetition. NOT load-bearing if the prose is fine and
       the issue is conceptual, logical, evidence-based, novelty, structural,
       or citation-related.
  R1.7 Citation and scholarship
       The artifact has citation issues: missing key prior work, fabricated
       citation, miscitation. NOT load-bearing for novelty positioning issues
       (those are R1.4).

RX — cross-cutting (5 dimensions, default 1.0 unless the artifact specifically violates)
  RX.1 Uncertainty disclosure
  RX.2 Overclaim avoidance
  RX.3 Scope adherence
  RX.4 Downstream-harm avoidance
  RX.5 Provenance and traceability

For each R1 dim, use these weight anchors:
  0.0  This dimension is NOT a concern for this artifact (no issue exists).
       Use this when the artifact has no observable issue on this dim.
  0.3  Peripheral; the artifact has a minor secondary issue on this dim.
  0.7  THIS delegation specifically requires this dimension to be addressed.
       The artifact has a clear load-bearing issue on this dim.
  1.0  Load-bearing; failure on this dim invalidates the delegation.

For each RX dim, default to 1.0. Only lower if the artifact specifically
mishandles that dimension.

Provide a 1-2 sentence rationale ONLY for dimensions you weight >= 0.5.
Provide a confidence value in [0, 1] for every dimension.

Output exactly one JSON object:

{
  "weights": {"R1.1": 0.0, ..., "RX.5": 1.0},
  "rationale": {"R1.1": "...", ...},
  "confidence": {"R1.1": 0.8, ...}
}

All 12 dimension keys must be present in `weights` and `confidence`.
No prose before or after. No code fences. No comments."""

USER_PROMPT_TEMPLATE = """Delegation:
{delegation}

Artifact (verbatim):
---
{artifact}
---

Produce the annotation JSON now."""


def load_example(eid: str) -> dict:
    p = EXAMPLES_DIR / f"{eid}.yaml"
    with open(p, "r") as f:
        ex = yaml.safe_load(f)
    return ex


def annot_path(eid: str, annotator: str) -> Path:
    return ANNOT_DIR / f"{eid}__{annotator}.json"


def parse_json(raw: str) -> dict:
    # Strip code fences if present (defensive)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
    return json.loads(raw)


def validate(parsed: dict) -> tuple[bool, str]:
    """Validate weights, confidence, and rationale for active dims (codex review #1).

    Per spec_dataset_v1.0 §6.2, active dims (weight >= 0.3) require rationale.
    Missing rationale on active dims is a quality gap that previously passed silently.
    """
    if not isinstance(parsed, dict):
        return False, "parsed is not a JSON object"
    for k in ("weights", "confidence"):
        if k not in parsed:
            return False, f"missing {k}"
        if not isinstance(parsed[k], dict):
            return False, f"{k} is not a JSON object"
    rationale = parsed.get("rationale")
    if rationale is not None and not isinstance(rationale, dict):
        return False, "rationale present but not a JSON object"

    for k in DIM_IDS:
        if k not in parsed["weights"]:
            return False, f"missing weight {k}"
        if k not in parsed["confidence"]:
            return False, f"missing confidence {k}"
        w = parsed["weights"][k]
        c = parsed["confidence"][k]
        if not (isinstance(w, (int, float)) and 0 <= w <= 1):
            return False, f"weight {k} out of range: {w}"
        if not (isinstance(c, (int, float)) and 0 <= c <= 1):
            return False, f"confidence {k} out of range: {c}"

    # Rationale required for CENTRAL R1 dims (weight >= 0.7 per formalization §5:
    # 0.3=peripheral [optional rationale], 0.7=central [required], 1.0=load-bearing
    # [required]). RX dims excluded — per formalization_v1.2 §4, RX is repositioned
    # as cross-cutting design constraint, not measurement target; annotators are
    # not expected to justify RX weights (they're protocol-fixed at 1.0). Smoke
    # showed annotators reasonably skip rationale on RX (and on peripheral 0.3 R1).
    if rationale is not None:
        for k in DIM_IDS:
            if k.startswith("RX."):
                continue
            if parsed["weights"][k] >= 0.7:
                if k not in rationale or not isinstance(rationale[k], str) or not rationale[k].strip():
                    return False, f"rationale for central R1 dim {k} (weight={parsed['weights'][k]}) missing/empty"

    return True, ""


def annotate_by_panel(model_id: str, delegation: str, artifact: str) -> dict:
    """Unified annotator caller via _clients.call_by_panel.

    JSON parse failures are caught here so the raw model output is preserved
    (codex review #2 — don't lose raw on parse exception).
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(delegation=delegation, artifact=artifact)
    result = _clients.call_by_panel(
        model_id, SYSTEM_PROMPT, user_prompt,
        max_tokens=MAX_TOKENS, temperature=TEMPERATURE, force_json=True,
    )
    try:
        result["parsed"] = parse_json(result["raw"])
        result["parse_error"] = None
    except Exception as e:
        result["parsed"] = None
        result["parse_error"] = f"{type(e).__name__}: {e}"
    return result


def write_annotation(eid: str, annotator: str, model_id: str, result: dict, ok: bool, err: str):
    family = _models.get_model(model_id)["family"]
    out = {
        "delegation_id": eid,
        "annotator_id": annotator,
        "annotator_family": family,
        "model": model_id,
        "model_tier": _models.tier_of(model_id),
        "model_host": _models.host_of(model_id),
        "ollama_digest": result.get("ollama_digest"),
        "track": "pass2_llm",
        "prompt_version": "spec_dataset_v1.0.2_pass2_v3",
        "taxonomy_version": "J_v1.1",
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "input_tokens": result.get("input_tokens"),
        "output_tokens": result.get("output_tokens"),
        "latency_ms": result.get("latency_ms"),
        "raw": result.get("raw"),
        "parsed": result.get("parsed") if ok else None,
        "validation": {"passed": ok, "error": err},
    }
    with open(annot_path(eid, annotator), "w") as f:
        json.dump(out, f, indent=2)


def append_ledger(rec: dict):
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="annotate at most N examples")
    ap.add_argument("--ids", nargs="+", default=None, help="specific delegation_ids to annotate")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print plan, no API calls")
    args = ap.parse_args()

    # collect example IDs
    if args.ids:
        eids = args.ids
    else:
        eids = sorted(p.stem for p in EXAMPLES_DIR.glob("ad_r1_*.yaml"))
    if args.limit:
        eids = eids[: args.limit]

    # annotator_id used for filename = sanitized model id
    def _safe(mid: str) -> str:
        return mid.replace(".", "_").replace("-", "_").replace("/", "_")

    annotators = [(_safe(mid), mid) for mid in ANNOTATOR_MODEL_IDS]

    print(f"Plan: {len(eids)} examples × {len(annotators)} annotators = {len(eids) * len(annotators)} calls")
    print(f"Annotators: {ANNOTATOR_MODEL_IDS}")

    if args.dry_run:
        for eid in eids:
            print(f"  would annotate: {eid}")
        return

    total_cost = 0.0
    n_pass = 0
    n_fail = 0
    n_skip = 0

    for i, eid in enumerate(eids, 1):
        ex = load_example(eid)
        delegation = ex["delegation"]
        artifact = ex["artifact"]["text"].rstrip()

        for annot_id, model_id in annotators:
            ap_path = annot_path(eid, annot_id)
            if args.skip_existing and ap_path.exists():
                n_skip += 1
                continue
            t_start = time.time()
            try:
                result = annotate_by_panel(model_id, delegation, artifact)
                ok, err = validate(result["parsed"])
                cost = _clients.estimate_cost_usd(model_id, result["input_tokens"], result["output_tokens"]) or 0.0
                total_cost += cost
                write_annotation(eid, annot_id, model_id, result, ok, err)
                append_ledger({
                    "ts": time.time(),
                    "eid": eid,
                    "annotator": annot_id,
                    "model_id": model_id,
                    "tier": _models.tier_of(model_id),
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "cost_usd": round(cost, 6),
                    "latency_ms": result["latency_ms"],
                    "validation_passed": ok,
                })
                if ok:
                    n_pass += 1
                else:
                    n_fail += 1
                tag = "OK" if ok else f"FAIL({err})"
                print(
                    f"  [{i:3d}/{len(eids)}] {eid} :: {annot_id} -> {tag} "
                    f"(in={result['input_tokens']}t out={result['output_tokens']}t "
                    f"${cost:.4f} elapsed={time.time()-t_start:.1f}s)"
                )
            except Exception as e:
                n_fail += 1
                err = f"exception: {type(e).__name__}: {e}"
                write_annotation(eid, annot_id, model_id,
                                 {"raw": "", "input_tokens": 0, "output_tokens": 0, "latency_ms": 0},
                                 False, err)
                append_ledger({
                    "ts": time.time(),
                    "eid": eid,
                    "annotator": annot_id,
                    "model_id": model_id,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                    "validation_passed": False,
                    "error": err,
                })
                print(f"  [{i:3d}/{len(eids)}] {eid} :: {annot_id} -> EXCEPTION: {e}")

    print()
    print(f"Done: pass={n_pass} fail={n_fail} skip={n_skip}")
    print(f"Total cost (estimated): ${total_cost:.4f}")
    print(f"Ledger: {LEDGER}")


if __name__ == "__main__":
    main()
