# `spec_models_v1.0` — Model Panel and Role Assignments

> **Status**: canonical source of truth for model choices in pilot v1.1 onward.
> **Iteration 2 (2026-05-04 evening)** — incorporates `review_feedback_v1_0` Part II decisions: P0 reference integration (Zheng / Panickssery / Stureborg replace analogical justification), Stage 1 human anchor extension to R1.4 + R1.1 *(later superseded — see Iteration 3 below)*, inter-dim correlation matrix promoted to v1.2 analysis, role-call-count update for 3-condition Exp 2 split (per `formalization_v1.2` §5).
> **Iteration 3 (2026-05-07)** — Stage 1 boundary-condition closure. The 3-dim Prolific extension was attempted, partially executed, and superseded; actual scope is R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation (no R1.4 evidence). §3 entry 3, §4 Stage 1 cost block, §5 α reporting, and §6 entry 4 all reflect the closure. See `paper_master_v1.3` §VI #4 + CHANGELOG 2026-05-07.
> Supersedes scattered model references in:
>   - `spec_pi_implementation_v1.0.md` §6, §10 (projection family list)
>   - `spec_evaluation_rubric_v1.0.md` §6.1 (judge panel)
>   - `spec_bid_v1.0.md` §11 (bidder family)
>   - `experiment_design_v1.1.md` §5–§6 (executor / judges / annotators)
>   - `paper_master_v1.1.md` §pilot-protocol (annotator / judge counts)
>
> Those docs should be updated to reference this spec rather than re-declaring model choices.

---

## 1. Why this spec exists (conceptual frame)

The pilot v1.1 redesign was triggered by a cascading discovery: every fix to the LLM-evaluation protocol exposed another flaw. We trace this to **three structural failure modes of LLM-based measurement**. Each is documented in the LLM-as-judge literature and each maps onto a perennial human-institutional problem (the analogues are heuristic; the citations are load-bearing):

| failure mode | description | literature backing | social analogue (heuristic) |
|---|---|---|---|
| **Recursive self-reference / self-preference** | LLM judges identify and favor outputs from their own family. | Panickssery et al. (2024) — *LLM Evaluators Recognize and Favor Their Own Generations*. Demonstrated empirically at multiple model scales. | *Quis custodiet ipsos custodes?* — no system audits itself. |
| **Family-prior covariance / panel inconsistency** | Models within and across families exhibit position bias, verbosity bias, and self-enhancement bias — agreement reflects shared priors, not validity. | Zheng et al. (2023, MT-Bench/Chatbot Arena); Stureborg et al. (2024) — *Large Language Models are Inconsistent and Biased Evaluators*. | Cartelization / regulatory capture — homogeneous panels produce false consensus. |
| **Capability heterogeneity** | When some judges cannot detect signal, panel agreement is silence not consensus; tier-stratified analysis is needed. | Stureborg et al. (2024) — recommends multi-tier panel + per-tier reporting as the diagnostic pattern. | Asymmetric-information democracy — uninformed and informed votes have equal weight. |

**Why scaling does not solve them**: LLMs are trained on overlapping human-generated data. They inherit *the structural patterns* of human social cognition, not just its content. Increasing model size adds capacity but does not remove the priors. Mitigation must therefore be **protocol-level**, not capability-level.

The protocol-level mitigations adopted in this spec, with the citation each is justified by:

