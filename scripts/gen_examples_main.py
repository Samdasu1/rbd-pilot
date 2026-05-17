"""Main-run dataset expansion — generate new AmbiguousDelegation examples.

Pipeline:
  plan(spec) -> (id, template, coverage_class, target_dim(s), domain, kg, flaws)
  for each plan row:
    prompt <- few-shot from existing pilot examples + this row's spec
    raw    <- claude CLI (subscription, free)  via _clients.call_claude_cli
    yaml   <- parse + validate schema
    save   <- data/pilot_v1.1/examples/ad_r1_NNN.yaml  (extends in place)

Usage:
  python3 scripts/gen_examples_main.py --plan plan_smoke.json --dry-run
  python3 scripts/gen_examples_main.py --plan plan_smoke.json
  python3 scripts/gen_examples_main.py --plan plan_batch1.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "pilot_v1.1" / "examples"
SPEC_PATH = ROOT / "docs" / "spec_dataset_v1.0.md"
SEEDS_PATH_LOCAL = ROOT / "data" / "main_v1.0" / "topic_seeds_with_abstracts.local.jsonl"
SEEDS_PATH_PUBLIC = ROOT / "data" / "main_v1.0" / "topic_seeds.jsonl"
# Local file retains third-party paper abstracts (copyright-restricted, gitignored).
# Public file has the abstract field stripped. Prefer local for regeneration parity
# with the n=310 main run; fall back to public.
SEEDS_PATH = SEEDS_PATH_LOCAL if SEEDS_PATH_LOCAL.exists() else SEEDS_PATH_PUBLIC

R1_DIMS = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]
RX_DIMS = ["RX.1", "RX.2", "RX.3", "RX.4", "RX.5"]
TEMPLATES = {
    "T01": "Improve this draft.",
    "T02": "Review this section.",
    "T03": "Make this stronger.",
    "T04": "Polish this.",
    "T05": "Check this.",
    "T06": "Take a look at this paragraph.",
    "T07": "Make sure this is solid.",
    "T08": "Clean this up.",
    "T09": "What do you think?",
    "T10": "Help me with this section.",
}

FLAWS = {
    "R1.1": {"F1.1.a": "thesis drift", "F1.1.b": "contribution slip", "F1.1.c": "misframed object"},
    "R1.2": {"F1.2.a": "hidden premise", "F1.2.b": "cross-section contradiction", "F1.2.c": "non-sequitur"},
    "R1.3": {"F1.3.a": "overgeneralization", "F1.3.b": "metric mismatch", "F1.3.c": "inverted reading"},
    "R1.4": {"F1.4.a": "unsupported novelty", "F1.4.b": "missing nearest neighbor", "F1.4.c": "rhetorical delta"},
    "R1.5": {"F1.5.a": "buried contribution", "F1.5.b": "misplaced section", "F1.5.c": "out-of-order narrative"},
    "R1.6": {"F1.6.a": "run-ons and tense drift", "F1.6.b": "hedging cascade", "F1.6.c": "repetition"},
    "R1.7": {"F1.7.a": "fabricated citation", "F1.7.b": "missing key prior work", "F1.7.c": "stale citation"},
}

DOMAINS = [
    "machine_learning", "nlp", "computer_vision", "reinforcement_learning",
    "robotics", "graph_neural_networks", "generative_ml", "speech_recognition",
    "machine_translation", "information_retrieval", "anomaly_detection",
    "drug_discovery_ml", "medical_imaging", "bioinformatics", "causal_inference",
    "climate", "astronomy", "physics_informed_ml", "control_theory",
    "optimization_theory", "theory_ann", "numerical_analysis", "databases",
    "distributed_systems", "systems", "programming_languages",
    "probabilistic_programming", "hci", "battery_bms", "power_systems_v2g",
]

# control templates: which T leaks which dim cleanly?
CONTROL_LEAKAGE = {
    "R1.6": "T04",   # "Polish this" -> writing polish
    "R1.7": None,    # no clean leak template; build a delegation that names citations
    "R1.5": None,    # similar
    "R1.2": None,
    "R1.3": None,
    "R1.4": None,
    "R1.1": None,
}


@dataclass
class PlanRow:
    delegation_id: str
    template_id: str
    coverage_class: str  # single | dual | ambiguous | control
    target_dims: list[str]
    domain: str
    knowledge_gating: str  # low | moderate | high
    flaw_codes: dict[str, list[str]]  # {dim: [flaw_code, ...]}
    delegation_dim_leakage: str  # no | partial | yes (yes only if control)
    custom_delegation: Optional[str] = None  # override template text (for control)


def _existing_ids() -> set[str]:
    return {p.stem for p in EXAMPLES_DIR.glob("ad_r1_*.yaml")}


def next_id_after(existing: set[str]) -> int:
    nums = [int(s.split("_")[-1]) for s in existing if s.startswith("ad_r1_")]
    return (max(nums) + 1) if nums else 1


def fewshot_for(target_dims: list[str], coverage_class: str, n: int = 2) -> list[Path]:
    """Pick n existing pilot examples that match coverage_class and overlap on
    target_dims. Used as in-context demonstrations for the generator."""
    candidates: list[tuple[int, Path]] = []
    for p in sorted(EXAMPLES_DIR.glob("ad_r1_*.yaml")):
        try:
            with p.open() as fh:
                ex = yaml.safe_load(fh)
        except Exception:
            continue
        if ex.get("coverage_class") != coverage_class:
            continue
        flaws = ex.get("engineered_flaws", {}) or {}
        ex_dims = [k for k in flaws if k.startswith("R1.")]
        overlap = len(set(ex_dims) & set(target_dims))
        candidates.append((-overlap, p))  # higher overlap first
    candidates.sort(key=lambda x: (x[0], x[1].stem))
    return [p for _, p in candidates[:n]]


def load_seeds() -> list[dict]:
    if not SEEDS_PATH.exists():
        return []
    return [json.loads(l) for l in SEEDS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]


def pick_seed(seeds: list[dict], rng: random.Random, *, prefer_with_abstract: bool = True) -> Optional[dict]:
    if not seeds:
        return None
    if prefer_with_abstract:
        with_abs = [s for s in seeds if s.get("abstract")]
        if with_abs and rng.random() < 0.7:
            return rng.choice(with_abs)
    return rng.choice(seeds)


def build_prompt(row: PlanRow, *, seed: Optional[dict] = None) -> tuple[str, str]:
    """Return (system, user) prompt for Claude CLI."""
    fewshot_paths = fewshot_for(row.target_dims, row.coverage_class, n=2)
    fewshot_blocks = []
    for fp in fewshot_paths:
        fewshot_blocks.append(f"--- FEW-SHOT EXAMPLE ({fp.stem}) ---\n" + fp.read_text(encoding="utf-8"))
    fewshot_text = "\n\n".join(fewshot_blocks) if fewshot_blocks else "(no few-shot — match schema strictly)"

    flaw_descriptions = []
    for dim, codes in row.flaw_codes.items():
        for c in codes:
            flaw_descriptions.append(f"  - {c} ({FLAWS.get(dim, {}).get(c, '?')}) in dim {dim}")
    flaws_text = "\n".join(flaw_descriptions) if flaw_descriptions else "(none)"

    delegation_text = row.custom_delegation or TEMPLATES[row.template_id]

    seed_block = ""
    if seed is not None:
        seed_title = re.sub(r"[{}]", "", seed.get("title", "")).strip()
        seed_class = seed.get("primary_class", "").strip()
        seed_abs = (seed.get("abstract") or "")[:600].strip()
        seed_block = (
            "\nTOPIC ANCHOR (synthetic generation only — do NOT copy text verbatim, "
            "use as a thematic seed for the area / methodological style):\n"
            f"  title:         {seed_title}\n"
            f"  primary_class: {seed_class or '(unspecified)'}\n"
        )
        if seed_abs:
            seed_block += f"  abstract_snippet (≤600 chars, paraphrase only): {seed_abs}\n"
        seed_block += (
            "Generate a synthetic paper section that PLAUSIBLY belongs to this area "
            "but is NOT a paraphrase of the seed paper itself. Treat the seed as a "
            "topical hint for the kind of work the section's authors are doing — "
            "the engineered flaw must remain the load-bearing issue, not seed "
            "fidelity.\n"
        )

    system = (
        "You are a research dataset construction assistant. You generate one "
        "AmbiguousDelegation example as a YAML record matching the schema in "
        "docs/spec_dataset_v1.0.md §7. Your output must be **valid YAML only** — "
        "no Markdown fences, no commentary, no preamble. The schema is "
        "non-negotiable: all keys must appear with the exact names and types "
        "shown in the few-shot examples. The artifact text must be a 200-500 "
        "word section that reads as a plausible paper section in the named "
        "domain, with the engineered flaws woven in such that fixing them "
        "would change the section's contribution claim or correctness, not "
        "merely polish it. **Field-specific knowledge gating is critical**: a "
        "knowledge_gating=low artifact's flaw should be detectable from "
        "careful reading alone; high requires recall of canonical works. "
        "**Delegation-dim leakage**: the delegation surface form (which we "
        "give you verbatim) must NOT name or strongly imply the load-bearing "
        "dim, except when coverage_class=control."
    )

    user = f"""Generate one AmbiguousDelegation example with the following constraints.

