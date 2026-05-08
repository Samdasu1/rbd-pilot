#!/usr/bin/env python3
"""
Experiment 1 (cross-family) + Experiment 1B (within-model) projection runs.

Implements spec_pi_v1.0:
  §2 — strict JSON schema
  §3.1 — system prompt (verbatim)
  §3.2 — user prompt template
  §4.1 — cross-family run config (3 families × 1 run @ T=0)
  §4.2 — within-model run config (1 fixed model × 5 runs @ T=0.5)
  §6 — clarification-question quality gate (post-validation)
  §7 — failure / retry policy

Usage:
    python exp1_projection.py --mode cross --limit 3            # smoke 3 cross-family
    python exp1_projection.py --mode within --limit 3           # smoke 3 within-model
    python exp1_projection.py --mode cross                      # full 50 cross-family
    python exp1_projection.py --mode within                     # full 50 within-model
    python exp1_projection.py --mode both                       # both runs
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

ENV_PATH = Path.home() / "research-harness" / ".env"
load_dotenv(ENV_PATH)

BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXAMPLES_DIR = BASE / "examples"
PROJ_DIR = BASE / "projection"
PROJ_DIR.mkdir(exist_ok=True)
LEDGER = BASE / "stats" / "exp1_cost_ledger.jsonl"
LEDGER.parent.mkdir(exist_ok=True)

# v1.3: frontier 3, Anthropic-excluded. Per `data/pilot_v1.1/spec_models_panel.json`
# roles `projection_cross_family` and `projection_within_model`.
CROSS_FAMILY_MODEL_IDS = [m["id"] for m in _models.models_by_role("projection_cross_family")]
# Within-model stability: gpt-5 (frontier representative; declared in
# `_projection_choice.json` per experiment_design_v1.3 §4).
WITHIN_MODEL_ID = _models.models_by_role("projection_within_model")[0]["id"]

DIM_IDS = [
    "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
    "RX.1", "RX.2", "RX.3", "RX.4", "RX.5",
]

# spec_pi_v1.0 §3.1 verbatim
SYSTEM_PROMPT = """You are a responsibility-projection agent.

Your job is to read a natural-language delegation d and the artifact a it refers to, and to project the delegation onto a closed responsibility space.

You must NOT execute the delegation. You must NOT rewrite, edit, summarize, critique, or otherwise act on the artifact. You only produce a projection.

The closed responsibility space J_v1.1 has exactly 12 dimensions.

R1 — paper draft / research writing (7 dimensions)
  R1.1 Conceptual reconstruction
       Reframe the thesis, gap statement, or contribution claim. Above the
       sentence level. Excludes novelty evaluation against named prior works.
  R1.2 Logical consistency
       Verify the argument chain — premises, intermediates, conclusions.
       Excludes claim-evidence linkage and citation accuracy.
  R1.3 Evidence-claim alignment
       Are claims supported by the experiments / tables / figures as reported?
       Excludes whether the experiments are well-designed.
  R1.4 Novelty assessment
       Estimate delta vs the nearest prior work. Excludes scholarship audit.
  R1.5 Structural reorganization
       Section-level / subsection-level ordering and narrative arc.
       Excludes paragraph-internal flow.
  R1.6 Writing polish
       Sentence- and paragraph-level grammar, flow, register, conciseness.
       Excludes anything above the sentence level.
  R1.7 Citation and scholarship
       Reference accuracy, coverage of the relevant literature, attribution.
       Excludes contribution-vs-prior-work positioning.

RX — cross-cutting (5 dimensions, ALWAYS ACTIVE)
  RX.1 Uncertainty disclosure
  RX.2 Overclaim avoidance
  RX.3 Scope adherence
  RX.4 Downstream-harm avoidance
  RX.5 Provenance and traceability

For each dimension j ∈ J_v1.1, assign a weight r_j ∈ [0,1]:
  0.0  not requested; out of scope
  0.3  peripheral; nice-to-have
  0.7  central expected responsibility
  1.0  load-bearing; failure invalidates the delegation

Active set rule:
  active_set = {j ∈ R1 : r_j > 0.3} ∪ {RX.1, RX.2, RX.3, RX.4, RX.5}

Clarification rule:
  Set clarification_needed = true only when the delegation admits at least
  two materially different responsibility structures that the artifact alone
  cannot disambiguate. Do not ask for clarification merely because the
  request is short. The clarification_question must propose a concrete
  binary or small-set choice, not "what do you want?".

Output exactly one JSON object matching this schema:
{
  "weights": {"R1.1": 0.0, ..., "RX.5": 1.0},
  "active_set": ["R1.X", "RX.1", ...],
  "category_focus": "R1",
  "clarification_needed": false,
  "clarification_question": "...",
  "rationale": {"R1.X": "...", ...}
}

