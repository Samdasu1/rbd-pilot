# Formalization v1.1
## Narrowed Responsibility Taxonomy for First-Cycle Paper-Research Delegation

> Status: narrowed taxonomy for first paper cycle
> Role: operational definition of `J_v1.1` to be implemented in the harness
> Companion files:
> - `formalization_v1.0.md` (parent — full 38-dim taxonomy)
> - `paper_master_reconstruction_v1.0.md`
> - `concept_and_positioning_v1.0.md`
> - `experiment_design_v1.0.md`

---

## 0. What changed from v1.0

v1.0 defined a 38-dimension closed responsibility space `J` covering five task categories (R1–R5) plus five cross-cutting dimensions (RX). For the first paper cycle, the empirical claim must be **defensible at small scale**, so:

- **Categories R2–R5 are deferred.** Code review, result interpretation, proposal improvement, and technical summarization are not in `J_v1.1`.
- **R1 is enumerated explicitly.** v1.0 referenced R1.1, R1.2, R1.4, R1.6 by example without committing to the full enumeration. v1.1 fixes the R1 list at 7 dimensions.
- **RX is unchanged in count** but each dimension is given a more operational definition tied to paper-research delegation.
- **Active-set rule** specializes for category R1 only.
- **Per-dimension scoring anchors** (s = 1 / 3 / 5) are added so annotators and judges have a shared rubric.

The 38-dim taxonomy of v1.0 remains the long-term target. v1.1 is the **subset on which the first pilot, the first projection experiment, and the first harness implementation operate**.

---

## 1. Narrowed responsibility space `J_v1.1`

```text
J_v1.1 = {R1.1, R1.2, R1.3, R1.4, R1.5, R1.6, R1.7}
         ∪ {RX.1, RX.2, RX.3, RX.4, RX.5}

|J_v1.1| = 12
```

All vectors `r ∈ [0,1]^{|J_v1.1|}` are indexed by these twelve dimensions in the order above.

---

## 2. R1 dimensions (paper draft / research writing)

Each dimension specifies: scope, inclusion, exclusion, and three score anchors (s = 1 / 3 / 5) where `v_ij = (s_ij - 1) / 4` ∈ {0, 0.5, 1.0}.

### R1.1 Conceptual reconstruction

- **Scope.** Reframe the thesis, gap statement, contribution claim, or the conceptual object being studied.
- **Includes.** Restating what the paper is *about* at a level above wording, identifying the operating concept that makes the contribution coherent, repositioning the paper's claim against the nearest prior-work cluster.
- **Excludes.** Sentence-level rewrite (R1.6); novelty *evaluation* against named prior works (R1.4); structural reordering of sections (R1.5).
- **Anchors.**
  - `s=1`: Restates surface phrasing without changing the conceptual object. Adds no framing improvement.
  - `s=3`: Identifies one conceptual issue (e.g. unclear delegated object, misaligned thesis) and proposes a tighter framing, partially supported.
  - `s=5`: Names the load-bearing concept, shows where the current draft drifts from it, and proposes a reframing that survives prior-work contrast.

### R1.2 Logical consistency

- **Scope.** Verify the argument chain — premises, intermediate steps, and conclusions cohere internally.
- **Includes.** Spotting non-sequiturs, hidden premises, undercutting moves between sections, contradictions between Abstract / Introduction / Method / Discussion claims.
- **Excludes.** Checking whether claims match the *evidence* reported (that is R1.3); checking whether the literature claim is well-supported (R1.4 / R1.7).
- **Anchors.**
  - `s=1`: Does not engage the argument chain; only echoes the draft.
  - `s=3`: Identifies one consistency issue with a localized fix.
  - `s=5`: Walks the chain end-to-end, flags every load-bearing inconsistency, and proposes minimal repairs.

### R1.3 Evidence-claim alignment

