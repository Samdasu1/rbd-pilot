# Concept and Positioning v1.1
## Sync Patch on `concept_and_positioning_v1.0` — Reference Integration and Related-Work Restructure

> Status: sync patch on v1.0, integrating 4 P0 + 4 P1 + 2 P2 references from `additional_prior_work_v1_0` (Stureborg promoted P2→P1 for consistency with formalization_v1.2 headline use) and applying the contrastive-framing discipline recommended in `review_feedback_v1_0` Part I §3 and `1st_review_1.txt` §6.
> Role: extends v1.0's 9-paper related-work cluster to **19 references** total (10 added) organized into 9 subsections (was 7). Sharpens contrastive framing — every reference is positioned by *what differs in our measurement object*, not by what overlaps.
> Companion files:
> - `concept_and_positioning_v1.0.md` (parent — 9 references, §1–§15)
> - `additional_prior_work_v1_0.md` (10-reference extension proposal)
> - `review_feedback_v1_0.md` (contrastive-framing recommendation)
> - `paper_master_v1.3.md` (forthcoming — Related Work section reflects this restructure)

---

## 0. What changed from v1.0

| element | v1.0 | v1.1 |
|---|---|---|
| Reference count | 9 | **19** total (v1.0 9 + 10 added). Of the 10 added: P0 ×4 (Zheng, FLASK, Plank, Contract Net), P1 ×4 (Panickssery, InFoBench, MetaGPT, **Stureborg promoted from P2** for consistency with formalization_v1.2 headline use), P2 ×2 (Prometheus 2, Aliannejadi) |
| Related-work subsections (§13/§2.x) | 7 | **9** (adds §2.8 LLM-judge bias, §2.9 Decomposed evaluation, §2.10 Annotator disagreement) |
| Framing discipline | mixed (some "close to ours" prose, some contrastive) | **strictly contrastive** — every adjacent work is positioned by what its measurement object is, and how ours differs |
| Citation priority signal | implicit | explicit P0/P1/P2 (per `additional_prior_work_v1_0` §12) — paper writer can compress to P0 only if page budget forces |
| Reference 8/Aliannejadi (ClariQ) | not in v1.0 | added to §2.2 alongside CLAMBER as historical anchor for cost-sensitive clarification |

