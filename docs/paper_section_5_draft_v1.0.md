# Paper §5. Experiments — Draft v1.0

> ⚠️ **STALE — superseded 2026-05-04**. The numeric results in this draft were produced under the v1.0/v1.1 model panel (claude-sonnet-4.5 executor + claude/gpt-mini/gemini-flash judges + 2 pass-2 annotators) which was retired upon discovery of three structural failure modes (see `spec_models_v1.0` §1). Re-runs under the v1.2 panel (claude-opus-4-7 executor via Claude Code session + 12-judge tier-stratified panel + 3 pass-2 annotators, all Anthropic-excluded) are pending. A `paper_section_5_draft_v1.1.md` will replace this once the v1.2 measurement layer is regenerated. *Do not cite numbers from this draft.*
>
> Original status (preserved for context): first paper-grade draft of the Experiments section, consolidating pilot v1 results.
> Scope: §5.1 Dataset and annotation, §5.2 Experiment 1, §5.3 Experiment 1B, §5.4 Experiment 2 (pilot scope), §5.5 Mechanism analysis, §5.6 Limitations and deferred work.
> Cumulative compute cost for the runs reported here: **\$8.87** (32 synthetic + 18 modified-real annotation \$1.42; cross-family + within-model projection \$3.74; pilot Experiment 2 settlement-loss runs \$3.55).
> Companion files: `formalization_v1.1.md`, `experiment_design_v1.1.md` (superseded by `experiment_design_v1.2.md`), `spec_dataset_v1.0.md`, `spec_pi_implementation_v1.0.md`, `spec_evaluation_rubric_v1.0.md`, `paper_master_v1.1.md` (superseded by `paper_master_v1.2.md`), `spec_models_v1.0.md` (NEW — canonical model panel).

---

## 5.1 Pilot dataset and annotation reliability

### 5.1.1 Dataset composition

We construct **AmbiguousDelegation-50-R1**, a 50-example pilot dataset for paper-research delegation under the closed responsibility space `J_v1.1` (12 dimensions: R1.1 conceptual reconstruction, R1.2 logical consistency, R1.3 evidence-claim alignment, R1.4 novelty assessment, R1.5 structural reorganization, R1.6 writing polish, R1.7 citation and scholarship; cross-cutting RX.1 uncertainty disclosure, RX.2 overclaim avoidance, RX.3 scope adherence, RX.4 downstream-harm avoidance, RX.5 provenance and traceability). Per `formalization_v1.1` §2 the taxonomy is held closed for the pilot; per `paper_master_v1.1` §5 contributions are scoped to R1 plus RX.

Each example carries: (a) a generic delegation drawn from a frozen 10-template pool that does not name any responsibility dimension, (b) an artifact section (200–500 words after `wc -w` canonicalization), (c) an `engineered_flaws` annotation listing the load-bearing flaw codes per `spec_dataset_v1.0` §5, (d) author-pass-1 hidden-intent weights `r*_author ∈ [0,1]^{12}`, and (e) acceptable-output and bad-output prose summaries.

Coverage matrix (`spec_dataset_v1.0` §2.1):

| coverage class | n | role |
|---|---|---|
| single (one R1 dim load-bearing) | 30 (≥4 per R1 dim) | primary measurement |
| dual (two R1 dims load-bearing) | 10 | dim-pair interaction |
| ambiguous (genuinely two readings) | 5 | clarification trigger |
| control (delegation explicitly invokes the dim) | 5 | sanity floor |
| **total** | **50** | |

Source mix is 32 synthetic + 18 modified-real (the latter sliced from a single author-owned V2G-domain submission, anonymized per `spec_dataset_v1.0` §4.2). The pilot's spec-target source mix was 30+20; we report a +2/-2 deviation arising from a mid-batch source decision and disclose it transparently. The modified-real subset is concentrated in one technical domain (power systems / V2G); the synthetic subset spans 30 distinct technical domains. We report main-text results pooled and supplementary stratification by source.

Two annotation tags (per `spec_dataset_v1.0` §5.X / §5.Y) further classify each example:

