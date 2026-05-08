# Experiment Design v1.2
## Sync Patch on `experiment_design_v1.1` for Model Panel Redesign

> Status: model-panel sync on v1.1 (pilot v1.1 second iteration)
> Role: re-states v1.1 setup tables under the `spec_models_v1.0` master panel
> Companion files:
> - `experiment_design_v1.0.md` (root)
> - `experiment_design_v1.1.md` (parent — first-cycle scope narrowing)
> - **`spec_models_v1.0.md` (NEW — canonical model assignments)**
> - `formalization_v1.1.md`
> - `paper_master_v1.2.md` (companion sync)

---

## 0. What changed from v1.1

The five claims and statistical tests of v1.1 are unchanged. **Model identities and counts** changed, driven by mid-pilot discovery of three structural failure modes (recursive self-reference, family-prior covariance, capability heterogeneity — see `spec_models_v1.0` §1):

| element | v1.1 | v1.2 (this) |
|---|---|---|
| Executor (Exp 2) | claude-sonnet-4.5 (single, single-family) | **claude-opus-4-7** via Claude Code session (single, Anthropic-family) |
| Projection cross-family | 3 families: claude, gpt-4o-mini, gemini-2.5-flash | **3 frontier**: gpt-5, gemini-2.5-pro, grok-4 (Anthropic-excluded) |
| Within-model stability | claude-sonnet-4.5 | gpt-5 (one frontier representative) |
| Pass-2 LLM annotators | 2 (claude-sonnet-4.5 + gemini-2.5-flash) | **3 mid-tier open** (llama-3.1-70b, qwen-2.5-72b, mistral-large-2) |
| Judges | 3 (claude / gpt-4o-mini / gemini-2.5-flash) | **12-panel** (3 frontier + 4 mid + 5 light, Anthropic-excluded) |
| Tier analysis | n/a | **stratified α**: `α_frontier / α_mid / α_light / α_panel` |

What does **not** change:
- The 5 claims (C1–C5) and hypothesis structure.
- Dataset and acceptance gates.
- Statistical-test choices (paired bootstrap CI, Wilcoxon signed-rank, Krippendorff α).
- Stage 1 human anchor on R1.7 (5 external annotators, Prolific).

---

## 1. Why v1.2 exists

Mid-pilot discovery during human-eval recruitment (Stage 1 batch 1 setup): the v1.1 model panel had three structural problems:
1. claude executor + claude judge → self-preference bias (LLM-as-judge documented effect)
2. claude-sonnet (top) + gpt-4o-mini + gemini-flash (mini) → tier mismatch confounded "anchor ambiguity vs judge capability gap"
3. R-code echo in projection_driven outputs (`R1.x (Descriptive name)` headers) violated sanitization for blinded human eval

`spec_models_v1.0` analyzes these as instances of inherent measurement-system failure modes (mapped to `Quis custodiet?`, cartelization, asymmetric-information democracy) and prescribes protocol-level mitigations (multi-family Anthropic-excluded panel, tier stratification, external human anchor on R1.7). v1.2 of this experiment design instantiates those mitigations.

Items the redesign does **not** fix and that paper §VI must disclose: see `spec_models_v1.0` §6.

---

## 2. Updated setup tables (replaces v1.1 §4.1 and §5.1)

### 2.1 Experiment 1 — Cross-Family Projection Mismatch (replaces v1.1 §4.1)

```text
3 frontier families (gpt-5, gemini-2.5-pro, grok-4) — per spec_models_v1.0 §4.2
Per-family model: as listed in spec_models_v1.0 §2 (recorded in output JSON)
1 projection run per (model, example)
Temperature: 0.0
50 R1 examples × 3 families = 150 projection calls
Estimated cost: ~$3 (API)
```

Rationale: §V Exp 1's central claim is **cross-family** divergence at maximum capability. Mid/light tiers are not used here because lower-capability projection introduces capability noise into the divergence metric (we want to attribute divergence to family, not capability). Anthropic is excluded for executor/judge independence (`spec_models_v1.0` §2).

### 2.2 Experiment 1B — Within-Model Stochastic Baseline (replaces v1.1 §5.1)

```text
1 fixed frontier model: gpt-5 (per spec_models_v1.0 §4.2)
5 projection runs per example
Temperature: 0.5
50 R1 examples × 1 model × 5 runs = 250 projection calls
Estimated cost: ~$5 (API)
```

Rationale for choosing gpt-5 over the other two frontier: arbitrary; declared up-front to prevent post-hoc selection. gemini-pro and grok-4 are reserved for the cross-family run.

### 2.3 Pass-2 annotation (replaces v1.1 §2 hidden-intent line)

