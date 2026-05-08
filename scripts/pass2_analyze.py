#!/usr/bin/env python3
"""
Analyze pass-2 annotation results — v1.3 (panel-aware).

Loads:
  - examples/*.yaml                           (author r*_author + metadata)
  - annotations/{eid}__{annotator_id}.json    (3 mid-tier Ollama annotators per spec_models_panel.json)

Computes:
  - r*_median per (example, dim) across (author + 3 LLM annotators)
  - Krippendorff's alpha per dim (interval-level)
  - Pairwise agreement among annotators
  - Author vs LLM agreement

Outputs:
  - stats/r_star_median.json
  - stats/alpha_per_dim.json
  - stats/agreement_pairs.json
  - prints headline tables
"""

import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import median

import numpy as np
import yaml
import krippendorff

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _models

BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXAMPLES_DIR = BASE / "examples"
ANNOT_DIR = BASE / "annotations"
STATS_DIR = BASE / "stats"
STATS_DIR.mkdir(exist_ok=True)

DIMS_R1 = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]
DIMS_RX = ["RX.1", "RX.2", "RX.3", "RX.4", "RX.5"]
DIMS = DIMS_R1 + DIMS_RX

EXPECTED_AUTHOR_VS_LLM_AGREEMENT = 0.5  # G-D-09 threshold for Spearman (we use alpha)


def _safe(mid: str) -> str:
    """Annotator id used in annotation filenames (matches pass2_annotate._safe)."""
    return mid.replace(".", "_").replace("-", "_").replace("/", "_")


# v1.3 annotators from spec_models_panel.json role=pass2_annotator
ANNOTATOR_IDS = [_safe(m["id"]) for m in _models.models_by_role("pass2_annotator")]
print(f"pass2 annotators (v1.3): {ANNOTATOR_IDS}", file=sys.stderr)

# ---- load ----
examples = sorted(EXAMPLES_DIR.glob("ad_r1_*.yaml"))
data = {}
for p in examples:
    with open(p) as f:
        ex = yaml.safe_load(f)
    eid = ex["delegation_id"]
    record = {
        "coverage_class": ex["coverage_class"],
        "load_bearing": list(ex["engineered_flaws"].keys() - {"notes"}),
        "knowledge_gating": ex["knowledge_gating"],
        "delegation_dim_leakage": ex["delegation_dim_leakage"],
        "source": ex["artifact"]["source"],
        "author_weights": ex["hidden_intent"]["weights"],
    }
    # load llm annotations (panel-driven; v1.3)
    for ann_id in ANNOTATOR_IDS:
        ap = ANNOT_DIR / f"{eid}__{ann_id}.json"
        if ap.exists():
            ad = json.loads(ap.read_text())
            if ad.get("parsed"):
                record[f"{ann_id}_weights"] = ad["parsed"]["weights"]
            else:
                # try re-parse from raw for failed validations
                import re
                m = re.search(r"\{.*\}", ad.get("raw") or "", re.DOTALL)
                if m:
                    try:
                        p2 = json.loads(m.group(0))
                        if "weights" in p2:
                            record[f"{ann_id}_weights"] = p2["weights"]
                    except Exception:
                        pass
    data[eid] = record

# ---- compute r* median ----
r_star = {}
for eid, rec in data.items():
    weights_per_dim = {}
    for dim in DIMS:
        vals = [rec["author_weights"].get(dim, 0.0)]
        for ann in ANNOTATOR_IDS:
            w = rec.get(f"{ann}_weights")
            if w and dim in w:
                vals.append(w[dim])
        weights_per_dim[dim] = round(median(vals), 3)
    r_star[eid] = weights_per_dim

(STATS_DIR / "r_star_median.json").write_text(json.dumps(r_star, indent=2))

# ---- Krippendorff alpha per dim (author + N LLM annotators) ----
RATERS = ["author"] + ANNOTATOR_IDS

alpha_per_dim = {}
for dim in DIMS:
    matrix = []  # rows = raters, cols = items
    for ann in RATERS:
        row = []
        for eid in sorted(data.keys()):
            rec = data[eid]
            if ann == "author":
                row.append(rec["author_weights"].get(dim, np.nan))
            else:
                w = rec.get(f"{ann}_weights")
                row.append(w.get(dim, np.nan) if w else np.nan)
        matrix.append(row)
    arr = np.array(matrix, dtype=float)
    try:
        a = krippendorff.alpha(reliability_data=arr, level_of_measurement="interval")
    except Exception:
        a = float("nan")
    alpha_per_dim[dim] = round(float(a), 3)

(STATS_DIR / "alpha_per_dim.json").write_text(json.dumps(alpha_per_dim, indent=2))

# ---- pairwise agreement: every annotator-pair (LLM-LLM + author-LLM) ----
agreement = {}
all_pairs = list(combinations(RATERS, 2))
for pair in all_pairs:
    name = f"{pair[0]}_vs_{pair[1]}"
    per_dim = {}
    for dim in DIMS:
        matrix = []
        for ann in pair:
            row = []
            for eid in sorted(data.keys()):
                rec = data[eid]
                if ann == "author":
                    row.append(rec["author_weights"].get(dim, np.nan))
                else:
                    w = rec.get(f"{ann}_weights")
                    row.append(w.get(dim, np.nan) if w else np.nan)
            matrix.append(row)
        arr = np.array(matrix, dtype=float)
        try:
            a = krippendorff.alpha(reliability_data=arr, level_of_measurement="interval")
        except Exception:
            a = float("nan")
        per_dim[dim] = round(float(a), 3)
    agreement[name] = per_dim