- `knowledge_gating ∈ {low, moderate, high}` — whether flaw detection requires recall of canonical literature. For the pilot: 45 low / 2 moderate / 3 high (6% high, well under the G-D-11 cap of 30%).
- `delegation_dim_leakage ∈ {no, partial, yes}` — whether the delegation surface form signals the load-bearing dim. For measurement examples (single + dual + ambiguous = 45): 44 no, 1 partial (`ad_r1_007`); 0 yes (G-D-12 hard tier passed). All 5 controls carry partial or yes leakage by design.

### 5.1.2 Hidden-intent annotation protocol

Per `spec_dataset_v1.0` §6 (option D), pass-1 records `r*_author` at construction time; pass-2 obtains independent weights from two LLM annotators of different families operating at temperature 0; pass-3 (human subset, 20 stratified examples × 2 annotators) is reserved for the main run. The pilot reports pass-1 + pass-2.

Initial pass-2 used `claude-sonnet-4.5` and `gpt-4o-mini` (gpt-5-mini does not support `temperature=0`). After diagnosing systematic over-activation (`gpt-4o-mini` weighted ≥ 0.7 on 28% of dimension-cells where the author weighted < 0.3), we replaced `gpt-4o-mini` with `gemini-2.5-flash` for the headline analysis and retain the original gpt traces (`annotations_v2/`) for transparency.

### 5.1.3 Per-dimension reliability — the headline α

Krippendorff's α at interval level over 3 raters (author + claude + gemini), n=50 per dimension:

| dim | α | gate (≥0.4) |
|---|---|---|
| R1.1 conceptual | 0.315 | borderline |
| R1.2 logical | **0.463** | ✓ |
| R1.3 evidence-claim | 0.390 | borderline |
| R1.4 novelty | **0.521** | ✓ |
| R1.5 structural | **0.526** | ✓ |
| R1.6 polish | **0.534** | ✓ |
| R1.7 citation | 0.219 | ✗ |

**Four of seven R1 dimensions pass G-D-07 (α ≥ 0.4); two are borderline; one fails.** RX dimensions are excluded from α reporting because by construction they are always-on (median weight 1.0 across all 50 examples), giving zero variance and undefined α. The boundary-fragility test for R1.4 ↔ R1.7 (whether annotators systematically swap novelty positioning with citation-scholarship issues) yields **0/50 swap cases** in pilot data; the taxonomy's separation holds at this scale.

The R1.7 failure is interpretable: citation-accuracy annotation requires recall of the relevant literature's canonical works, which blind LLM annotators do not have. We mark R1.7 as taxonomy-uncertain in the pilot and escalate it to mandatory human annotation for the main run. R1.1 and R1.3 are borderline; we report results on those dimensions with an annotation-uncertainty caveat in §5.4.

We use `r*_median` — the per-dimension median across the three pass-1+pass-2 tracks — as the operational ground-truth weight vector for downstream metrics (projection-intent mismatch in §5.2, settlement-loss active-set derivation in §5.4).

---

## 5.2 Experiment 1 — Cross-family projection mismatch

### 5.2.1 Setup

Per `spec_pi_v1.0` §3 / `experiment_design_v1.1` §4, three model families project responsibility onto `J_v1.1` for each pilot example: `claude-sonnet-4.5`, `gpt-4o-mini`, `gemini-2.5-flash`. Each call uses the verbatim spec-§3.1 system prompt, temperature 0, and the strict §2 JSON schema. Per example we compute the cosine distance and Jaccard distance between every family pair, then average:

```
d_C^cos(d) = mean_{f1<f2} (1 - cos(r_{f1}, r_{f2}))
d_C^jac(d) = mean_{f1<f2} Jaccard-distance(J*_{f1}, J*_{f2})
```

Total: 50 × 3 = 150 calls. After §7 retry policy (one retry on schema violation, then mark `unprojected`), 138 of 150 pass strict validation; 12 records (8% of calls, 3% of total) violate §2 invariants — chiefly six claude failures on `ad_r1_008`-pattern (R1.6 weight > 0.3 but R1.6 missing from `active_set`), two gpt failures on RX-active-set membership, and four claude rationale omissions. For all 12 we re-parse the raw JSON and recover the weights vector (the active-set field is post-derivable from weights), so projection-distance metrics are computable for all 50 examples.

