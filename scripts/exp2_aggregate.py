#!/usr/bin/env python3
"""
Aggregate Exp 2 raw outputs into the continuous-metric tables specified in
`experiment_design_v1.3.md` §2.7.1.

Reads:
  - data/pilot_v1.1/execution/{eid}__{condition}__opus.json   (executor outputs + parsed q_ij)
  - data/pilot_v1.1/judge/{eid}__{condition}__opus__{judge}.json
  - data/pilot_v1.1/projection/{eid}__{model_id}__t0.0_run0.json   (for L_projection)
  - data/pilot_v1.1/stats/r_star_median.json                       (for r*_j)

Writes:
  - data/pilot_v1.1/stats/exp2_per_row.parquet     (one row per example × condition × dim)
  - data/pilot_v1.1/stats/exp2_per_example.parquet (per-example aggregates: L_projection, L_calibration, L_overclaim, L_settlement^*)
  - data/pilot_v1.1/stats/exp2_aggregate.json      (per-condition summary + bootstrap CIs)

Discipline (per formalization_v1.2 §9.3 + experiment_design_v1.3 §4):
  - Raw continuous metric logging is primary.
  - Binary classifications are post-hoc — see scripts/diagnostic_gates.py
    (forthcoming, separate file).
  - No hard-coded pass/fail; all metrics computed regardless of magnitude.

Usage:
    python exp2_aggregate.py                  # aggregate all available data
    python exp2_aggregate.py --bootstrap 10000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

import _models

BASE = Path("/home/treu46/paper/6. agent/data/pilot_v1.1")
EXEC_DIR = BASE / "execution"
JUDGE_DIR = BASE / "judge"
PROJ_DIR = BASE / "projection"
STATS_DIR = BASE / "stats"
STATS_DIR.mkdir(exist_ok=True)

R1_DIMS = ["R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7"]
RX_SCORED = ["RX.1", "RX.3", "RX.4", "RX.5"]   # judge anchor-scores these
RX_UNSCORED = ["RX.2"]                          # operationalized via L_overclaim, not anchor
J_V1_1 = R1_DIMS + RX_SCORED + RX_UNSCORED      # full 12-dim taxonomy (per §2.7.1 schema)
CONDITIONS = ["direct_naive", "direct_with_claim", "projection_driven"]


# ------------------ JUDGE PANEL MEDIAN ------------------

def judge_median_score(eid: str, condition: str, dim: str) -> float | None:
    """Median over 12-judge panel (or whatever subset has parsed scores).

    Returns None if all judges blocked or no judges available.
    """
    pattern = f"{eid}__{condition}__opus__*.json"
    scores = []
    for p in JUDGE_DIR.glob(pattern):
        d = json.loads(p.read_text())
        if not d.get("validation", {}).get("passed"):
            continue
        s = (d.get("parsed") or {}).get("scores", {}).get(dim)
        if isinstance(s, (int, float)) and 1 <= s <= 5:
            scores.append(int(s))
    if not scores:
        return None
    return float(np.median(scores))


# ------------------ SELF-CLAIM PARSING ------------------

_SELF_CLAIM_RE = re.compile(r'^\s*(\{\s*"covered_dims"\s*:.*?\})\s*$', re.MULTILINE)


def parse_q_ij(output_text: str) -> dict[str, float] | None:
    """Extract `covered_dims` JSON from the first line of agent output.

    Returns None if condition was direct_naive (no JSON) OR JSON is malformed.
    """
    if not output_text:
        return None
    first_line = output_text.lstrip().split("\n", 1)[0]
    try:
        obj = json.loads(first_line)
    except json.JSONDecodeError:
        m = _SELF_CLAIM_RE.search(output_text[:1000])
        if not m:
            return None
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            return None
    cov = obj.get("covered_dims") if isinstance(obj, dict) else None
    if not isinstance(cov, dict):
        return None
    out = {}
    for k, v in cov.items():
        if not isinstance(v, (int, float)):
            continue
        if 0.0 <= v <= 1.0:
            out[k] = float(v)
    return out


# ------------------ R* / ACTIVE SET ------------------

def load_r_star_median() -> dict[str, dict[str, float]]:
    p = STATS_DIR / "r_star_median.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def active_set_for(eid: str, r_star: dict[str, dict[str, float]]) -> list[str]:
    weights = r_star.get(eid, {})
    return [d for d in R1_DIMS if weights.get(d, 0) > 0.3] + RX_SCORED


# ------------------ PROJECTION (for L_projection) ------------------

def load_projection_for_eid(eid: str) -> tuple[str, dict] | None:
    """Return (projection_family_used, parsed) for a (eid, family) pair from Exp 1.

    For L_projection we average / report per family — but per
    `_projection_choice.json` v1.3, the projection_driven executor uses gpt-5.
    Here we load all available cross-family projections at T=0 run0.
    """
    out = {}
    for family in ["gpt-5", "gemini-2.5-pro", "grok-4"]:
        p = PROJ_DIR / f"{eid}__{family}__t0.0_run0.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        if d.get("validation", {}).get("passed"):
            out[family] = d["parsed"]
    return out


def cosine_distance(r1: dict[str, float], r2: dict[str, float], dims: list[str]) -> float:
    a = np.array([float(r1.get(d, 0)) for d in dims])
    b = np.array([float(r2.get(d, 0)) for d in dims])
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    return float(1.0 - np.dot(a, b) / (na * nb))


# ------------------ AGGREGATION ------------------

def build_per_row(r_star_median: dict) -> pd.DataFrame:
    """Per-row table covers the full 12-dim taxonomy (codex review #1).

    RX.2 has anchor-score=NaN by design (operationalized via L_overclaim instead),
    but its row appears so the schema matches `experiment_design_v1.3` §2.7.1
    "one row per example × condition × dim where dim ∈ J_v1.1".
    """
    rows = []
    for exec_p in sorted(EXEC_DIR.glob("ad_r1_*__opus.json")):
        d = json.loads(exec_p.read_text())
        eid = d["example_id"]
        cond = d["condition"]
        q = parse_q_ij(d.get("output_text", "")) if cond != "direct_naive" else None
        weights = r_star_median.get(eid, {})
        active = active_set_for(eid, r_star_median)
        for dim in J_V1_1:
            # RX.2 is unscored — judge_median_score returns None by construction
            anchor_scored = dim not in RX_UNSCORED
            s_ij = judge_median_score(eid, cond, dim) if (anchor_scored and dim in active) else None
            v_ij = (s_ij - 1) / 4 if s_ij is not None else float("nan")
            q_ij = q.get(dim) if (q and dim in q) else float("nan")
            rows.append({
                "example_id": eid,
                "condition": cond,
                "dim": dim,
                "r_star_j": float(weights.get(dim, 0.0)),
                "s_ij": s_ij if s_ij is not None else float("nan"),
                "v_ij": v_ij,
                "q_ij": q_ij,
                "is_R1": dim in R1_DIMS,
                "is_RX": dim in RX_SCORED + RX_UNSCORED,
                "is_anchor_scored": anchor_scored,
                "is_active": dim in active,
            })
    return pd.DataFrame(rows)


def per_example_aggregates(per_row: pd.DataFrame, r_star_median: dict) -> pd.DataFrame:
    out = []
    grp = per_row.groupby(["example_id", "condition"], dropna=False)
    for (eid, cond), df in grp:
        active_R1 = df[df.is_R1 & df.is_active & ~df.s_ij.isna()]
        # L_calibration / L_overclaim only on rows with both q and v
        both = active_R1.dropna(subset=["q_ij", "v_ij"])
        L_cal = float((both.q_ij - both.v_ij).abs().mean()) if len(both) else float("nan")
        L_oc = float(((both.q_ij - both.v_ij).clip(lower=0)).mean()) if len(both) else float("nan")
        # L_settlement^R1 weighted
        if len(active_R1) and active_R1.r_star_j.sum() > 0:
            num = (active_R1.r_star_j * (1 - active_R1.v_ij)).sum()
            den = active_R1.r_star_j.sum()
            L_set_R1_w = float(num / den)
        else:
            L_set_R1_w = float("nan")
        # L_settlement^uniform-R1
        L_set_R1_u = float((1 - active_R1.v_ij).mean()) if len(active_R1) else float("nan")
        # L_settlement^RX over RX.1/RX.3/RX.4/RX.5 (always-active)
        rx_rows = df[df.is_RX & ~df.s_ij.isna()]
        L_set_RX = float((1 - rx_rows.v_ij).mean()) if len(rx_rows) else float("nan")
        out.append({
            "example_id": eid,
            "condition": cond,
            "L_calibration": L_cal,
            "L_overclaim": L_oc,
            "L_settlement_R1_weighted": L_set_R1_w,
            "L_settlement_R1_uniform": L_set_R1_u,
            "L_settlement_RX": L_set_RX,
        })
    return pd.DataFrame(out)


def add_l_projection(per_example: pd.DataFrame, r_star_median: dict) -> pd.DataFrame:
    """L_projection is per (example, projection-family); merge as separate columns."""
    rows = []
    for eid in per_example.example_id.unique():
        weights = r_star_median.get(eid, {})
        if not weights:
            continue
        proj_by_family = load_projection_for_eid(eid) or {}
        rec = {"example_id": eid}
        for family, parsed in proj_by_family.items():
            r = parsed.get("weights", {}) if isinstance(parsed, dict) else {}
            d = cosine_distance(r, weights, R1_DIMS + RX_SCORED + ["RX.2"])
            rec[f"L_projection__{family}"] = d
        rows.append(rec)
    proj_df = pd.DataFrame(rows)
    if proj_df.empty:
        return per_example
    return per_example.merge(proj_df, on="example_id", how="left")


def bootstrap_ci(values: np.ndarray, n: int = 10000, alpha: float = 0.05,
                 seed: int = 42) -> tuple[float, float, float]:
    """Returns (mean, lower, upper) at (1-alpha) CI over `n` example-level resamples."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        sample = rng.choice(values, size=len(values), replace=True)
        means.append(sample.mean())
    means = np.asarray(means)
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return float(values.mean()), lo, hi


def self_claim_parse_failure_rate(per_row: pd.DataFrame) -> dict:
    """Codex review #2: report q_ij parse failure rate per condition as quality metric.

    For conditions with self-claim line (direct_with_claim, projection_driven), q_ij
    should be parseable from the agent's first-line JSON. NaN q_ij on R1∩active rows
    indicates parse failure.
    """
    out = {}
    for cond in CONDITIONS:
        if cond == "direct_naive":
            out[cond] = {"applicable": False}
            continue
        df = per_row[(per_row.condition == cond) & per_row.is_R1 & per_row.is_active]
        per_example_failed = df.groupby("example_id").apply(
            lambda g: g.q_ij.isna().all(), include_groups=False
        )
        n_examples = int(len(per_example_failed))
        n_failed = int(per_example_failed.sum())
        out[cond] = {
            "applicable": True,
            "n_examples": n_examples,
            "n_parse_failed": n_failed,
            "parse_failure_rate": (n_failed / n_examples) if n_examples else float("nan"),
        }
    return out


def per_condition_summary(per_example: pd.DataFrame, per_row: pd.DataFrame,
                          n_boot: int, seed: int) -> dict:
    out = {}
    metric_cols = [c for c in per_example.columns if c.startswith("L_")]
    for cond in CONDITIONS:
        cond_df = per_example[per_example.condition == cond]
        out[cond] = {}
        for col in metric_cols:
            mean, lo, hi = bootstrap_ci(cond_df[col].values, n=n_boot, seed=seed)
            out[cond][col] = {"mean": mean, "ci_lo": lo, "ci_hi": hi,
                              "n_examples": int((~cond_df[col].isna()).sum())}
    out["__quality__"] = {
        "self_claim_parse_failure_rate_per_condition":
            self_claim_parse_failure_rate(per_row),
    }
    # Pairwise deltas (paired by example_id)
    deltas = {}
    for c1, c2 in [("direct_naive", "direct_with_claim"),
                   ("direct_naive", "projection_driven"),
                   ("direct_with_claim", "projection_driven")]:
        deltas[f"{c2}_minus_{c1}"] = {}
        for col in metric_cols:
            paired = (per_example[per_example.condition == c2].set_index("example_id")[col]
                      .subtract(per_example[per_example.condition == c1].set_index("example_id")[col],
                                fill_value=float("nan")))
            mean, lo, hi = bootstrap_ci(paired.values, n=n_boot, seed=seed)
            deltas[f"{c2}_minus_{c1}"][col] = {
                "mean": mean, "ci_lo": lo, "ci_hi": hi,
                "n_paired": int((~paired.isna()).sum()),
            }
    out["paired_deltas"] = deltas
    return out


# ------------------ MAIN ------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    r_star = load_r_star_median()
    if not r_star:
        print("WARN: r_star_median.json missing; aggregates that depend on r* will be NaN.")

    print("[1/3] building per-row table...")
    per_row = build_per_row(r_star)
    per_row_path = STATS_DIR / "exp2_per_row.parquet"
    per_row.to_parquet(per_row_path, index=False)
    print(f"      wrote {per_row_path} ({len(per_row)} rows)")

    print("[2/3] computing per-example aggregates...")
    per_example = per_example_aggregates(per_row, r_star)
    per_example = add_l_projection(per_example, r_star)
    per_example_path = STATS_DIR / "exp2_per_example.parquet"
    per_example.to_parquet(per_example_path, index=False)
    print(f"      wrote {per_example_path} ({len(per_example)} rows)")

    print(f"[3/3] bootstrap CIs (n={args.bootstrap}, seed={args.seed})...")
    summary = per_condition_summary(per_example, per_row, args.bootstrap, args.seed)
    summary_path = STATS_DIR / "exp2_aggregate.json"
    summary["meta"] = {
        "panel_version": _models.panel_version(),
        "bootstrap_n": args.bootstrap,
        "bootstrap_seed": args.seed,
        "n_examples_total": int(per_example.example_id.nunique()),
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"      wrote {summary_path}")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
