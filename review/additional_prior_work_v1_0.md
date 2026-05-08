# Additional Prior Work v1.0
## Ten More References to Cite — Mapped to Concepts Surfaced During v1.0+v1.1+v1.2 Review

> Status: extension to `concept_and_positioning_v1.0`'s 9-paper related-work cluster
> Role: closes four gaps identified in `review_feedback_v1.0` — LLM-as-judge bias, decomposed evaluation, annotator disagreement / construct validity, bidding & role allocation
> Companion files:
> - `concept_and_positioning_v1.0.md` (parent — 9 references)
> - `review_feedback_v1.0.md` (motivates these additions)
> - `paper_master_v1.2.md` (Related Work § structure)

---

## 0. What is added vs the original 9

The 9 references in `concept_and_positioning_v1.0` cover task-aware delegation, ambiguity (CLAMBER), underspecification (LHAW), uncertainty calibration (Metacognition + Confidence Dichotomy), behavioral variance (Same Prompt + Consistency Amplifies), MAS failure (MAST), and selection bottleneck (When Agents Disagree). These are well-chosen along the original axes.

Review of v1.2 docs surfaced four conceptual gaps that the original 9 do not address:

| gap | concept | added refs |
|---|---|---|
| A | LLM-as-judge bias, self-preference, panel-level inconsistency | 1, 2, 3 |
| B | Closed-taxonomy / decomposed-skill evaluation as paradigm | 4, 5 |
| C | Annotator disagreement, label variation, construct validity | 6, 7 |
| D | Clarification root, bidding mechanism, role-based MAS | 8, 9, 10 |

---

## A. LLM-as-judge bias and self-preference (gap A)

These references justify the v1.2 12-panel / Anthropic-excluded design. `spec_models_v1.0` §1 currently invokes the three failure modes (self-reference, family-prior covariance, capability heterogeneity) by analogy alone (`Quis custodiet`, cartelization, asymmetric-information democracy) — these references provide empirical grounding.

### 1. Zheng et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023.

The standard reference for LLM-judge bias modes — position bias, verbosity bias, self-enhancement bias. Establishes the multi-judge protocol as a known mitigation.

**Where to cite in our paper:**
- §V experiments protocol — when introducing the 12-panel judge
- §VI limitations — when disclosing residual bias modes
- (new) §2.8 LLM-as-judge bias subsection in Related Work

### 2. Panickssery et al. (2024). "LLM Evaluators Recognize and Favor Their Own Generations."

Demonstrates that LLM judges identify their own outputs and rate them more favorably. **Direct empirical justification for excluding Anthropic-family models from the judge panel when the executor is `claude-opus-4-7`.**

**Where to cite:**
- `spec_models_v1.0` §1 — converts "self-reference failure mode" from analogy to citation-backed claim
- §III/IV introduction of the panel — load-bearing single citation
- §VI residual limit #4 ("self-reference at the rubric layer") — establishes that we mitigate the executor-judge axis even though we cannot mitigate the rubric-author axis

### 3. Stureborg et al. (2024). "Large Language Models are Inconsistent and Biased Evaluators."

Shows that even multi-judge panels carry residual inconsistency and bias. **Justifies the tier-stratified α analysis** (`α_frontier / α_mid / α_light / α_panel`) in `experiment_design_v1.2` §2.5 — without this reference the stratification reads as our own choice rather than a literature-recommended mitigation.

**Where to cite:**
- §V experiments — when reporting tier-stratified α
- (new) §2.8 — alongside refs 1 and 2

---

## B. Decomposed / closed-taxonomy evaluation (gap B)

These references give the J_v1.1 closed-taxonomy decision a paradigm-level home. The closure becomes "an instance of decomposed evaluation applied to paper-research delegation," not "an arbitrary 12-element list."

### 4. Ye et al. (2024). "FLASK: Fine-grained Language Model Evaluation Based on Alignment Skill Sets." ICLR 2024.

Evaluates LLM alignment along a closed 12-skill taxonomy (logical correctness, factuality, comprehension, etc.). **The structurally closest precedent to J_v1.1 in the evaluation literature.**

**Where to cite:**
- §III closed taxonomy introduction — primary precedent
- §V dataset/annotation — in describing the per-dim rubric protocol
- (new) §2.9 Decomposed evaluation subsection in Related Work
- The differentiation: FLASK evaluates outputs along skills; we evaluate *projection commitment* along responsibility dims. Parallel structure, different object.