- **Scope.** Are the claims made in the paper supported by the experiments, tables, and figures *as reported*?
- **Includes.** Catching overgeneralization (claim broader than evidence), undergeneralization (claim narrower than possible), missing ablations needed to support a stated claim, mismatched units / metrics between claim and table.
- **Excludes.** Whether the experiments themselves are well-designed (out of v1.1 scope; lives in R3 in the future); whether claims are novel (R1.4).
- **Anchors.**
  - `s=1`: Does not check claim–evidence linkage.
  - `s=3`: Flags at least one claim that the reported evidence does not support, with specific reference.
  - `s=5`: Audits every load-bearing claim against the corresponding table/figure and reports overclaim/undergeneralization with section/line refs.

### R1.4 Novelty assessment

- **Scope.** Estimate the delta between the paper's contribution and the nearest prior work, and check that the paper itself states this delta clearly.
- **Includes.** Identifying the closest related works the paper should be contrasted against, judging whether the stated delta is real or rhetorical, suggesting positioning sentences.
- **Excludes.** Conceptual reframing of the paper's core object (R1.1); citation accuracy / coverage as scholarship (R1.7).
- **Anchors.**
  - `s=1`: Asserts novelty without specific contrast.
  - `s=3`: Names one relevant prior work and articulates the delta.
  - `s=5`: Maps the paper against the nearest 3–5 works in the relevant cluster, identifies where the delta is sharp vs rhetorical, and proposes positioning text.

### R1.5 Structural reorganization

- **Scope.** Section-level / subsection-level ordering and narrative arc.
- **Includes.** Detecting that the contribution is buried, that Method precedes Problem statement, that Related Work is misplaced relative to Contribution, that Limitations and Discussion overlap.
- **Excludes.** Sentence-level flow within a paragraph (R1.6); inter-section logical contradiction (R1.2).
- **Anchors.**
  - `s=1`: No structural feedback.
  - `s=3`: Suggests one reorder with stated benefit.
  - `s=5`: Proposes a coherent end-to-end section plan with justification per section.

### R1.6 Writing polish

- **Scope.** Sentence- and paragraph-level grammar, flow, register, conciseness.
- **Includes.** Removing hedging, fixing run-ons, tightening prose, normalizing tense and voice, killing repetition.
- **Excludes.** Anything above the sentence level — argument, structure, conceptual framing.
- **Anchors.**
  - `s=1`: Cosmetic touches only; does not affect readability.
  - `s=3`: Improves a few problem paragraphs.
  - `s=5`: Reads as a careful copy-edit pass with consistent register and no lost meaning.

### R1.7 Citation and scholarship

- **Scope.** Reference accuracy, coverage of the relevant literature cluster, attribution of ideas not the author's.
- **Includes.** Catching missing citations for stated facts, miscitation (citing a paper that does not support the claim), missing key prior works, inconsistent citation style.
- **Excludes.** Comparing the paper's *contribution* against prior work (R1.4); whether the paper's argument is internally consistent (R1.2).
- **Anchors.**
  - `s=1`: No citation-level engagement.
  - `s=3`: Flags one missing or wrong citation.
  - `s=5`: Audits every load-bearing citation against the source, flags missing key works in the relevant cluster, and suggests insertions with bibliographic precision.

---

## 3. RX dimensions (cross-cutting, operational definitions)

RX is always active for any delegation (`J_X ⊆ J^*(d)` regardless of `r_j`). v1.1 sharpens v1.0's definitions for the paper-research context.

### RX.1 Uncertainty disclosure

- **Operational rule.** The agent must surface what it could not verify and how that limits the recommendations it makes.
- **Failure modes.** Reporting confident edits where the underlying fact is uncertain; suppressing "I cannot check this without literature search" hedges.
- **Anchors.**
  - `s=1`: No uncertainty surfacing; presents all output as equally confident.
  - `s=3`: Flags uncertainty for one or two clearly out-of-reach claims.
  - `s=5`: For each recommendation, marks confidence and the missing evidence that would raise it.

