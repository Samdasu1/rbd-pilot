# Paper Master v1.3
## Sync Patch on `paper_master_v1.2` — Theory Restructure and Three-Condition Pilot

> Status: paper-scope sync on v1.2, propagating `formalization_v1.2`, `spec_models_v1.0` (iter 2), and `concept_and_positioning_v1.1`.
> Role: re-states pilot MVP scope, claim compression, §VI Limitations expansion, and §VII Discussion frame under the post-review-feedback design. **Iteration 2 (2026-05-04 evening, post-codex review)** tightens C3 demotion, §VII tone, causal language on M1–M4, and Entry 3/4 of §VI.
> Companion files:
> - `paper_master_v1.2.md` (parent)
> - **`formalization_v1.2.md` (iteration 2 — theoretical decoupling, 3-layer loss, mechanism diagnostics)**
> - **`spec_models_v1.0.md` (iteration 2 — citation-backed conceptual frame, 3-dim Stage 1 anchor, 3-condition cost update)**
> - **`concept_and_positioning_v1.1.md` (19 refs total — P0 ×4 + P1 ×4 + P2 ×2 added; 9 subsections; contrastive framing)**
> - `experiment_design_v1.2.md` (operational spec; pending sync to absorb 3-condition split)
> - `review_feedback_v1_0.md` / `1st_review_1.txt` (motivation)

---

## 0. What changed from v1.2