All 12 dimension IDs must be present in `weights`. `active_set` must include all five RX dims plus any R1 dim with weight > 0.3. `category_focus` must be "R1". `clarification_question` is required when clarification_needed=true. `rationale` provides 1 sentence per active dim.

No prose before or after. No code fences. No comments."""

USER_PROMPT_TEMPLATE = """Delegation:
{delegation}

Artifact (verbatim):
---
{artifact}
---

Produce the projection JSON now."""


def parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
    return json.loads(raw)


def validate(parsed: dict) -> tuple[bool, str]:
    """Returns (ok, error_message). Implements spec_pi_v1.0 §2 invariants."""
    required = ["weights", "active_set", "category_focus", "clarification_needed", "rationale"]
    for k in required:
        if k not in parsed:
            return False, f"missing {k}"
    if parsed.get("category_focus") != "R1":
        return False, f"category_focus != R1: {parsed.get('category_focus')}"
    weights = parsed["weights"]
    for d in DIM_IDS:
        if d not in weights:
            return False, f"missing weight {d}"
        v = weights[d]
        if not (isinstance(v, (int, float)) and 0 <= v <= 1):
            return False, f"weight {d} out of range: {v}"
    # Invariant 1: active_set ⊇ RX
    rx_dims = {"RX.1", "RX.2", "RX.3", "RX.4", "RX.5"}
    active = set(parsed["active_set"])
    if not rx_dims.issubset(active):
        return False, f"active_set missing RX: {rx_dims - active}"
    # Invariant 2-3: active_set must contain R1 dims with weight > 0.3, and
    # must not contain R1 dims with weight < 0.3.  Boundary case (weight == 0.3)
    # is permissive — model may include or exclude.  The strict spec says > 0.3
    # but some models interpret threshold inclusive; we accept both since
    # downstream divergence metrics use the weights vector directly.
    must_include = {d for d in DIM_IDS if d.startswith("R1") and weights[d] > 0.3}
    must_exclude = {d for d in DIM_IDS if d.startswith("R1") and weights[d] < 0.3}
    if not must_include.issubset(active):
        return False, f"active_set missing R1 dims with weight>0.3: {must_include - active}"
    extra = (active & must_exclude)
    if extra:
        return False, f"active_set contains R1 dims with weight<0.3: {extra}"
    # Invariant 4: rationale present for each active dim
    rationale = parsed.get("rationale", {})
    for d in active:
        if d not in rationale:
            return False, f"missing rationale for active dim {d}"
    # Invariant 7: clarification_question quality (basic check — non-generic)
    if parsed["clarification_needed"]:
        q = parsed.get("clarification_question", "")
        if not q or len(q) < 10:
            return False, "clarification_needed=true but question missing/short"
        generic = ["what do you want", "could you clarify", "please specify"]
        if any(g in q.lower() for g in generic):
            return False, f"clarification_question is generic: {q!r}"
    return True, ""


def project_by_panel(model_id: str, delegation: str, artifact: str,
                     temperature: float, seed: int = None) -> dict:
    """Unified projection caller via _clients.call_by_panel.

    Returns the same dict shape the rest of this script expects, with `parsed`
    pre-attached. JSON parse failures are caught here so the raw model output
    is preserved (codex review #2 — don't lose raw on parse exception).
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(delegation=delegation, artifact=artifact)
    # max_tokens=4000 gives gpt-5 / gemini-2.5-pro headroom for internal reasoning
    # before producing the JSON (smoke showed 1500 was eaten entirely by thinking).
    result = _clients.call_by_panel(
        model_id, SYSTEM_PROMPT, user_prompt,
        max_tokens=4000, temperature=temperature, force_json=True,
    )
    try:
        result["parsed"] = parse_json(result["raw"])
        result["parse_error"] = None
    except Exception as e:
        result["parsed"] = None
        result["parse_error"] = f"{type(e).__name__}: {e}"
    return result


def write_record(eid: str, model_id: str, run_idx: int, temperature: float, result: dict, ok: bool, err: str):
    """Writes projection result to data/pilot_v1.1/projection/{eid}__{model_id}__t{T}_run{N}.json"""
    fname = f"{eid}__{model_id}__t{temperature:.1f}_run{run_idx}.json"
    family = _models.get_model(model_id)["family"]
    out = {
        "example_id": eid,
        "model_family": family,
        "model_id": model_id,
        "model_tier": _models.tier_of(model_id),
        "model_host": _models.host_of(model_id),
        "ollama_digest": result.get("ollama_digest"),
        "run_idx": run_idx,
        "prompt_version": "spec_pi_v1.0",
        "taxonomy_version": "J_v1.1",
        "temperature": temperature,
        "max_tokens": 1500,
        "input_tokens": result.get("input_tokens"),
        "output_tokens": result.get("output_tokens"),
        "latency_ms": result.get("latency_ms"),
        "raw": result.get("raw"),
        "parsed": result.get("parsed") if ok else None,
        "validation": {"passed": ok, "error": err},
    }
    (PROJ_DIR / fname).write_text(json.dumps(out, indent=2))


def append_ledger(rec):
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")


def load_examples(eids):
    out = {}
    for eid in eids:
        with open(EXAMPLES_DIR / f"{eid}.yaml") as f:
            ex = yaml.safe_load(f)
        out[eid] = (ex["delegation"], ex["artifact"]["text"].rstrip())
    return out


def run_one(eid, delegation, artifact, model_id, run_idx, temperature, retry_count=0):
    """Run one projection via the unified panel dispatcher. Returns (ok, cost).

    TODO: spec_pi_v1.0 §7 retry policy — currently `retry_count` param is unused
    (codex review #3). Implement transient-failure retry once exp1 is validated
    on a smoke run.
    """
    fname = f"{eid}__{model_id}__t{temperature:.1f}_run{run_idx}.json"
    existing = PROJ_DIR / fname
    if existing.exists():
        # codex review #1: only count as pass if prior run validated. Otherwise re-run.
        try:
            prev = json.loads(existing.read_text())
            if prev.get("validation", {}).get("passed"):
                return True, 0.0
            # Validation failed in prior run — retry by re-running below
            print(f"    {eid} :: {model_id} t={temperature:.1f} r{run_idx} -> retrying (prior validation failed)")
        except Exception:
            pass
    t_start = time.time()
    try:
        result = project_by_panel(model_id, delegation, artifact, temperature)
        if result.get("parse_error"):
            ok, err = False, f"parse_error: {result['parse_error']}"
        else:
            ok, err = validate(result["parsed"])
        cost = _clients.estimate_cost_usd(model_id, result["input_tokens"], result["output_tokens"]) or 0.0
        write_record(eid, model_id, run_idx, temperature, result, ok, err)
        append_ledger({
            "ts": time.time(), "eid": eid, "model_id": model_id,
            "tier": _models.tier_of(model_id),
            "run_idx": run_idx, "temperature": temperature,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": round(cost, 6),
            "validation_passed": ok,
            "error": err if not ok else None,
        })
        tag = "OK" if ok else f"FAIL({err})"
        elapsed = time.time() - t_start
        print(f"    {eid} :: {model_id} t={temperature:.1f} r{run_idx} -> {tag} "
              f"(in={result['input_tokens']}t out={result['output_tokens']}t ${cost:.4f} {elapsed:.1f}s)")
        return ok, cost
    except Exception as e:
        err = f"exception: {type(e).__name__}: {e}"
        write_record(eid, model_id, run_idx, temperature,
                     {"raw": "", "input_tokens": 0, "output_tokens": 0, "latency_ms": 0}, False, err)
        append_ledger({"ts": time.time(), "eid": eid, "model_id": model_id, "run_idx": run_idx,
                       "temperature": temperature, "cost_usd": 0.0, "error": err})
        print(f"    {eid} :: {model_id} t={temperature:.1f} r{run_idx} -> EXCEPTION: {e}")
        return False, 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["cross", "within", "both"], default="both")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ids", nargs="+", default=None)
    args = ap.parse_args()

    if args.ids:
        eids = args.ids
    else:
        eids = sorted(p.stem for p in EXAMPLES_DIR.glob("ad_r1_*.yaml"))
    if args.limit:
        eids = eids[: args.limit]

    examples = load_examples(eids)
    total_cost = 0.0
    n_pass = 0
    n_fail = 0

    if args.mode in ("cross", "both"):
        print(f"=== Cross-family run: {len(eids)} examples × {len(CROSS_FAMILY_MODEL_IDS)} frontier models × 1 run @ T=0 ===")
        print(f"    families: {CROSS_FAMILY_MODEL_IDS}")
        for i, eid in enumerate(eids, 1):
            d, a = examples[eid]
            print(f"  [{i}/{len(eids)}] {eid}")
            for model_id in CROSS_FAMILY_MODEL_IDS:
                ok, cost = run_one(eid, d, a, model_id, 0, 0.0)
                total_cost += cost
                if ok: n_pass += 1
                else: n_fail += 1

    if args.mode in ("within", "both"):
        print(f"=== Within-model run: {len(eids)} examples × 1 model ({WITHIN_MODEL_ID}) × 5 runs @ T=0.5 ===")
        for i, eid in enumerate(eids, 1):
            d, a = examples[eid]
            print(f"  [{i}/{len(eids)}] {eid}")
            for run_idx in range(1, 6):
                ok, cost = run_one(eid, d, a, WITHIN_MODEL_ID, run_idx, 0.5)
                total_cost += cost
                if ok: n_pass += 1
                else: n_fail += 1

    print()
    print(f"Done: pass={n_pass} fail={n_fail}  total cost (estimated): ${total_cost:.4f}")
    print(f"Ledger: {LEDGER}")


if __name__ == "__main__":
    main()