```text
3 LLM annotators (mid-tier open): llama-3.1-70b, qwen-2.5-72b, mistral-large-2
Per spec_models_v1.0 §4.3
Temperature: 0.0
50 examples × 3 annotators = 150 calls
Estimated cost: $0 (Ollama, 96GB VRAM available locally)
```

Rationale: pass-2 annotators feed `r_star_median`, used by projection-driven executor's active set. v1.1 used 2 annotators (after gpt-4o-mini was diagnosed for over-activation); v1.2 uses 3 mid-tier open annotators for distinct-vendor diversity (Meta, Alibaba, Mistral) and stronger median against single-rater outliers.

### 2.4 Experiment 2 — Executor + Judge (replaces v1.1 §6.1)

```text
Executor: claude-opus-4-7 (Claude Code interactive session)
50 examples × 2 conditions (direct, projection_driven) = 100 executor calls
Cost: subscription (no per-call billing)

Judge: 12-panel per spec_models_v1.0 §4.4
50 × 2 × 12 = 1200 judge calls
Estimated cost: API ~$8 (3 frontier) + $0 (9 Ollama)
```

The projection_driven prompt for v1.2 uses `EXEC_PROJECTION_SYSTEM_V2` (from `scripts/exp2_run.py`) which suppresses dim-code and dim-name echo in agent output — required for blinded human evaluation. v1.1 used `_V1` which echoed taxonomy in headers.

### 2.5 Tier-stratified judge analysis (NEW — extends v1.1 §6.2)

```text
α_frontier   : Krippendorff α among gpt-5, gemini-pro, grok-4
α_mid        : α among llama-3.1-70b, qwen-2.5-72b, mistral-large-2, deepseek-v3-distill-70b
α_light      : α among the 5 light models
α_panel      : α across all 12
α_with_author: panel + author
α_with_human : panel + 5 human raters (Stage 1 batch 1, R1.7 only)
```

Interpretation:
- `α_frontier > α_mid > α_light` → capability heterogeneity confirmed; reported and disclosed.
- `α_frontier ≈ α_mid ≈ α_light` → anchor reliability is robust to tier; stronger paper claim.
- `α_with_human << α_panel` → LLM panel and humans diverge; paper headlines the human anchor.

---

## 3. Cost summary (v1.2 pilot total)

| step | cost |
|---|---|
| Pass-2 (Ollama) | $0 |
| Projection cross-family (API) | ~$3 |
| Projection within-model (API) | ~$5 |
| Executor (subscription) | n/a |
| Judge frontier (API) | ~$8 |
| Judge mid+light (Ollama) | $0 |
| Stage 1 human (Prolific) | ~$100 |
| **Total** | **~$116** |

Far below v1.0 pilot's ~$200 and below v1.1's projected ~$300 (with paid frontier judges). Reduction is from Ollama hosting of 9 of 12 judges + 3 of 3 pass-2 annotators.

---

## 4. Reproducibility considerations (NEW)

Per `spec_models_v1.0` §3:

- **Closed-API models** (gpt-5, gemini-2.5-pro, grok-4): record the exact model id including version date returned in API response. Re-running on a future date may hit a different version; document in §VI.
- **Ollama models** (9 open): record the Ollama tag and the SHA256 digest of the GGUF blob. Weight-pinned reproducibility — re-running 1 year later gives identical outputs at T=0.
- **Executor (Claude Code session)**: record session start time, conversation phase boundaries (= when the executor turn for each example began), and the model id reported by `/model` at session start. No `temperature` or other knob is set; provider defaults apply. Conversation-context bleed is bounded by phase boundaries (see `spec_models_v1.0` §4.1).

Paper §VI explicitly notes: "Closed-API model versions may have version-bumped between pilot and submission. Open-weight (Ollama) judges and pass-2 annotators are weight-pinned and reproducible."

---

## 5. What `paper_master_v1.2` must reflect

The companion `paper_master_v1.2.md` updates §9 (MVP scope) and §10 (workflow) to match this v1.2 spec. Numeric counts (annotator: 2 → 3, judge: 3 → 12) propagate. Pilot acceptance gates (G-D-01..10 in `spec_dataset_v1.0` §10) are unchanged.

---

## 6. Backward compatibility with v1.0/v1.1 results

All v1.0/v1.1 pilot results (in `data/pilot_v1.1/execution/`, `judge/`, `annotations*/`, `projection/`, `stats/exp1_*`, `stats/exp2_*`) were produced under the superseded model panel and **must not be mixed** with v1.2 outputs. The migration path is a clean re-run after `data/pilot_v1.1/` cleanup; see the cleanup task in `docs/CHANGELOG.md` 2026-05-04 entry.

`spec_dataset_v1.0` (the dataset itself, 50 examples) is unchanged and re-used. Only the *measurement* — projections, executions, judges, annotations — is regenerated.