1. **Multi-family panel, Anthropic-excluded** — addresses self-preference (Panickssery 2024). Executor is Anthropic-family; judges and annotators exclude Anthropic.
2. **Tier-stratified pyramid (frontier + mid + light)** — exposes capability heterogeneity rather than hiding it (Stureborg 2024). Analysis is run per-tier and aggregated; the pattern is literature-recommended, not our invention.
3. **External human anchor (Stage 1)** — *(superseded 2026-05-07 — see §6 entry 4 below)*. The original v1.0 design called for at least three dimensions (R1.1, R1.4, R1.7) calibrated against humans, breaking the LLM-only feedback loop for the slice of the rubric most exposed to LLM-LLM disagreement. The 2026-05-07 Stage 1 closure replaced this with a narrower scope (R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation) and a methodological boundary-condition finding (paper §VI #4); see CHANGELOG 2026-05-07 and `experiment_design_v1.3` §2.6 for the active spec. The "necessary but not sufficient" framing of this row still holds; what changes is which form of "sufficient" we attempted and what ceiling it ran into.

These mitigations are *necessary but not sufficient*. Residual limits — listed in §6 below — are explicit paper §VI items, not unresolved bugs.

---

## 2. Master panel — 12 LLMs, no Anthropic

| tier | n | model | family | host | rationale |
|---|---|---|---|---|---|
| frontier | 1 | `gpt-5` | OpenAI | API | top closed |
| frontier | 2 | `gemini-2.5-pro` | Google | API | top closed |
| frontier | 3 | `grok-4` | xAI | API | top closed, third independent vendor |
| mid (~70B) | 4 | `llama-3.1-70b-instruct` | Meta | Ollama | open frontier-1 |
| mid (~70B) | 5 | `qwen-2.5-72b-instruct` | Alibaba | Ollama | open frontier-1 |
| mid (~123B) | 6 | `mistral-large-2-2407` | Mistral | Ollama | open frontier-1 |
| mid (~70B) | 7 | `deepseek-v3-distill-70b` | DeepSeek | Ollama | open frontier-1, distinct architecture lineage |
| light (~8B) | 8 | `llama-3.1-8b-instruct` | Meta | Ollama | open small |
| light (~7B) | 9 | `qwen-2.5-7b-instruct` | Alibaba | Ollama | open small |
| light (~9B) | 10 | `gemma-2-9b-it` | Google | Ollama | open small (Google open lineage ≠ closed Gemini family) |
| light (~14B) | 11 | `phi-3-medium-14b-instruct` | Microsoft | Ollama | open small, Microsoft lineage |
| light (~7B) | 12 | `mistral-7b-instruct-v0.3` | Mistral | Ollama | open small |

**Anthropic exclusion**: the executor is `claude-opus-4-7` (Claude Code session). Including any Anthropic model in the panel would re-introduce self-preference. Anthropic is excluded from projection, pass2 annotation, and judging.

**Family diversity**: 8 distinct vendors (OpenAI, Google [closed + open], xAI, Meta, Alibaba, Mistral, DeepSeek, Microsoft). gemini-2.5-pro (closed) and gemma-2-9b (open) share a Google lineage but were trained as separate model lines; treated as distinct family members for the purposes of this spec.

---

## 3. Hosting and reproducibility

| host | models | configuration |
|---|---|---|
| API (OpenAI) | gpt-5 | `temperature=0` for deterministic roles; pinned model version recorded per call |
| API (Google) | gemini-2.5-pro | same |
| API (xAI) | grok-4 | same |
| Ollama (local) | 9 open models | server: 96 GB VRAM (NVIDIA RTX PRO 6000 Blackwell). Model weights pulled once and frozen by hash; ollama pull tag and SHA256 recorded per call. `temperature=0` via Ollama API. |

**Why Ollama for opens** (vs e.g. Together / Fireworks): weight-pinning. Closed APIs may silently version-bump (`gpt-5` → `gpt-5-2026-XX-XX`); Ollama runs a specific weight blob with a content hash that does not change. This gives the paper stronger reproducibility than pure-API setups.

**Per-call records** (in JSON output for every LLM call across all roles):

```
{
  "model_family": "...",        # vendor
  "model_id": "...",            # exact model id including version date if any
  "host": "api" | "ollama",
  "ollama_digest": "...",       # if host=ollama
  "temperature": 0.0,
  "prompt_version": "...",      # from this spec or downstream specs
  "input_tokens": ...,
  "output_tokens": ...,
  "latency_ms": ...,
  "cost_usd_estimated": ...     # null for Ollama
}
```

---

## 4. Role assignments

| role | assigned models | per-example calls | total calls (50 examples) | host | est. cost |
|---|---|---|---|---|---|
| **Executor** | `claude-opus-4-7` (Claude Code session) — single | **3 (one per condition: direct_naive / direct_with_claim / projection_driven)** | **150** | session | n/a (subscription) |
| **Projection (cross-family)** | frontier 3 (gpt-5, gemini-2.5-pro, grok-4), T=0 | 3 | 150 | API | ~$3 |
| **Projection (within-family stability)** | gpt-5, T=0.5, 5 runs | 5 | 250 | API | ~$5 |
| **Pass-2 annotator** | mid 3 (llama-70b, qwen-72b, mistral-large-2), T=0 | 3 | 150 | Ollama | $0 |
| **Judge** | full panel of 12, T=0 | **3 (per condition) × 12 = 36** | **1800** | mixed | API ~$13 + Ollama $0 |

**Total estimated cost (LLM only)**: ~$21 API + $0 Ollama ≈ **$21**.

**Stage 1 human anchor — *(updated 2026-05-07: original plan superseded; see §6 entry 4 + `experiment_design_v1.3` §2.6 for active spec)***:

*Original plan (per `review_feedback_v1_0` #6, superseded)*:
- 3 dim-specific batches: R1.7, R1.4, R1.1 (one batch per dim).
- Each batch: 9 dim-load-bearing examples × 2 conditions × 5 humans = 90 ratings.
- 3 batches × 90 = 270 ratings total via Prolific. ~$300.

*Actual scope (post 2026-05-07 closure)*:
- R1.1 Prolific salvage: 3 validated raters from sb1+sb2 (~£100/$127 spent, 33% pass rate), ~54 ratings.
- R1.7 v2 author + peer co-annotation: 6 citation-rich packages, sharpened anchor with `event_count` field per `human_annotation/rater_protocol_v1.md`, ~18 ratings.
- R1.4: no human evidence collected.
- Total Stage 1 spend ~£100/$127, not $300.

**Pilot total**:
- *Planned (pre-closure)*: LLM ~$21 + Stage 1 ~$300 = ~$321.
- *Actual (post-closure)*: LLM ~$21 + Stage 1 ~$127 = ~**$148**.

### 4.1 Executor — single, Anthropic-family, 3 conditions

Rationale: paper's Exp 2 isolates the *projection-driven vs direct* treatment effect within one executor family. Multi-executor (3-family × 3 conditions × 50 = 450 executor calls) is deferred to main run; pilot fixes one executor for power. Executor is `claude-opus-4-7` invoked through the Claude Code interactive session.

**Three conditions** (per `formalization_v1.2` §5.1):
- `direct_naive` — original v1.0 direct prompt, no self-claim line. P2 settlement baseline (P1 measurement runs in Exp 1, not Exp 2; this condition only baselines P2 settlement comparison).
- `direct_with_claim` — direct + self-claim line for `L_calibration` measurement. Pairs with direct_naive on same examples for built-in priming ablation.
- `projection_driven` — V2 prompt (R-code echo suppressed) + self-claim line. Treatment condition.

The third condition adds ~50 executor calls and ~600 judge calls compared to the v1.1 2-condition design. Cost increase ~$5; methodologically necessary to separate behavior-intervention effect (self-claim line) from treatment effect (projection input).

Implications and disclosures (paper §VI):
- No `temperature` override (Claude Code session uses provider defaults).
- No per-call cost ledger; cost is approximated as zero against subscription.
- Within-conversation outputs are more correlated than independent API calls would be; if any reordering matters, conversation phase boundaries are documented in `data/pilot_v1.1/execution/_session_log.md` (created at execution time).

### 4.2 Projection — frontier 3 for cross-family + gpt-5 for within-family stability

Rationale: paper §V Exp 1's central claim is **cross-family projection divergence**. This requires ≥ 3 vendor families. The frontier 3 (gpt-5, gemini-pro, grok-4) provides max-capability cross-family signal; mid/light tiers are not used for projection because lower-capability projection introduces capability noise into the divergence metric (we want to attribute divergence to family, not capability).

For within-family stability (Exp 1.2), we run gpt-5 five times at T=0.5 on each example. Choice of gpt-5 over the other two frontier: arbitrary; declared.

### 4.3 Pass-2 annotator — mid 3 for r* generation

Rationale: pass-2 annotators produce hidden-intent vectors r* used to compute `r_star_median` (which feeds projection-driven executor's active set). The role needs *capable but diverse* annotators. Mid-tier 3 (llama-70b, qwen-72b, mistral-large-2) gives:
- 3 distinct vendors (Meta, Alibaba, Mistral)
- All open-weight (reproducibility)
- Capability sufficient for rubric interpretation (per Open LLM Leaderboard 2026)
- Cost zero (Ollama)

The pilot's prior pass-2 was *2 LLM annotators* (after gpt-4o-mini was removed); the new spec is *3 LLM annotators*, strengthening r_star_median against single-rater outliers.

### 4.4 Judge — full 12-panel, tier-stratified analysis

Rationale: judge agreement (Krippendorff's α) is THE central reliability metric for the rubric. The 12-panel provides:
- Cross-family diversity (8 vendors)
- Tier stratification (3 frontier + 4 mid + 5 light) → α can be computed *per-tier* and *across all 12*; per-tier α isolates capability effect

**Tier-stratified analysis is literature-recommended** (Stureborg et al. 2024 — *LLMs are Inconsistent and Biased Evaluators*), not our invention. Per-tier α reporting is the standard mitigation when judge capability cannot be assumed homogeneous.

**Analysis stratification** (computed in `stats/exp2_aggregate.json`):

```
α_frontier   : 3-rater α among gpt-5, gemini-pro, grok-4
α_mid        : 4-rater α among llama-70b, qwen-72b, mistral-large-2, deepseek-distill-70b
α_light      : 5-rater α among the 5 light models
α_panel      : 12-rater α across all
α_with_author: panel + author (= ground truth pairing)
α_with_human : (planned, superseded 2026-05-07) panel + 5 human raters per-dim across R1.1/R1.4/R1.7
               (actual) replaced by per-arm reporting in `experiment_design_v1.3` §2.6.3:
                 R1.1 → 3-validated-rater Krippendorff α + Spearman vs panel
                 R1.7 → author + peer Axis-1 engagement-score table (no inferential α)
                 R1.4 → no human evidence
```

If `α_frontier > α_mid > α_light`, capability heterogeneity is confirmed and disclosed. If they're similar, anchor reliability is robust to capability tier. The original `α_with_human` per-dim plan was scoped at R1.1 / R1.4 / R1.7; **only R1.1 Prolific salvage retains an inferential α** under the post-2026-05-07 closure. R1.7 anchoring is qualitative (Axis-1 score-event table); R1.4 has no human anchoring.

**RX dims**: per `formalization_v1.2` §4, RX is repositioned as cross-cutting design constraint, not measurement target. Judges score RX.1 / RX.3 / RX.4 / RX.5 (RX.2 is operationalized via `L_overclaim`, not anchor-scored), but α is **not reported** for RX dims (always-active → zero variance → α undefined). Stratified α is computed over R1 dims only.

---

## 5. Master-panel reuse pattern (for future specs / scripts)

Downstream code should not hardcode model lists. Instead:

```python
# scripts/_models.py  (single source)
PANEL = json.load(open("data/pilot_v1.1/spec_models_panel.json"))
# fields: tier, model_family, model_id, host, ollama_tag

ROLES = {
    "executor": [m for m in PANEL if m.get("role") == "executor"],   # = claude-opus-4-7
    "projection": [m for m in PANEL if m["tier"] == "frontier"],
    "pass2_annotator": [m for m in PANEL if m["tier"] == "mid"][:3],
    "judge": [m for m in PANEL],
}
```

`spec_models_panel.json` (canonical machine-readable companion) lives at `data/pilot_v1.1/spec_models_panel.json` and is generated from this spec at script-init time.

---

## 6. What this spec does NOT solve — explicit paper §VI items

Adopting this spec mitigates internal validity threats but leaves residual limits to disclose, not fix. The list below extends with `review_feedback_v1_0` Phase 4 recovery (inter-dim correlation promoted from future work to v1.2 analysis) and the **post-2026-05-07 Stage 1 boundary-condition finding** (entry 4) — which replaces the originally planned 3-dim anchor scoping rationale with a methodological boundary-condition report on anchor specifiability + domain-expertise gating.

1. **Inherited human priors**: Even with 8 distinct vendors and Anthropic exclusion, all panel models train on overlapping web-scale human text. Cross-family agreement still partially reflects shared human priors, not external validity. Discussion §VII.

2. **Construct validity of rubric anchors** — partially addressed by inter-dim correlation matrix: This spec assumes the 12 R1/RX dims are coherent constructs. Pilot results (R1.7 α = 0.07 in v1.0) suggest some anchors may be *multi-dimensional in disguise*. **As a v1.2 pilot deliverable** (per `formalization_v1.2` §8), the inter-dim correlation matrix on `r*_median` across 50 examples is computed and reported in paper §5.1. Pairs with `|r| > 0.7` are flagged as candidates for "fronting one latent factor." This converts the limit from hidden weakness to declared limit with effect-size data; full factor decomposition (PCA / EFA) remains future work.

3. **Single-executor design**: Exp 2's treatment effect estimate is bound to claude-opus-4-7 executor. Generalization across executor families is reserved for main run.

4. **Self-reference at the rubric layer** — *(updated 2026-05-07/08 — Stage 1 boundary-condition finding + 5-rater pre/post-protocol corroboration)*: Rubric was authored by the paper's author (one human) and validated against LLM α. The v1.0 plan extended Stage 1 anchor to **R1.1, R1.4, R1.7** (3 dims, ~$300 Prolific) per `review_feedback_v1_0` #6 to *reduce* the *"r* is just LLM-LLM consensus"* objection. **Stage 1 did not validate r\* at the planned breadth** — the pilot exposed two binding constraints not anticipated by the plan: (i) Prolific pass rate ~33% on R1.1 sb1+sb2 (cost asymmetry under low pass rate), (ii) author own first pass over R1.7 18-package form regressed to a generic intent-fit lens because only 6 of 50 examples in the pool contained citation events ≥1 in the artifact (dim–data mismatch), and (iii) even after a redesigned R1.7 v2 form with sharpened anchor + `event_count` field, two specifiability ambiguities (counting cluster-vs-item; correctness verification requiring source-of-truth) remained — not solved by rater count alone. Stage 1 actual scope was reduced to R1.1 salvage + R1.7 v2 author/peer co-annotation. The R1.7 v2 arm closed 2026-05-08 at **n=5 raters** with a natural pre/post-protocol partition (rater A = paper author pre-protocol baseline; raters B, C = anonymized peers pre-protocol; raters D, E = anonymized peers post-protocol after receiving `rater_protocol_v1.md` separately). The boundary-condition finding is now corroborated by both pre-protocol regression (raters B, C plateau scoring) and post-protocol partial mitigation (raters D, E monotonic anchor-aligned scoring; rater E reaches the s=5 anchor row, the only such score across all 5 raters). Residual specifiability gap remains post-protocol (D=0 vs E=1 cluster-as-1 disagreement on pkg_01). Qualitative; n=2 per pre/post group is below inferential power. The §VI entry reports this as a methodological finding (paper §VI #4 in `paper_master_v1.3`; `human_annotation/rater_protocol_v1.md` is the durable artifact; `human_annotation/recruitment/r17_v2_5_rater_analysis.md` is the empirical source). Remaining R1 dims (R1.2, R1.3, R1.5, R1.6) carry the unmitigated form; RX dims fall outside this measurement frame entirely (per `formalization_v1.2` §4). The reframing is from "rubric author was unaudited" to "rubric author audit attempted at planned breadth, ran into anchor specifiability + domain-expertise ceiling, scope reduced and ceiling reported."

5. **Plank framework not transferable to LLM-only annotation** (per `formalization_v1.2` §7.2): The headline reference for "annotator disagreement is signal not noise" (Plank 2022) was developed for human annotators; LLM-only annotator panels (which we use for `r*` on dims that did not retain a human anchor under the post-2026-05-07 closure — i.e., all R1 dims except R1.1, since R1.7 author/peer Axis-1 ratings are non-inferential and R1.4 has no human evidence) share training-data priors and do not benefit from the Plank framework's perspective-variation argument. This is reserved as a future-work pointer toward distributional `r*` over human annotators in main run.

These five are §VI Limitations entries in `paper_master_v1.3` (when forthcoming) or `paper_master_v1.2` §VI in the interim. They are *not* TODO items — they are the explicit boundary of this paper's claims.

---

## 7. Versioning

- `spec_models_v1.0` — this doc. Pilot v1.1 onward.
- Future `v1.1` would update model identities (e.g., gpt-5 → gpt-6 if released before main run). Tier structure and Anthropic-exclusion principle are stable across minor versions.
- Major version bump (`v2`) reserved for protocol changes (e.g., adding multi-executor, removing tier stratification).

CHANGELOG entries for downstream doc updates referencing this spec belong in `docs/CHANGELOG.md`, not here.
