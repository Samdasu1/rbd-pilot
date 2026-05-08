#!/usr/bin/env python3
"""
Analyze Experiment 2 results.

Inputs:
  data/pilot_v1.1/execution/{eid}__{condition}__{executor}.json
  data/pilot_v1.1/judge/{eid}__{condition}__{executor}__{judge}.json
  data/pilot_v1.1/stats/r_star_median.json     (for active set)
  data/pilot_v1.1/examples/*.yaml               (for metadata)

Computes per (example, condition):
  v_ij = (s_ij - 1) / 4         (normalized fulfillment per dim)
  ℓ_ij = 1 - v_ij               (loss per dim)
  L_i = mean over active dims    (settlement loss; w_j uniform for pilot)
  RX.3 score                     (scope adherence)
  RX.2 score                     (overclaim avoidance)
  Per-class breakdown
  Direct vs projection_driven paired comparison
"""

import json
from collections import defaultdict
from itertools import product
from pathlib import Path

import numpy as np
import yaml

BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXAMPLES_DIR = BASE / "examples"
EXEC_DIR = BASE / "execution"
JUDGE_DIR = BASE / "judge"
STATS_DIR = BASE / "stats"

CONDITIONS = ["direct", "projection_driven"]
EXECUTOR = "claude"
JUDGE_FAMILIES = ["claude", "gpt", "gemini"]
DIMS_R1 = ["R1.1","R1.2","R1.3","R1.4","R1.5","R1.6","R1.7"]
RX_DIMS = ["RX.1","RX.2","RX.3","RX.4","RX.5"]
DIMS = DIMS_R1 + RX_DIMS


def load_judge_scores(eid, condition):
    """Returns {judge_family: {dim: score}} for valid judges. score median across judges per dim."""
    judges = {}
    for jf in JUDGE_FAMILIES:
        p = JUDGE_DIR / f"{eid}__{condition}__{EXECUTOR}__{jf}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        if not d.get("validation", {}).get("passed"):
            continue
        judges[jf] = d["parsed"]["scores"]
    return judges


def median_v_ij(judges, active_set):
    """Aggregate score across judges per dim, return v_ij = (median(s)-1)/4."""
    out = {}
    for d in active_set:
        vals = []
        for jf, scores in judges.items():
            if d in scores:
                vals.append(scores[d])
        if vals:
            s = np.median(vals)
            out[d] = (s - 1) / 4.0
    return out