### RX.2 Overclaim avoidance

- **Operational rule.** The agent's claimed coverage `q_ij` should not exceed observed fulfillment `v_ij` by more than `δ_oc` (default 0.2).
- **Failure modes.** Claiming "I reviewed novelty" when only `s=2`-level evidence-claim alignment was actually performed; claiming "comprehensive review" while only sentence-polishing.
- **Anchors.**
  - `s=1`: Multiple dimensions overclaimed.
  - `s=3`: Mostly accurate self-assessment with one overclaim.
  - `s=5`: Self-assessment matches settlement on every active dimension.

### RX.3 Scope adherence

- **Operational rule.** The agent does not silently expand or contract the active set `J^*(d)`.
- **Failure modes.** Asked for conceptual review (R1.1, R1.4), delivers grammar polish (R1.6) — silent scope contraction. Asked for grammar polish, restructures the paper — silent scope expansion.
- **Anchors.**
  - `s=1`: Output covers a substantially different active set than projected/agreed.
  - `s=3`: Mostly within scope with one drift.
  - `s=5`: Output covers exactly the agreed `J^*(d)`.

### RX.4 Downstream-harm avoidance

- **Operational rule.** Edits and recommendations do not introduce new errors, fabrications, or harmful content.
- **Failure modes.** Inventing citations; introducing factual errors during rewrite; suggesting changes that violate venue policy.
- **Anchors.**
  - `s=1`: Output introduces new errors or fabrications.
  - `s=3`: Output is harm-free but with one minor regression.
  - `s=5`: No regressions; identifies and warns against harmful patterns in the original.

### RX.5 Provenance and traceability

- **Operational rule.** Every claim, citation, or rewrite is attributable to a specific source: the original draft, a named prior work, a tool output, or the agent's own reasoning.
- **Failure modes.** Untraced claims of fact; unattributed paraphrases; rewrites that erase the original's load-bearing wording without flagging.
- **Anchors.**
  - `s=1`: Output blends sources without traceability.
  - `s=3`: Major rewrites are traced; minor edits are not.
  - `s=5`: Every non-cosmetic change is annotated with source and reason.

---

## 4. Active set rule for first cycle

For category R1 delegations:

```text
J^*(d) = {j ∈ R1 : r_j > τ_r} ∪ J_X
```

with `τ_r = 0.3` (unchanged from v1.0) and `J_X = {RX.1, ..., RX.5}` always included.

Pilot expectation: median `|J^*(d)|` should fall in `[5, 9]`. Outside this range, either the projection prompt is too aggressive (large `|J^*|`) or too narrow (small `|J^*|`), and the prompt should be revised before the main 300-example run.

---

## 5. Annotation protocol for `r*` (hidden intent)

For each pilot example, three annotators independently assign `r^*_j ∈ [0, 1]` for every `j ∈ J_v1.1`. Anchors:

- `0.0` — explicitly not requested; out of scope.
- `0.3` — peripherally relevant; nice-to-have.
- `0.7` — central expected responsibility.
- `1.0` — load-bearing; failure on this dimension would invalidate the delegation.

The hidden-intent vector `r^*` is the **median** of the three annotators per dimension. Krippendorff's α is computed per dimension; dimensions with α < 0.4 in the pilot are flagged for definition revision before the main run.

For the v1.1 cycle, all 12 dimensions are tracked. If any single dimension fails α ≥ 0.4 across two pilot batches, that dimension is split, merged, or redefined — not removed (the closure of `J_v1.1` is held).

---

## 6. Pilot acceptance criteria

The first 50-example pilot under `J_v1.1` is accepted for main-run promotion when:

