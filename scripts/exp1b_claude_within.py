"""Within-model variance with claude-sonnet-4-6 via Claude Code CLI subscription.

Re-creates the within-model baseline that the paper's R(d)=14.4 number was
based on. Paper used claude-sonnet-4.5 via API at T=0.5; this script uses
claude-sonnet-4-6 via the Claude Code subscription path (closest available
match — same family, same tier, one minor version newer than paper's). No
API spend.

Goal: 5 reps × N examples → projection JSON files at
  data/pilot_v1.1/projection/{eid}__claude__t0.5_run{N}.json

The {eid}__claude__... naming intentionally mirrors what exp1_analyze.py
expected before the panel swap; the v1.3 panel uses gpt-5 instead, which
gives much larger d_W and a smaller R. This script is the comeback path.

Usage:
  python scripts/exp1b_claude_within.py --ids ad_r1_001 ad_r1_002 ad_r1_003 ad_r1_004 ad_r1_005
  python scripts/exp1b_claude_within.py --ids-range 1 310 --reps 5
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path("/home/treu46/paper/6. agent")
EXAMPLES_DIR = ROOT / "data" / "pilot_v1.1" / "examples"
PROJ_DIR = ROOT / "data" / "pilot_v1.1" / "projection"
LEDGER = ROOT / "data" / "pilot_v1.1" / "stats" / "exp1_cost_ledger.jsonl"

DIMS_R1 = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]
DIMS_RX = ["RX.1", "RX.2", "RX.3", "RX.4", "RX.5"]

SYSTEM_PROMPT = """\
You are a responsibility-projection agent.

Your job: read the user's natural-language delegation `d` and the artifact `a`,
and produce a 12-dimension responsibility weight vector r over the closed
taxonomy J_v1.1 (R1.1..R1.7 category dims + RX.1..RX.5 cross-cutting dims).

Each weight r_j ∈ [0, 1] uses the following anchors:
  0.0 — not requested / out of scope
  0.3 — peripherally relevant
  0.7 — central expected responsibility
  1.0 — load-bearing; failure invalidates the delegation

The R1 dimensions:
  R1.1 conceptual reconstruction (thesis, gap statement, contribution claim)
  R1.2 logical consistency (premises, intermediates, conclusions, cross-section coherence)
  R1.3 evidence-claim alignment (claims supported by experiments/tables/figures)
  R1.4 novelty assessment (delta vs nearest prior work)
  R1.5 structural reorganization (section ordering, narrative arc)
  R1.6 writing polish (sentence/paragraph quality)
  R1.7 citation and scholarship (reference accuracy, coverage, attribution)

RX (always-active, cross-cutting):
  RX.1 uncertainty disclosure
  RX.2 overclaim avoidance
  RX.3 scope adherence
  RX.4 downstream-harm avoidance
  RX.5 provenance and traceability

Set RX dimensions to 1.0 by default. Set R1 dimensions based on what the
delegation + artifact actually demand.

Active set: J*(d) = {j ∈ R1 : r_j > 0.3} ∪ {RX.1..RX.5}.

If the delegation is ambiguous in a way that materially changes the
responsibility structure (two or more R1 dims could plausibly be load-bearing
and you cannot tell which), set clarification_needed=true and write a concrete
binary clarification_question. Otherwise clarification_needed=false.

Output exactly one JSON object with this shape:
{
  "weights": {"R1.1": <float>, ..., "R1.7": <float>, "RX.1": <float>, ..., "RX.5": <float>},
  "active_set": ["R1.x", ..., "RX.y"],
  "rationale": {"R1.x": "<short reason>", ...},  // one entry per active R1 dim
  "clarification_needed": <bool>,
  "clarification_question": "<string or empty>"
}

No prose before or after. No markdown fences."""

USER_PROMPT_TEMPLATE = """\
delegation: {delegation}