def main():
    r_star = json.loads((STATS_DIR / "r_star_median.json").read_text())
    examples = {}
    for f in sorted(EXAMPLES_DIR.glob("ad_r1_*.yaml")):
        ex = yaml.safe_load(open(f))
        examples[ex["delegation_id"]] = ex

    per_ex = {}
    for eid in sorted(examples.keys()):
        meta = examples[eid]
        weights = r_star[eid]
        active = [d for d in DIMS_R1 if weights[d] > 0.3] + RX_DIMS
        rec = {
            "coverage_class": meta["coverage_class"],
            "knowledge_gating": meta["knowledge_gating"],
            "delegation_dim_leakage": meta["delegation_dim_leakage"],
            "load_bearing": list(meta["engineered_flaws"].keys() - {"notes"}),
            "active_set": active,
            "by_condition": {},
        }
        for cond in CONDITIONS:
            judges = load_judge_scores(eid, cond)
            v = median_v_ij(judges, active)
            if not v:
                continue
            # uniform weight settlement loss
            losses = [1 - v[d] for d in active if d in v]
            L = float(np.mean(losses)) if losses else float("nan")
            # weighted by hidden intent (r* importance) on R1 only
            r1_active = [d for d in active if d.startswith("R1") and d in v]
            if r1_active:
                w_sum = sum(weights[d] for d in r1_active)
                if w_sum > 0:
                    L_weighted_R1 = sum(weights[d] * (1 - v[d]) for d in r1_active) / w_sum
                else:
                    L_weighted_R1 = float("nan")
            else:
                L_weighted_R1 = float("nan")
            rec["by_condition"][cond] = {
                "n_judges": len(judges),
                "v_ij": v,
                "L_uniform": L,
                "L_weighted_R1_only": L_weighted_R1,
                "RX_3_score_v": v.get("RX.3", float("nan")),
                "RX_2_score_v": v.get("RX.2", float("nan")),
            }
        per_ex[eid] = rec

    (STATS_DIR / "exp2_per_example.json").write_text(json.dumps(per_ex, indent=2, default=str))

    # ---- aggregate ----
    print("="*72)
    print("EXPERIMENT 2: SETTLEMENT LOSS (Direct vs Projection-driven)")
    print("="*72)

    # collect per-condition L
    L_by_cond = defaultdict(list)
    for eid, rec in per_ex.items():
        for cond in CONDITIONS:
            if cond in rec["by_condition"]:
                L_by_cond[cond].append(rec["by_condition"][cond]["L_uniform"])
    print()
    print("--- Settlement loss L (uniform weight, lower is better) ---")
    for cond in CONDITIONS:
        v = L_by_cond[cond]
        print(f"  {cond:20} n={len(v):3} mean={np.mean(v):.4f}  median={np.median(v):.4f}  std={np.std(v):.4f}")

    # paired diff (direct - projection_driven; positive = projection wins)
    paired = []
    for eid, rec in per_ex.items():
        bc = rec["by_condition"]
        if "direct" in bc and "projection_driven" in bc:
            paired.append((eid, bc["direct"]["L_uniform"], bc["projection_driven"]["L_uniform"]))
    diffs = np.array([d - p for _, d, p in paired])
    print()
    print(f"--- Paired (direct - projection_driven) on n={len(paired)} ---")
    print(f"  mean L_direct        = {np.mean([d for _,d,_ in paired]):.4f}")
    print(f"  mean L_projection    = {np.mean([p for _,_,p in paired]):.4f}")
    print(f"  mean diff (D - P)    = {np.mean(diffs):.4f}    (positive = projection wins)")
    print(f"  median diff          = {np.median(diffs):.4f}")
    n_better = sum(1 for x in diffs if x > 0.01)
    n_worse = sum(1 for x in diffs if x < -0.01)
    n_tie = sum(1 for x in diffs if abs(x) <= 0.01)
    print(f"  Projection better: {n_better}/{len(paired)}  Direct better: {n_worse}/{len(paired)}  Tie: {n_tie}")

    # bootstrap CI on diff
    rng = np.random.default_rng(42)
    boot = np.array([np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(5000)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"  95% bootstrap CI on (D - P): [{lo:.4f}, {hi:.4f}]")
    print(f"  Hypothesis H2.1 (CI excludes 0, projection better): {'PASS' if lo > 0 else 'FAIL or no significant difference'}")

    # Wilcoxon
    try:
        from scipy.stats import wilcoxon
        if len(diffs) > 0:
            stat, p = wilcoxon(diffs, alternative="greater")
            print(f"  Wilcoxon (D > P): stat={stat:.2f}, p={p:.4f}")
    except ImportError:
        pass

    # ---- breakdown by class ----
    print()
    print("--- Settlement loss by coverage class ---")
    by_cls_cond = defaultdict(lambda: defaultdict(list))
    for eid, rec in per_ex.items():
        cls = rec["coverage_class"]
        for cond in CONDITIONS:
            if cond in rec["by_condition"]:
                by_cls_cond[cls][cond].append(rec["by_condition"][cond]["L_uniform"])
    print(f"  {'class':<12} {'cond':<22} {'n':>3} {'mean L':>9} {'median':>9}")
    for cls in sorted(by_cls_cond.keys()):
        for cond in CONDITIONS:
            v = by_cls_cond[cls][cond]
            if v:
                print(f"  {cls:<12} {cond:<22} {len(v):>3} {np.mean(v):>9.4f} {np.median(v):>9.4f}")

    # ---- RX.3 (scope) and RX.2 (overclaim) per condition ----
    print()
    print("--- RX.3 (scope adherence) and RX.2 (overclaim avoidance), v_ij higher = better ---")
    for cond in CONDITIONS:
        rx3 = [rec["by_condition"][cond]["RX_3_score_v"] for rec in per_ex.values()
               if cond in rec["by_condition"] and not np.isnan(rec["by_condition"][cond]["RX_3_score_v"])]
        rx2 = [rec["by_condition"][cond]["RX_2_score_v"] for rec in per_ex.values()
               if cond in rec["by_condition"] and not np.isnan(rec["by_condition"][cond]["RX_2_score_v"])]
        print(f"  {cond:20} RX.3 mean={np.mean(rx3):.3f}  RX.2 mean={np.mean(rx2):.3f}  n={len(rx3)}")

    # ---- per-dim L by condition (top R1 dims) ----
    print()
    print("--- Mean v_ij per active R1 dim (higher = better quality) ---")
    print(f"  {'dim':<6} {'direct':>10} {'projection':>10} {'diff':>10}")
    per_dim_by_cond = defaultdict(lambda: defaultdict(list))
    for eid, rec in per_ex.items():
        for cond in CONDITIONS:
            bc = rec["by_condition"].get(cond)
            if not bc: continue
            for d, v in bc["v_ij"].items():
                per_dim_by_cond[d][cond].append(v)
    for d in DIMS_R1:
        di = per_dim_by_cond[d]["direct"]
        pj = per_dim_by_cond[d]["projection_driven"]
        if not (di and pj): continue
        m_d = np.mean(di); m_p = np.mean(pj)
        print(f"  {d:<6} {m_d:>10.3f} {m_p:>10.3f} {m_p - m_d:>+10.3f}")

    # ---- save ----
    agg = {
        "n_examples": len(per_ex),
        "L_direct_mean": float(np.mean(L_by_cond["direct"])) if L_by_cond["direct"] else None,
        "L_projection_mean": float(np.mean(L_by_cond["projection_driven"])) if L_by_cond["projection_driven"] else None,
        "paired_n": len(paired),
        "paired_diff_mean": float(np.mean(diffs)) if len(diffs) else None,
        "paired_diff_ci_95": [float(lo), float(hi)] if len(diffs) else None,
        "n_projection_better": int(n_better),
        "n_direct_better": int(n_worse),
        "n_tie": int(n_tie),
    }
    (STATS_DIR / "exp2_aggregate.json").write_text(json.dumps(agg, indent=2))
    print()
    print(f"Per-example: {STATS_DIR}/exp2_per_example.json")
    print(f"Aggregate:   {STATS_DIR}/exp2_aggregate.json")


if __name__ == "__main__":
    main()