What does **not** change:
- §0 core repositioning (the paper's central object is "responsibility projection", not "task type matching" or "ambiguity recognition").
- §1 why "responsibility projection" is the right object.
- §11–§14 final conceptual map / gap statement / terms-to-avoid — all preserved.
- §15 final recommendation.

The 7 subsections that existed in v1.0 (§13.2.1–§13.2.7) are retained with text-level edits where contrastive framing was loose; the 3 new subsections (§13.2.8–§13.2.10) are additions.

---

## 1. Why this patch exists

`review_feedback_v1_0` Part I §3 (SA-3, prior-work positioning) flagged that v1.0's CLAMBER differentiation was conceptually clean but operationally hard to distinguish at measurement level. Two consequences:

1. The 9 references in v1.0 cover well the *adjacent work being differentiated against*, but four important neighbors are missing — the LLM-as-judge bias literature, the decomposed-evaluation paradigm, the annotator-disagreement / construct-validity literature, and the bidding-mechanism root (Contract Net). Without these, several v1.2 design decisions read as "our choices" rather than as "literature-recommended choices."

2. `1st_review_1.txt` §6 recommends related work be **contrastive only**: "routing, ambiguity clarification, underspecification, MAS failure taxonomy, generate-then-select와의 차이를 '측정 객체가 다르다'로 밀어야 합니다." v1.0's prose is already mostly contrastive but loose in places (some sections describe overlap before differentiation). v1.1 tightens this.

The 10 added references are not new conceptual territory — they are evidentiary backing for design decisions the v1.2 doc set has already made. Without them, those decisions appear as the paper's invention; with them, they are recognizable instances of established practice.

---

## 2. The 10 added references (compact)

Full discussion of each is in `additional_prior_work_v1_0` §1–§10. Compact summary here:

### A. LLM-as-judge bias (refs 1, 2, 3 — applied in §13.2.8)

- **Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.** NeurIPS 2023. Standard reference for LLM-judge bias modes. **P0.**
- **Panickssery et al. (2024). LLM Evaluators Recognize and Favor Their Own Generations.** Empirical demonstration of self-preference. **P1.**
- **Stureborg et al. (2024). Large Language Models are Inconsistent and Biased Evaluators.** Shows residual bias even in multi-judge panels; recommends tier-stratified analysis. **P2 (but used as headline citation in `formalization_v1.2` §2.1 — promote to P1 here for consistency).**

### B. Decomposed / rubric-based evaluation (refs 4, 5, 7 — applied in §13.2.9)

- **Ye et al. (2024). FLASK.** ICLR 2024. Closed 12-skill taxonomy for LLM alignment. **P0** — closest paradigm precedent for `J_v1.1`.
- **Qin et al. (2024). InFoBench.** Per-requirement instruction-following decomposition. **P1.**
- **Kim et al. (2024). Prometheus 2.** Open-source rubric-based judge model. **P2.**

### C. Annotator disagreement / construct validity (ref 6 — applied in §13.2.10)

- **Plank, B. (2022). The 'Problem' of Human Label Variation.** EMNLP 2022. Argues annotator disagreement is signal not noise (for **human** annotators). **P0.** Note: per `formalization_v1.2` §7.2, Plank's framework does not transfer cleanly to LLM-only annotator panels; usage here is for the *human* annotator part of `r*` (Stage 1 anchor on R1.1, R1.4, R1.7) and as future-work pointer for distributional `r*`.

### D. Bidding mechanism (ref 9 — applied in §13.2.7 extended)

- **Smith (1980). The Contract Net Protocol.** IEEE Transactions on Computers. The 1980 origin of bidding-based task allocation. **P0.** Historical anchor for `spec_bid_v1.0`'s announce → bid → award → execute → result cycle.

### E. Role-based MAS (ref 10 — applied in §13.2.6 extended OR new §13.2.11)

- **Hong et al. (2024). MetaGPT.** ICLR 2024. Role-based LLM MAS architecture with SOPs. **P1.** Justifies the role index `y` in `ρ_{i,y,j,t}`.

### F. Clarification root (ref 8 — applied in §13.2.2 extended)

- **Aliannejadi et al. (2019). Asking Clarifying Questions in Open-Domain Information-Seeking Conversations.** SIGIR 2019. + ClariQ dataset (2021). IR-side root of clarification literature, predating CLAMBER. **P2.**

---

## 3. Updated related-work section skeleton (replaces v1.0 §13)

Each subsection's *measurement object* (what it's measuring) is stated up-front, and our differentiation is given as a contrast on the object — not on overlap.

### §13.2.1 Task-aware delegation and routing — unchanged from v1.0

*Their object*: best-model-for-task selection.
*Our object*: pre-execution responsibility projection.
*Contrast sentence*: "Routing decides who executes; we decide what is being delegated to be executed."

### §13.2.2 Ambiguity and clarification (extended with ref 8)

*Their object*: information-need ambiguity in user queries (CLAMBER, ClariQ).
*Our object*: responsibility-structure ambiguity in delegation.
*Contrast sentence*: "Information-seeking clarification asks 'what does the user want to know?'; responsibility-bearing clarification asks 'which dimensions of accountability has the agent committed to?'"

Aliannejadi (2019) / ClariQ is added as historical anchor for cost-sensitive clarification — the question of *when* to clarify (not just *whether*) was already structured in IR before LLM-era CLAMBER. Our contribution is the *responsibility-projection* form of the trigger (`C^{operational}(d) = 1[D_π(d) > τ_D]`, per `formalization_v1.2` §3.1).

### §13.2.3 Underspecification in long-horizon workflows — unchanged from v1.0

*Their object*: instruction underspecification in multi-step tasks (LHAW).
*Our object*: pre-execution responsibility commitment.
*Contrast sentence*: "Their work catalogs underspecification post-hoc; we measure projection commitment ex-ante."

### §13.2.4 Uncertainty communication and calibration — unchanged from v1.0

*Their object*: per-claim confidence and metacognitive uncertainty.
*Our object*: per-dimension claim calibration `L_calibration` (per `formalization_v1.2` §2.2.1).
*Contrast sentence*: "Their object is confidence about content; ours is coverage calibration over a closed responsibility taxonomy."

### §13.2.5 Behavioral variance and reproducibility — unchanged from v1.0

