#!/usr/bin/env python3
"""
Analyze Experiment 1 (cross-family) + 1B (within-model) projection results.

Implements experiment_design_v1.1 §4-§5 metrics:
  d_C^cos  — cross-family cosine distance (mean over family pairs)
  d_C^jac  — cross-family Jaccard distance on active sets
  d_W^cos  — within-model cosine distance (mean over 5C2 = 10 pairs)
  d_W^jac  — within-model Jaccard distance
  R(d) = d_C / d_W
  M_i(d)  — projection-intent mismatch (against r* median, computed in pass2)
  Under/Over projection on R1 dims
  Clarification rate per family
  R1.4 ↔ R1.7 boundary check (extension of pass2 finding)

Outputs:
  - stats/exp1_per_example.json  (d_C, d_W, R, M, etc per example)
  - stats/exp1_aggregate.json    (means, medians, CIs, hypothesis test results)
  - prints headline tables
"""

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import yaml

BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXAMPLES_DIR = BASE / "examples"
PROJ_DIR = BASE / "projection"
STATS_DIR = BASE / "stats"

DIMS = ["R1.1","R1.2","R1.3","R1.4","R1.5","R1.6","R1.7","RX.1","RX.2","RX.3","RX.4","RX.5"]
DIMS_R1 = ["R1.1","R1.2","R1.3","R1.4","R1.5","R1.6","R1.7"]
RX_SET = {"RX.1","RX.2","RX.3","RX.4","RX.5"}

FAMILIES = ["gpt-5", "gemini-2.5-pro", "grok-4"]   # v1.3 panel (spec_models_panel.json projection_cross_family)
WITHIN_RUNS = [1, 2, 3, 4, 5]
# Within-model uses the "claude" filename alias (claude-sonnet-4-6 via Claude
# Code CLI subscription, see scripts/exp1b_claude_within.py). This mirrors what
# paper §V.2 R=14.4 was computed on (claude family within), even though
# spec_models_panel.json now lists gpt-5 as the within source — both datasets
# exist on disk; the claude one is the paper-comparable headline.
WITHIN_FAMILY_ALIAS = "claude"


def vec(weights, dims=DIMS):
    return np.array([weights.get(d, 0.0) for d in dims], dtype=float)


