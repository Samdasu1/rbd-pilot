# Formalization v1.2
## Sync Patch on `formalization_v1.1` — Two-Proposition Decoupling and Three-Layer Loss

> Status: theoretical sync patch on v1.1. **Iteration 2** (2026-05-04 evening) incorporates self-review feedback.
> Role: separates measurability from actionability, decomposes settlement loss into 3 layers, repositions RX, formalizes 4 mechanism indicators
> Companion files:
> - `formalization_v1.0.md` (root — full 38-dim taxonomy)
> - `formalization_v1.1.md` (parent — narrowed `J_v1.1`)
> - **`spec_models_v1.0.md` / `_v1.0.1` (canonical model panel)**
> - `experiment_design_v1.2.md` (operational spec under v1.2; will sync 3-condition split in next patch)
> - `paper_master_v1.3.md` (companion, forthcoming)
> - `review_feedback_v1_0.md` (motivation for §1, §2 decoupling)
> - `additional_prior_work_v1_0.md` (citation anchors)

---

## 0. What changed from v1.1

The 12-dim taxonomy (`J_v1.1`), score anchors, and active-set rule (`τ_r = 0.3`) are **unchanged**. Theoretical-framework changes:

| element | v1.1 | v1.2 |
|---|---|---|
| Thesis structure | single coupled claim | **two propositions P1 (measurability) + P2 (actionability)**, evidence-asymmetric |
| Settlement loss | single `L_i = Σ w_j ℓ_ij` | **3-layer**: `L_projection`, `L_calibration` (headline) + `L_overclaim` (RX.2 op def), `L_settlement^R1` (headline) + `L_settlement^RX` (constraint) |
| Settlement weighting | uniform | weighted by `r*_j` (uniform → ablation) |
| RX.2 anchor scoring | judges score s ∈ {1,3,5} | **dropped** — operationalized as `L_overclaim` instead |
| Conditions in Exp 2 | direct, projection_driven | **3**: direct_naive, direct_with_claim, projection_driven |
| Clarification trigger | 2-clause OR (theoretical) | 2-clause **theoretical** + 1-clause **operational proxy** (multi-projection setting) |
| RX role | tracked dims with α undefined | **cross-cutting design constraint enforced by protocol**, not measurement target |
| Self-claim source | implicit / inferred | **explicit declarative line in executor** (`direct_with_claim` and `projection_driven`); behavior intervention disclosed |
| 4 mechanisms (v1.0 §5.5) | prose-only | formal indicators **M1–M4** (§2.5); **diagnostic-only** per §9 (continuous primary, binary post-hoc; not acceptance gates) |
| Inter-dim correlation | future work | **promoted to v1.2 pilot analysis** (free `np.corrcoef` on `r*_median`) |

What does **not** change:
- 12-dim closed taxonomy `J_v1.1`.
- Per-dimension anchors at s ∈ {1, 3, 5} for **R1.1–R1.7 and RX.1, RX.3, RX.4, RX.5**. RX.2 anchor scoring dropped.
- Active-set rule `J*(d) = {j ∈ R1 : r_j > 0.3} ∪ J_X`.
- Hidden-intent annotation protocol (3 LLM annotators per `experiment_design_v1.2`).
- Reputation update `ρ_{i,y,j,t+1}` formula (deferred to follow-up; pilot evidence simulation-only per `paper_master_v1.3`).

---

## 1. Two-proposition decoupling

The pilot evidence supports two distinct claims with asymmetric strength. v1.1 stated them as one coupled thesis. The decoupling is essential because:

- Coupled framing exposes the paper to a single reject-coding sentence: *"Exp 2 CI includes 0; headline claim and measurement disagree."*
- Decoupled framing lets each proposition stand on its own evidence base, with the gap between them treated as a *finding* (mechanism analysis) rather than a *failure*.