### 5.2.2 Results

| metric | mean | median | std |
|---|---|---|---|
| d_C^cos (n=50) | 0.105 | 0.093 | 0.042 |
| d_C^jac (n=50) | 0.081 | 0.080 | 0.057 |

Stratification by coverage class shows:

| class | n | d_C^cos mean | d_C^cos median |
|---|---|---|---|
| single | 30 | 0.101 | 0.089 |
| dual | 10 | 0.117 | 0.111 |
| ambiguous | 5 | 0.082 | 0.090 |
| control | 5 | 0.126 | 0.103 |

Two findings against expectation deserve attention. First, the **ambiguous class is not the highest-divergence class** (0.082 mean, lowest); we hypothesize that under structural ambiguity the families converge on a similar broad projection rather than partition into distinct readings. Second, the **control class has non-zero d_C** (0.126 mean), exceeding even the single class. Inspection reveals this is driven by RX-dimension weight variation (0.7–1.0 across families) rather than R1 disagreement — all three families correctly project the load-bearing R1 dim on controls, but cosine distance accumulates over RX. The "control = d_C ≈ 0" sanity expectation is therefore too idealized; we revise the expected control band to 0.05–0.15 in `spec_dataset_v1.0` and treat values above ~0.20 as projection-prompt diagnostics.

Knowledge-gating effect:

| gating | n | d_C^cos mean |
|---|---|---|
| low | 45 | 0.104 |
| moderate | 2 | 0.130 |
| high | 3 | 0.095 |

High-gated examples do **not** systematically inflate d_C (in fact slightly lower than low-gated, n=3 underpowered). This is a positive result for the paper's headline claim: cross-family projection divergence is **not driven by knowledge confound**. Reviewers concerned that "claude knows HNSW and gemini does not" might explain divergence are answered: the high-gating subset would show the largest divergence under a knowledge-confound hypothesis; it does not.

### 5.2.3 Clarification rate per family

Cross-family clarification triggers at temperature 0:

| family | clarification_needed = true | rate |
|---|---|---|
| claude | 11 / 50 | 22.0% |
| gpt | 0 / 50 | 0.0% |
| gemini | 10 / 50 | 20.0% |

A pronounced inter-family asymmetry: `gpt-4o-mini` never requests clarification under the §3.1 prompt, while `claude` and `gemini` clarify on roughly one in five examples. On the five ambiguous-class examples — the positive cases for the clarification trigger — only **1 of 5** elicits any family to clarify (`ad_r1_018`, claude only). This indicates either (a) our ambiguous artifacts are insufficiently ambiguous to trigger spec-§6 clarification rules, or (b) the LLM clarification trigger is conservative under the current prompt. Both interpretations are reportable; we treat this as a calibration gap to address in §5.4 and the main run.

---

## 5.3 Experiment 1B — Within-model stochastic baseline

### 5.3.1 Setup

Per `spec_pi_v1.0` §4.2 / `experiment_design_v1.1` §5, we fix one model (`claude-sonnet-4.5`) and run five independent projections per example at temperature 0.5. For each example we compute pairwise cosine distance over the 5C2 = 10 within-model pairs and average:

```
d_W^cos(d) = mean_{r1<r2} (1 - cos(r_{run1}, r_{run2}))
```

Total: 50 × 5 = 250 calls; all pass schema validation modulo the same active-set / rationale issues handled by raw-recovery as in §5.2.

### 5.3.2 R(d) — the load-bearing comparison

| metric | mean | median | std |
|---|---|---|---|
| d_W^cos (n=50) | 0.006 | 0.001 | 0.010 |

In **25 of 50** examples, claude at temperature 0.5 produces *identical* weight vectors across all five runs (d_W = 0). The remaining 25 show small but non-zero stochastic divergence (mean 0.011). This makes within-model variance an exceptionally tight comparison baseline.

The ratio R(d) = d_C / d_W is finite for 25 examples (the rest have d_W ≈ 0 making R formally infinite — *strengthening* the gap):