def cos_dist(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    return 1.0 - float(np.dot(a, b) / (na * nb))


def jac_dist(set_a, set_b):
    sa, sb = set(set_a), set(set_b)
    union = sa | sb
    if not union:
        return float("nan")
    return 1.0 - len(sa & sb) / len(union)


def load_proj(eid, family, run_idx, t):
    p = PROJ_DIR / f"{eid}__{family}__t{t:.1f}_run{run_idx}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    if not d.get("validation", {}).get("passed"):
        # try re-parse from raw
        import re
        if d.get("raw"):
            try:
                m = re.search(r"\{.*\}", d["raw"], re.DOTALL)
                if m:
                    p2 = json.loads(m.group(0))
                    if "weights" in p2 and "active_set" in p2:
                        return p2
            except Exception:
                pass
        return None
    return d["parsed"]


def main():
    # load r_star (from pass2)
    r_star = json.loads((STATS_DIR / "r_star_median.json").read_text())

    # load examples for metadata
    examples = {}
    for f in sorted(EXAMPLES_DIR.glob("ad_r1_*.yaml")):
        ex = yaml.safe_load(open(f))
        eid = ex["delegation_id"]
        examples[eid] = {
            "coverage_class": ex["coverage_class"],
            "knowledge_gating": ex["knowledge_gating"],
            "delegation_dim_leakage": ex["delegation_dim_leakage"],
            "load_bearing": list(ex["engineered_flaws"].keys() - {"notes"}),
        }

    per_ex = {}
    for eid in sorted(examples.keys()):
        rec = {"meta": examples[eid]}

        # cross-family @ T=0
        cross = {}
        for fam in FAMILIES:
            p = load_proj(eid, fam, 0, 0.0)
            if p:
                cross[fam] = p
        if len(cross) >= 2:
            # pairwise distances
            d_cos = []
            d_jac = []
            for f1, f2 in combinations(cross.keys(), 2):
                d_cos.append(cos_dist(vec(cross[f1]["weights"]), vec(cross[f2]["weights"])))
                d_jac.append(jac_dist(cross[f1]["active_set"], cross[f2]["active_set"]))
            rec["cross"] = {
                "n_families": len(cross),
                "families": list(cross.keys()),
                "d_C_cos_mean": float(np.nanmean(d_cos)),
                "d_C_jac_mean": float(np.nanmean(d_jac)),
                "weights_per_family": {f: cross[f]["weights"] for f in cross},
                "clarification_per_family": {f: cross[f].get("clarification_needed", False) for f in cross},
            }
            # projection-intent mismatch per family (skipped when r_star unavailable —
            # r_star comes from the closed pilot human-annotation track and only
            # covers ad_r1_001..050; main-run eids 51-310 have no r_star).
            if eid in r_star:
                r_star_vec = vec(r_star[eid])
                rec["cross"]["M_per_family"] = {
                    f: cos_dist(vec(cross[f]["weights"]), r_star_vec) for f in cross
                }
                # under/over projection on R1 only
                for f, p in cross.items():
                    w = p["weights"]
                    rstar_w = r_star[eid]
                    under_num = sum(1 for d in DIMS_R1 if w[d] <= 0.3 and rstar_w[d] > 0.7)
                    under_den = sum(1 for d in DIMS_R1 if rstar_w[d] > 0.7) or 1
                    over_num = sum(1 for d in DIMS_R1 if w[d] > 0.3 and rstar_w[d] <= 0.2)
                    over_den = sum(1 for d in DIMS_R1 if w[d] > 0.3) or 1
                    rec["cross"].setdefault("under_per_family", {})[f] = under_num / under_den
                    rec["cross"].setdefault("over_per_family", {})[f] = over_num / over_den

        # within-model @ T=0.5 (5 runs of WITHIN_FAMILY_ALIAS = claude-sonnet-4-6)
        within = {}
        for r in WITHIN_RUNS:
            p = load_proj(eid, WITHIN_FAMILY_ALIAS, r, 0.5)
            if p:
                within[r] = p
        if len(within) >= 2:
            d_cos = []
            d_jac = []
            for r1, r2 in combinations(within.keys(), 2):
                d_cos.append(cos_dist(vec(within[r1]["weights"]), vec(within[r2]["weights"])))
                d_jac.append(jac_dist(within[r1]["active_set"], within[r2]["active_set"]))
            rec["within"] = {
                "n_runs": len(within),
                "d_W_cos_mean": float(np.nanmean(d_cos)),
                "d_W_jac_mean": float(np.nanmean(d_jac)),
            }

        # R(d)
        if "cross" in rec and "within" in rec:
            d_w = rec["within"]["d_W_cos_mean"]
            if d_w > 1e-6:
                rec["R_cos"] = rec["cross"]["d_C_cos_mean"] / d_w
            else:
                rec["R_cos"] = float("inf") if rec["cross"]["d_C_cos_mean"] > 1e-6 else float("nan")

        per_ex[eid] = rec

    (STATS_DIR / "exp1_per_example.json").write_text(json.dumps(per_ex, indent=2, default=str))

    # ---- aggregate ----
    print("=" * 72)
    print("EXPERIMENT 1 + 1B: PROJECTION RESULTS")
    print("=" * 72)

    # cross-family d_C
    d_C_all = [r["cross"]["d_C_cos_mean"] for r in per_ex.values()
               if "cross" in r and not np.isnan(r["cross"]["d_C_cos_mean"])]
    d_W_all = [r["within"]["d_W_cos_mean"] for r in per_ex.values()
               if "within" in r and not np.isnan(r["within"]["d_W_cos_mean"])]
    R_all = [r["R_cos"] for r in per_ex.values() if "R_cos" in r and np.isfinite(r["R_cos"])]

    print()
    print(f"--- Cross-family distance d_C^cos (n={len(d_C_all)}) ---")
    print(f"  mean   = {np.mean(d_C_all):.4f}")
    print(f"  median = {np.median(d_C_all):.4f}")
    print(f"  std    = {np.std(d_C_all):.4f}")

    print()
    print(f"--- Within-model distance d_W^cos (n={len(d_W_all)}) ---")
    print(f"  mean   = {np.mean(d_W_all):.4f}")
    print(f"  median = {np.median(d_W_all):.4f}")
    print(f"  std    = {np.std(d_W_all):.4f}")

    print()
    print(f"--- R(d) = d_C / d_W (n={len(R_all)}) ---")
    print(f"  mean   = {np.mean(R_all):.4f}")
    print(f"  median = {np.median(R_all):.4f}")
    print(f"  std    = {np.std(R_all):.4f}")
    n_R_gt_1 = sum(1 for r in R_all if r > 1.0)
    n_R_gt_1_2 = sum(1 for r in R_all if r > 1.2)
    print(f"  R > 1.0: {n_R_gt_1}/{len(R_all)} ({n_R_gt_1/len(R_all)*100:.1f}%)")
    print(f"  R > 1.2: {n_R_gt_1_2}/{len(R_all)} ({n_R_gt_1_2/len(R_all)*100:.1f}%)")

    # paired bootstrap CI for d_C - d_W
    print()
    paired = [(r["cross"]["d_C_cos_mean"], r["within"]["d_W_cos_mean"])
              for r in per_ex.values()
              if "cross" in r and "within" in r
              and not np.isnan(r["cross"]["d_C_cos_mean"]) and not np.isnan(r["within"]["d_W_cos_mean"])]
    diffs = np.array([c - w for c, w in paired])
    rng = np.random.default_rng(42)
    n_boot = 5000
    boot_means = np.array([np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(n_boot)])
    ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])
    print(f"--- Paired d_C - d_W (n={len(paired)}) ---")
    print(f"  mean diff = {np.mean(diffs):.4f}")
    print(f"  95% bootstrap CI = [{ci_lo:.4f}, {ci_hi:.4f}]")
    print(f"  Hypothesis H1.1 (CI excludes 0): {'PASS' if ci_lo > 0 else 'FAIL'}")

    # Wilcoxon signed-rank
    try:
        from scipy.stats import wilcoxon
        stat, p = wilcoxon(diffs, alternative="greater")
        print(f"  Wilcoxon signed-rank (d_C > d_W): stat={stat:.2f}, p={p:.4f}")
        print(f"  Hypothesis H1B.3 (p < 0.05): {'PASS' if p < 0.05 else 'FAIL'}")
    except ImportError:
        print(f"  (scipy not installed — Wilcoxon skipped)")

    # ---- by coverage class ----
    print()
    print("--- d_C by coverage class ---")
    by_class = {}
    for eid, r in per_ex.items():
        if "cross" not in r:
            continue
        cls = r["meta"]["coverage_class"]
        by_class.setdefault(cls, []).append(r["cross"]["d_C_cos_mean"])
    for cls, vals in sorted(by_class.items()):
        print(f"  {cls:10} n={len(vals):3} d_C mean={np.mean(vals):.4f}  median={np.median(vals):.4f}")

    # ---- by knowledge_gating ----
    print()
    print("--- d_C by knowledge_gating ---")
    by_kg = {}
    for eid, r in per_ex.items():
        if "cross" not in r:
            continue
        kg = r["meta"]["knowledge_gating"]
        by_kg.setdefault(kg, []).append(r["cross"]["d_C_cos_mean"])
    for kg in ["low", "moderate", "high"]:
        if kg in by_kg:
            v = by_kg[kg]
            print(f"  {kg:10} n={len(v):3} d_C mean={np.mean(v):.4f}  median={np.median(v):.4f}")

    # ---- clarification rates ----
    print()
    print("--- Clarification rate per family (cross-family runs) ---")
    clar_count = {f: 0 for f in FAMILIES}
    n_cross = 0
    for r in per_ex.values():
        if "cross" not in r:
            continue
        n_cross += 1
        for f, c in r["cross"]["clarification_per_family"].items():
            if c:
                clar_count[f] += 1
    for f in FAMILIES:
        print(f"  {f}: {clar_count[f]}/{n_cross} ({clar_count[f]/max(1,n_cross)*100:.1f}%)")

    # ---- ambiguous-class clarification ----
    print()
    print("--- Clarification on AMBIGUOUS examples (n=5 expected to clarify) ---")
    ambig_eids = [eid for eid, r in per_ex.items() if r["meta"]["coverage_class"] == "ambiguous"]
    for eid in ambig_eids:
        r = per_ex.get(eid, {}).get("cross", {})
        clars = r.get("clarification_per_family", {})
        d_c = r.get("d_C_cos_mean", float("nan"))
        print(f"  {eid}: d_C={d_c:.3f}  clar={clars}")

    # ---- control-class sanity ----
    print()
    print("--- d_C on CONTROL examples (expected ~0) ---")
    ctrl_eids = [eid for eid, r in per_ex.items() if r["meta"]["coverage_class"] == "control"]
    for eid in ctrl_eids:
        d_c = per_ex.get(eid, {}).get("cross", {}).get("d_C_cos_mean", float("nan"))
        d_w = per_ex.get(eid, {}).get("within", {}).get("d_W_cos_mean", float("nan"))
        print(f"  {eid}: d_C={d_c:.4f}  d_W={d_w:.4f}")

    # ---- save aggregate ----
    agg = {
        "n_examples": len(per_ex),
        "d_C_cos_mean": float(np.mean(d_C_all)) if d_C_all else None,
        "d_C_cos_median": float(np.median(d_C_all)) if d_C_all else None,
        "d_W_cos_mean": float(np.mean(d_W_all)) if d_W_all else None,
        "d_W_cos_median": float(np.median(d_W_all)) if d_W_all else None,
        "R_mean": float(np.mean(R_all)) if R_all else None,
        "R_median": float(np.median(R_all)) if R_all else None,
        "R_gt_1_count": n_R_gt_1,
        "R_gt_1_2_count": n_R_gt_1_2,
        "paired_diff_mean": float(np.mean(diffs)) if len(diffs) else None,
        "paired_diff_ci_95": [float(ci_lo), float(ci_hi)] if len(diffs) else None,
        "by_class": {k: {"n": len(v), "mean": float(np.mean(v)), "median": float(np.median(v))} for k, v in by_class.items()},
        "by_knowledge_gating": {k: {"n": len(v), "mean": float(np.mean(v)), "median": float(np.median(v))} for k, v in by_kg.items()},
        "clarification_per_family": clar_count,
    }
    (STATS_DIR / "exp1_aggregate.json").write_text(json.dumps(agg, indent=2))
    print()
    print(f"Per-example: {STATS_DIR}/exp1_per_example.json")
    print(f"Aggregate:   {STATS_DIR}/exp1_aggregate.json")


if __name__ == "__main__":
    main()