```text
P1 (measurability)
   The projection commitment r = π(d, u, t, a) — a function of delegation,
   user context, time, and agent — is computable, and Δ(r, r*) is
   family-attributable: holding (d, u, t) fixed and varying a across
   model families, cross-family projection divergence exceeds within-model
   stochastic variance (R(d) = d_C / d_W > 1).

   Evidence: Experiment 1 + 1B (cross-family ~17× within-model in pilot v1).
   Strength: STRONG.

P2 (actionability)
   Knowledge of the projection commitment can be used to reduce execution
   loss — through clarification, projection-driven execution, or settlement.

   Evidence: Experiment 2 (CI includes 0 in pilot v1; mixed across class).
   Strength: SUGGESTIVE / INCONCLUSIVE.
   Mechanism analysis: §2.5 below formalizes four protocol-design indicators
   (M1–M4) characterizing the gap between measurement and execution
   improvement. v1.2 rerun reports M1–M4 effect sizes regardless of
   magnitude (continuous primary; binary post-hoc per §9 — diagnostic-only,
   not acceptance gates).
```

The paper's contribution is jointly:
1. **A measurement instrument** for P1.
2. **A characterization of the protocol-design space** required to translate measurability into actionability — i.e., why naive projection injection is insufficient.

---

## 2. Three-layer loss decomposition

v1.1's single `L_i = Σ w_j ℓ_ij` conflates three theoretically distinct sources of loss. v1.2 decomposes them.

### 2.1 L_projection — pre-execution alignment

Measures how much the agent's projection `r` diverges from the hidden-intent ground truth `r*`. Computed *before* execution, hence a property of the projection step only.

```math
L_{\text{projection}}(d, a) = \Delta(r, r^*) = 1 - \cos(r, r^*)
```

**Property**: since r, r* ∈ [0,1]^12 are componentwise non-negative, cos(r, r*) ∈ [0, 1] and `L_projection ∈ [0, 1]`. Lower is better. (Cosine distance is the headline; Jaccard distance over `J*` and L1 are reported as alternatives in appendix.)

**Measurable in pilot**: yes — `r` is the projection JSON output (per Exp 1, 3 frontier families); `r*` is the median of pass-2 LLM annotators (per `experiment_design_v1.2`). No additional instrumentation.

**r\* validity prerequisite (load-bearing for interpretation; updated 2026-05-07)**:

> The interpretability of `L_projection` rests on `r*`'s validity as an external anchor. The v1.2 plan named the planned 3-dim Prolific extension (R1.1 + R1.4 + R1.7, 270 ratings) as the documented prerequisite for the headline interpretation. **The 2026-05-07 Stage 1 closure (CHANGELOG entry of that date) supersedes that plan**: the planned breadth validation was not delivered, and a methodological boundary-condition finding was reported in its place (paper §VI #4). The interpretability tier of `L_projection` is now:
>
> - *(tier A, available with v1.0 R1.7 batch + 2026-05-07/08 R1.7 v2 qualitative 5-rater corroboration with pre/post-protocol partition)*: `L_projection` is interpretable as *"executor projection diverges from the LLM annotator panel, on a dimension where 5 human raters (rater A = paper author pre-protocol, raters B and C = anonymized peers pre-protocol, raters D and E = anonymized peers post-protocol) produce Axis-1 engagement scores that converge with the panel's r\* in two cases: (1) on the high-density unambiguous package (pkg_05) all raters report event_count=3–6, and post-protocol rater E reaches the anchor table's s=5 row; (2) on the zero-event package (pkg_04) the post-protocol pass converges to s=1 across both raters D and E even though pre-protocol peers had failed. **Divergence persists in the pre-protocol group** (raters B, C plateau scores 4.0–4.5 across all event counts) **and in residual borderline cases post-protocol** (raters D, E disagree on cluster-as-1 application: pkg_01 D=0 vs E=1)."* The interpretation is bounded by the *pattern* of rater disagreement and the protocol-exposure conditional, not by inferential α — see `human_annotation/recruitment/r17_v2_5_rater_analysis.md` and paper §VI #4. This is narrower than the v1.1 reading; it does not extend to "intended responsibility" across all R1 dims.
> - *(tier B, would require future work)*: full *"executor projection diverges from intended responsibility"* reading would require either (i) a domain-expert panel with Axis-2 correctness verification on the cited literature, or (ii) a redesigned anchor whose specifiability bounds (counting + correctness) are tighter than rater_protocol_v1's. Both are deferred — see paper §VI #4 and §VII follow-up.
>
> The relevant scalability ceiling is **anchor specifiability + domain-expertise gating**, not rater throughput. Increasing rater count alone does not strengthen tier A toward tier B (per the 2026-05-07 finding). Stureborg et al. 2024 (LLM evaluators' inconsistency) remains the empirical citation anchor for why an LLM-only r\* is insufficient; the 2026-05-07 finding adds an empirical citation anchor for why scaling the human side requires more than rater count.

**Citation anchor**: see Stureborg et al. 2024 (LLM evaluators' inconsistency) for the empirical concern that an LLM annotator panel may not constitute a valid r* without human anchoring. (Plank 2022 is reserved for §VI Limitations as a future-work pointer for distributional r* over human annotators — Plank's framework is human-annotator-specific and does not transfer cleanly to LLM panels.)

**Maps to**: Experiment 1 / 1B in `experiment_design_v1.2` §2.1 / §2.2.

### 2.2 L_calibration (headline) and L_overclaim (RX.2 operational definition)

Measures the gap between the agent's *self-reported coverage* `q_i` (from the explicit declarative line — see §5) and the *observed fulfillment* `v_ij` (judge-derived, R1 dims only).

#### 2.2.1 L_calibration (headline)

Symmetric two-sided calibration error, parallel to ECE-style metrics in calibration literature:

```math
L_{\text{calibration}}(d, a) = \frac{1}{|J^*(d) \cap \text{R1}|} \sum_{j \in J^*(d) \cap \text{R1}} |q_{ij} - v_{ij}|
```

**Property**: bounded in [0, 1]; lower is better. Two-sided counts both overclaim (q > v) and underclaim (q < v). R1-restricted to avoid the RX-dominance issue (RX dims always r*=1 dominate any RX-inclusive aggregate).

**Connection to calibration literature**: this metric is consistent with calibration-error practice (e.g., ECE, MCE) where the function of interest is `|predicted - observed|`. Reviewers familiar with calibration will recognize the form.

#### 2.2.2 L_overclaim (RX.2 operational definition)

One-sided positive gap, used as the operational form of RX.2:

```math
L_{\text{overclaim}}(d, a) = \frac{1}{|J^*(d) \cap \text{R1}|} \sum_{j \in J^*(d) \cap \text{R1}} \max(0, q_{ij} - v_{ij})
```

**Role**: replaces the s ∈ {1,3,5} anchor-based scoring of RX.2. Judges no longer score RX.2 as an anchor; the dim's score is computed as `s_RX.2 = 1 + 4 · (1 - L_overclaim)` (continuous mapping), or RX.2 is reported only as `L_overclaim` directly (recommended). This eliminates the v1.1 double-counting where RX.2 was scored both as anchor and as a behavior measured implicitly via output.

**Property**: bounded in [0, 1]; lower is better. Reported alongside `L_calibration` so the asymmetry is visible.

**Measurement gating**: `L_calibration` and `L_overclaim` are measurable only in conditions that include the self-claim line — `direct_with_claim` and `projection_driven`, not `direct_naive`. See §5.

### 2.3 L_settlement — fulfillment, R1/RX split

#### 2.3.1 L_settlement^R1 (headline) — weighted by hidden intent

```math
L_{\text{settlement}}^{\text{R1}}(d, a) = \frac{\sum_{j \in J^*(d) \cap \text{R1}} r^*_j \cdot \ell_{ij}}{\sum_{j \in J^*(d) \cap \text{R1}} r^*_j}, \quad \ell_{ij} = 1 - v_{ij}
```

**Defensive note (must appear in paper §V.4)**:

> We evaluate fulfillment over the responsibility set that entered execution (active set J*(d), agent-projected), but weight each dimension by hidden-intent importance (r*_j, annotator-derived) to avoid rewarding broad but non-load-bearing active sets. The measurement target is *agent-attended dimensions* and the weighting reflects *importance to the user*; this is the deliberate design, not an inconsistency.

**Why R1-only**: with RX always-active (r*≈1.0 for all 5 RX dims) and R1 typically having 1 load-bearing dim (r*≈1.0) plus 2-3 peripheral (r*≈0.3–0.5), an R1+RX aggregate would be ~76% RX-dominant, contradicting §4's repositioning of RX as design constraint not measurement target. Splitting R1 / RX preserves theoretical coherence.

**Property**: bounded in [0, 1]; lower is better.

#### 2.3.2 L_settlement^RX — constraint fulfillment indicator

For RX dims (excluding RX.2, which is operationalized via `L_overclaim`):

```math
L_{\text{settlement}}^{\text{RX}}(d, a) = \frac{1}{4} \sum_{j \in \{\text{RX.1, RX.3, RX.4, RX.5}\}} \ell_{ij}
```

Reported alongside `L_settlement^R1` as a constraint-fulfillment indicator; not a measurement-target loss. RX.2 is reported separately as `L_overclaim`.

#### 2.3.3 L_settlement^all — appendix-only ablation

```math
L_{\text{settlement}}^{\text{all}} = \tfrac{1}{2}(L_{\text{settlement}}^{\text{R1}} + L_{\text{settlement}}^{\text{RX}})
```

Reported in appendix only, for transparency. Not used as headline.

#### 2.3.4 Uniform weighting — ablation form

```math
L_{\text{settlement}}^{\text{uniform-R1}}(d, a) = \frac{1}{|J^*(d) \cap \text{R1}|} \sum_{j \in J^*(d) \cap \text{R1}} \ell_{ij}
```

Reported as ablation alongside the weighted headline. Per `review_feedback_v1_0` recommendation, the weighted form partially mitigates the active-set propagation bias mechanism (M2): peripheral dims enter at weight ≈0.3 instead of 1.0, so they no longer dilute load-bearing dim evaluation.

**Citation anchor**: per-requirement decomposition with importance weighting is established in instruction-following evaluation (InFoBench, Qin et al. 2024). Our distinction: InFoBench's requirements are extracted from the instruction itself; our `J*(d)` is *projected* by the agent before fulfillment. Decomposition target differs but the per-component weighted aggregation paradigm is the precedent.

### 2.4 Why three layers, not one

The three loss layers target three theoretically distinct questions:

| layer | question | failure mode |
|---|---|---|
| L_projection | "Did the agent interpret the request correctly?" | misprojection — wrong responsibility structure |
| L_calibration | "Was the agent honest about what it covered?" | mis-calibration — gap between claimed and delivered (either direction) |
| L_settlement^R1 | "Did the agent execute the responsibilities?" | underdelivery — low fulfillment on load-bearing dims |

A single `L_i` cannot disentangle these. An agent can have high `L_projection` (misinterpreted) but low `L_settlement^R1` (delivered well on what it *did* address). Or low `L_projection` (interpreted correctly) but high `L_calibration` (claimed broader than executed). The protocol-design discussion (paper §5.5) becomes coherent only when these three are separated.

### 2.5 Mechanism indicators (M1–M4)

The four mechanisms identified in v1.0 `paper_section_5_draft` §5.5 are formalized as **continuous diagnostic indicators** per (example, condition) pair, supplemented by example-level binary classifications under explicitly **pilot-calibrated** thresholds. Continuous values are the load-bearing reporting form; binary classifications are diagnostic.

#### 2.5.1 Continuous indicators (primary reporting form)

```math
\widetilde{M_1} \;(\text{format coupling}): \mathbb{1}\big[\text{output-type}(\text{output}_{\text{direct\_naive}}) \neq \text{output-type}(\text{output}_{\text{projection\_driven}})\big]
```

(Inherently binary per-example: output type is a categorical attribute. Rate across examples is the continuous report.)

```math
\widetilde{M_2} \;(\text{active-set breadth excess}): |J^*(d)| - |\text{loadbearing}(d)|, \quad \text{loadbearing}(d) = \{j : r^*_j > 0.7\}
```

(Continuous in ℤ ≥ 0; reported as median + IQR across examples per condition.)

```math
\widetilde{M_3} \;(\text{self-claim symmetric difference}): \frac{|\{j : q_{ij} > c_q\} \triangle \{j : v_{ij} > c_v\}|}{|J^*(d) \cap \text{R1}|}
```

(Continuous in [0, 1]. `c_q` and `c_v` are continuous-cutoff parameters — see §2.5.3 for treatment. Measurable only in conditions with self-claim line.)

```math
\widetilde{M_4} \;(\text{RX boost magnitude}): \frac{1}{4} \sum_{j \in \{\text{RX.1,3,4,5}\}} (v_{ij}^{\text{projection\_driven}} - v_{ij}^{\text{direct\_naive}})
```

(Continuous in [-1, 1]; reported as median + bootstrap CI.)

#### 2.5.2 Binary classification (diagnostic only)

For protocol-refinement reporting, each example may be classified as "exhibits Mₖ" under a threshold:

| indicator | continuous metric | binary cutoff (pilot-calibrated) |
|---|---|---|
| M1 | (binary by definition) | ≥ 1 cross-condition output-type mismatch in 50 examples → "M1 present" |
| M2 | `\widetilde{M_2}` per example | `\widetilde{M_2} ≥ ε_{M2}`, ε_{M2} pilot-calibrated (initial estimate ≈ 2) |
| M3 | `\widetilde{M_3}` per example | `\widetilde{M_3} ≥ ε_{M3}`, ε_{M3} pilot-calibrated (initial estimate ≈ 0.2) |
| M4 | `\widetilde{M_4}` per example | `\widetilde{M_4} ≥ ε_{M4}`, ε_{M4} pilot-calibrated (initial estimate ≈ 0.05) |

Initial cutoff estimates are *not* hypothesis-test gates. They are initial values for diagnostic reporting only; the actual values used in the paper are determined post-pilot via the procedure in §2.5.3.

#### 2.5.3 Threshold treatment (load-bearing protective framing)

> **Thresholds used for mechanism indicators (M1–M4 binary cutoffs, the M3 continuous-cutoff parameters c_q / c_v, the §9 priming bound, and the §9 max correlation) are treated as pilot calibration parameters. They are not used as primary hypothesis-test cutoffs. The main P1 / P2 evidence relies on continuous effect sizes (e.g., `R(d) = d_C / d_W` distribution, `L_settlement^R1` Δ between conditions with bootstrap CI) and Spearman / Krippendorff α point estimates with CIs. Binary mechanism gates are used only for diagnostic reporting and protocol refinement; they appear in §V and §VI as supplementary descriptive statistics, not as significance tests.**

Operationally: thresholds are chosen via a pre-registered rule rather than visual selection on results. Suggested rules (to be fixed before re-run):
- ε_{M2}: median `\widetilde{M_2}` across 50 examples in the v1.2 pilot, computed before treatment-effect analysis.
- ε_{M3}: median `\widetilde{M_3}` across the conditions with self-claim line.
- ε_{M4}: zero (i.e., classify as "RX boosted" if positive); median is reported alongside.
- c_q, c_v in M3: continuous-to-set conversion for symmetric difference; reported with sensitivity sweep over {0.2, 0.3, 0.5} for c_q and {0.4, 0.5, 0.6} for c_v.

This makes binary classifications reproducible across labs and immune to "post-hoc threshold engineering" critique.

---

## 3. Clarification trigger — theoretical vs operational proxy

`formalization_v1.0` §9 / `formalization_v1.1` §10 stated:

```text
C(d) = 1 if D_π(d) > τ_D OR E[L_direct(d)] - E[L_clarified(d)] > Cost_clarify(d)
```

The second clause is **operationally unmeasurable in deployment** — `E[L_clarified]` requires already running clarification. v1.2 splits:

### 3.1 Operational proxy (used in pilot)

```math
C^{\text{operational}}(d) = \mathbb{1}[D_\pi(d) > \tau_D]
```

where `D_π(d)` is the cross-family projection divergence `d_C(d)` from Exp 1. Computable in a *multi-projection setting* — i.e., when ≥ 2 projection samples of the same delegation are available (cross-family or repeated single-family). This requires deploying the projection step itself with multiple model calls, so "deployable" with cost — not zero-cost. Pilot uses this form.

### 3.2 Theoretical (motivational only)

```math
C^{\text{theoretical}}(d) = \mathbb{1}[D_\pi(d) > \tau_D \;\text{or}\; \mathbb{E}[L_{\text{direct}}] - \mathbb{E}[L_{\text{clarified}}] > \text{Cost}_{\text{clarify}}]
```

**v1.2 decision**: paper's §3 motivation references the theoretical form (justifying *why* clarification can have value); paper's §4 protocol uses `C^{operational}`. The second clause is reserved as future-work meta-controller objective.

This avoids the "you cannot measure your own threshold" reject vector.

---

## 4. RX repositioning — design constraint, not measurement target

```text
RX is a cross-cutting design CONSTRAINT enforced by the protocol, not a
MEASUREMENT TARGET whose reliability we attempt to demonstrate.

  - The protocol requires the executor to address RX.1, RX.3, RX.4, RX.5
    (RX.2 operationalized via L_overclaim) on every delegation, regardless of r.

  - We do not report α for RX dims (mathematically undefined; would mislead).
  - We do not include RX dims in correlation analysis with R1 dims.
  - We DO score RX.1, RX.3, RX.4, RX.5 in the judge protocol; the scores
    feed L_settlement^RX (constraint fulfillment indicator), not headline loss.
  - RX.2 is dropped from anchor-based judge scoring entirely — its operational
    measurement is L_overclaim (computed from agent self-claim line vs judge
    R1 fulfillment scores; see §2.2.2).
```

**Implication for paper §3**: RX is introduced as "five cross-cutting protocol constraints we enforce," not "five additional dimensions whose reliability we measure." Single-paragraph clarification with significant downstream effect on §5 reporting.

---

## 5. Executor self-claim line — protocol change with three conditions

To make `L_calibration` measurable in the pilot without activating the full bid mechanism (deferred per `spec_bid_v1.0` supersession), the executor prompt for *some* conditions adds one declarative line:

```
Before your response, declare your coverage on each active dimension as
a JSON line:

  {"covered_dims": {"R1.X": q_X, ...}}

where each q_X ∈ [0, 1] indicates the strength of coverage you intend to
provide on that dimension. Then provide your response as before.
```

### 5.1 Three conditions (replaces v1.1's two-condition Exp 2)

| condition | self-claim line? | role |
|---|---|---|
| **direct_naive** | ❌ no | naive baseline. Used for **P2 settlement-comparison baseline** and M1 (format coupling) cross-comparison. P1 measurement runs in Exp 1 (cross-family projection), not in Exp 2 conditions; this condition specifically baselines P2. Original v1.0 direct prompt. |
| **direct_with_claim** | ✅ yes | L_calibration / L_overclaim measurement in non-projection-driven setting. Paired with direct_naive on same examples to isolate self-claim's behavior intervention. |
| **projection_driven** | ✅ yes | Exp 2 treatment condition. Receives projection r as input; declares q_i; executes with V2 prompt (R-code echo suppressed per `scripts/exp2_run.py`). |

50 examples × 3 conditions = **150 executor calls** (was 100). Cost increase: ~50 more frontier-judge calls × 12 judges = 600 extra judge calls; frontier 3 share ≈ 150 calls × ~$0.03 = **~$5 extra**. Pilot total cost still well under budget.

### 5.2 Self-claim line as behavior intervention (disclosure)

Adding a self-claim line to the prompt is **not just a measurement** — it is a **behavior intervention**. The agent's attention is partially directed to the dim list during generation, which can change output structure even without leaking RX-codes (per the Confound 3 concern in `review_feedback_v1_0` Phase 3).

Implications:
- `direct_with_claim` is *not* equivalent to `direct_naive + measurement`. It is its own condition.
- Comparing `direct_naive` vs `direct_with_claim` on the same 50 examples gives a **built-in ablation** for the priming effect: if judge scores on R1 dims differ systematically between the two, priming exists and must be disclosed.
- This built-in ablation makes a separate priming-ablation subset (originally proposed) unnecessary.

**Paper §5.X** must report:
- `L_settlement^R1` for all three conditions
- `Δ(L_settlement^R1)` between direct_naive and direct_with_claim — the priming-effect estimate
- `L_calibration` for direct_with_claim and projection_driven
- The interpretation of P1 evidence is based on `direct_naive` (cleanest baseline), not on the claim-augmented conditions

### 5.3 Sanitization for human evaluation

The JSON line is removed from the output before human-annotator views per `human_annotation/README.md` §3 sanitization. Note: sanitization removes the line text but does not remove its priming effect on the body — that effect is captured in the Δ between direct_naive and direct_with_claim and disclosed in §VI.

---

## 6. Updated equations (replaces v1.1 §10)

```math
r = \pi(d, u, t, a), \quad r \in [0, 1]^{12}
```

```math
J^*(d) = \{j \in \text{R1} : r_j > 0.3\} \cup J_X
```

```math
M(d, u, t) = \Delta(r, r^*) \;\;\Rightarrow\;\; L_{\text{projection}}
```

```math
L_{\text{projection}} = 1 - \cos(r, r^*) \in [0, 1]
```

```math
L_{\text{calibration}} = \frac{1}{|J^*(d) \cap \text{R1}|} \sum_{j \in J^*(d) \cap \text{R1}} |q_{ij} - v_{ij}|
```

```math
L_{\text{overclaim}} = \frac{1}{|J^*(d) \cap \text{R1}|} \sum_{j \in J^*(d) \cap \text{R1}} \max(0, q_{ij} - v_{ij})
```

```math
L_{\text{settlement}}^{\text{R1}} = \frac{\sum_{j \in J^*(d) \cap \text{R1}} r^*_j \cdot \ell_{ij}}{\sum_{j \in J^*(d) \cap \text{R1}} r^*_j}, \quad \ell_{ij} = 1 - v_{ij}
```

```math
L_{\text{settlement}}^{\text{RX}} = \frac{1}{4} \sum_{j \in \{\text{RX.1, RX.3, RX.4, RX.5}\}} \ell_{ij}
```

```math
C^{\text{operational}}(d) = \mathbb{1}[D_\pi(d) > \tau_D]
```

```math
\rho_{i,y,j,t+1} = (1 - \lambda)\,\rho_{i,y,j,t} + \lambda\,v_{ij}, \quad j \in J_{v1.1}
```

(`ρ` update unchanged; applies only to simulated agents in the pilot per `paper_master_v1.3` C3 demotion.)

Mechanism indicators M1–M4 per §2.5.

---

## 7. References

### 7.1 P0 / P1 references load-bearing in v1.2

- **Stureborg et al. (2024). Large Language Models are Inconsistent and Biased Evaluators.** Cited in §2.1 as the empirical concern that an LLM-only annotator panel may not constitute a valid r* without human anchoring. Replaces Plank in the L_projection justification.
- **Bavaresco et al. (2024). LLMs instead of Human Judges: A Large Scale Empirical Study.** Alternative / complementary citation to Stureborg for the same concern; cite if page allows.
- **Qin et al. (2024). InFoBench.** Cited in §2.3 as the per-requirement weighted-aggregation paradigm precedent for `L_settlement^R1`. Differentiation: instruction-extracted (InFoBench) vs agent-projected (ours).

### 7.2 Reserved for §VI Limitations

- **Plank (2022). The 'Problem' of Human Label Variation.** Reserved for §VI Limitations as a future-work pointer toward distributional r* over **human** annotators. Plank's framework is human-annotator-specific and does not transfer cleanly to LLM panels (which share training-data priors); using Plank to justify median-over-LLM-panel would be a stretch.

### 7.3 Other v1.2 references

For self-preference and judge bias literature backing `spec_models_v1.0` §1 conceptual frame, see `concept_and_positioning_v1.1` §2.8 (Zheng / Panickssery / Stureborg).

---

## 8. v1.2 pilot analyses promoted from "future work"

Per `review_feedback_v1_0` recovery item #1, the **inter-dimension correlation matrix** on `r*_median` across 50 examples is promoted from future work to required v1.2 analysis. Computed as:

```python
import numpy as np
r_star = np.array([example.r_star_median for example in pilot])  # (50, 12)
corr = np.corrcoef(r_star.T)                                       # (12, 12)
```

**Reporting**:
- Heatmap of the 12×12 correlation matrix in paper §5.1 or §VI.
- Pairs with |r| > 0.7 flagged in prose as candidates for "fronting one latent factor" — relevant to construct-validity disclosure.
- This matrix becomes evidence for §VI Limitations entry on construct validity, transforming it from hidden weakness to declared limit with effect-size data.

---

## 9. Diagnostic checks and risk (NOT hypothesis-test gates)

> **Critical framing**: items 8–10 below are *diagnostic descriptive statistics* used to characterize the v1.2 pilot's behavior. They are **not** hypothesis-test cutoffs that gate publication. The v1.1 acceptance gates (§6 of `formalization_v1.1`) — projection JSON validity, |J*(d)| range, α threshold per dim, R(d) > 1.2, RX populated, cost budget, dim-confusion < 0.3 — remain the pre-registered acceptance gates and are unchanged. Items 8–10 below are added as diagnostic checks whose values are reported regardless of outcome; *no value of these diagnostics blocks paper submission.*

### 9.1 Diagnostic checks (added in v1.2)

8. **Mechanism prevalence (diagnostic)**: For each M_k ∈ {M1–M4}, the binary-classification rate across 50 examples is reported under the pilot-calibrated thresholds (§2.5.3). Continuous indicator distributions (`\widetilde{M_k}`) are reported alongside as primary form. *No threshold for "mechanism present"* — readers see the distribution and judge.
9. **Self-claim priming magnitude (diagnostic)**: `Δ(L_settlement^R1, direct_naive vs direct_with_claim)` per R1 dim is reported as a per-dim point estimate with bootstrap CI. *No fixed bound* — magnitudes are disclosed in §VI as part of the limitation statement.
10. **r\* inter-dim correlation (diagnostic)**: The inter-dim correlation matrix on `r*_median` is reported (heatmap in §5.1; per-pair |r| values listed). Pairs with `|r| > 0.7` are flagged for narrative discussion (candidates for "fronting one latent factor"). *No exclusion / pass-fail threshold* — the matrix is the report.

### 9.2 Risk paragraph (must appear in paper §VI as Limitation)

> The mechanism analysis (paper §5.5, formalization §2.5) was developed from v1.0 pilot observations under a different model panel and prompt set. The v1.2 rerun, conducted under the new panel and 3-condition split, will produce its own continuous mechanism indicators and binary classifications. We report the v1.2 results regardless of magnitude. If the v1.2 effect sizes for any indicator are smaller than v1.0, we disclose the change as a finding ("the mechanism appears weaker under the redesigned panel") rather than retroactively raising thresholds; if larger, we report that finding similarly. The paper does not adjudicate "did the mechanism replicate?" via a binary gate — it reports the v1.2 effect size and lets readers compare to v1.0 narrative.

### 9.3 Code-implementation discipline

To preserve the diagnostic-only posture across the analysis pipeline:

- **Raw continuous metric logging**: `scripts/exp2_aggregate.py` (forthcoming) writes per-(example, condition, dim) raw values for `v_ij`, `q_ij`, `\widetilde{M_2}`, `\widetilde{M_3}`, `\widetilde{M_4}`, and the L_* family — without binary classification.
- **Binary classification as post-hoc**: a separate script (e.g., `scripts/diagnostic_gates.py`) reads raw values and applies thresholds. Multiple threshold settings can be swept; sensitivity tables are reported in appendix.
- **No hard-coded pass/fail in pipeline**: the pipeline does not abort on threshold violation. It produces all metrics; thresholds are reporting choices.
- **Pre-registration**: the threshold values used in the published §V are pre-registered in `data/pilot_v1.1/_diagnostic_thresholds.json` before v1.2 rerun completes. Post-hoc threshold changes are version-bumped (separate file) and reported alongside as sensitivity check.

This discipline answers the *"results-driven threshold tuning"* reject vector by structurally separating measurement from classification.

---

## 10. What stays as future work

- **L_calibration with explicit bid mechanism** (full `b_i` per `spec_bid_v1.0`): pilot uses self-claim line approximation. Main run activates bid for stronger calibration measurement.
- **Reputation update on real agents**: pilot is simulation-only per `paper_master_v1.3` C3 demotion. Real-agent reputation evidence is future work.
- **Distributional r\*** (per Plank 2022): v1.2 retains median for tractability; distributional treatment over human annotators is future work.
- **Full factor decomposition** (PCA / EFA on r* matrix): only inter-dim correlation matrix is v1.2 output; full factor analysis is future work.
- **3rd condition cross-comparison metrics beyond M1**: the direct_naive ↔ direct_with_claim ↔ projection_driven triple opens additional cross-condition metrics (e.g., consistency of self-claim across direct vs projection settings); deferred to follow-up.

---

## 11. Backward compatibility

`formalization_v1.1` results (the v1.0 pilot) used:
- single `L_i` (uniform weight, `paper_section_5_draft_v1.0` §5.4)
- no L_projection / L_calibration / L_overclaim as named metrics
- 2-clause clarification trigger as headline
- 2 conditions (direct, projection_driven)
- RX.2 anchor-scored

These v1.1-era results are stale per `paper_section_5_draft_v1.0` STALE marker (2026-05-04). v1.2 results, generated under `experiment_design_v1.2` rerun (with 3-condition split), will report the new metric set.

`J_v1.1` itself (taxonomy + R1 anchors + RX.1/3/4/5 anchors) is identical between v1.1 and v1.2; only RX.2 anchor scoring is dropped.