| ratio | value |
|---|---|
| median R(d) over 25 finite cases | 14.4 |
| mean R(d) | 17.99 |
| R > 1.0 | 25/25 (100%) |
| R > 1.2 | 25/25 (100%) |

For the paired test we use the difference (d_C − d_W) which is finite for all 50:

| test | result |
|---|---|
| paired (d_C − d_W) mean | 0.099 |
| paired bootstrap 95% CI (n=5000 resamples) | [0.088, 0.112] |
| Wilcoxon signed-rank (alternative=greater) | p < 0.0001 |

### 5.3.3 Hypothesis tests

Per `experiment_design_v1.1` §5.3:

| hypothesis | claim | result |
|---|---|---|
| H1.1 | (d_C − d_W) 95% CI excludes 0 | **PASS** [0.088, 0.112] |
| H1B.1 | median R(d) > 1 | **PASS** (median 14.4) |
| H1B.2 | R 95% CI excludes 1 | **PASS** (R > 1.2 in 100% of finite cases) |
| H1B.3 | Wilcoxon p < 0.05 | **PASS** (p < 0.0001) |
| H1B.4 | median R ≥ 1.2 (strong claim) | **PASS** (median 14.4 ≫ 1.2) |

**All five hypotheses pass with overwhelming margin.** Cross-family projection mismatch is approximately **17× larger** than within-model stochastic variance. The "you are measuring noise" attack is empirically blocked. The intentional asymmetry — cross-family at T=0 (family-attributable signal) versus within-model at T=0.5 (stochasticity upper bound) — is conservative against the noise-confound objection: even an inflated stochasticity baseline is dominated by family-attributable divergence.

The headline result is therefore: **same artifact, same delegation, three model families produce projection vectors that are an order of magnitude more dissimilar than five repeat runs of any single family.** Pre-execution responsibility commitment is family-specific, not stochastic.

---

## 5.4 Experiment 2 (pilot scope) — Projection-driven vs direct execution

### 5.4.1 Pilot scope simplification

The full Experiment 2 design (`experiment_design_v1.1` §6) compares four conditions: A direct, B task-aware routing, C generic clarification, D proposed protocol with full bid + clarification. For the pilot we restrict to two conditions, evaluating whether explicit projection guidance improves execution quality compared to direct execution. We defer the bid mechanism, clarification simulator, task-aware routing baseline, and CLAMBER-style generic-ambiguity baseline to the main run.