*Their object*: cross-prompt / cross-temperature output variance.
*Our object*: cross-family vs within-model projection divergence (`R(d) = d_C / d_W`).
*Contrast sentence*: "Their work measures whether models are stable; we measure whether projection commitment is family-attributable above stochastic noise."

### §13.2.6 MAS failure diagnosis (folded with role-based MAS, MetaGPT)

*Their object* (MAST): post-hoc taxonomy of multi-agent failures.
*Their object* (MetaGPT): role-based MAS architecture with SOP-driven role specification.
*Our object*: pre-execution responsibility-projection mismatch as a measurable *cause* of MAS failures.
*Contrast sentence*: "Their work taxonomizes failures or specifies roles by SOP; we measure projection commitment whose mismatch with hidden intent is one named pre-execution failure mode."

MetaGPT's `(agent, role)` indexing is precedent for our `ρ_{i,y,j,t}` reputation form. Differentiation: their roles are SOP-assigned; ours emerge from responsibility projection over the closed taxonomy.

### §13.2.7 Aggregation, selection, and bidding (extended with Contract Net)

*Their object* (When Agents Disagree, generate-then-select): post-execution selection from multiple agent outputs.
*Their object* (Contract Net, FIPA): announce-bid-award-execute task allocation cycle.
*Our object*: responsibility-coverage-conditioned bidding (`b_i = (q_i, u_i, p_i, z_i)`) where the bid is structured by the responsibility taxonomy.
*Contrast sentence*: "Their bid is `(capability, cost)`; ours is `(per-dim coverage, per-dim uncertainty, price, latency)` over the closed responsibility taxonomy. The bid object is structured by responsibilities, not by capabilities alone."

### §13.2.8 LLM-as-judge bias and reliability — NEW

*Their object* (Zheng 2023): LLM-judge bias modes (position, verbosity, self-enhancement).
*Their object* (Panickssery 2024): LLM-judge self-preference for own-family outputs.
*Their object* (Stureborg 2024): residual bias and inconsistency in multi-judge panels; tier-stratified mitigation.
*Our use*: load-bearing for `spec_models_v1.0` §1's three failure modes (now citation-backed rather than analogy-backed). Justifies the 12-panel Anthropic-excluded design (Panickssery), the tier-stratified α reporting (Stureborg), and the multi-judge protocol itself (Zheng).
*Contrast sentence*: "We do not contribute new judge-bias findings; we adopt established mitigations (multi-family Anthropic-excluded panel, tier-stratified α) and report them as engineering decisions, not research contributions."

### §13.2.9 Decomposed and rubric-based evaluation — NEW

*Their object* (FLASK): closed 12-skill taxonomy for evaluating LLM outputs.
*Their object* (InFoBench): per-requirement instruction-fulfillment decomposition.
*Their object* (Prometheus 2): rubric-based judge model with per-criterion 1–5 scoring.
*Our use*: paradigm precedent for `J_v1.1` (closed 12-dim taxonomy) and `L_settlement^R1` (weighted per-dim aggregation over `J*(d)`).
*Contrast sentence*: "Their decomposition target is the *output* (what the model produced); ours is the *projection* (what the model committed to before producing). The decomposition technique is shared; the object differs."

### §13.2.10 Annotator disagreement and construct validity — NEW

*Their object* (Plank 2022): human annotator label variation as signal of perspective heterogeneity.
*Our use*: justifies the median-of-annotators aggregation for `r*` for the 3 Stage-1-anchored dims (R1.1, R1.4, R1.7) where humans contribute. Reframes low-α dimensions as candidates for "perspective-variation-inherent" rather than "rubric-failure" (paper §VI Limitations entry).
*Note*: Plank's framework was developed for human annotators. For LLM-only annotator panels (which we use for r* outside the Stage-1-anchored dims), it does not transfer cleanly — LLM-only `r*` carries the LLM-LLM-disagreement objection from `formalization_v1.2` §2.1 prerequisite paragraph. Plank serves as both supporting citation (for the human-anchored slice) and as future-work pointer (distributional `r*` over human annotators in main run).
*Contrast sentence*: "We treat annotator disagreement on the human-anchored slice as inherent perspective variation per Plank; on the LLM-only slice we acknowledge the disagreement reflects shared LLM priors rather than perspective heterogeneity, and we limit our claims accordingly."