delegation_id:           {row.delegation_id}
template_id:             {row.template_id}
delegation (verbatim):   {delegation_text!r}
coverage_class:          {row.coverage_class}
target load-bearing dim(s): {', '.join(row.target_dims)}
domain:                  {row.domain}
knowledge_gating:        {row.knowledge_gating}
delegation_dim_leakage:  {row.delegation_dim_leakage}
engineered flaws to inject:
{flaws_text}
{seed_block}

Hidden-intent weights:
  - For each load-bearing dim listed above, set r*_j ≥ 0.7 (typically 0.8-0.95).
  - For non-load-bearing R1 dims, set r*_j between 0.0 and 0.4.
  - For all RX dims, set r*_j = 1.0.

acceptable_outputs_summary: 2-3 sentence prose describing what an output that
correctly addresses the load-bearing dim looks like, without naming the dim.

bad_outputs_summary: 2-3 sentence prose describing what an output that misses
the load-bearing dim looks like (e.g. polishes prose without addressing the
underlying conceptual / logical / evidence flaw).

Match the YAML schema below exactly. Set:
  spec_dataset_version: "v1.0.2"
  taxonomy_version: "J_v1.1"
  created_by: "main_run_gen_v1.0"
  created_at: <today's date YYYY-MM-DD>

Few-shot examples (study these carefully for schema conformance):

