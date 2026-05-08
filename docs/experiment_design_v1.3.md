# Experiment Design v1.3
## Sync Patch on `experiment_design_v1.2` — 3-Condition Exp 2, 3-Layer Loss, 3-Dim Stage 1 Anchor

> Status: operational sync on v1.2 absorbing the theory restructure from `formalization_v1.2` (iter 2) and `paper_master_v1.3` (iter 2). Translates the v1.3 thesis structure into the actual experimental run table that the harness executes.
> Role: defines what calls happen, in what order, with what panel, recording what fields. Numeric counts and pre-registered settings live here; theoretical justification lives in `formalization_v1.2` and `paper_master_v1.3`.
> Companion files:
> - `experiment_design_v1.0.md` (root)
> - `experiment_design_v1.1.md` (first-cycle scope narrowing)
> - `experiment_design_v1.2.md` (parent — model panel redesign)
> - **`formalization_v1.2.md` (iter 2 — 3-layer loss, P1/P2 decoupling, M1–M4 diagnostics)**
> - **`spec_models_v1.0.md` (iter 2 — 12-judge panel, 3-dim Stage 1 anchor)**
> - **`paper_master_v1.3.md` (iter 2 — claim compression + §VI Limitations + §VII follow-up signpost)**

---

## 0. What changed from v1.2

The 5 claims (C1–C5) in `experiment_design_v1.0` §1 and the dataset (50 examples in `J_v1.1`) are unchanged. Operational changes:

