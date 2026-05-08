#!/usr/bin/env python3
"""v1.3 mechanism analysis — M1-M4 indicators + per-tier breakdown + per-dim drill-down.

Reads:
  - data/pilot_v1.1/stats/exp2_per_row.parquet  (1800 rows: example × condition × dim)
  - data/pilot_v1.1/judge/{eid}__{cond}__opus__{judge}.json  (per-judge raw)
  - data/pilot_v1.1/execution/{eid}__{cond}__opus.json  (executor raw, for M1 output-type)

Writes:
  - data/pilot_v1.1/stats/exp2_v1_3_mechanism.json (M1-M4 + tier breakdown)
  - data/pilot_v1.1/stats/exp2_v1_3_per_tier.parquet (v_ij per (example, condition, dim, tier))
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/treu46/paper/6. agent")
JUDGE_DIR = ROOT / "data/pilot_v1.1/judge"
EXEC_DIR = ROOT / "data/pilot_v1.1/execution"
STATS = ROOT / "data/pilot_v1.1/stats"

import sys
sys.path.insert(0, str(ROOT / "scripts"))
import _models

JUDGES = [m["id"] for m in _models.models_by_role("judge")]
# Build TIER_OF from the panel JSON directly
import json as _json
_panel = _json.load(open(ROOT / "data/pilot_v1.1/spec_models_panel.json"))
TIER_OF = {m["id"]: m.get("tier", "?") for m in _panel.get("models", [])}

CONDITIONS = ["direct_naive", "direct_with_claim", "projection_driven"]
R1_DIMS = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]
RX_FOR_M4 = ["RX.1", "RX.3", "RX.4", "RX.5"]

# Continuous-cutoff parameters for M3 (per formalization §2.5.3 default)
C_Q = 0.3
C_V = 0.5


def load_per_judge():
    """Load per (example, condition, judge) judge JSONs into a flat DataFrame."""
    rows = []
    for f in sorted(JUDGE_DIR.glob("*.json")):
        # filename: ad_r1_NNN__condition__opus__judgeid.json
        m = re.match(r"(ad_r1_\d+)__([^_]+(?:_[^_]+)*?)__opus__(.+)\.json$", f.name)
        if not m:
            continue
        eid, cond, judge = m.groups()
        if cond not in CONDITIONS:
            continue
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        parsed = d.get("parsed") or {}
        scores = parsed.get("scores") or {}
        for dim, s in scores.items():
            if not isinstance(s, (int, float)):
                continue
            v = (s - 1) / 4.0  # anchor 1-5 → v 0-1
            rows.append({
                "example_id": eid,
                "condition": cond,
                "judge_id": judge,
                "tier": TIER_OF.get(judge, "?"),
                "dim": dim,
                "s_ij": s,
                "v_ij": v,
            })
    return pd.DataFrame(rows)


def load_executor_q():
    """Load q_ij from executor self-claim line. Returns dict[(eid, cond, dim)] = q."""
    out = {}
    for f in sorted(EXEC_DIR.glob("*.json")):
        m = re.match(r"(ad_r1_\d+)__([^_]+(?:_[^_]+)*?)__opus\.json$", f.name)
        if not m:
            continue
        eid, cond = m.groups()
        if cond not in CONDITIONS:
            continue
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        # The self-claim line is the first line of output, e.g., {"covered_dims": {"R1.1": 0.8, ...}}
        text = d.get("output_text", "") or ""
        first_line = text.lstrip().split("\n", 1)[0].strip()
        if first_line.startswith('{"covered_dims"'):
            try:
                claim = json.loads(first_line).get("covered_dims", {})
                for dim, q in claim.items():
                    if isinstance(q, (int, float)):
                        out[(eid, cond, dim)] = float(q)
            except Exception:
                pass
    return out


def load_r_star():
    """Median r_star per dim per example. Returns dict[(eid, dim)] = r_star_j."""
    rs = json.load(open(STATS / "r_star_median.json"))
    out = {}
    for eid, dim_map in rs.items():
        for dim, r in dim_map.items():
            out[(eid, dim)] = float(r)
    return out


def output_type(text: str) -> str:
    """Heuristic categorization of executor output: 'revised_draft' vs 'analytical_list' vs 'mixed'."""
    if not text:
        return "empty"
    body = text.lstrip()
    # Strip self-claim first line if present
    if body.startswith('{"covered_dims"'):
        _, _, body = body.partition("\n")
    body = body.lstrip()
    # Heuristics: count bullet markers vs paragraph runs
    bullets = len(re.findall(r"(?m)^\s*(?:[-*•]|\d+\.)\s", body))
    paragraphs = len([p for p in re.split(r"\n\n+", body) if len(p.split()) > 30])
    if bullets >= 5 and paragraphs <= 2:
        return "analytical_list"
    if bullets <= 2 and paragraphs >= 3:
        return "revised_draft"
    return "mixed"


def main():
    df_judges = load_per_judge()
    print(f"loaded {len(df_judges)} per-judge rows")

    # === Per-tier v_ij breakdown ===
    tier_table = (df_judges.groupby(["condition", "tier", "dim"])["v_ij"]
                  .mean().unstack("condition"))
    print("\n=== Per-tier mean v_ij per (R1) dim per condition ===")
    present_r1 = [d for d in R1_DIMS if d in tier_table.index.get_level_values("dim").unique()]
    if present_r1:
        sub = tier_table[tier_table.index.get_level_values("dim").isin(present_r1)]
        print(sub.round(3))
    tier_table.reset_index().to_parquet(STATS / "exp2_v1_3_per_tier.parquet")

    # === L_settlement^R1 (weighted by r*) per (example, condition) — using mean across judges ===
    df_per_row = pd.read_parquet(STATS / "exp2_per_row.parquet")
    def L_r1(g):
        m = g[g["is_R1"] & g["is_active"] & g["v_ij"].notna()]
        if len(m) == 0:
            return np.nan
        return ((1 - m["v_ij"]) * m["r_star_j"]).sum() / m["r_star_j"].sum()
    L_settle = df_per_row.groupby(["example_id", "condition"]).apply(L_r1).rename("L_r1").reset_index()
    L_pivot = L_settle.pivot(index="example_id", columns="condition", values="L_r1")
    print("\n=== L_settlement^R1 per condition ===")
    for c in CONDITIONS:
        print(f"  {c:20s} mean={L_pivot[c].mean():.4f}  median={L_pivot[c].median():.4f}")

    # === M2: active-set breadth excess per (example, condition) ===
    # |J*(d)| = number of R1 dims declared active for that condition (from agent perspective).
    # For projection_driven, use the agent's own active_set; for direct_*, |R1∩active| from data.
    # loadbearing = {j ∈ R1 : r*_j > 0.7}
    r_star = load_r_star()
    M2_rows = []
    for (eid, cond), g in df_per_row.groupby(["example_id", "condition"]):
        active_r1 = g[g["is_R1"] & g["is_active"]]["dim"].tolist()
        loadbearing = [d for d in R1_DIMS if r_star.get((eid, d), 0) > 0.7]
        M2_rows.append({"example_id": eid, "condition": cond,
                        "active_r1_count": len(active_r1),
                        "loadbearing_count": len(loadbearing),
                        "M2": len(active_r1) - len(loadbearing)})
    df_M2 = pd.DataFrame(M2_rows)
    print("\n=== M2 (active-set breadth excess) per condition ===")
    for c in CONDITIONS:
        m2 = df_M2[df_M2["condition"] == c]["M2"]
        print(f"  {c:20s} median={m2.median():.1f}  mean={m2.mean():.2f}  IQR=[{m2.quantile(0.25):.1f}, {m2.quantile(0.75):.1f}]")

    # === M3: self-claim symmetric difference (q vs v binarization) ===
    q_map = load_executor_q()
    print(f"\nloaded {len(q_map)} executor q_ij values")
    M3_rows = []
    for (eid, cond), g in df_per_row.groupby(["example_id", "condition"]):
        if cond == "direct_naive":
            continue
        active_R1 = g[g["is_R1"] & g["is_active"]]["dim"].tolist()
        if not active_R1:
            continue
        sym_diff = 0
        for d in active_R1:
            q = q_map.get((eid, cond, d))
            v_row = g[g["dim"] == d]["v_ij"]
            v = v_row.iloc[0] if len(v_row) > 0 else None
            if q is None or v is None or pd.isna(v):
                continue
            in_q = q > C_Q
            in_v = v > C_V
            if in_q != in_v:
                sym_diff += 1
        M3_rows.append({"example_id": eid, "condition": cond,
                        "M3": sym_diff / len(active_R1)})
    df_M3 = pd.DataFrame(M3_rows)
    print("\n=== M3 (self-claim symmetric diff, c_q=0.3 c_v=0.5) per condition ===")
    for c in CONDITIONS:
        if c == "direct_naive":
            continue
        m3 = df_M3[df_M3["condition"] == c]["M3"]
        print(f"  {c:20s} median={m3.median():.3f}  mean={m3.mean():.3f}")

    # === M4: RX boost magnitude (projection - direct_naive) ===
    rx_v = (df_per_row[df_per_row["dim"].isin(RX_FOR_M4) & df_per_row["v_ij"].notna()]
            .groupby(["example_id", "condition", "dim"])["v_ij"].mean().unstack("condition"))
    M4_rows = []
    for eid in rx_v.index.get_level_values(0).unique():
        sub = rx_v.loc[eid]
        diffs = (sub["projection_driven"] - sub["direct_naive"]).dropna()
        if len(diffs) > 0:
            M4_rows.append({"example_id": eid, "M4": diffs.mean()})
    df_M4 = pd.DataFrame(M4_rows)
    print(f"\n=== M4 (RX boost: projection_driven - direct_naive over RX.{{1,3,4,5}}) ===")
    print(f"  median={df_M4['M4'].median():.4f}  mean={df_M4['M4'].mean():.4f}  std={df_M4['M4'].std():.4f}")
    print(f"  positive (RX boosted): {(df_M4['M4'] > 0).sum()}/{len(df_M4)}")

    # === M1: output-type mismatch direct_naive vs projection_driven ===
    M1_rows = []
    for f in sorted(EXEC_DIR.glob("*__direct_naive__opus.json")):
        eid = f.name.split("__")[0]
        try:
            d_dn = json.loads(f.read_text())
            d_pd = json.loads((EXEC_DIR / f"{eid}__projection_driven__opus.json").read_text())
            t_dn = output_type(d_dn.get("output_text", ""))
            t_pd = output_type(d_pd.get("output_text", ""))
            M1_rows.append({"example_id": eid, "type_direct": t_dn, "type_projection": t_pd,
                            "mismatch": t_dn != t_pd})
        except Exception:
            continue
    df_M1 = pd.DataFrame(M1_rows)
    print(f"\n=== M1 (output-type mismatch direct_naive vs projection_driven) ===")
    print(f"  mismatch rate: {df_M1['mismatch'].sum()}/{len(df_M1)} = {df_M1['mismatch'].mean():.2%}")
    type_pairs = df_M1.groupby(["type_direct", "type_projection"]).size().reset_index(name="n")
    print("  type-pair distribution:")
    for _, r in type_pairs.iterrows():
        print(f"    {r['type_direct']:18s} -> {r['type_projection']:18s} : {r['n']}")

    # === Save ===
    out = {
        "n_examples": 50,
        "judges": JUDGES,
        "M1": {
            "mismatch_rate": float(df_M1["mismatch"].mean()),
            "n_mismatch": int(df_M1["mismatch"].sum()),
            "type_pairs": {f"{r['type_direct']}->{r['type_projection']}": int(r["n"])
                           for _, r in type_pairs.iterrows()},
        },
        "M2": {
            c: {
                "median": float(df_M2[df_M2["condition"] == c]["M2"].median()),
                "mean": float(df_M2[df_M2["condition"] == c]["M2"].mean()),
                "iqr": [float(df_M2[df_M2["condition"] == c]["M2"].quantile(0.25)),
                        float(df_M2[df_M2["condition"] == c]["M2"].quantile(0.75))],
            } for c in CONDITIONS
        },
        "M3": {
            c: {
                "median": float(df_M3[df_M3["condition"] == c]["M3"].median()),
                "mean": float(df_M3[df_M3["condition"] == c]["M3"].mean()),
            } for c in CONDITIONS if c != "direct_naive"
        },
        "M4": {
            "median": float(df_M4["M4"].median()),
            "mean": float(df_M4["M4"].mean()),
            "std": float(df_M4["M4"].std()),
            "positive_count": int((df_M4["M4"] > 0).sum()),
            "n": int(len(df_M4)),
        },
        "L_settlement_R1": {
            c: {
                "mean": float(L_pivot[c].mean()),
                "median": float(L_pivot[c].median()),
                "std": float(L_pivot[c].std()),
            } for c in CONDITIONS
        },
        "paired_diffs_L_settlement_R1": {
            "direct_naive_minus_projection_driven": {
                "mean": float((L_pivot["direct_naive"] - L_pivot["projection_driven"]).mean()),
                "median": float((L_pivot["direct_naive"] - L_pivot["projection_driven"]).median()),
            },
            "direct_naive_minus_direct_with_claim": {
                "mean": float((L_pivot["direct_naive"] - L_pivot["direct_with_claim"]).mean()),
                "median": float((L_pivot["direct_naive"] - L_pivot["direct_with_claim"]).median()),
            },
        },
    }
    out_path = STATS / "exp2_v1_3_mechanism.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