(STATS_DIR / "agreement_pairs.json").write_text(json.dumps(agreement, indent=2))

# ---- coverage summary ----
def class_dist():
    out = defaultdict(int)
    for rec in data.values():
        out[rec["coverage_class"]] += 1
    return dict(out)

def per_dim_load_bearing(threshold=0.7):
    """For each dim, count examples where median r*>=0.7."""
    out = {}
    for dim in DIMS:
        cnt = sum(1 for v in r_star.values() if v[dim] >= threshold)
        out[dim] = cnt
    return out

cov = {
    "n_examples": len(data),
    "class_distribution": class_dist(),
    "per_dim_load_bearing_at_0.7": per_dim_load_bearing(0.7),
    "per_dim_active_at_0.3": {dim: sum(1 for v in r_star.values() if v[dim] > 0.3) for dim in DIMS},
}
(STATS_DIR / "coverage_summary.json").write_text(json.dumps(cov, indent=2))

# ---- high-disagreement examples ----
disagreement = []
for eid in sorted(data.keys()):
    rec = data[eid]
    # Need at least 2 LLM annotators with parsed weights to compute spread
    avail = [aid for aid in ANNOTATOR_IDS if rec.get(f"{aid}_weights")]
    if len(avail) < 2:
        continue
    spread = 0.0
    for dim in DIMS_R1:  # focus on R1 — RX is always 1.0 by construction
        vals = [rec["author_weights"][dim]] + [rec[f"{aid}_weights"][dim] for aid in avail]
        spread += max(vals) - min(vals)
    disagreement.append((eid, round(spread, 3), rec["coverage_class"], rec["load_bearing"]))
disagreement.sort(key=lambda x: -x[1])

# ---- print headline ----
print("=" * 70)
print("PASS-2 ANNOTATION ANALYSIS")
print("=" * 70)
print()
print(f"Examples: {len(data)}")
print(f"Class distribution: {cov['class_distribution']}")
print()

print(f"--- Krippendorff's α per dim ({len(RATERS)} raters: {', '.join(RATERS)}) ---")
print(f"  G-D-07 acceptance gate: α >= 0.4 on at least 10 of 12 dims")
n_ok = sum(1 for a in alpha_per_dim.values() if a >= 0.4)
for dim in DIMS:
    a = alpha_per_dim[dim]
    flag = "✓" if a >= 0.4 else "✗"
    print(f"  {flag} {dim}: α = {a:.3f}")
print(f"  → dims with α >= 0.4: {n_ok}/12  {'PASS' if n_ok >= 10 else 'FAIL'}")
print()

print("--- pairwise alpha (informational) ---")
for pair_name, per_dim in agreement.items():
    avg = round(np.mean(list(per_dim.values())), 3)
    print(f"  {pair_name}: mean α = {avg:.3f}")
print()

print("--- per-dim load-bearing count (median r* >= 0.7) ---")
for dim in DIMS:
    n = cov["per_dim_load_bearing_at_0.7"][dim]
    print(f"  {dim}: {n}")
print()

print("--- top-10 highest disagreement examples (R1 dims only) ---")
for eid, spread, cls, lb in disagreement[:10]:
    print(f"  {eid}  spread={spread:.2f}  class={cls}  lb={lb}")
print()

# R1.4 vs R1.7 boundary check (panel-driven; v1.3)
print("--- R1.4 ↔ R1.7 boundary fragility check (deferred concern) ---")
# Swap = author has high one dim, ANY LLM annotator puts it on the other dim.
errs_47 = []
for eid in sorted(data.keys()):
    rec = data[eid]
    avail = [aid for aid in ANNOTATOR_IDS if rec.get(f"{aid}_weights")]
    if not avail:
        continue
    a47 = (rec["author_weights"]["R1.4"], rec["author_weights"]["R1.7"])
    swapped_by = []
    llm_47s = []
    for aid in avail:
        w = rec[f"{aid}_weights"]
        l47 = (w["R1.4"], w["R1.7"])
        llm_47s.append((aid, l47))
        if (a47[0] >= 0.5 and l47[1] >= 0.5 and a47[1] < 0.3 and l47[0] < 0.3) or \
           (a47[1] >= 0.5 and l47[0] >= 0.5 and a47[0] < 0.3 and l47[1] < 0.3):
            swapped_by.append(aid)
    errs_47.append((eid, bool(swapped_by), a47, llm_47s, swapped_by))
n_swap = sum(1 for _, s, *_ in errs_47 if s)
print(f"  R1.4 ↔ R1.7 swap cases (author and ≥1 LLM annotator disagree on which dim is high): {n_swap}/{len(errs_47)}")
if n_swap > 0:
    print("  Detailed swap cases:")
    for eid, s, a, llm_47s, swappers in errs_47:
        if s:
            llm_str = "  ".join(f"{aid}=(R1.4={l47[0]}, R1.7={l47[1]})" for aid, l47 in llm_47s)
            print(f"    {eid}  author=(R1.4={a[0]}, R1.7={a[1]})  {llm_str}  swapped_by={swappers}")

print()
print(f"All stats written to {STATS_DIR}/")