| element | v1.2 | v1.3 |
|---|---|---|
| Exp 2 conditions | 2 (direct, projection_driven) | **3** (direct_naive, direct_with_claim, projection_driven) |
| Executor calls | 100 (50 × 2) | **150** (50 × 3) |
| Judge calls | 1200 (100 × 12) | **1800** (150 × 12) |
| Self-claim line in executor prompt | not present | **present in `direct_with_claim` and `projection_driven`** (per `formalization_v1.2` §5) |
| RX.2 anchor scoring | scored s ∈ {1,3,5} | **dropped** — operationalized via `L_overclaim` (per `formalization_v1.2` §4) |
| Settlement loss reporting | single `L_i` (uniform headline) | **3-layer**: `L_projection`, `L_calibration` (+ `L_overclaim` for RX.2), `L_settlement^R1` (weighted, headline) + `L_settlement^RX` (constraint) |
| Stage 1 human anchor | R1.7-only (1 batch, 18 ratings, ~$100) | **planned: R1.1 + R1.4 + R1.7** (3 batches, 270 ratings, ~$300) — **superseded 2026-05-07** by R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation (~72 ratings actual; see §2.6 + paper §VI #4 + CHANGELOG 2026-05-07) |
| Mechanism reporting | acceptance gates ≥ 3 of M1–M4 | **diagnostic only** — continuous `\widetilde{M_1..4}` distributions + binary post-hoc with sensitivity sweeps (per `formalization_v1.2` §9.3) |
| LLM cost (excl. Stage 1) | ~$16 API + Ollama $0 | **~$21** API + Ollama $0 |
| Pilot total | ~$116 | **planned ~$321; actual ~$148** (post 2026-05-07 Stage 1 closure; see §3 cost table + §2.6) |

**Non-operational dependency changes** (recorded for traceability; do not affect Exp 2 setup or harness wiring):
- `formalization_v1.2` §3 splits the clarification trigger into theoretical (2-clause) and operational (1-clause practical proxy). Affects paper §3 motivation prose, not run config.
- `paper_master_v1.3` §2 demotes C3 (multi-round reputation update mechanism) to simulation-only future-work. Affects paper §V claim table and §VII signpost, not run config.

What does **not** change:
- Dataset (50 examples in `J_v1.1`).
- v1.2 acceptance gates (G-D-01..10 from `spec_dataset_v1.0` + projection JSON validity ≥ 98%, |J*(d)| ∈ [5,9], median R(d) > 1.2, RX populated ≥ 95%, dim-confusion < 0.3).
- Model panel master list (`spec_models_v1.0` §2 — 12 LLMs, Anthropic-excluded).
- Executor identity (claude-opus-4-7 via Claude Code session — single Anthropic touchpoint).
- Tier-stratified α reporting structure (`α_frontier / α_mid / α_light / α_panel / α_with_author`). The original `α_with_human` row is **superseded 2026-05-07** — replaced by per-arm reporting in §2.6.3 (R1.1 inferential α; R1.7 Axis-1 engagement-score table; no R1.4 human evidence).

---

## 1. Why v1.3 exists

`experiment_design_v1.2` was drafted before the theoretical restructure (P1/P2 decoupling, 3-layer loss decomposition, mechanism formalization). v1.2's Exp 2 setup specified 2 conditions and a single `L_i`; the v1.3 theory requires:

1. A `direct_naive` condition (no self-claim line) — to preserve a clean P2 settlement-comparison baseline that is not biased by the priming effect of the self-claim line.
2. A `direct_with_claim` condition (self-claim line) — to enable `L_calibration` measurement in the no-projection setting and provide a within-pair priming ablation against `direct_naive`.
3. A `projection_driven` condition (V2 prompt, R-code echo suppressed, self-claim line) — the treatment condition.
4. Stage 1 human anchor *originally planned* on **3 dimensions** (R1.1, R1.4, R1.7), not just R1.7 — to block the "human anchor reads as fixing weak spot" objection (per `review_feedback_v1_0` #6). **Superseded 2026-05-07**: the planned 3-dim Prolific extension was not delivered as breadth validation; Stage 1 closed at R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation, with the §VI #4 entry repositioned as a methodological boundary-condition finding. The "weak-spot" objection is now answered by *transparency about the boundary*, not by breadth coverage. See §2.6.

v1.3 is the operational translation of those theoretical commitments into the actual run table.

Per `paper_master_v1.3` §0, v1.3 *supersedes* the v1.2 Exp 2 measurement layer rather than strictly extending it (RX.2 anchor scoring is dropped; condition count is 2→3). Backward compatibility is via the dataset (`examples/`, `INDEX.jsonl`, `provenance/` — preserved) not via the measurement outputs (`execution/`, `judge/`, `annotations*/`, `stats/exp*` — re-run from scratch).

---

## 2. Updated setup tables (replaces v1.2 §2.4 and adds Stage 1)

### 2.1 Experiment 1 — Cross-Family Projection Mismatch (unchanged from v1.2 §2.1)

```text
3 frontier families (gpt-5, gemini-2.5-pro, grok-4) — per spec_models_v1.0 §4.2
Per-family model: as listed in spec_models_v1.0 §2 (recorded in output JSON)
1 projection run per (model, example)
Temperature: 0.0
50 R1 examples × 3 families = 150 projection calls
Estimated cost: ~$3 (API)
```

### 2.2 Experiment 1B — Within-Model Stochastic Baseline (unchanged from v1.2 §2.2)

```text
1 fixed frontier model: gpt-5
5 projection runs per example
Temperature: 0.5
50 R1 examples × 1 model × 5 runs = 250 projection calls
Estimated cost: ~$5 (API)
```

### 2.3 Pass-2 annotation (unchanged from v1.2 §2.3)

```text
3 LLM annotators (mid-tier open): llama-3.1-70b, qwen-2.5-72b, mistral-large-2
Per spec_models_v1.0 §4.3
Temperature: 0.0
50 examples × 3 annotators = 150 calls
Estimated cost: $0 (Ollama)
```

### 2.4 Experiment 2 — Executor + Judge (replaces v1.2 §2.4)

```text
Executor: claude-opus-4-7 (Claude Code interactive session)
50 examples × 3 conditions:
  - direct_naive          (50 outputs)
  - direct_with_claim     (50 outputs)
  - projection_driven     (50 outputs)
= 150 executor outputs
Cost: subscription (no per-call billing); session phase boundaries logged in
data/pilot_v1.1/execution/_session_log.md

Judge: 12-panel per spec_models_v1.0 §4.4
50 × 3 × 12 = 1800 judge calls
Estimated cost: API ~$13 (3 frontier × 150 each) + $0 (9 Ollama)
```

**Per-condition prompt specification**:

| condition | system prompt | self-claim line | projection input |
|---|---|---|---|
| `direct_naive` | `EXEC_DIRECT_SYSTEM` (v1.0 — unchanged) | ❌ no | none |
| `direct_with_claim` | `EXEC_DIRECT_SYSTEM` + self-claim line block | ✅ yes (R1 dim list, agent self-declares q_i) | none |
| `projection_driven` | `EXEC_PROJECTION_SYSTEM_V2` (R-code echo suppressed) + self-claim line block | ✅ yes (q_i declared over input active set) | weights vector + active set J*(d) from Exp 1 cross-family projection (claude family — TBD: gpt-5 projection or fixed-family choice; declare in pre-registration) |

**Self-claim line block** (added before "Produce your response now."):

```
Before your response, declare your coverage on each active dimension as
a single JSON line, exactly as the first line of your output:

  {"covered_dims": {"R1.X": q_X, ...}}

where each q_X ∈ [0, 1] indicates the strength of coverage you intend
to provide on that dimension. This JSON declaration is the ONLY place
where dimension codes (R1.X, RX.X) may appear in your output —
elsewhere, do not echo dim codes or their descriptive names. Then
provide your response as before.
```

**V2 prompt compatibility**: `EXEC_PROJECTION_SYSTEM_V2` in `scripts/exp2_run.py` currently forbids any dim code or dim descriptive name in agent output. The self-claim JSON line is an **explicit exception** — the only output location where dim codes are permitted. To make this exception machine-checkable: `scripts/exp2_run.py` must be updated to (a) add the self-claim block to `EXEC_USER_TEMPLATE` (currently has no slot for it; insertion point is between `{projection_block}` and `Produce your response now.`), and (b) add an exception clause to V2's "Do NOT mention any dim code" rule. The exception clause should read approximately: *"Exception: the JSON declaration on the very first line of your output may use R1.X / RX.X codes — that line is the only allowed location."* This is required reading for `task #10` (script refactor) and is not optional.

Sanitization (per `human_annotation/README.md` §3) strips this JSON line (i.e., the entire first line if it parses as `{"covered_dims": ...}`) before showing output to human annotators in Stage 1. Sanitization removes the *text* of the JSON line; behavior intervention from the self-claim instruction itself (priming the body) is not removed and is the reason `direct_naive` exists as a paired control (per §2.4 condition table and `formalization_v1.2` §5.2).

**Judge prompt** (per `spec_evaluation_rubric_v1.0` §5; v1.2 sync via supersession note):
- Active set = `r*_median`-derived (threshold 0.3) ∪ {RX.1, RX.3, RX.4, RX.5} — RX.2 dropped from anchor scoring.
- Anchors as defined in `spec_evaluation_rubric_v1.0` §4 for the 11 anchor-scored dims (R1.1–R1.7 + RX.1, RX.3, RX.4, RX.5).
- T = 0.0; max_tokens = 1536; per-judge model id recorded per call.

### 2.5 Tier-stratified judge analysis (unchanged from v1.2 §2.5, with reporting set updated)

```
α_frontier   : 3-rater α among gpt-5, gemini-pro, grok-4
α_mid        : 4-rater α among llama-70b, qwen-72b, mistral-large-2, deepseek-distill-70b
α_light      : 5-rater α among the 5 light models
α_panel      : 12-rater α across all
α_with_author: panel + author (= ground truth pairing)
α_with_human : (planned) panel + 5 human raters per-dim across R1.1 / R1.4 / R1.7
               (actual, 2026-05-07): no inferential α — replaced by per-arm reporting in §2.6.3:
                   R1.1 → pass-rate + 3-validated-rater Krippendorff α + Spearman vs panel
                   R1.7 → author + peer Axis-1 engagement-score table (no α, n too small)
                   R1.4 → no human evidence
```

Computed over R1 dims only (RX excluded per `formalization_v1.2` §4).

### 2.6 Stage 1 human anchor — actual scope (UPDATED 2026-05-07; supersedes the 3-dim Prolific plan that was the original §2.6 content)

**Status**: the 3-dim Prolific extension (R1.1 + R1.4 + R1.7, 5 raters × 9 examples × 2 conditions × 3 dims = 270 ratings, ~$300 Prolific gross) **was attempted, partially executed, and superseded** on 2026-05-07. Reasons and replacement scope are recorded in CHANGELOG (2026-05-07) and paper §VI #4. The original §2.6 plan-text is preserved in CHANGELOG for traceability and is **not** the active spec; what follows is the active spec.

#### 2.6.1 Stage 1 actual scope

| arm | dim | source | size | reporting role |
|---|---|---|---|---|
| **A. Prolific salvage (R1.1)** | R1.1 (Conceptual reconstruction) | `human_annotation/recruitment/r11_validated_raters.md` (3 validated raters out of 9 attempts in sb1+sb2; 6 rejected for AI-assisted submissions or task-misunderstanding) | 18 ratings × 3 raters = 54 ratings (single dim, single anchor) | one data point on r\* alignment with humans on R1.1, with explicit pass-rate disclosure (33%) |
| **B. R1.7 v2 author + peer co-annotation** | R1.7 (Citation and scholarship) | `human_annotation/texts/stage1/R1_7_v2/` (6 citation-rich examples × `projection_driven`, sharpened anchor with `event_count` field per `rater_protocol_v1.md`) | 6 packages × 3 expected raters (author + 1–2 peers) = 18 expected ratings | one data point on Axis-1 engagement-score alignment between author, peers, and the LLM panel; per-event Axis-2 correctness fills sparsely as a domain-expert side-pass |
| ~~C. Prolific R1.7 sb1/sb2/sb3~~ | R1.7 | unpublished drafts on Prolific | 0 actual | unused; retained as backup for follow-up paper if rater_protocol_v2 is drafted |
| ~~D. Prolific R1.4 sb1/sb2/sb3~~ | R1.4 | deleted 2026-05-07 | 0 | dropped; no R1.4 evidence in this paper |

**Total active Stage 1 ratings**: 54 (Prolific R1.1) + ~18 (R1.7 v2 author/peer) = **~72 ratings**, replacing the planned 270.

**Why direct_with_claim is excluded from Stage 1**: per `paper_master_v1.3` §6, direct_with_claim is for `L_calibration` measurement (a property of the agent's self-claim), not for human anchor. The cleanest comparison for human anchor is direct_naive ↔ projection_driven. The R1.7 v2 set picks `projection_driven` only because the protocol-finding objective does not require the within-pair contrast.

#### 2.6.2 Sample selection (actual)

| dim | active sample | rule |
|---|---|---|
| R1.1 | 9 examples (sb1+sb2 per `data/pilot_v1.1/_stage1_sampling.json`) | unchanged from v1.3 plan |
| R1.7 | 6 examples — `ad_r1_009, 024, 046, 026, 016, 013` | regex audit of artifact text for author-year patterns; `cite_total ≥ 1` filter applied (only 6 of 50 examples pass; full rank in `data/pilot_v1.1/_r17_density_rank.json`). The 9-example sample originally selected by LLM-panel "load-bearing R1.7" labels was retired because 12 of 18 packages contained zero citations in the artifact, making R1.7 anchor application impossible — see CHANGELOG 2026-05-07 §3.2 dim–data mismatch |
| R1.4 | none | no Stage 1 evidence collected; carries the unmitigated form of §VI #4 |

#### 2.6.3 Reporting form (replaces α_with_human plan)

The §V.1 reporting plan changes from "per-dim α including human anchor (R1.1, R1.4, R1.7)" to:

- **R1.1 arm**: report (i) Prolific pass rate (3/9 ≈ 33%) with reject-reason taxonomy, (ii) Krippendorff α among the 3 validated raters, (iii) human–LLM-panel Spearman correlation on R1.1 scores, (iv) cost-per-validated-rating diagnostic.
- **R1.7 arm** *(updated 2026-05-08 — n=5 actual data with pre/post-protocol partition; full analysis in `human_annotation/recruitment/r17_v2_5_rater_analysis.md`)*: report (i) the 5-rater Axis-1 engagement-score table reproduced below; (ii) score-event mapping diagnostic (descriptive, not inferential); (iii) the **pkg_04 zero-event stress-test pass rate** (pre-protocol 1/3 — only rater A; post-protocol 2/2 — both raters D and E pass); (iv) the cluster-vs-item disagreement count (observed on pkg_01 across all raters: A=1 / B=5 / C=3 / D=0 / E=1, and pkg_06: A=0 / B=5 / C=4 / D=1 / E=1); (v) the **s=5 row reachability** result (1/5 — only rater E pkg_05; the s=5 row is reachable in principle only after protocol-reading); (vi) a secondary form-design observation: 4/5 raters did not match the form's three-option role dropdown across both pre- and post-protocol groups (B, C, D, E mis-handled; only A handled it correctly) (reported as v2 form-control input, not as core finding; the form-instruction layer is independent of the dim-anchor protocol layer); (vii) Axis-2 correctness coverage = 0 in this round (no domain-expert pass was conducted).

  Concrete 5-rater Axis-1 table (events / score per rater; rater A = paper author pre-protocol; raters B, C = anonymized peers pre-protocol; raters D, E = anonymized peers post-protocol):

  | pkg | example | rater A | rater B | rater C | rater D | rater E | anchor reference |
  |---|---|---|---|---|---|---|---|
  | 01 | DrugDock priority claim (cluster-as-1; rater A excluded due to consultation) | 1 / 1.0 | 5 / 4.5 | 3 / 4.0 | 0 / 1.0 | 1 / 3.0 | 1 → s=3 |
  | 02 | SentiBridge (3 mis-attributions + missing comparators) | 2 / 2.0 | 6 / 4.5 | 4 / 4.0 | 2 / 4.0 | 2 / 4.0 | 3 → s=4 |
  | 03 | V2G/Lagrangian (Achiam mis-cast + Chen unverifiable) | 2 / 2.5 | 4 / 4.0 | 5 / 4.5 | 2 / 4.0 | 2 / 4.0 | 2 → s=4 |
  | 04 | PINN — agent says *"did not... touch citations"* | **0 / 1.0 ✓** | **5 / 4.0 ✗** | **2 / 4.5 ✗** | **0 / 1.0 ✓** | **0 / 1.0 ✓** | **0 → s=1** |
  | 05 | ANN/FastNav (anchor s=5 case) | 5 / 4.0 | 6 / 4.0 | 6 / 4.0 | 3 / 4.5 | **4 / 5.0** | 5 → s=5 |
  | 06 | GraphFlow (R-GCN/CompGCN/HGT cluster) | 0 / 1.5 | 5 / 4.0 | 4 / 4.0 | 1 / 3.0 | 1 / 2.0 | 1 → s=3 |

  Score-event mapping diagnostic (qualitative; n=6 per rater, not inferential):
  - Pre-protocol: rater A is near-monotonic with a systematic −1 step relative to the anchor table; raters B and C show decoupling/plateauing — peer scores cluster at 4.0–4.5 across submitted event counts 2–6, including the pkg_04 case where the anchor reference count is 0.
  - Post-protocol: raters D and E both produce monotonic score-event mappings closely aligned with the anchor table. Rater D submitted counts 0–3 with scores 1.0–4.5; rater E submitted counts 0–4 with scores 1.0–5.0 (reaching the s=5 row on pkg_05 — the only such score across all 5 raters).
  - We deliberately report descriptive language rather than computed Pearson r; n=6 per rater makes Pearson fragile.

- **5-rater qualitative comparison table** in §V.1: rows = the 6 R1.7 v2 packages, columns = (rater A | rater B | rater C | rater D | rater E | LLM panel r\*), cell = Axis-1 score. Plus the R1.1 arm result (3 Prolific validated raters + LLM panel α + Spearman). Reported as a qualitative pattern + the F1–F5 findings in `r17_v2_5_rater_analysis.md`, not as a statistical α — n=5 (and n=2 per pre/post group) precludes inferential claims, but the *pattern of pre-protocol decoupling vs post-protocol monotonic alignment* is itself the load-bearing reporting object for §VI #4.

#### 2.6.4 What is *not* claimed

- No claim that 270-rating breadth was reached.
- No claim that R1.4 was anchored against humans.
- No claim that the Axis-1 engagement score validates the original R1.7 anchor's "audits every load-bearing citation against the source" criterion. Axis 1 is an operational engagement-count proxy.
- No claim that rater_protocol_v1 generalizes to R1.3 / R1.4 without further work — those event taxonomies are queued for v2.

These limits are §VI #4 entries, not TODOs (CHANGELOG 2026-05-07).

### 2.7 3-layer loss reporting (NEW)

For each (example × condition × dim), the analysis pipeline computes:

```text
L_projection (per example × projection-family)    -- pre-execution; from Exp 1
L_calibration (per example × condition with self-claim)  -- only for direct_with_claim, projection_driven
L_overclaim   (per example × condition with self-claim)  -- RX.2 operational definition
L_settlement^R1   (per example × condition)              -- weighted by r*_j on R1 only
L_settlement^RX   (per example × condition)              -- mean over RX.1/3/4/5
L_settlement^uniform-R1 (ablation)                       -- equal weight for §V appendix
```

**Headline reporting**: `L_settlement^R1` (weighted) per condition with bootstrap CI. Δ between conditions reported as the P2 actionability evidence.

#### 2.7.1 Aggregation schema (`stats/exp2_aggregate.json` and `.parquet`)

To make the aggregation reproducible, `scripts/exp2_aggregate.py` (forthcoming, task #10) writes one row per (example_id, condition, dim) with the following columns. Defaults declared here are pre-registered:

| column | type | source / formula | missing handling |
|---|---|---|---|
| `example_id` | str | `INDEX.jsonl` | required |
| `condition` | str ∈ {direct_naive, direct_with_claim, projection_driven} | run config | required |
| `dim` | str ∈ J_v1.1 | per-judge active-set entry | required |
| `r_star_j` | float | `stats/r_star_median.json` | required (re-computed in v1.3) |
| `s_ij` | int ∈ {1..5} | judge median over 12 panel | NaN if all judges blocked; row excluded from `L_settlement` agg |
| `v_ij` | float = (s_ij − 1) / 4 | derived | NaN propagated |
| `q_ij` | float ∈ [0, 1] | parsed from agent's first-line JSON `"covered_dims"` | NaN if condition = direct_naive (no JSON) OR JSON parse failed; row excluded from `L_calibration`/`L_overclaim` for that example |
| `is_R1` | bool | dim ∈ R1 | derived |
| `is_RX` | bool | dim ∈ RX | derived |
| `is_active` | bool | dim ∈ J*(d) | derived from per-example `active_set` field |

Per-example aggregates (separate file `stats/exp2_per_example.parquet`):

```text
L_projection            = 1 - cos(r, r_star)             (one value per (example, projection_family); NaN if projection unparsable)
L_calibration           = mean over {j: is_R1 ∧ is_active ∧ q_ij ≠ NaN ∧ s_ij ≠ NaN} of |q_ij - v_ij|
L_overclaim             = mean over same set of max(0, q_ij - v_ij)
L_settlement^R1         = (Σ over {j: is_R1 ∧ is_active} of r_star_j · (1 - v_ij))
                          / (Σ over same set of r_star_j)            -- denominator must be > 0; if all r_star_j == 0 across active R1, set NaN and flag
L_settlement^RX         = mean over {j ∈ {RX.1, RX.3, RX.4, RX.5}} of (1 - v_ij)         -- RX.2 excluded
L_settlement^uniform-R1 = mean over {j: is_R1 ∧ is_active} of (1 - v_ij)
```

**Edge cases**:
- M3 / `\widetilde{M_3}` symmetric difference normalized: if `|J*(d) ∩ R1| == 0` for an example, `\widetilde{M_3}` is undefined and reported as NaN; the example is excluded from M3 aggregate.
- `q_ij` JSON parse failure for `direct_with_claim` or `projection_driven`: example × condition row carries NaN `q_ij` for all dims; `L_calibration` and `L_overclaim` are NaN for that example × condition. Failure rate is reported alongside as a quality metric.
- `direct_naive` rows have `q_ij = NaN` by definition (no JSON line emitted) and contribute only to `L_settlement^*` family, not `L_calibration` / `L_overclaim`.

**Bootstrap unit**: example-level (50 examples) with paired-by-example structure for Δ between conditions. 10000 resamples for headline figures; appendix shows narrower bands at 1000 for reproducibility-comparison.

**Defensive note required in §V.4** (verbatim from `formalization_v1.2` §2.3.1; reproduced in `paper_master_v1.3` §6): "*We evaluate fulfillment over the responsibility set that entered execution (active set J*(d), agent-projected), but weight each dimension by hidden-intent importance (r*_j, annotator-derived) to avoid rewarding broad but non-load-bearing active sets...*"

**Required appendix ablations** (per `paper_master_v1.3` §7 backward-compat note — addresses active-set fairness concern):
- Uniform-R1 ablation: `L_settlement^uniform-R1` reported alongside weighted form.
- Fixed-hidden-intent-support ablation: re-compute `L_settlement^R1` over the fixed support `J_R1 ∩ {j : r*_j > 0.3}` — same denominator across all conditions, so comparison is not biased by differing active set widths.
- These appendix tables bound the magnitude of the active-set-width-induced bias in the headline metric.

### 2.8 M1–M4 mechanism indicators (NEW)

Per `formalization_v1.2` §2.5. Continuous indicators are primary; binary classifications are post-hoc with pilot-calibrated thresholds.

```text
M1 (format coupling)        : binary per example, cross-condition
M2 (active-set breadth excess): |J*(d)| - |loadbearing(d)|, continuous
M3 (self-claim drift)        : symmetric difference (declared, produced) / |J*∩R1|, continuous
M4 (RX boost magnitude)      : 1/4 Σ over RX.1,3,4,5 of (v^projection_driven - v^direct_naive), continuous
```

**Pilot-calibrated thresholds** are declared in `data/pilot_v1.1/_diagnostic_thresholds.json`, **frozen by SHA-256 hash and ISO-8601 timestamp before the v1.3 rerun analysis stage** (the file's SHA256 is committed to the docs repo as part of the analysis pre-registration). To minimize the "analysis staging on the rerun data" critique, threshold values are **calibrated on the v1.0 pilot data** (already collected, model panel different but mechanism distributions estimable) rather than on the v1.3 rerun data. If v1.0 calibration is infeasible for a given indicator (e.g., M3 requires self-claim line which v1.0 prompts lacked), the calibration falls back to a held-out 10-example v1.3-rerun split that is excluded from the §V headline reporting; this fallback is also pre-registered in the same JSON file with a `calibration_source` field per indicator.

Specific threshold definitions:
- ε_{M2}: median of `\widetilde{M_2}` across the 50 v1.0 examples (M2 is condition-independent — same `J*(d)` and load-bearing dims regardless of executor).
- ε_{M3}: median of `\widetilde{M_3}` across self-claim conditions on a 10-example held-out v1.3 split (reason: M3 needs `q_ij`, not available in v1.0).
- ε_{M4}: zero (positive value classifies as RX-boosted; no calibration needed).
- c_q ∈ {0.2, 0.3, 0.5}, c_v ∈ {0.4, 0.5, 0.6} for M3 sensitivity sweep across the published threshold value.

**Reporting**: continuous distributions + binary rates for the pre-registered threshold set. Sensitivity sweep across alternate threshold values appears in appendix. The `_diagnostic_thresholds.json` file's SHA256 hash and timestamp are reported in §V.5 prose so reviewers can verify pre-registration.

---

## 3. Cost summary (v1.3 pilot total)

| step | calls | host | est. cost |
|---|---|---|---|
| Pass-2 annotation | 150 (3 × 50) | Ollama | $0 |
| Projection cross-family | 150 (3 × 50) | API | ~$3 |
| Projection within-model | 250 (1 × 5 × 50) | API | ~$5 |
| Executor (Exp 2) | 150 (3 × 50) | Claude Code session | n/a (subscription) |
| Judge frontier (3 × 150) | 450 | API | ~$13 |
| Judge mid + light (9 × 150) | 1350 | Ollama | $0 |
| **LLM subtotal** | — | — | **~$21 API + Ollama $0** |
| ~~Stage 1 human anchor (planned 3 batches × 90)~~ | ~~270 ratings~~ | ~~Prolific~~ | ~~~$300~~ |
| Stage 1 actual (post 2026-05-07 closure) | ~72 ratings | Prolific R1.1 sb1+sb2 + co-annotation form | ~£100 spent + £0 author/peer |
| **Pilot total (planned, pre-closure)** | | | ~~$321~~ |
| **Pilot total (actual, post-closure)** | | | **~$148** (LLM $21 + R1.1 Prolific ~£100/$127 + author/peer £0) |

Compares to v1.0 pilot ~$200 LLM and v1.1 (planned) ~$116. v1.3 *planned* total was ~$321 (3-dim Prolific extension); the *actual* post-closure total is ~$148 because the Stage 1 plan was superseded — see §2.6 + paper §VI #4 + CHANGELOG 2026-05-07.

---

## 4. Reproducibility considerations (extends v1.2 §4)

Per `spec_models_v1.0` §3 (closed-API version recording, Ollama weight pinning) — unchanged from v1.2.

v1.3 additions:

- **Pre-registration files** (declared before analysis; each file's SHA-256 and timestamp are committed to the docs repo and reported in paper §V):
  - `data/pilot_v1.1/_diagnostic_thresholds.json` — ε_{M2}, ε_{M3}, ε_{M4}, c_q, c_v values used in the published §V, with `calibration_source` field per indicator (`v1.0_pilot` or `v1.3_holdout_10`).
  - `data/pilot_v1.1/_stage1_sampling.json` — RNG seed, stratification rule, selected example IDs per dim batch.
  - `data/pilot_v1.1/_projection_choice.json` — **decision: gpt-5 cross-family projection** (declared here; any deviation requires version bump). Rationale: gpt-5 is the within-family stability anchor (Exp 1B), so feeding gpt-5's projection into projection_driven keeps the projection-driven executor input on the same family whose stability is independently characterized. The alternative (each example gets its own projection family from the cross-family run) is operationally messier and is reserved for an ablation in main run.
- **Code-implementation discipline** (per `formalization_v1.2` §9.3):
  - Raw continuous metric logging is primary in pipeline output.
  - Binary classifications are post-hoc, configurable via the `_diagnostic_thresholds.json` file.
  - No hard-coded pass/fail in the analysis pipeline; all metrics are computed regardless of magnitude.
  - Post-hoc threshold changes are recorded in a separate `_diagnostic_thresholds_v2.json` and reported as sensitivity check.

---

## 5. What `paper_section_5_draft_v1.1` must reflect (NEW)

The v1.1 Experiments draft (replaces stale `paper_section_5_draft_v1.0`) reports the v1.3 measurement layer:

- §5.1 Dataset and annotation reliability — per-dim α among the LLM panel; **Stage 1 human anchor reporting follows §2.6.3** (R1.1 pass-rate + 3-validated-rater α + Spearman-vs-panel; R1.7 author/peer Axis-1 engagement-score table; no R1.4 human evidence). The original "α_with_human across R1.1/R1.4/R1.7" plan was superseded 2026-05-07. Plus **inter-dim correlation matrix on R1 dims** (R1-only per `formalization_v1.2` §4) as construct-validity screening diagnostic.
- §5.2 Experiment 1 (Cross-family projection) — `R(d)` distribution + median; CI on the cross-family vs within-model ratio.
- §5.3 Experiment 1B (Within-model stability) — `R(d)` ratio result, paired with §5.2.
- §5.4 Experiment 2 (3-condition + 3-layer loss) — `L_settlement^R1` per condition with bootstrap CI; `L_calibration` for direct_with_claim and projection_driven; `L_overclaim` (RX.2 op def) for the same; mandatory defensive note on J*(d) projection-derived vs r* weighting; appendix ablations (uniform-R1, fixed support).
- §5.5 Mechanism characterization — `\widetilde{M_1..4}` continuous distributions per condition; binary rates under pilot-calibrated thresholds + sensitivity sweep; **finding framing** ("naive projection injection is insufficient; the gap is *characterized by* M1–M4 — not *mediated by*").
- §5.6 Limitations and deferred work — references the 5 §VI Limitations entries from `paper_master_v1.3` §4.

---

## 6. Backward compatibility with v1.2 results

`experiment_design_v1.2` setup tables remain the canonical reference for the 2-condition design (now superseded). v1.3 supersedes v1.2 Exp 2 (50 × 2 = 100 outputs → 50 × 3 = 150 outputs); no v1.2 Exp 2 measurement output is portable to v1.3 (different conditions, different prompt structure, different anchor scoring set). Exp 1, Exp 1B, and pass-2 are unchanged from v1.2 — those measurement outputs would be portable in principle, but since `data/pilot_v1.1/` cleanup (task #9) is the migration path, they are also re-run from scratch for cleanliness.

The dataset (`examples/`, `INDEX.jsonl`, `provenance/`) is unchanged across v1.0 → v1.1 → v1.2 → v1.3.