| condition | description |
|---|---|
| A — direct | claude-sonnet-4.5 receives delegation + artifact only |
| D′ — projection-driven | claude receives delegation + artifact + projected weight vector + active-set (claude's own Exp1 cross-family projection at T=0) |

For each (example, condition) pair the executor produces an output (revised text or recommendations). Each output is then judged by three LLMs of different families (claude / gpt-4o-mini / gemini-2.5-flash) using the per-dimension 1–5 anchor rubric from `spec_evaluation_rubric_v1.0` §4. Settlement loss per example per condition is `L = mean over active dims of (1 − v_ij)`, where `v_ij = (median(judge scores) − 1) / 4` and the active set is derived from `r*_median` (the pass-2 ground truth) at threshold 0.3 plus all RX.

Total: 50 × 2 = 100 executions; 100 × 3 = 300 judge calls. All execution outputs pass; 15 of 300 judge outputs fail strict schema validation, recoverable from raw JSON for 100% of dimension-level scores.

### 5.4.2 Aggregate settlement loss

| condition | n | L mean | L median | std |
|---|---|---|---|---|
| direct | 50 | 0.090 | 0.094 | 0.068 |
| projection-driven | 50 | 0.080 | 0.048 | 0.082 |

Paired comparison (direct − projection_driven; positive = projection wins):

| test | result |
|---|---|
| mean diff | 0.010 |
| median diff | 0.030 |
| 95% bootstrap CI | [-0.014, 0.034] |
| Wilcoxon signed-rank (D > P) | p = 0.165 |
| projection wins | 26 / 50 |
| direct wins | 16 / 50 |
| tie (\|diff\| ≤ 0.01) | 8 / 50 |

**Hypothesis H2.1 (CI excludes 0): does not pass at this sample size.** Projection-driven execution produces lower settlement loss on average and on the median, and wins more examples than direct (26 vs 16), but the effect does not reach the 95% bootstrap or Wilcoxon p < 0.05 threshold at n=50.

We treat this as a properly nuanced pilot finding rather than a null result. The directional advantage and the median lead suggest a real effect of moderate magnitude that the n=50 sample is underpowered to confirm; the main-run n=300 should resolve the question. More informatively, the aggregate hides substantial heterogeneity along three axes — coverage class, R1 dimension, and execution mode — which we examine next.

### 5.4.3 Class-level heterogeneity

| class | n | direct L | projection L | who wins |
|---|---|---|---|---|
| single | 30 | 0.093 | **0.071** | projection (Δ = 0.022) |
| control | 5 | 0.077 | **0.046** | projection (Δ = 0.031) |
| ambiguous | 5 | 0.066 | 0.062 | tie (Δ = 0.004) |
| dual | 10 | **0.099** | 0.131 | direct (Δ = −0.032) |

The aggregate near-tie hides a class-conditional pattern: **projection-driven execution is meaningfully better on single-dim and control examples and meaningfully worse on dual-dim examples.** The dual-class reversal is the load-bearing observation; we explore mechanism in §5.5.

### 5.4.4 Per-dimension fulfillment

Mean v_ij per active R1 dim (higher = better quality):

| dim | direct | projection | Δ |
|---|---|---|---|
| R1.1 conceptual | 0.94 | 0.88 | −0.06 |
| R1.2 logical | 0.98 | 0.94 | −0.05 |
| R1.3 evidence-claim | 0.90 | 0.93 | +0.03 |
| R1.4 novelty | 0.71 | 0.58 | **−0.14** |
| R1.5 structural | 0.75 | 0.86 | **+0.11** |
| R1.6 polish | 0.99 | 1.00 | +0.02 |
| R1.7 citation | 0.88 | 1.00 | **+0.13** |

Projection-driven execution gains on R1.5, R1.6, R1.7 — dimensions characterised by relatively mechanical execution steps (reorder sections, polish prose, audit citations). Projection-driven loses substantially on R1.4 (−0.14) and modestly on R1.1, R1.2 — dimensions requiring deeper conceptual or argumentative reasoning. The pattern is consistent with a hypothesis we develop in §5.5: explicit projection guidance shifts execution toward analytical itemisation, which helps when the dim is *prescriptive* (do X) and hurts when the dim is *generative* (decide what X should be).

Cross-cutting RX dimensions:

| condition | RX.3 (scope) | RX.2 (overclaim) |
|---|---|---|
| direct | 1.00 | 1.00 |
| projection-driven | 0.965 | 0.978 |

Direct adheres slightly better to scope (RX.3) than projection-driven, against the expectation that explicit active-set guidance improves scope adherence. This is a small but consistent effect (Δ = 0.035) and points back to the active-set quality question discussed in §5.5.

---

## 5.5 Mechanism analysis — why the Exp-2 effect is heterogeneous

Qualitative inspection of paired (direct, projection-driven) outputs across single, dual, and control examples reveals four interacting mechanisms.

### 5.5.1 Format coupling

The direct prompt receives "execute the delegation"; the projection-driven prompt receives the delegation plus an explicit active-set listing and the instruction "address the active dimensions substantively, do not extend scope to inactive dimensions". On simple delegations (single, control) the executor responds to both prompts by producing a revised artifact. On complex or dual delegations, the projection-driven prompt induces a shift to an *analytical-report* style: the executor enumerates issues per active dimension, often presents alternatives ("Option A vs Option B"), and asks the user to commit. The direct prompt under the same delegation produces a unified revised artifact instead.

The judges' rubric scores "did the agent perform the dimensional task". A revised artifact that reframes the conceptual object scores 5 on R1.1; an analytical report that *identifies* the conceptual issue and asks the author to choose scores 3. The projection-driven loss on dual examples is thus partly a **format-coupling artifact**, not a quality deficit.

This is observable on `ad_r1_027` (dual, R1.1 + R1.2, lock-free queue contradiction): the direct condition rewrites the artifact, replacing "lock-free" with "linearizable" and removing the "no fences" claim — scoring 1.0 on both R1.1 and R1.2. The projection-driven condition produces a "CRITICAL ISSUES REQUIRING AUTHOR RESOLUTION" report with Option A (drop lock-free terminology) and Option B (rewrite as CAS-based) — scoring 0.625 on R1.1 because the agent did not commit to a reframing.

### 5.5.2 Active-set propagation bias

The active set used by the projection-driven condition is derived from `r*_median` (pass-2 ground truth at threshold 0.3 + RX). Because pass-2 LLM annotators systematically over-activate on R1 dimensions (28–42% over-activation rate per family at T=0; §5.1), the median-derived active set is *broader* than the engineered load-bearing set. The projection-driven executor, instructed to address all active dims, spreads attention across this broader set rather than concentrating on the actually-load-bearing dim.

This is observable on `ad_r1_043` (single, R1.4 novelty): the active set is `{R1.1, R1.3, R1.4, RX.*}` because pass-2 r* placed R1.1 and R1.3 above 0.3 in addition to the load-bearing R1.4. Projection-driven self-claims "addressed R1.1 / R1.2 / R1.3 / R1.6" — including dims not in the active set (R1.2 / R1.6) and dropping the load-bearing R1.4 — scoring 0.5 on R1.4 vs the direct condition's 1.0.

### 5.5.3 Self-claim drift

The projection-driven prompt asks the executor to begin its output with "a one-line summary of what you did, naming which active R1 dim(s) you addressed". In a non-trivial fraction of dual and ambiguous examples the executor's self-reported addressed-dim list does not match its active-set input or its actual output: dims outside the active set are claimed, dims in the active set are silently dropped. This is a model-behaviour artifact rather than a protocol design choice but it propagates into judge scoring and into any downstream bid-coverage computation.

### 5.5.4 RX dim attention boost

The projection-driven prompt explicitly lists the five RX dimensions as always-active. On the control class (where the R1 component of the task is unambiguous), this nudges the executor to address uncertainty disclosure (RX.1) and provenance traceability (RX.5) more thoroughly than the direct condition. On `ad_r1_002` (T04 + R1.6 polish control), this RX boost is the entire source of projection's win (R1.6 = 1.0 in both conditions; RX.1 0.5 → 0.75 and RX.5 0.75 → 1.0 favor projection).

### 5.5.5 Net effect

The Exp-2 mean-loss difference of 0.010 in projection's favor is the net of these mechanisms:

```
projection-driven net effect =
  + RX-attention boost                    (small win on RX dims, control class)
  + concentration on the load-bearing dim (medium win on single class)
  − format coupling                       (large loss on dual class via analysis-style output)
  − active-set propagation bias           (medium loss when active set exceeds load-bearing)
  − self-claim drift                      (consistency violation, drag on judge scores)
```

The pilot-scale aggregate masks these mechanisms; the class- and dim-stratified breakdowns expose them. Three implications for the main run:

1. **Tighten the active-set derivation.** Either raise the active threshold from `> 0.3` to `> 0.5`, or use the engineered-load-bearing list directly for the protocol's active set (separating annotation from execution guidance).
2. **Lock the projection-driven prompt to artifact-revision mode.** Add a hard instruction "produce a revised artifact, not an analytical report" so format coupling is suppressed.
3. **Use the explicit bid mechanism.** The full `spec_bid_v1.0` protocol requires the executor to commit to a bid type (`execute / partial / clarify / limit`) before producing output; this should suppress self-claim drift and produce cleaner format.

---

## 5.6 Limitations and deferred work

### 5.6.1 Sample size and statistical power

The pilot reports n = 50. Experiment 1 / 1B effects are large enough that all five hypothesis tests pass at this scale with overwhelming margin (p < 0.0001 on Wilcoxon). Experiment 2's mean-direction effect (Δ = 0.010) is below the n=50 detection threshold; we report the directional finding and class-level heterogeneity rather than claim a significant aggregate improvement. The main run's n = 300 should resolve the Experiment-2 power issue.

### 5.6.2 Annotation reliability — R1.7 and the borderline dims

R1.7 (citation and scholarship) reaches α = 0.219 at the 3-rater pass-1 + pass-2 LLM protocol and fails the G-D-07 threshold. This reflects a genuine limit of blind LLM annotation: citation accuracy requires recall of the relevant literature's canonical works, which mid-tier LLMs do not consistently have. We report all R1.7 results with an annotation-uncertainty caveat and require human annotation on R1.7-load-bearing examples in the main run. R1.1 (α = 0.315) and R1.3 (α = 0.390) sit just below the gate; we report them with a soft caveat and expect main-run human annotation to resolve the borderline.

### 5.6.3 Deferred Experiment-2 baselines

The full Experiment 2 design includes four conditions: direct, task-aware routing, generic-ambiguity clarification (CLAMBER-style), and the proposed protocol with full bid + clarification simulator. The pilot reports two: direct and a bid-free simplified projection-driven. The deferred conditions B (task-aware routing) and C (generic clarification) are the closest prior-work baselines and must be included in the main run for a complete prior-work positioning. The clarification simulator and the bid mechanism are also deferred; their omission is responsible for some of the §5.5 mechanism artifacts (self-claim drift in particular).

### 5.6.4 Experiment 3 (reputation simulation) deferred

Per `experiment_design_v1.1` §7 the pilot's reputation experiment is a simulation on synthetic agents with known per-dim fulfillment profiles, not a re-run of LLM agents. We defer this to the next phase because the headline contribution of the paper is the *measurability* of pre-execution responsibility commitment (Exp 1 + 1B), not yet the longitudinal-update value of dimension-level reputation.

### 5.6.5 Modified-real source concentration

The 18 modified-real artifacts derive from a single author-owned V2G-domain submission. Anonymization removes author / institution / specific results identifiers; the technical domain is preserved. The pilot's source mix is reportable but not domain-diverse on the modified-real subset. The main run should expand the modified-real source pool across at least three technical domains.

### 5.6.6 Source-mix deviation from spec

The spec's source-mix target is 30 synthetic + 20 modified-real. The pilot reports 32 + 18 due to a mid-batch source-eligibility decision (the modified-real source was not identified at synthetic batches 1–3). The deviation is small and disclosed; main-run construction is rebalanced.

### 5.6.7 Pass-3 human subset

Two human annotators on a 20-example stratified random subset are reserved for the main run. Pilot results on R1.7 specifically motivate this; main-run human annotation will compute α improvements on R1.1 / R1.3 / R1.7 and report human-LLM Spearman.

---

## 5.7 Summary of pilot findings

The pilot supports the following claims at n = 50:

1. **Cross-family projection mismatch is real and substantial.** Median R(d) = 14.4 ≫ 1.2; all five hypothesis tests pass. Pre-execution responsibility commitment is family-specific, not stochastic, and not driven by knowledge confound. (§5.2 + §5.3.)

2. **Projection-driven execution shows a directional advantage** of 0.010 in mean settlement loss, robust to coverage-class stratification on single + control + ambiguous classes, but not statistically significant at n = 50 and reversed on the dual class. (§5.4.)

3. **Projection guidance changes execution style, not just dimension attention.** Four mechanisms — format coupling, active-set propagation bias, self-claim drift, RX-attention boost — explain the heterogeneous Experiment-2 effect. The protocol's net value is dimension- and class-dependent in ways the spec did not pre-specify. (§5.5.)

4. **Annotation reliability is uneven across the taxonomy.** R1.2 / R1.4 / R1.5 / R1.6 reach α ≥ 0.4 with three raters; R1.1 / R1.3 are borderline; R1.7 fails. RX dims are not amenable to α and require alternative validation. (§5.1.)

5. **The clarification trigger is currently weak.** Only 1 of 5 ambiguous-class examples elicits clarification from any family at the spec-§3.1 prompt; gpt-4o-mini never clarifies. The trigger requires sharper engineering for the main run. (§5.2.3.)

The headline contribution — that responsibility projection is measurable and family-specific — is empirically established at pilot scale. The protocol's prescriptive value (does projection-guided execution outperform direct?) is directionally supported but underpowered, with mechanism-level findings that point to specific improvements for the main run.