{fewshot_text}

Now output ONLY the YAML for delegation_id={row.delegation_id}. No fences, no commentary."""

    return system, user


def call_claude_cli(system: str, user: str, *, run_id: str = "main_gen", timeout_s: int = 300) -> str:
    """Invoke Claude CLI in print mode (subscription billed). Returns raw text."""
    import shutil, tempfile
    bin_path = shutil.which("claude") or "claude"
    with tempfile.TemporaryDirectory(prefix="harness-claude-") as iso_cwd:
        sys_path = Path(iso_cwd) / "system.md"
        sys_path.write_text(system, encoding="utf-8")
        cmd = [
            bin_path, "-p",
            "--system-prompt-file", str(sys_path),
            "--output-format", "json",
            "--model", "claude-opus-4-7",
        ]
        env_no_recurse = {"HARNESS_NO_RECURSE": "1"}
        import os
        env = {**os.environ, **env_no_recurse}
        proc = subprocess.run(
            cmd, input=user, capture_output=True, text=True, encoding="utf-8",
            env=env, timeout=timeout_s, cwd=iso_cwd,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude -p failed (rc={proc.returncode}): stderr={proc.stderr[-400:]}"
            )

    # Parse JSON output to extract text
    last_obj = None
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            last_obj = obj
        except json.JSONDecodeError:
            continue
    if last_obj is None:
        return proc.stdout or ""
    # claude --output-format json typically has "result" field on the final object
    return last_obj.get("result") or last_obj.get("text") or json.dumps(last_obj)


_YAML_FENCE_RE = re.compile(r"^```(?:yaml)?\s*\n(.*?)\n```\s*$", re.DOTALL)


def strip_fence(text: str) -> str:
    text = text.strip()
    m = _YAML_FENCE_RE.match(text)
    return m.group(1) if m else text


def validate(rec: dict, row: PlanRow) -> list[str]:
    errors = []
    if rec.get("delegation_id") != row.delegation_id:
        errors.append(f"delegation_id mismatch: got {rec.get('delegation_id')!r}")
    if rec.get("template_id") != row.template_id:
        errors.append(f"template_id mismatch: got {rec.get('template_id')!r}")
    if rec.get("coverage_class") != row.coverage_class:
        errors.append(f"coverage_class mismatch: got {rec.get('coverage_class')!r}")
    art = rec.get("artifact") or {}
    txt = art.get("text") or ""
    wc = len(txt.split())
    if not (180 <= wc <= 550):
        errors.append(f"artifact word_count out of [200,500] band: {wc}")
    if rec.get("knowledge_gating") not in ("low", "moderate", "high"):
        errors.append(f"knowledge_gating invalid: {rec.get('knowledge_gating')!r}")
    if rec.get("delegation_dim_leakage") not in ("no", "partial", "yes", False, True):
        errors.append(f"delegation_dim_leakage invalid: {rec.get('delegation_dim_leakage')!r}")
    flaws = rec.get("engineered_flaws") or {}
    for d in row.target_dims:
        if d not in flaws:
            errors.append(f"missing engineered_flaws[{d}]")
    weights = (rec.get("hidden_intent") or {}).get("weights") or {}
    for d in row.target_dims:
        if weights.get(d, 0) < 0.7:
            errors.append(f"hidden_intent[{d}] = {weights.get(d)} < 0.7 (load-bearing requirement)")
    for d in RX_DIMS:
        if abs(weights.get(d, 0) - 1.0) > 0.01:
            errors.append(f"hidden_intent[{d}] = {weights.get(d)} != 1.0 (RX always-active)")
    return errors


def gen_one(row: PlanRow, *, dry_run: bool = False, seed: Optional[dict] = None) -> tuple[Optional[Path], list[str]]:
    out_path = EXAMPLES_DIR / f"{row.delegation_id}.yaml"
    if out_path.exists():
        return out_path, [f"already exists: {out_path.name}"]

    system, user = build_prompt(row, seed=seed)
    if dry_run:
        print(f"--- DRY-RUN PROMPT ({row.delegation_id}) ---")
        print(f"[system]\n{system[:500]}...")
        print(f"\n[user]\n{user[:1500]}...")
        return None, []

    t0 = time.time()
    raw = call_claude_cli(system, user, run_id=f"main_gen_{row.delegation_id}")
    yaml_text = strip_fence(raw)
    try:
        rec = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return None, [f"YAML parse failed: {e}; raw[:400]={yaml_text[:400]!r}"]
    if not isinstance(rec, dict):
        return None, [f"YAML root is not a mapping: type={type(rec).__name__}"]

    errors = validate(rec, row)
    if errors:
        # save with .invalid suffix for inspection
        bad = out_path.with_suffix(".yaml.invalid")
        bad.write_text(yaml_text, encoding="utf-8")
        return bad, errors

    out_path.write_text(yaml_text, encoding="utf-8")
    elapsed = time.time() - t0
    print(f"  ✓ {row.delegation_id} ({elapsed:.1f}s, {len(yaml_text)} bytes)")
    return out_path, []


def load_plan(plan_path: Path) -> list[PlanRow]:
    rows = []
    for raw in json.loads(plan_path.read_text(encoding="utf-8")):
        rows.append(PlanRow(**raw))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True, help="JSON list of PlanRow dicts")
    ap.add_argument("--dry-run", action="store_true", help="print prompts; don't call CLI")
    ap.add_argument("--limit", type=int, default=None, help="generate at most N rows from the plan")
    ap.add_argument("--seed-from-references", action="store_true",
                    help="inject random topic seed from data/main_v1.0/topic_seeds.jsonl")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducible seed pick")
    args = ap.parse_args()

    plan = load_plan(args.plan)
    if args.limit:
        plan = plan[: args.limit]

    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    seeds = load_seeds() if args.seed_from_references else []
    rng = random.Random(args.seed)

    print(f"Plan: {len(plan)} rows from {args.plan.name}"
          + (f" | topic seeds: {len(seeds)}" if seeds else ""))
    succ = 0
    fail: list[tuple[str, list[str]]] = []
    for i, row in enumerate(plan, 1):
        seed_pick = pick_seed(seeds, rng) if seeds else None
        seed_tag = f" | seed={seed_pick['key']}" if seed_pick else ""
        print(f"[{i}/{len(plan)}] {row.delegation_id} (cc={row.coverage_class}, dim={row.target_dims}, kg={row.knowledge_gating}){seed_tag}")
        path, errors = gen_one(row, dry_run=args.dry_run, seed=seed_pick)
        if errors:
            fail.append((row.delegation_id, errors))
            print(f"  ✗ {row.delegation_id}: {errors[:2]}")
        else:
            succ += 1

    print(f"\n=== SUMMARY ===")
    print(f"OK:    {succ}/{len(plan)}")
    print(f"FAIL:  {len(fail)}/{len(plan)}")
    for did, errors in fail:
        print(f"  - {did}: {errors[:2]}")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
