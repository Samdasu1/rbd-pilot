"""Build a 250-row plan for the main-run dataset expansion (n=300 total).

Distribution (proportionally scaled from pilot spec §2):
  - single:    154   (22 per R1 dim × 7)
  - dual:       50   (5 per pair × 10 pairs)
  - ambiguous:  25
  - control:    21
  Total:       250

Constraints:
  - knowledge_gating: ≤30% high overall (~75 max). Mix: 60% low, 25% moderate, 15% high.
  - template T01-T10: roughly uniform (25 each)
  - delegation_dim_leakage: 'yes' only for control; 'partial' ≤ 5%
  - domains: random sample from DOMAINS list (with replacement weighted)

Run from repo root:
  python3 scripts/build_main_plan.py --start-id 61 --count 250 --out scripts/plan_main_250.json
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

R1_DIMS = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]

DUAL_PAIRS = [
    ["R1.1", "R1.4"],  # conceptual + novelty
    ["R1.1", "R1.2"],  # conceptual + logical
    ["R1.2", "R1.3"],  # logical + evidence
    ["R1.3", "R1.7"],  # evidence + citation
    ["R1.4", "R1.7"],  # novelty + citation
    ["R1.1", "R1.5"],  # conceptual + structural
    ["R1.5", "R1.6"],  # structural + polish
    ["R1.3", "R1.6"],  # evidence + polish
    ["R1.2", "R1.4"],  # logical + novelty
    ["R1.5", "R1.7"],  # structural + citation
]

AMBIGUOUS_PAIRS = [  # for clarification cases
    ["R1.1", "R1.4"], ["R1.2", "R1.3"], ["R1.5", "R1.6"],
    ["R1.3", "R1.7"], ["R1.4", "R1.7"], ["R1.1", "R1.2"],
]

# control: dim → leakage-rich template + custom delegation
CONTROL_PROFILES = [
    ("R1.6", "T04", "Polish this."),                  # polish leaks R1.6
    ("R1.7", None, "Check the citations."),           # explicit citation cue
    ("R1.4", None, "Position this against prior work."),
    ("R1.5", None, "Restructure the section flow."),
    ("R1.3", None, "Verify the evidence supports the claims."),
    ("R1.2", None, "Check the logical consistency."),
    ("R1.1", None, "Reframe the conceptual story."),
]

FLAW_CODES = {
    "R1.1": ["F1.1.a", "F1.1.b", "F1.1.c"],
    "R1.2": ["F1.2.a", "F1.2.b", "F1.2.c"],
    "R1.3": ["F1.3.a", "F1.3.b", "F1.3.c"],
    "R1.4": ["F1.4.a", "F1.4.b", "F1.4.c"],
    "R1.5": ["F1.5.a", "F1.5.b", "F1.5.c"],
    "R1.6": ["F1.6.a", "F1.6.b", "F1.6.c"],
    "R1.7": ["F1.7.a", "F1.7.b", "F1.7.c"],
}

TEMPLATES_NONLEAK = ["T01", "T02", "T03", "T05", "T06", "T08", "T09", "T10"]

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

KG_LEVELS = ["low", "low", "low", "low", "moderate", "moderate", "high"]  # ~57/29/14


def build_plan(start_id: int, count: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    next_id = start_id

    # distribution targets
    n_single = int(count * 0.616)        # 154 of 250
    n_dual = int(count * 0.20)           # 50
    n_ambig = int(count * 0.10)          # 25
    n_control = count - n_single - n_dual - n_ambig  # rest

    # ----- single -----
    per_dim = [n_single // 7] * 7
    for i in range(n_single - sum(per_dim)):
        per_dim[i] += 1
    for di, dim in enumerate(R1_DIMS):
        for _ in range(per_dim[di]):
            rows.append({
                "delegation_id": f"ad_r1_{next_id:03d}",
                "template_id": rng.choice(TEMPLATES_NONLEAK),
                "coverage_class": "single",
                "target_dims": [dim],
                "domain": rng.choice(DOMAINS),
                "knowledge_gating": rng.choice(KG_LEVELS),
                "flaw_codes": {dim: [rng.choice(FLAW_CODES[dim])]},
                "delegation_dim_leakage": "no",
            })
            next_id += 1

    # ----- dual -----
    per_pair = [n_dual // len(DUAL_PAIRS)] * len(DUAL_PAIRS)
    for i in range(n_dual - sum(per_pair)):
        per_pair[i] += 1
    for pi, pair in enumerate(DUAL_PAIRS):
        for _ in range(per_pair[pi]):
            rows.append({
                "delegation_id": f"ad_r1_{next_id:03d}",
                "template_id": rng.choice(TEMPLATES_NONLEAK),
                "coverage_class": "dual",
                "target_dims": list(pair),
                "domain": rng.choice(DOMAINS),
                "knowledge_gating": rng.choice(KG_LEVELS),
                "flaw_codes": {d: [rng.choice(FLAW_CODES[d])] for d in pair},
                "delegation_dim_leakage": "no",
            })
            next_id += 1

    # ----- ambiguous -----
    for i in range(n_ambig):
        pair = rng.choice(AMBIGUOUS_PAIRS)
        rows.append({
            "delegation_id": f"ad_r1_{next_id:03d}",
            "template_id": rng.choice(TEMPLATES_NONLEAK),
            "coverage_class": "ambiguous",
            "target_dims": list(pair),
            "domain": rng.choice(DOMAINS),
            "knowledge_gating": rng.choice(KG_LEVELS[:5]),  # avoid high for ambig
            "flaw_codes": {d: [rng.choice(FLAW_CODES[d])] for d in pair},
            "delegation_dim_leakage": "no",
        })
        next_id += 1

    # ----- control -----
    profiles = list(CONTROL_PROFILES)
    rng.shuffle(profiles)
    for i in range(n_control):
        dim, tmpl, deleg = profiles[i % len(profiles)]
        row = {
            "delegation_id": f"ad_r1_{next_id:03d}",
            "template_id": tmpl or "T05",  # placeholder if custom delegation
            "coverage_class": "control",
            "target_dims": [dim],
            "domain": rng.choice(DOMAINS),
            "knowledge_gating": "low",
            "flaw_codes": {dim: [rng.choice(FLAW_CODES[dim]), rng.choice(FLAW_CODES[dim])]},
            "delegation_dim_leakage": "yes",
        }
        if tmpl is None:
            row["custom_delegation"] = deleg
        rows.append(row)
        next_id += 1

    # final sanity: knowledge_gating cap
    high_count = sum(1 for r in rows if r["knowledge_gating"] == "high")
    cap = int(count * 0.30)
    while high_count > cap:
        # demote some 'high' to 'moderate' deterministically
        for r in rows:
            if r["knowledge_gating"] == "high":
                r["knowledge_gating"] = "moderate"
                high_count -= 1
                if high_count <= cap:
                    break
    rng.shuffle(rows)  # interleave so generation order isn't grouped by class
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-id", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    plan = build_plan(args.start_id, args.count, args.seed)
    args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    # summary
    from collections import Counter
    cc = Counter(r["coverage_class"] for r in plan)
    kg = Counter(r["knowledge_gating"] for r in plan)
    tmpl = Counter(r["template_id"] for r in plan)
    print(f"wrote {args.out} ({len(plan)} rows)")
    print(f"  coverage_class: {dict(cc)}")
    print(f"  knowledge_gating: {dict(kg)}")
    print(f"  template: {dict(sorted(tmpl.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
