# Paper Master v1.2
## Sync Patch on `paper_master_v1.1` for Model Panel Redesign

> Status: paper-scope sync on v1.1, propagating `spec_models_v1.0` and `experiment_design_v1.2`
> Role: re-states pilot MVP scope and workflow under the new model panel
> Companion files:
> - `paper_master_v1.1.md` (parent)
> - **`spec_models_v1.0.md` (NEW — canonical model assignments)**
> - **`experiment_design_v1.2.md` (NEW — sync patch on v1.1)**
> - `formalization_v1.1.md`, `spec_dataset_v1.0`, `spec_evaluation_rubric_v1.0`, `spec_pi_implementation_v1.0`, `spec_bid_v1.0`

---

## 0. What changed from v1.1

Numeric counts in §9 (MVP scope) and roadmap in §10 (workflow). The 5 paper claims and the formal framework (J_v1.1, projection, settlement loss) are unchanged.

| element | v1.1 | v1.2 |
|---|---|---|
| LLM annotators per example (pass-2) | 2 | **3** (mid-tier open) |
| Projection model families | 3 (claude/gpt-mini/gemini-flash) | **3 frontier** (gpt-5/gemini-pro/grok-4, Anthropic-excluded) |
| LLM judges per output | 3 | **12** (3 frontier + 4 mid + 5 light, Anthropic-excluded) |
| Executor | claude-sonnet-4.5 | **claude-opus-4-7** (Claude Code session) |
| Tier analysis | scalar α | **stratified α** (α_frontier / α_mid / α_light / α_panel) |
| Human anchor | 20-example subset (deferred) | **Stage 1 batch 1 = 5 humans on R1.7, 9 examples × 2 conditions = 18 ratings** |

The §VI Limitations section gains four new entries (per `spec_models_v1.0` §6): inherited human priors, construct validity of anchors, single-executor design, rubric-layer self-reference.

---

## 1. Replaces v1.1 §9 — Minimum viable paper scope

```text
- 1 task category (R1)                    — unchanged from v1.1
- 12 responsibility dimensions (J_v1.1)   — unchanged
- 50 controlled examples                  — unchanged (spec_dataset_v1.0)
- author + 3 LLM annotators per example   — was 2; tier+vendor diversified (mid-tier open)
- Stage 1 human anchor on R1.7            — 5 external annotators, 18 ratings (Prolific)
- 3 frontier projection families          — gpt-5, gemini-2.5-pro, grok-4
- 12-panel LLM judges (tier-stratified)   — 3 frontier + 4 mid + 5 light, Anthropic-excluded
- 4 baselines (direct, task-aware routing, generic clarification, generate-then-select)
- settlement/reputation simulation on simulated agents
```

The paper claims **scoped** rather than **production-ready**. The pyramid judge structure provides a reviewer-defensible answer to "did you only test on one model family?" without spending main-run-scale budget.

---

## 2. Replaces v1.1 §10 — Roadmap (current status as of 2026-05-04)

```text
[done]   formalization_v1.1            (12-dim taxonomy)
[done]   spec_pi_implementation_v1.0   (projection prompt + schema)
[done]   spec_dataset_v1.0             (pilot dataset construction)
[done]   paper_master_v1.1             (predecessor)
[done]   experiment_design_v1.1        (sync patch on v1.0)
[done]   spec_evaluation_rubric_v1.0   (judge rubric prompt + schema)
[done]   spec_bid_v1.0                 (bid prompt + schema, deferred to main run)
[done]   build pilot dataset           (50 examples, INDEX.jsonl)
[done]   pilot v1 (claude-sonnet)      (executor + 3-family judge — superseded)
[done]   spec_models_v1.0              (NEW — model panel, Anthropic-excluded)
[done]   experiment_design_v1.2        (NEW — sync patch on v1.1)
[done]   paper_master_v1.2             (NEW — this document)

[next]   data/pilot_v1.1/ cleanup      (delete v1 outputs; keep examples/, INDEX, provenance/)
[next]   scripts refactor              (load spec_models_panel.json; add Ollama + xAI clients)
[then]   pass-2 annotation v1.2        (mid-tier 3 × 50 = 150 Ollama calls)
[then]   projection v1.2               (frontier 3 × 50 = 150 API + within-model 250 API)
[then]   executor v1.2                 (Opus in Claude Code session, 50 × 2 = 100 outputs)
[then]   judge v1.2                    (panel of 12 × 100 = 1200 calls)
[then]   stats v1.2                    (per-tier α, Spearman with author + Stage 1 humans)
[parallel] Stage 1 human eval          (5 raters on R1.7, 18 ratings via Prolific Google Form)
[then]   draft paper sections          (after v1.2 results stable + Stage 1 humans returned)
[then]   convert to LaTeX (existing main.tex updated)
```

---

## 3. §VI Limitations — new entries (must appear in main.tex)

The pilot's `spec_models_v1.0` §6 lists four residual limits not addressed by the redesign. These must appear as numbered Limitations entries in §VI of main.tex:

1. **Inherited human priors**. Even with 8 distinct vendors and Anthropic exclusion, all panel models train on overlapping web-scale human text. Cross-family agreement still partially reflects shared human priors, not external validity.
2. **Construct validity of rubric anchors**. R1.7 α was very low in v1.0 pilot (0.07), motivating the Stage 1 human anchor; this exposes a pattern where some anchors may be multi-dimensional in disguise. Construct validation is reserved for future work.
3. **Single-executor design**. Exp 2's treatment effect is bound to claude-opus-4-7 executor. Cross-executor generalization is reserved for main run.
4. **Self-reference at the rubric layer**. The rubric was authored by the paper's author (one human) and validated against LLM α. The Stage 1 5-human anchor partially mitigates this for R1.7, not for the rubric as a whole.

These are explicit Limitations entries, not unresolved bugs.

---

## 4. §VII Discussion — frame anchor for follow-up paper

`spec_models_v1.0` §1 maps the three core failure modes to perennial human-institutional problems (`Quis custodiet?`, cartelization, asymmetric-information democracy). This mapping suggests a deeper claim — *protocol-level governance is necessary because LLMs inherit human social-cognition structures, and scaling does not fix inherited priors* — but that claim requires its own evidence base. **Defer to a follow-up paper**; in this paper's §VII, include only one paragraph noting the structural pattern observed and pointing to the follow-up as future work. Do not expand §V around the meta-claim (paper scope strategy: small ripple first, theoretical depth later).

---

## 5. Backward compatibility

`paper_master_v1.1` remains the canonical reference for the pilot v1 results that were produced under the old panel; those results are recorded but not used in the v1.2 paper draft. The pilot v1 → v1.2 transition is a clean re-run of the measurement layer (`data/pilot_v1.1/{execution,judge,annotations*,projection,stats/exp*}`); the dataset (`data/pilot_v1.1/examples/`, INDEX.jsonl, provenance/) is unchanged.