artifact:
{artifact}"""


def call_claude_cli(system: str, user: str, *, timeout_s: int = 300) -> dict:
    """Invoke Claude CLI in print mode (subscription billed). Returns dict with raw text."""
    bin_path = shutil.which("claude") or "claude"
    with tempfile.TemporaryDirectory(prefix="harness-claude-") as iso_cwd:
        sys_path = Path(iso_cwd) / "system.md"
        sys_path.write_text(system, encoding="utf-8")
        cmd = [
            bin_path, "-p",
            "--system-prompt-file", str(sys_path),
            "--output-format", "json",
            "--model", "claude-sonnet-4-6",
        ]
        env = {**os.environ, "HARNESS_NO_RECURSE": "1"}
        t0 = time.time()
        proc = subprocess.run(
            cmd, input=user, capture_output=True, text=True, encoding="utf-8",
            env=env, timeout=timeout_s, cwd=iso_cwd,
        )
        elapsed_ms = int((time.time() - t0) * 1000)
    if proc.returncode != 0:
        return {"error": f"rc={proc.returncode} stderr={(proc.stderr or '')[-400:]}"}
    raw = ""
    last_obj = None
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            last_obj = json.loads(line)
        except json.JSONDecodeError:
            continue
    if last_obj:
        raw = last_obj.get("result") or last_obj.get("text") or ""
    return {
        "raw": raw,
        "input_tokens": (last_obj or {}).get("usage", {}).get("input_tokens", -1),
        "output_tokens": (last_obj or {}).get("usage", {}).get("output_tokens", -1),
        "latency_ms": elapsed_ms,
    }


_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)


def parse_projection(raw: str) -> dict | None:
    text = raw.strip()
    m = _FENCE_RE.search(text)
    if m:
        text = m.group(1)
    # find first {...} block
    j_start = text.find("{")
    j_end = text.rfind("}")
    if j_start == -1 or j_end == -1 or j_end <= j_start:
        return None
    try:
        return json.loads(text[j_start:j_end + 1])
    except json.JSONDecodeError:
        return None


def validate(parsed: dict) -> tuple[bool, str]:
    if not parsed:
        return False, "no JSON parsed"
    w = parsed.get("weights")
    if not isinstance(w, dict):
        return False, "weights missing"
    for d in DIMS_R1 + DIMS_RX:
        if d not in w:
            return False, f"missing weight {d}"
        if not isinstance(w[d], (int, float)):
            return False, f"weight {d} not numeric"
    if "active_set" not in parsed or not isinstance(parsed["active_set"], list):
        return False, "active_set missing/wrong type"
    if "clarification_needed" not in parsed:
        return False, "clarification_needed missing"
    return True, ""


def append_ledger(rec: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def run_one(eid: str, delegation: str, artifact: str, run_idx: int) -> tuple[bool, str]:
    out_path = PROJ_DIR / f"{eid}__claude__t0.5_run{run_idx}.json"
    if out_path.exists():
        return True, "skip (exists)"

    user = USER_PROMPT_TEMPLATE.format(delegation=delegation, artifact=artifact)
    r = call_claude_cli(SYSTEM_PROMPT, user)
    if "error" in r:
        return False, r["error"]
    parsed = parse_projection(r.get("raw", ""))
    ok, err = validate(parsed)
    record = {
        "example_id": eid,
        "model_family": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "model_tier": "mid",
        "model_host": "claude_code_session",
        "ollama_digest": None,
        "run_idx": run_idx,
        "prompt_version": "spec_pi_v1.0",
        "taxonomy_version": "J_v1.1",
        "temperature": 0.5,            # nominal — opus-4-7 doesn't expose temperature
        "max_tokens": 1500,
        "input_tokens": r.get("input_tokens", -1),
        "output_tokens": r.get("output_tokens", -1),
        "latency_ms": r.get("latency_ms"),
        "raw": r.get("raw"),
        "parsed": parsed if ok else None,
        "validation": {"passed": ok, "error": err},
    }
    out_path.write_text(json.dumps(record, indent=2))
    append_ledger({
        "ts": time.time(),
        "eid": eid,
        "model_id": "claude-sonnet-4-6",
        "tier": "mid",
        "run_idx": run_idx,
        "temperature": 0.5,
        "input_tokens": record["input_tokens"],
        "output_tokens": record["output_tokens"],
        "cost_usd": 0.0,    # subscription
        "validation_passed": ok,
        "error": err,
    })
    return ok, err


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", default=None, help="explicit list of eids")
    ap.add_argument("--ids-range", nargs=2, type=int, default=None,
                    help="inclusive range (start end), e.g. 1 310")
    ap.add_argument("--reps", type=int, default=5)
    args = ap.parse_args()

    if args.ids_range:
        s, e = args.ids_range
        eids = [f"ad_r1_{i:03d}" for i in range(s, e + 1)]
    elif args.ids:
        eids = args.ids
    else:
        ap.error("need --ids or --ids-range")

    PROJ_DIR.mkdir(parents=True, exist_ok=True)
    succ = 0
    fail = 0
    skipped = 0

    for i, eid in enumerate(eids, 1):
        ex_path = EXAMPLES_DIR / f"{eid}.yaml"
        if not ex_path.exists():
            print(f"[{i}/{len(eids)}] {eid} :: missing example file, skip")
            skipped += 1
            continue
        ex = yaml.safe_load(ex_path.read_text())
        delegation = ex["delegation"]
        artifact = ex["artifact"]["text"].rstrip()
        for r in range(1, args.reps + 1):
            t0 = time.time()
            ok, err = run_one(eid, delegation, artifact, r)
            dt = time.time() - t0
            if "skip" in err:
                print(f"[{i}/{len(eids)}] {eid} r{r} :: skip ({dt:.1f}s)")
                skipped += 1
            elif ok:
                print(f"[{i}/{len(eids)}] {eid} r{r} :: OK ({dt:.1f}s)")
                succ += 1
            else:
                print(f"[{i}/{len(eids)}] {eid} r{r} :: FAIL ({err[:80]})")
                fail += 1

    print(f"\n=== DONE: pass={succ} fail={fail} skip={skipped} ===")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