---

## 4. Reference table (consolidated, with priority and section)

| ref | citation | priority | sec used |
|---|---|---|---|
| 1 | Zheng et al. (2023). MT-Bench / Chatbot Arena. NeurIPS. | P0 | §13.2.8 |
| 2 | Panickssery et al. (2024). LLM Evaluators Recognize and Favor Their Own Generations. | P1 | §13.2.8, `spec_models_v1.0` §1 |
| 3 | Stureborg et al. (2024). LLMs are Inconsistent and Biased Evaluators. | P1 | §13.2.8, `spec_models_v1.0` §1, §4.4, `formalization_v1.2` §2.1 |
| 4 | Ye et al. (2024). FLASK. ICLR. | P0 | §13.2.9 |
| 5 | Qin et al. (2024). InFoBench. | P1 | §13.2.9, `formalization_v1.2` §2.3 |
| 6 | Plank (2022). The 'Problem' of Human Label Variation. EMNLP. | P0 | §13.2.10, `formalization_v1.2` §VI / §10 |
| 7 | Kim et al. (2024). Prometheus 2. EMNLP. | P2 | §13.2.9 |
| 8 | Aliannejadi et al. (2019). ClariQ. SIGIR. | P2 | §13.2.2 |
| 9 | Smith (1980). Contract Net Protocol. IEEE Trans Comp. | P0 | §13.2.7 |
| 10 | Hong et al. (2024). MetaGPT. ICLR. | P1 | §13.2.6 |

P0 alone (4 refs: 1, 4, 6, 9) closes the four conceptual gaps. P0+P1 (7 refs: + 2, 3, 5, 10) gives full-strength positioning. All 10 (+ 7, 8) is the comprehensive option for journal/extended-tech-report version.

---

## 5. Carry-forward — what stays from v1.0

- **§0 Core repositioning** — the central object is responsibility projection, paper is *not* a benchmark / universal intent theory.
- **§1 Why "responsibility projection" is the right core object** — preserved verbatim.
- **§11 Final conceptual map** — preserved.
- **§12 Final gap statement** — preserved.
- **§14 Terms to avoid or use carefully** — preserved.
- **§15 Final conceptual recommendation** — preserved.

Existing differentiation prose in §2–§10 (Task-Aware Delegation, CLAMBER, LHAW, etc.) is preserved with light edits where v1.0 used "close to" framing; v1.1 tightens to "their object is X, ours is Y" pattern.

---

## 6. Page-budget compression strategy

If `paper_master_v1.3` Related Work section faces page budget (typical conference 1–1.5 pages):

| level | refs included | subsection count |
|---|---|---|
| **Compressed (P0 only)** | 1, 4, 6, 9 + v1.0's 9 = 13 | 9 subsections |
| **Standard (P0+P1, with Stureborg promoted)** | 1, 2, 3, 4, 5, 6, 9, 10 + v1.0's 9 = 17 | 9 subsections (P2 refs 7, 8 cut) |
| **Comprehensive (all)** | 10 added + v1.0's 9 = 19 | 9 subsections |

Even at P0-only, all 9 subsections are needed because the gaps are conceptual (LLM-judge bias, decomposed evaluation, annotator disagreement) not just citation-volume. Cutting subsections is not equivalent to cutting refs.

---

## 7. Carry-forward — what is deferred

- **Liao & Xiao (2023). Rethinking Model Evaluation as Narrowing the Socio-Technical Gap.** Held as backup if §13.2.10 needs sociotechnical-framing strengthening at submission grade. Currently Plank serves the role.
- **AutoGen (Wu et al. 2024).** Held as comparison citation in §13.2.6 if reviewer asks for non-MetaGPT role-based MAS comparison.
- **Inverse RL** literature (`r*` as inverse problem). Held for Discussion §VII or reviewer-response.
- **Constitutional AI / norm extraction.** Tangential to projection (per `additional_prior_work_v1_0` §13). Not cited.

---

## 8. Backward compatibility

`concept_and_positioning_v1.0` remains the canonical reference for the 9-paper cluster. v1.1 extends without retracting any v1.0 framing. Downstream docs that referenced v1.0 (e.g., older formalization revisions) are unaffected; new docs (paper_master_v1.3, §VII Discussion) reference v1.1.