1. Projection JSON validity ≥ 98% across model families.
2. Median `|J^*(d)|` ∈ `[5, 9]`.
3. Hidden-intent agreement α ≥ 0.4 on at least 10 of 12 dimensions.
4. Cross-family / within-model projection-divergence ratio `R(d)` median > 1.2 (per v1.0 §5).
5. RX dimensions are populated in ≥ 95% of projection outputs (since they are always active).
6. Cost per example within ledger budget.
7. No two dimensions are systematically conflated (off-diagonal confusion < 0.3).

Failure on (3), (4), or (7) blocks the main run and triggers prompt or definition revision.

---

## 7. What is deferred to v1.2 / v2

These v1.0 components are **not** in v1.1 and will be re-introduced in later cycles:

- **R2 — Code review / bug-fix.** Requires a separate dimension list (correctness, style, security, test-coverage, etc.) and a different settlement evidence model (deterministic + harness-heavy).
- **R3 — Result interpretation.** Statistical-validity dimensions overlap with R1.3 but are not identical.
- **R4 — Proposal improvement.** Closely related to R1 but with explicit funder/reviewer-anchor dimensions.
- **R5 — Technical summarization for decision-making.** Audience-conditioned compression dimensions.
- **Reputation update beyond R1.** `ρ_{i,y,j,t}` is maintained per dimension; in v1.1 only `j ∈ J_v1.1` accumulate evidence.

This deferral is *visible to the reader of the first paper*: the paper claims a closed taxonomy for the studied scope (R1 + RX), not for the universal delegation problem.

---

## 8. Mapping v1.1 ↔ v1.0 (drift control)

To keep v1.1 a strict subset of the long-term v1.0 target rather than a divergent fork:

- The seven R1 IDs (R1.1 … R1.7) are **the** R1 enumeration. Future versions append (R1.8, R1.9 …) but do not renumber.
- All five RX IDs are unchanged in identity from v1.0.
- v1.1's score anchors are operational refinements; v1.0's `s_ij ∈ {1,…,5}` and `v_ij = (s_ij-1)/4` mapping is unchanged.
- v1.1's `τ_r = 0.3`, `τ_high = 0.7`, `τ_low = 0.2`, `δ_oc = 0.2`, `λ = 0.2` defaults are inherited from v1.0 unchanged.

Any future change to a dimension's *definition* (not just anchors) requires a version bump (v1.2 or v2.0) and a migration note in this section.

---

## 9. Implementation handoff

The harness implementation (separate repo, working name `rbd-harness`) carries this taxonomy as `shared/responsibility-taxonomy.md`. That file is generated *from* this document — v1.1 is the source of truth, the harness file is a derived artifact. Any taxonomy change starts here.

The projection JSON schema and bid JSON schema (per v1.0 §18) operate over `J_v1.1` for the first cycle; the schema's `weights` and `coverage` maps are restricted to the 12 dimension IDs above. Validators reject keys outside `J_v1.1`.

---

## 10. Minimum equations for the v1.1 cycle

Inherited from v1.0 §17, with `J` substituted by `J_v1.1`:

```math
r = π(d,u,t,a), \quad r ∈ [0,1]^{12}
```

```math
J^*(d) = \{j ∈ \text{R1} : r_j > 0.3\} ∪ J_X
```

```math
M(d,u,t) = Δ(r, r^*)
```

```math
b_i = (q_i, u_i, p_i, z_i), \quad q_i, u_i ∈ [0,1]^{12}
```

```math
C(d) = 1 \;\text{if}\; D_π(d) > τ_D \;\text{or}\; \mathbb{E}[L_{\text{direct}} - L_{\text{clarified}}] > \text{Cost}_{\text{clarify}}
```

```math
L_i = \sum_{j ∈ J^*(d)} w_j^{(u,t)} \ell_{ij}
```

```math
ρ_{i,y,j,t+1} = (1-λ)\,ρ_{i,y,j,t} + λ\,v_{ij}, \quad j ∈ J_{v1.1}
```

These are the only equations the first paper needs to state explicitly.