The 12-dim taxonomy `J_v1.1` and the dataset (50 examples) are **unchanged**. The **thesis structure, loss decomposition, condition set, mechanism formalization, and reference base** are restructured in response to `review_feedback_v1_0` Part I+II + `1st_review_1.txt`. v1.3 changes both the *interpretation* and the *measurement* layer (the prior v1.2 spec required 2 conditions × R1.7-only human anchor; v1.3 adds a third condition `direct_with_claim` for `L_calibration` measurement and *planned* to extend the human anchor to 3 dims — that planned extension was **superseded 2026-05-07** by a narrower closure, see §VI #4 + CHANGELOG 2026-05-07; the actual scope is R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation, no R1.4 human evidence). Calling this "interpretation only" would still understate the change.

| element | v1.2 | v1.3 |
|---|---|---|
| Thesis structure | single coupled claim | **two propositions P1 (measurability, strong) + P2 (actionability, suggestive)** |
| Settlement loss | single `L_i` | **3-layer**: `L_projection` / `L_calibration` (+ `L_overclaim`) / `L_settlement^R1` (+ `L_settlement^RX`) |
| Exp 2 conditions | direct + projection_driven | **3**: direct_naive (P2 settlement baseline) + direct_with_claim (L_calibration measurement, paired-priming ablation) + projection_driven (treatment) |
| Stage 1 human anchor | R1.7 only (~$100) | **planned 3-dim Prolific extension (R1.1 + R1.4 + R1.7, ~$300, 270 ratings) was superseded 2026-05-07** by R1.1 Prolific salvage (3 validated raters, ~£100 spent) + R1.7 v2 author/peer co-annotation. The §VI#4 entry now reports a methodological boundary-condition finding instead of breadth validation. See CHANGELOG 2026-05-07 + `human_annotation/rater_protocol_v1.md`. |
| C3 (reputation+settlement) | listed as 4 main claims | **demoted to conditional simulation-only future-work** |
| Mechanism analysis | "weakness confession" framing | **finding**: "naive projection injection is insufficient; protocol-design space has 4 identifiable mechanisms" |
| Mechanism thresholds | hard pass-fail acceptance gates | **diagnostic only** (continuous effect sizes + CI as primary; binary classifications post-hoc) |
| §VI Limitations | 4 entries | **5** (adds Plank non-transferability to LLM-only annotation) |
| §VII Discussion | not yet structured | **1-paragraph note + follow-up signpost** for the LLM-inherits-human-structures meta-claim |
| Reference count | 9 (v1.0 cluster) | **19** total (10 added; P0 ×4 + P1 ×4 + P2 ×2; cite set per `concept_and_positioning_v1.1` §6 page-budget table — Standard P0+P1 = 17 with Stureborg promoted) |

What does **not** change:
- Dataset (50 examples; 12-dim closed taxonomy `J_v1.1`).
- Acceptance gates inherited from `formalization_v1.1` §6 (projection JSON validity, |J*(d)| range, **median** R(d) > 1.2, etc.). v1.3 adds *diagnostic checks* (not gates) per `formalization_v1.2` §9.
- ~~Stage 1 protocol (5 humans, Prolific). Only the dim coverage extends.~~ *Superseded 2026-05-07*: Stage 1 protocol is now R1.1 Prolific salvage (3 validated raters) + R1.7 v2 author/peer co-annotation; no R1.4 human evidence. See §VI #4 + CHANGELOG 2026-05-07.
- §V Mechanism analysis structure (4 mechanisms M1–M4). Reframed as finding, but the same four.

---

## 1. Replaces v1.2 §0 — Two-proposition thesis

The pilot evidence supports two distinct claims with asymmetric strength. v1.2's coupled framing exposed a single reject vector ("Exp 2 CI includes 0; headline claim and measurement disagree"). v1.3 decouples explicitly:

```text
P1 (measurability)
   The projection commitment r = π(d, u, t, a) is computable, and
   Δ(r, r*) is family-attributable: holding (d, u, t) fixed and varying
   a across model families, cross-family projection divergence exceeds
   within-model stochastic variance.

   Theoretical inequality (formal):       R(d) = d_C / d_W > 1
   Pilot acceptance criterion (operational, inherited from
                  formalization_v1.1 §6 G-D):   R(d) median > 1.2

   Evidence: Experiment 1 + 1B.
   Strength: STRONG (pilot v1: cross-family ~17× within-model).

P2 (actionability — tested, not claimed)
   We test whether knowledge of the projection commitment can be used to
   reduce per-dim settlement loss — through projection-driven execution
   compared to a naive baseline.

   Evidence: Experiment 2 (3 conditions: direct_naive, direct_with_claim,
   projection_driven).
   Strength: SUGGESTIVE / INCONCLUSIVE. Pilot v1 found CI on Δ(L_settlement)
   includes 0; under specific protocol designs there may be reduction, but
   the paper does not claim general improvement.
   Mechanism analysis: §V identifies four protocol-design factors (M1–M4)
   characterizing the gap between measurement (P1) and execution improvement
   (P2), formalized as continuous diagnostic indicators in
   formalization_v1.2 §2.5. M1–M4 describe the gap; we do NOT claim
   mediation in the causal-inference sense.
```

The paper's headline contribution is jointly:
1. **A measurement instrument** for P1 (responsibility projection commitment, Δ(r, r*), cross-family > within-model).
2. **A characterization of the protocol-design space** required to translate measurability into actionability — i.e., why naive projection injection is insufficient.

The mechanism analysis is positioned as a **finding** ("we identify 4 protocol-design factors") rather than a confession ("our protocol failed"). The paper claims a measurement contribution + a mechanism-characterization contribution.

---

## 2. Replaces v1.2 §9 — Minimum viable paper scope

```text
- 1 task category (R1)                      — paper-research delegation
- 12 responsibility dimensions (J_v1.1)     — unchanged closed taxonomy
- 50 controlled examples                    — spec_dataset_v1.0
- author + 3 LLM annotators per example     — mid-tier open (Ollama)
- Stage 1 human anchor (actual scope, post 2026-05-07 closure) — R1.1 Prolific salvage (3 validated raters, ~54 ratings) + R1.7 v2 author + peer co-annotation (~18 ratings). No R1.4 human evidence. See §VI #4.
- 3 frontier projection families            — gpt-5, gemini-2.5-pro, grok-4
- 12-panel LLM judges (tier-stratified α)   — Anthropic-excluded
- Exp 2: 3 conditions × 50 examples         — direct_naive, direct_with_claim, projection_driven
- 3-layer loss reporting                    — L_projection, L_calibration, L_settlement^R1
- 4 mechanism diagnostic indicators (M1–M4) — continuous + binary (post-hoc)
- 4 baselines (direct, task-aware routing, generic clarification, generate-then-select)
- C3 (multi-round reputation update mechanism) — simulation-only, future-work for real-agent confirmation. NOTE: settlement *loss* (`L_settlement^R1`) is an Exp 2 empirical metric — kept as headline P2 reporting; only the *reputation update protocol* is demoted.
```

The paper claims **scoped, not production-ready**. **Two main contributions** (C3 demoted to conditional future-work, not a co-equal contribution):

- **C1 (formal)**: closed responsibility taxonomy + 3-layer loss decomposition + projection-mismatch metric.
- **C2 (empirical)**: P1 measurability (strong) + 4-mechanism characterization of the gap between measurement and execution improvement (suggestive + finding).

**Terminology disambiguation — important**: in this paper, "**settlement loss**" (`L_settlement^R1`, etc.) is an **empirical Exp 2 metric** measuring per-dim fulfillment ℓ_ij; this is *kept and reported as a headline P2 metric*. The "**settlement and reputation mechanism**" (C3 below) refers to the multi-round reputation-update protocol (`ρ_{i,y,j,t+1}`) that uses settlement losses as input — this is *demoted to simulation-only future-work*. The two share the word "settlement" but are different objects: one is a per-execution loss metric, the other is a multi-round protocol component. Reviewer-facing prose must keep them distinct.

**C3 (simulation-only future-work, NOT a main contribution)**: the multi-round reputation update mechanism (`ρ_{i,y,j,t+1}` per `formalization_v1.1` §10 / `formalization_v1.2` §6) is exercised in simulation only. The paper presents this as *conditional* evidence under the framing "*Conditional on dimension-level fulfillment heterogeneity, scalar reputation underperforms in simulation; empirical confirmation in real agents is future work.*" C3 supports the framework's coherence at simulation level but does not carry main-claim weight in this paper. Real-agent reputation evidence is reserved for a future paper, not promised as the next addition to *this* paper.

---

## 3. Replaces v1.2 §10 — Roadmap (current status as of 2026-05-04 evening)

```text
[done]   formalization_v1.1            (12-dim taxonomy)
[done]   spec_pi_implementation_v1.0   (projection prompt + schema)
[done]   spec_dataset_v1.0             (pilot dataset construction)
[done]   paper_master_v1.1             
[done]   experiment_design_v1.1        
[done]   spec_evaluation_rubric_v1.0   
[done]   spec_bid_v1.0                 (deferred to main run)
[done]   build pilot dataset           (50 examples, INDEX.jsonl)
[done]   pilot v1 (claude-sonnet)      (executor + 3-family judge — superseded)
[done]   spec_models_v1.0              (model panel, Anthropic-excluded — iteration 2 with citations)
[done]   experiment_design_v1.2        (sync patch on v1.1)
[done]   paper_master_v1.2             (sync patch on v1.1)
[done]   formalization_v1.2            (theory restructure — iteration 2; cf. file header)
[done]   concept_and_positioning_v1.1  (16 refs, 9 subsections)
[done]   paper_master_v1.3             (NEW — this document)

[done]   experiment_design_v1.3        (sync patch on v1.2 — absorb 3-condition split, 1800 judge calls; Stage 1 originally 270 ratings was **superseded 2026-05-07** to ~72 actual; see experiment_design_v1.3 §2.6)
[next]   data/pilot_v1.1/ cleanup      (delete v1 outputs; keep examples/, INDEX, provenance/)
[next]   scripts refactor              (load spec_models_panel.json; add Ollama + xAI clients; raw continuous metric logging per formalization_v1.2 §9.3)
[then]   pass-2 annotation v1.2        (mid-tier 3 × 50 = 150 Ollama calls)
[then]   projection v1.2               (frontier 3 × 50 = 150 API + within-model 250 API)
[then]   executor v1.2                 (Opus in Claude Code session, 50 × 3 conditions = 150 outputs)
[then]   judge v1.2                    (12-panel × 150 = 1800 calls)
[then]   stats v1.2                    (per-tier α, 3-layer loss, M1–M4 continuous, inter-dim correlation matrix)
[parallel] Stage 1 closure             (R1.1 Prolific salvage 3 validated raters + R1.7 v2 author/peer co-annotation per rater_protocol_v1; ~72 ratings actual; see experiment_design_v1.3 §2.6 — supersedes the 270-rating Prolific plan as of 2026-05-07)
[then]   draft paper_section_5_v1.1    (mechanism finding framing, weighted L_settlement^R1, M1–M4 diagnostic reporting)
[then]   convert to LaTeX (existing main.tex updated)
```

---

## 4. §VI Limitations — five entries (must appear in main.tex)

Per `spec_models_v1.0` §6 (iteration 2) + `formalization_v1.2` §7.2 / §9.2 + the construct-validity screening diagnostic (inter-dim correlation matrix promoted from future work to v1.2 deliverable). The framing throughout is "**residual despite mitigation**", not "addressed":

1. **Inherited human priors (residual)**. Even with 8 distinct vendors and Anthropic exclusion, all panel models train on overlapping web-scale human text. Cross-family agreement still partially reflects shared human priors, not external validity. Mitigation (multi-family panel) does not eliminate this. Backed by `concept_and_positioning_v1.1` §13.2.8 (Zheng / Panickssery / Stureborg).

2. **Construct validity of rubric anchors (residual; screening diagnostic provided)**. We compute and report the inter-dim correlation matrix on `r*_median` across 50 examples (R1 dims only, since RX is repositioned as cross-cutting design constraint per `formalization_v1.2` §4 and excluded from correlation analysis). Pairs with `|r| > 0.7` are flagged in §V.1 as candidates for "fronting one latent factor." This is a **screening diagnostic**, not a construct-validity validation; PCA / EFA factor decomposition remains future work. The matrix converts the limit from hidden weakness to declared limit with effect-size data, but does not resolve it.

3. **Single-executor design + Claude Code session disclosure (residual)**. Exp 2's treatment effect is bound to claude-opus-4-7 executor invoked through the Claude Code interactive session (per `spec_models_v1.0` §4.1). Specific disclosures:
   - No `temperature` override applied; provider defaults govern.
   - No per-call cost ledger; cost approximated as zero against subscription.
   - Within-conversation outputs are more correlated than independent API calls would be; phase boundaries are documented in `data/pilot_v1.1/execution/_session_log.md` (created at execution time).
   - Cross-executor (multi-family) generalization is reserved for main run.

4. **Stage 1 boundary condition: anchor specifiability and domain-expertise gating (supersedes v1.3 §VI#4 "Self-reference reduced on 3 dims")**. The v1.3 plan extended Stage 1 human anchor to R1.1 + R1.4 + R1.7 (5 raters × 3 dims × 9 examples × 2 conditions = 270 ratings, ~$300 Prolific gross) to *reduce* the *"r* is just LLM-LLM consensus"* objection. **Stage 1 did not validate r\* at the planned breadth**. It produced a methodological finding about the conditions under which human anchoring is itself specifiable, which we report here in place of the planned breadth-validation:

   *Empirical evidence (CHANGELOG 2026-05-07/08; full data in `human_annotation/recruitment/`).* (i) Prolific R1.1 pilot (9 rater attempts across sb1+sb2) yielded a 33% pass rate against quality screening (3 validated; 6 rejected for AI-assisted submissions or task-misunderstanding). Holding the same pass rate, the planned 270-rating breadth would imply roughly £550–800 gross recruitment exposure (~$700–1000 USD at the time of the pilot) rather than the planned ~$300. (ii) The author's own first pass over the R1.7 18-package form regressed from R1.7 (Citation and scholarship) to a generic intent-fit lens (mixture of R1.1 / R1.3 / R1.6 considerations) on 16/18 packages. The regression was diagnosed as **dim–data mismatch**: only 6 of 50 examples in the pilot pool contained citation events ≥1 in the artifact (regex audit on author-year patterns), while LLM-panel-derived "R1.7 load-bearing" labels assigned weight 0.9 to method/scaling examples with zero citations. (iii) A redesigned form (6 citation-rich examples × `projection_driven`, sharpened anchor with explicit citation-event count decision tree, added `event_count` field) was evaluated by **5 raters** — rater A (paper author, self-test, pkg_01 excluded due to prior consultation) + raters B, C (independent anonymized peers, pre-protocol pass: only the form-embedded anchor) + raters D, E (independent anonymized peers, post-protocol pass: received `rater_protocol_v1.md` separately and redid the same 6 packages); data and per-package detail in `human_annotation/recruitment/r17_v2_5_rater_analysis.md`. Two patterns emerge:

   *Pre-protocol (raters B, C) — generic-quality lens regression.* On the pkg_04 zero-event stress test (PINN package, agent explicitly disclaims "I did not... touch citations"), rater B scored s=4.0 with event_count=5 and rater C scored s=4.5 with event_count=2 (counting non-citation prose-cleanup or "agent retained existing citation" as events — the protocol §3 explicitly excludes both). Both peers' scores cluster at 4.0–4.5 across submitted event counts 2–6, decoupled from the anchor table. On high-density pkg_05 (anchor-correct s=5), both reach event_count 5–6 but cap their score at 4.0.

   *Post-protocol (raters D, E) — anchor-aligned mapping.* Both pass the pkg_04 zero-event stress test (event_count=0, s=1). Score-event mapping becomes monotonic: rater D's submitted counts span 0–3 with scores 1.0–4.5; rater E spans 0–4 with 1.0–5.0 and reaches s=5 on pkg_05 — the only s=5 score across all 5 raters. Both invoke protocol-specific markers in their rationales (e.g., "1. (c): 인용 오류" — rater D; "no full citations (no authors or years)" — rater E, applying the §3 borderline rule by name).

   The pre/post-protocol contrast supports — but does not inferentially validate (n=2 each group, natural-exposure not controlled) — the hypothesis that **the form-embedded anchor alone is insufficient and a separately-read protocol document appears necessary in this small pass for reliable application**. Rater A (author, pre-protocol baseline) anchors the comparison: A's event counts largely followed the taxonomy but scores were systematically conservative relative to the mechanical table (5 events → 4.0 instead of 5.0), placing A between the decoupled peer pre-protocol group and the anchor-aligned post-protocol group.

   The residual gap is **three layered specifiability constraints, not solved by rater count alone**: (a) **counting convention** at the form layer — closed by protocol-reading on most packages but unstable on cluster-as-1 cases (observed post-protocol: pkg_01 D=0 vs E=1; both followed the protocol but disagreed on its borderline rule); (b) **score-event mapping** at the form layer — closed by protocol-reading (D, E monotonic vs B, C decoupled); (c) **correctness verification** — uncoupled from form/protocol layer; judging whether a flag like "Achiam 2017 = CPO, not per-step safety" is right requires source-of-truth domain knowledge that no rater claimed. A separate form-design observation (4 of 5 raters mis-handled the `author/peer1/peer2` role dropdown — raters B, C, D, E; only rater A handled it correctly — persisting across both pre- and post-protocol groups) suggests the form-instruction layer is independent of the dim-anchor layer — useful for v2 form-control design but not load-bearing for the main finding. A trained expert panel could close (c) but only at substantially higher per-rating cost; a sharper v2 protocol could close more of (a)'s residual cluster-as-1 disagreement.

   *Implication.* The dominant scalability constraint on human anchor in our setting was not rater throughput (the v1.3 plan assumed throughput as the binding factor and budgeted accordingly) but **specification specifiability + domain-expertise gating, partially mitigated by a separately-read protocol document**. The 5-rater pre/post-protocol corroboration suggests the form-embedded anchor layer and the rater-training layer are *separable* protocol-design moves: 2 pre-protocol peers regressed to generic-quality scoring; 2 post-protocol peers achieved monotonic score-event alignment and (in one case) reached the anchor table's s=5 row. We do not claim inferential validation at n=2 per group; we report the pattern qualitatively. The paper documents the response in two artifacts: `human_annotation/rater_protocol_v1.md` (operational two-axis scoring — *Axis 1* = citation-event engagement count, applicable by any rater; *Axis 2* = per-event correctness, expert-gated and sparse) and `experiment_design_v1.3.md` §2.6 (Stage 1 actual scope = R1.1 Prolific salvage + R1.7 v2 author/peer qualitative corroboration). The v1.0 R1.7 α=0.219 result is consistent with the protocol-specifiability ceiling. R1.1 borderline (α=0.315) and R1.3 borderline (α=0.390) may exhibit related but not identical patterns; we have no direct evidence on R1.4 yet.

   *Scope of mitigation.* The entry reports: (i) what we attempted (3-dim Prolific extension), (ii) why it did not deliver breadth validation in the form proposed (specifiability + cost asymmetry under the observed Prolific pass rate), (iii) what we did instead (Stage 1 closure to author + peer qualitative corroboration on R1.7; rater_protocol_v1 as the durable artifact for future passes). The "Axis-1 engagement score" produced by rater_protocol_v1 is an *operational proxy* for the original R1.7 anchor's "audits every load-bearing citation against the source" criterion — it measures engagement, not full source verification. Remaining R1 dims (R1.2, R1.5, R1.6) carry the unmitigated form of this limit; RX dims fall outside this measurement frame entirely (per `formalization_v1.2` §4).

5. **Mechanism replication uncertainty (residual; absorbs `formalization_v1.2` §9.2 risk)**. The four mechanisms M1–M4 (§V mechanism analysis) were observed in the v1.0 pilot under a different model panel and prompt set. The v1.2 rerun under the redesigned panel + 3-condition split + V2 projection_driven prompt may produce different effect sizes for any indicator. We report v1.2 effect sizes regardless of magnitude rather than retroactively raising thresholds; the paper does not adjudicate "did the mechanism replicate?" via a binary gate. Continuous distributions and bootstrap CIs are the load-bearing reporting form. This is also relevant to the **Plank framework non-transferability** caveat: Plank 2022's "annotator disagreement is signal" is human-annotator-specific and does not transfer cleanly to LLM-only `r*` outside the 3 Stage-1-anchored dims (per `formalization_v1.2` §7.2).

These five are §VI Limitations entries. They are *not* TODO items — they are the explicit boundary of this paper's claims.

---

## 5. §VII Discussion — frame anchor for follow-up paper (1-paragraph)

`spec_models_v1.0` §1 (iteration 2) maps the three core LLM-evaluation failure modes (recursive self-reference, family-prior covariance, capability heterogeneity) to perennial human-institutional problems via citation-backed analogy:

- self-reference ↔ *Quis custodiet ipsos custodes?* (Panickssery 2024 empirical)
- family-prior covariance ↔ cartelization / regulatory capture (Zheng 2023, Stureborg 2024)
- capability heterogeneity ↔ asymmetric-information democracy (Stureborg 2024)

The deeper claim — *protocol-level governance is necessary because LLMs inherit human social-cognition structures, and scaling does not fix inherited priors* — is **deferred to a follow-up paper**. In §VII Discussion of the current paper, include only one paragraph noting the structural pattern observed and pointing to the follow-up. Do not expand §V around the meta-claim (paper scope strategy: small ripple first, theoretical depth later — per user-validated strategy).

Suggested paragraph (heuristically framed; we do not test the meta-claim in this paper):

> Our pilot encountered three failure modes of LLM-based evaluation documented in the LLM-as-judge literature: recursive self-reference (Panickssery 2024), family-prior covariance (Zheng 2023; Stureborg 2024), and capability heterogeneity (Stureborg 2024). We adopt the literature-recommended mitigations (multi-family panel, external human anchor, tier-stratified analysis). Heuristically, these failure modes suggest an analogy with persistent problems in human institutional design; we do not test that analogy here. The present paper's contribution is bounded to the projection-mismatch instrument and the mechanism characterization within the closed taxonomy. Whether the failure modes are inherited structural patterns or scaling-tractable artifacts is an empirical question we leave to follow-up work.

---

## 6. §V (Experiments) — claim and reporting compression

Per `1st_review_1.txt` §6, the paper compresses to **a P1 main effect + a P1 robustness test + a P2 mechanism finding** (reported in §V as three result clusters):

| cluster | evidence | strength | metric |
|---|---|---|---|
| **P1 main effect** — projection mismatch is family-attributable | Exp 1 (50 examples × 3 frontier projections, T=0) | STRONG | `R(d) = d_C / d_W` distribution; pilot acceptance criterion median > 1.2 |
| **P1 robustness** — cross-family ≠ within-model stochasticity | Exp 1B (gpt-5 within-model T=0.5 × 5 runs per example) | STRONG | bootstrap CI on `R(d)` excludes 1 |
| **P2 mechanism finding** — protocol design space is non-trivial | Exp 2 (3 conditions × 50 examples × 12 judges) + M1–M4 indicators | SUGGESTIVE + FINDING | continuous `\widetilde{M_1..4}` with binary post-hoc per `formalization_v1.2` §2.5; `Δ(L_settlement^R1)` between conditions with bootstrap CI |

Note: the **P1 main effect** and **P1 robustness** result clusters draw on the *same* underlying pilot run (Exp 1 + 1B); they are reported as paired result clusters because they answer two distinct objections ("does cross-family divergence exist?" and "is it just stochasticity?"), not because they are independent experiments.

C3 (settlement+reputation) is **not** in this table — per §2 above, C3 is conditional / simulation-only future-work, not a co-equal contribution.

The headline claim of P2 actionability is *not* "projection_driven beats direct" (v1.0 showed CI includes 0). It is "naive projection injection is insufficient; the gap is **characterized by** 4 protocol-design factors (M1–M4)." We use *characterized by*, not *mediated by* — M1–M4 are descriptive diagnostic indicators (per `formalization_v1.2` §2.5), not causal-mediation estimates.

**Defensive note on `L_settlement^R1` (must appear in paper §V.4)** — required by `formalization_v1.2` §2.3.1 and reproduced here so it is not lost: *"We evaluate fulfillment over the responsibility set that entered execution (active set J*(d), agent-projected), but weight each dimension by hidden-intent importance (r*_j, annotator-derived) to avoid rewarding broad but non-load-bearing active sets. The measurement target is agent-attended dimensions and the weighting reflects importance to the user; this is the deliberate design, not an inconsistency."*

---

## 7. Backward compatibility

`paper_master_v1.2` remains the canonical reference for the v1.2 model-panel sync. v1.3 **supersedes some measurement and interpretation commitments while preserving the dataset and 12-dim taxonomy `J_v1.1`** — it does not strictly extend, since RX.2 anchor scoring is dropped and the 2-condition Exp 2 design is replaced by a 3-condition design.

v1.3 changes **both the measurement layer and the interpretation layer**:
- *Measurement layer changes*: adds `direct_with_claim` condition (50 more executor calls, 600 more judge calls); **planned to extend** Stage 1 human anchor from R1.7-only to R1.1 + R1.4 + R1.7 (270 ratings vs prior 18), but that extension was **superseded 2026-05-07** by a narrower closure (R1.1 Prolific salvage + R1.7 v2 author/peer co-annotation per `human_annotation/rater_protocol_v1.md`; no R1.4 human evidence) — see §VI #4 for the boundary-condition finding; drops RX.2 from anchor-based judge scoring (operationalized via `L_overclaim` instead — per `formalization_v1.2` §2.2.2 and §4).
- *Interpretation layer changes*: 3-layer loss decomposition; M1–M4 reframed from acceptance gates to continuous diagnostic indicators (`formalization_v1.2` §9 supersedes the earlier gate wording in §2.5 binary classification); `L_settlement` split into R1 (headline) / RX (constraint) / all (appendix).

What is **preserved** from v1.2: dataset (50 examples, INDEX.jsonl, provenance/), 12-dim taxonomy `J_v1.1`, score-anchor format at s ∈ {1,3,5} for the 11 dims still anchor-scored (R1.1–R1.7 + RX.1, RX.3, RX.4, RX.5), Anthropic-exclusion principle, tier-stratified pyramid panel structure.

`paper_section_5_draft_v1.0` STALE marker remains; v1.1 of that draft will be written under `paper_master_v1.3` framing (claim compression, mechanism finding, weighted `L_settlement^R1` headline with defensive note from §6 above; appendix to include uniform-R1 and fixed-hidden-intent-support ablations addressing the active-set fairness concern raised in codex review iteration 2 — the agent-projected `J*(d)` denominator gives projection_driven a wider responsibility surface than direct_naive, which the headline metric does not adjust for; ablations bound the magnitude of this effect).