### 5. Qin et al. (2024). "InFoBench: Evaluating Instruction Following Ability in Large Language Models."

Decomposes instructions into per-requirement constraints and scores fulfillment per constraint. **The structural precedent for `L_i = Σ_j w_j ℓ_ij` — settlement loss as per-dim aggregation.**

**Where to cite:**
- §IV settlement loss — direct precedent
- §V experiments — when justifying per-dim judge scoring as a known protocol
- (new) §2.9 alongside FLASK
- Our distinction: InFoBench's requirements come from the instruction itself; our active set J*(d) is *projected* by the agent before the instruction yields requirements. The decomposition target differs.

---

## C. Annotator disagreement and construct validity (gap C)

These references defend the r* protocol and reframe the low-α dimensions from "weakness" to "literature-recognized phenomenon."

### 6. Plank (2022). "The 'Problem' of Human Label Variation: On Ground Truth in Data, Modeling and Evaluation." EMNLP 2022.

Argues that annotator disagreement is signal, not noise — particularly for tasks where multiple valid perspectives exist. **Reframes R1.1 (α=0.315) and R1.7 (α=0.219) from "low reliability" to "the dimension carries inherent perspective variation."**

**Where to cite:**
- §V dataset/annotation reliability — when reporting per-dim α
- §VI limitations — supports keeping r*_median as a legitimate aggregation without claiming it represents a single ground truth
- (new) §2.10 Annotation reliability subsection
- Future-work pointer: r* as distribution rather than median (Plank's broader recommendation)

### 7. Kim et al. (2024). "Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models." EMNLP 2024.

Open-source rubric-based judge model. **Positions `spec_evaluation_rubric_v1.0` § 4 (per-dim 1–5 anchor scoring) as an instance of the Prometheus pattern, not an ad-hoc protocol.** Particularly relevant because Prometheus 2 explicitly endorses mid-tier open-weight judges, justifying our 4 mid + 5 light Ollama judges.

**Where to cite:**
- §V judge protocol — primary precedent for the rubric format
- `spec_models_v1.0` §4.4 — supports the choice of open mid-tier judges
- (new) §2.9 Decomposed evaluation alongside FLASK and InFoBench

---

## D. Clarification, bidding, role-based MAS (gap D)

These three close out the protocol-component axis: clarification (where the literature root is older than CLAMBER), bidding (where Contract Net is the unspoken precedent), and role-based MAS (which selection-bottleneck literature does not cover).

### 8. Aliannejadi et al. (2019). "Asking Clarifying Questions in Open-Domain Information-Seeking Conversations." SIGIR 2019. + ClariQ dataset (2021).

The IR-side root of the clarification literature, predating CLAMBER. **Useful for sharpening the CLAMBER differentiation in `concept_and_positioning_v1.0` §3** by showing that the broader information-seeking-clarification tradition exists and our work differs from both.

**Where to cite:**
- §2.2 Ambiguity and clarification subsection — alongside CLAMBER
- §IV.3 clarification trigger — historical anchor for cost-sensitive clarification

### 9. Smith (1980). "The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver." IEEE Transactions on Computers.

The 1980 origin of bidding-based task allocation, formalized later in FIPA Contract Net. **The unspoken precedent for `spec_bid_v1.0`'s announce → bid → award → execute → result cycle.**

**Where to cite:**
- §IV.2 responsibility-bearing bid — primary historical precedent
- The differentiation: Contract Net's bid is `(capability, cost)`; ours is `b_i = (q_i, u_i, p_i, z_i)` where q_i is *responsibility coverage* and u_i is per-dimension uncertainty. The bid is structured by the responsibility taxonomy, not by capability declaration alone.
- (new) §2.7 (current Aggregation/selection) extended or split to include "bidding-based allocation" with Contract Net as anchor

### 10. Hong et al. (2024). "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework." ICLR 2024.

Role-based LLM MAS architecture with Standard Operating Procedures driving role specification. (AutoGen, Wu et al. 2024, is an alternative; MetaGPT's role-explicitness is a closer fit.) **Justifies the role index `y` in `ρ_{i,y,j,t}` — responsibility-conditioned reputation is per-(agent, role, dim, task), and "role" is not an invention of this paper.**

**Where to cite:**
- §IV.4 agent selection — when introducing role-conditioned utility
- §IV.7 reputation update — when justifying the y-index
- §2.6 (current MAS failure) extended or new §2.10 Role-based MAS architectures
- The differentiation: MetaGPT assigns roles by protocol design (Architect, Engineer, etc.); our roles emerge from responsibility projection over the closed taxonomy. The role assignment object differs but the y-indexed bookkeeping is shared.

---

## 11. Recommended Related Work section restructure

Current `paper_master_v1.2` §7 has 7 subsections (2.1–2.7). Adding the 10 references suggests a 9- or 10-subsection structure:

```
2.1  Task-aware delegation and routing             — unchanged (1 paper)
2.2  Ambiguity and clarification                   — +ref 8 (Aliannejadi)
2.3  Underspecification in long-horizon workflows  — unchanged (LHAW)
2.4  Uncertainty communication and calibration     — unchanged (2 papers)
2.5  Behavioral variance and reproducibility       — unchanged (2 papers)
2.6  MAS failure diagnosis                         — unchanged (MAST)
2.7  Aggregation, selection, and bidding           — +ref 9 (Contract Net)
2.8  LLM-as-judge bias and reliability             — NEW (refs 1, 2, 3)
2.9  Decomposed and rubric-based evaluation        — NEW (refs 4, 5, 7)
2.10 Annotation disagreement and construct validity — NEW (ref 6)
2.11 Role-based multi-agent architectures          — NEW (ref 10) [optional, can fold into 2.6]
```

11 subsections is heavy for a single paper; if compression is needed:
- Fold 2.10 into 2.4 (uncertainty/reliability cluster).
- Fold 2.11 into 2.6.
- This compresses to 9 subsections.

---

## 12. Citation priority

If page budget forces compression:

| priority | refs | reason |
|---|---|---|
| **P0 (must cite)** | 1, 4, 6, 9 | One per gap (A/B/C/D); each is the most direct precedent |
| P1 (strongly recommend) | 2, 5, 10 | Self-preference empirics, decomposed-eval paradigm, role-based MAS |
| P2 (cite if room) | 3, 7, 8 | Panel inconsistency, Prometheus pattern, clarification root |

P0 alone (4 refs) closes the four conceptual gaps. P0+P1 (7 refs) gives full-strength positioning. All 10 (P0+P1+P2) is the comprehensive option for a journal version or extended technical report.

---

## 13. What this list deliberately omits

References considered but excluded, with reasoning, to make the choices auditable:

- **AutoGen (Wu et al. 2024)** — close alternative to MetaGPT; MetaGPT's SOP-driven role specification is a sharper fit for our y-index. Cite as comparison point in MetaGPT discussion if needed.
- **Constitutional AI (Bai et al. 2022)** — about norm specification, not delegation; tangential.
- **ReAct / Plan-and-Solve / Tree-of-Thoughts** — pre-execution planning literature; conceptually adjacent to "pre-execution" framing but our object (responsibility projection) differs from their object (action plan / reasoning trace). Risk of over-extending the related-work section.
- **InverseConstitutionalAI / similar norm-extraction work** — tangential to projection; r* is not a norm.
- **Inverse RL** — historical precedent for goal/intent inference but the field diverges from LLM literature substantially. Cite only if reviewer specifically asks about r* as an inverse problem.
- **Prompt sensitivity (Sclar et al. 2023)** — adjacent to cross-family divergence but the mechanism differs (prompt format vs model family).
- **Liao & Xiao (2023) "Rethinking Model Evaluation as Narrowing the Socio-Technical Gap"** — strong on construct validity in NLP eval; could replace or augment Plank (ref 6) if the paper takes a more sociotechnical framing. Currently kept as backup.

---

## 14. Action items

Before the next code-modification cycle:

1. **Fetch the 4 P0 papers** and verify the precise framing each one supports (some claims above are paraphrased from memory; bibliographic precision matters at submission grade).
2. **Decide between Option A and Option B** for the Related Work restructure (9 vs 11 subsections).
3. **Draft the §2.8 / §2.9 / §2.10 subsection prose** (each ~150–250 words) per the `paper_master_v1.2` §7 pattern.
4. **Update `concept_and_positioning_v1.0.md`** in place, or create `concept_and_positioning_v1.1.md` as a sync patch following the v1.x convention used elsewhere in the doc tree. Patch is preferred to preserve the v1.0 → v1.1 → v1.2 lineage discipline.
