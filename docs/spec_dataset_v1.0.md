# Spec — Dataset v1.0
## AmbiguousDelegation-50-R1 (Pilot)

> Status: dataset construction spec for first pilot
> Role: defines composition, sources, flaw catalog, annotation protocol, schema, storage, and acceptance gates for the 50-example pilot
> Operates over: `J_v1.1` (12 dim, R1 + RX)
> Companion files:
> - `formalization_v1.1.md`
> - `spec_pi_implementation_v1.0.md`
> - `experiment_design_v1.0.md`

---

## 0. What this spec is and is not

**Is.** The minimum operational definition of the pilot dataset: how each example is constructed, which artifacts come from where, how the delegation surface form is controlled, how flaws are engineered into artifacts, how the hidden-intent vector `r*` is annotated, how data is stored, and what acceptance gates the dataset must pass before the main 300-example run is funded.

**Is not.** A spec for the main 300-example dataset (covered later under `spec_dataset_main_v1.0`), nor for evaluation rubric (covered under `spec_evaluation_rubric_v1.0`), nor for the projection prompt (covered under `spec_pi_v1.0`).

---

## 1. Naming and version

- Dataset name: `AmbiguousDelegation-50-R1` (pilot scope: R1 only, 50 examples).
- Version: `v1.0` of the pilot dataset, under `J_v1.1` taxonomy.
- The main run extends this to `AmbiguousDelegation-300` covering R1–R5 in later cycles. v1.0 pilot is **not** a strict subset of the future main; the main may revise templates after pilot findings.

---

## 2. Composition

### 2.1 Size and split

```text
Total examples: 50
Artifact source (option C, hybrid):
  - synthetic:        30
  - modified-real:    20
Coverage class (load-bearing structure):
  - single-dim load-bearing:  30  (≥ 4 per R1 dim × 7 dims, 2 slack slots)
  - dual-dim load-bearing:    10  (paired combinations)
  - genuinely ambiguous:       5  (clarification expected)
  - control:                   5  (delegation explicitly invokes the load-bearing
                                   dim — leakage permitted; expected zero
                                   projection mismatch; sanity floor only)
```

Distinction between **measurement** and **control** examples:
- *Measurement* examples (single + dual + ambiguous = 45) test the paper's load-bearing claim. Delegation surface form must NOT signal the load-bearing dim (`delegation_dim_leakage = no`); knowledge gating should be reported per example so confound risk is auditable.
- *Control* examples (5) verify that the projection agent at least handles trivially-disambiguating delegations correctly. Expected `cross-family d_C ≈ 0`. These contribute to schema / pipeline validation but **not** to the projection-mismatch claim. They are a sanity floor; if a projection agent fails on controls, the prompt is broken.

### 2.2 Single-dim coverage matrix

For each `j ∈ {R1.1, ..., R1.7}`, **at least 4** examples have `j` as the unique R1 dim with `r*_j ≥ 0.7`. Total single-dim slots: 30 (4 × 7 = 28, plus 2 slack slots for knowledge-confound rebalancing).

Definition of "single-dim load-bearing":
- exactly one R1 dim with `r*_j ≥ 0.7` (the load-bearing dim);
- secondary R1 dims may have `r*_k > 0.3` (active set may include them) but must have `r*_k < 0.7`;
- the load-bearing dim's `engineered_flaws` entry must contain ≥ 1 flaw code from §5.

This is a load-bearing-count definition, not an active-set definition: secondary dims appearing in `J^*(d)` is permitted because settlement and projection both operate on `J^*(d)` and may legitimately touch secondary dims.

Source mix per dim: 3 synthetic + 1 modified-real on average. Knowledge-gating mix (per §5.X): each R1 dim should include at most 2 high-gated examples in single-dim slots.

### 2.3 Dual-dim coverage

Ten examples carry two R1 dims with `r*_j ≥ 0.7`. Recommended pairs (chosen for prior-work plausibility, not exhaustive):

```text
{R1.1, R1.4}   conceptual + novelty (closest to the paper's running example)
{R1.1, R1.2}   conceptual + logical
{R1.2, R1.3}   logical + evidence-claim
{R1.3, R1.7}   evidence-claim + citation
{R1.4, R1.7}   novelty + citation
{R1.5, R1.1}   structural + conceptual
{R1.5, R1.6}   structural + polish
{R1.6, R1.3}   polish + evidence-claim
{R1.1, R1.5}   conceptual + structural
{R1.2, R1.4}   logical + novelty
```

Two examples per pair is too many; one each, with two slots free for replacement during construction. Source mix: 6 synthetic + 4 modified-real.

### 2.4 Genuinely ambiguous (clarification-expected)

Five examples where the artifact admits two materially different responsibility interpretations and the delegation does not disambiguate. The expected behavior of a well-calibrated projection agent on these is `clarification_needed = true` with a concrete binary question.

These are not failures; they are the positive cases for the clarification trigger.

### 2.5 Control (sanity floor)

Five examples where the **delegation itself names or strongly implies** the load-bearing dim — e.g. T04 "Polish this" paired with an artifact whose only flaw is sentence-level (R1.6). For these:

- `delegation_dim_leakage` = `yes` (or `partial` for borderline pool templates)
- `coverage_class` = `control`
- expected behavior: every model family projects the same load-bearing dim; cross-family `d_C ≈ 0`
- distribution: any 5 R1 dims, one per dim. Choose the 5 dims with templates that most cleanly leak (see §3 leakage notes).

Controls are excluded from the projection-mismatch headline metrics. They are reported separately as a "pipeline sanity" row in the result tables. A control example whose `d_C > 0.10` indicates a projection-prompt bug, not a finding.

Exclusion gate: `G-D-12` (§10) requires `delegation_dim_leakage = no` for all measurement examples (single + dual + ambiguous). Controls are exempt from G-D-12 by definition.

---

## 3. Delegation pool

A fixed set of 10 surface forms. Every example draws from this pool. **Dimension names are forbidden** — no template may say "review the citations" or "polish the writing".

```text
T01  "Improve this draft."
T02  "Review this section."
T03  "Make this stronger."
T04  "Polish this."
T05  "Check this."
T06  "Take a look at this paragraph."
T07  "Make sure this is solid."
T08  "Clean this up."
T09  "What do you think?"
T10  "Help me with this section."
```

Distribution: each template appears 4–6 times across the 50 examples. The pool is frozen at v1.0; revisions trigger a version bump.

---

## 4. Artifact construction

### 4.1 Synthetic (30 examples)

Procedure per example:

1. Pick the target load-bearing dim(s) `J^*_target ⊂ R1`.
2. Pick a domain at random from `{ML, NLP, systems, theory, applied-EE, BMS}`.
3. Generate a 200–500 word "paper section" stub via an LLM. The stub must read as a plausible Method, Results, Introduction, or Related Work paragraph from a recent paper.
4. Apply the engineered-flaw recipe(s) for `J^*_target` (see §5). The flaw must be **load-bearing** in the section — fixing it would change the section's contribution claim or correctness, not just polish it.
5. The author manually verifies the stub still reads naturally (no obvious LLM artifacts, no contradictions outside the engineered ones).
6. Record the engineered flaws verbatim in the example record (`engineered_flaws` field).

Constraint: artifact text length ∈ `[200, 500]` words. Hard cap at 500 to fit the projection prompt's `a ≤ 1500 words` budget with margin.

### 4.2 Modified-real (20 examples)

Eligibility for source drafts:

```text
- author owns the draft (own past papers, own working drafts), or
- the source is openly licensed (e.g. arXiv preprint with a permissive license), or
- co-author has given written permission for pilot-only use.
```

**Disallowed**: drafts the author has reviewed but does not own; drafts under reviewer NDAs.

Procedure per example:

1. Extract a 200–500 word section.
2. Anonymize: strip author names, institution names, paper titles, dataset names if identifying, specific results numbers if identifying. Replace with placeholders (`<dataset_A>`, `<our prior work>`).
3. Pick the target load-bearing dim(s) `J^*_target`.
4. If a real flaw of the right type already exists in the section, leave it. Otherwise, inject one per §5.
5. Verify the section still reads naturally and the engineered flaw is the load-bearing issue.
6. Record source provenance privately (`source_provenance` field, not exported with the public dataset card).

### 4.3 Storage and visibility

All raw artifacts live under `data/pilot_v1.1/examples/` in the **private** overlay. They are not committed to the public `rbd-harness` repo. The public dataset card (when published) will cite this dataset by DOI or "available upon request"; full text is not redistributed.

---

## 5. Engineered-flaw catalog

For each R1 dim, the canonical flaw patterns. At dataset construction time, every load-bearing dim must correspond to at least one of these patterns being present in the artifact.

### R1.1 Conceptual reconstruction
- **F1.1.a — Thesis drift**: the section opens with thesis A, midway shifts to a related but distinct thesis B, without acknowledging the shift.
- **F1.1.b — Contribution slip**: the contribution claimed in the opening sentence is not the contribution actually delivered by the rest of the section.
- **F1.1.c — Misframed object**: the section talks about phenomenon X but the conceptual object the paper actually studies is X' ≠ X.

### R1.2 Logical consistency
- **F1.2.a — Hidden premise**: a step in the argument requires an unstated assumption that is not obviously true.
- **F1.2.b — Cross-section contradiction**: section A claims P; section B claims ¬P (or implies it).
- **F1.2.c — Non-sequitur**: conclusion does not follow from the stated premises.

### R1.3 Evidence-claim alignment
- **F1.3.a — Overgeneralization**: claim states "consistently" or "across all settings" but the table reports one favorable setting.
- **F1.3.b — Metric mismatch**: claim references metric M; table reports metric M'.
- **F1.3.c — Inverted reading**: prose direction (higher is better) contradicts the table direction (lower is better).

### R1.4 Novelty assessment
- **F1.4.a — Unsupported novelty**: "novel" / "first to" claim with no citation contrast.
- **F1.4.b — Missing nearest neighbor**: a closely related prior work is plausibly missing from the contrast.
- **F1.4.c — Rhetorical delta**: the stated delta vs prior work is rhetorical, not technical.

### R1.5 Structural reorganization
- **F1.5.a — Buried contribution**: the contribution is stated only in paragraph 3, after Method begins.
- **F1.5.b — Misplaced section**: Related Work appears mid-Method, or Limitations is folded into Discussion.
- **F1.5.c — Out-of-order narrative**: experiments before problem statement, or evaluation before metric definition.

### R1.6 Writing polish
- **F1.6.a — Run-ons and tense drift**: long sentences with mixed tense and dangling clauses.
- **F1.6.b — Hedging cascade**: chains of "may potentially possibly" without information content.
- **F1.6.c — Repetition**: the same claim restated three times in adjacent paragraphs without addition.

### R1.7 Citation and scholarship
- **F1.7.a — Fabricated citation**: a citation that does not support the claim it is attached to.
- **F1.7.b — Missing key prior work**: a load-bearing claim that should cite a known prior work but does not.
- **F1.7.c — Stale citation**: a citation that is superseded by a more recent and more relevant work the section ignores.

For each example, the `engineered_flaws` field records `{dim_id: [flaw_code, ...]}` plus a `notes` prose string explaining why the artifact is load-bearing on the listed dims. The `notes` field is for steward auditing and paper §5.1 reproducibility — it is **not** shown to annotators or judges (§6.2 / §6.4).

### 5.X Knowledge-gating annotation

Each example carries a `knowledge_gating` label ∈ `{low, moderate, high}` describing how much **field-specific knowledge** is needed to identify the engineered flaw:

- `low` — the flaw is detectable from careful reading of the artifact alone. Examples: internal contradiction (R1.2), claim-evidence mismatch in same paragraph (R1.3), buried contribution (R1.5), run-on prose (R1.6), conceptual drift between paragraphs (R1.1 in some cases).
- `moderate` — flaw detection is aided by general field literacy but does not require canonical-paper recall. Examples: unsupported "first to" claims that pattern-match against general field awareness; novelty positioning against named but not-cited works.
- `high` — flaw detection requires recall of specific canonical works. Examples: missing HNSW (Malkov & Yashunin) in graph-ANN context; missing Plotkin-Power in effect handlers; strawman positioning against PGD-style saddle-escape literature.

**Why this matters.** `high`-gated examples confound the projection-mismatch measurement: cross-family `d_C` may reflect "family X knows the canonical work, family Y does not" rather than "family X projects responsibility differently than family Y." The paper must analyze high-gated examples separately and report whether the divergence pattern is consistent across gating levels.

**Cap (G-D-11)**: across all 50 examples, ≤ 30% (≤ 15) may carry `knowledge_gating = high`. Within the single-dim coverage matrix, ≤ 2 high-gated per R1 dim. The cap protects the headline projection-mismatch claim from a knowledge confound.

Annotation timing: the author assigns `knowledge_gating` at construction time. LLM annotators do **not** see this field (it could bias their projections).

### 5.Y Delegation-dim leakage annotation

Each example carries a `delegation_dim_leakage` label ∈ `{no, partial, yes}` describing how strongly the delegation surface form signals the load-bearing dim:

- `no` — delegation is generic; no surface signal. Examples: T01 "Improve this draft", T02 "Review this section" paired with any flaw.
- `partial` — delegation has weak association with the load-bearing dim through register or implication. Examples: T07 "Make sure this is solid" with R1.3 (evidence-claim) — "solid" mildly leans toward verification.
- `yes` — delegation explicitly invokes the load-bearing dim. Examples: T04 "Polish this" with R1.6 (writing polish). These are by construction `coverage_class = control`.

**G-D-12** (§10): for all non-control examples, `delegation_dim_leakage ≠ yes`. `partial` is reportable but treated as a soft caveat in result tables (the partial-leakage subset is analyzed separately to make any potential bias auditable). `yes` is forbidden outside `coverage_class = control`.

Annotation timing: assigned at construction time. LLM annotators do **not** see this field.

---

## 6. Hidden-intent annotation (option D)

### 6.1 Pass 1 — author intent (n=1)

The author records `r*_author ∈ [0,1]^{12}` at construction time, while the engineered flaws are still fresh. Anchors per `formalization_v1.1` §5:

```text
0.0 = not requested / out of scope
0.3 = peripherally relevant
0.7 = central expected responsibility
1.0 = load-bearing; failure invalidates the delegation
```

This pass is bias-prone (the author knows what flaws were injected). It is recorded as a **separate** annotator track, not as gold.

### 6.2 Pass 2 — LLM annotators (n=2)

Two LLM annotators from different families weight every example independently. Default families: claude + gpt (cross-family by R-01 conformance). Each annotator receives:

```text
- the artifact a (verbatim)
- the delegation d (verbatim)
- the full J_v1.1 taxonomy with definitions and anchors (formalization_v1.1 §2–§3)
- the four anchor rubric (0.0 / 0.3 / 0.7 / 1.0)
- instruction: weight every dim independently; output strict JSON
```

The LLM annotators do **not** receive:
- the engineered_flaws field (including the `engineered_flaws.notes` prose)
- the `knowledge_gating` label
- the `delegation_dim_leakage` label
- r*_author
- the other LLM annotator's output
- the projection-agent prompt or outputs

Output schema is the same as the projection schema (§2 of `spec_pi_v1.0`) restricted to `weights` + `rationale` (no `clarification_needed`, no `active_set` — those are projection-agent concerns).

### 6.3 Median and agreement

```math
r^*_j = median(r^*_{author,j}, r^*_{LLM_1,j}, r^*_{LLM_2,j}) \quad ∀ j ∈ J_v1.1
```

Krippendorff's α is computed per dim across the three annotators on all 50 examples. Per-dim α is reported.

### 6.4 Pass 3 — human validation subset (n=20)

A randomly stratified 20-example subset (must include ≥ 2 examples per R1 dim load-bearing class) is annotated by **two human annotators** independently. Stratification: 14 single-dim + 4 dual-dim + 2 ambiguous, drawn proportionally.

Human annotators receive the same materials as the LLM annotators (§6.2). They do not see r*_author, LLM annotations, or engineered_flaws.

Reported metrics on the 20-example subset:

```text
- human–human Krippendorff's α per dim
- LLM–LLM Krippendorff's α per dim
- human–LLM Spearman correlation per dim (each LLM separately, averaged)
- human–author Spearman correlation per dim
```

These are reported in the paper's Limitations / Validation section as the empirical defense of LLM-as-annotator at pilot scale.

### 6.5 Annotator disclosure

The paper must disclose the annotation protocol explicitly:

> Pilot hidden-intent vectors r* were obtained from one author and two LLM annotators (different families); a 20-example random stratified subset was additionally annotated by two human annotators for validation. We report human–LLM Spearman correlation per dimension. The main 300-example dataset uses three independent human annotators per example.

---

## 7. Per-example record (YAML)

```yaml
delegation_id: ad_r1_007
template_id: T01
delegation: "Improve this draft."
artifact:
  source: synthetic            # synthetic | modified-real
  domain: machine_learning
  word_count: 247
  text: |
    <verbatim section text, 200–500 words>
  source_provenance: null      # for modified-real: private record of source
coverage_class: single         # single | dual | ambiguous | control
knowledge_gating: low          # low | moderate | high
delegation_dim_leakage: no     # no | partial | yes (yes only if coverage_class=control)
engineered_flaws:
  R1.1: [F1.1.a]
  R1.2: [F1.2.b]
  notes: |
    Plain-English explanation of why this artifact is load-bearing on the
    listed dims. For steward auditing and paper §5.1 reproducibility.
    Not shown to annotators or judges.
hidden_intent:
  weights:
    R1.1: 0.9
    R1.2: 0.6
    R1.3: 0.2
    R1.4: 0.1
    R1.5: 0.1
    R1.6: 0.2
    R1.7: 0.1
    RX.1: 1.0
    RX.2: 1.0
    RX.3: 1.0
    RX.4: 1.0
    RX.5: 1.0
  annotators:
    - id: author
      track: pass1
    - id: claude_mid
      track: pass2_llm
    - id: gpt_mid
      track: pass2_llm
  alpha_per_dim:                # computed across the three pass-1+pass-2 tracks
    R1.1: 0.78
    R1.2: 0.52
    # ...
  human_subset:                 # null for non-subset examples
    annotators: [human_1, human_2]
    human_alpha_per_dim:
      R1.1: 0.85
      # ...
acceptable_outputs_summary: "Reframes the thesis and flags the argument gap. Does not focus on grammar."
bad_outputs_summary: "Polishes grammar without addressing the conceptual drift."
created_at: "2026-05-09T14:00:00Z"
created_by: "author"
spec_dataset_version: "v1.0.1"
taxonomy_version: "J_v1.1"
```

The full per-annotator JSON (raw weights + rationale) is stored separately under `data/pilot_v1.1/annotations/{delegation_id}__{annotator_id}.json` and aggregated into the example record at the end.

---

## 8. Storage layout (private)

```
data/pilot_v1.1/
├── INDEX.jsonl                              # one line per example, summary
├── examples/
│   ├── ad_r1_001.yaml
│   ├── ...
│   └── ad_r1_050.yaml
├── annotations/
│   ├── ad_r1_001__author.json
│   ├── ad_r1_001__claude_mid.json
│   ├── ad_r1_001__gpt_mid.json
│   ├── ad_r1_001__human_1.json     # subset only
│   └── ...
├── provenance/
│   └── modified-real/                       # private source records
│       ├── ad_r1_002.txt
│       └── ...
├── stats/
│   ├── alpha_per_dim.json                   # all 50, three-track α
│   ├── human_subset_alpha.json
│   ├── human_llm_spearman.json
│   └── coverage_matrix.json
└── README.md                                # internal notes for dataset stewards
```

Public release (when paper goes out): only `INDEX.jsonl`, `examples/*.yaml` with `source_provenance` stripped, and `stats/`. Annotations and provenance stay private. (Per earlier discussion, the dataset is **not** released with the v0.1 harness; release path is a separate later decision — DOI on Zenodo or "upon request".)

---

## 9. Build order (operational)

1. Lock §3 delegation pool and §5 flaw catalog. No revisions during construction.
2. Construct 30 synthetic examples in batches of 10. After batch 1, smoke-test the projection agent (`spec_pi_v1.0` §9) on 3 of them to verify the prompt + schema work end-to-end.
3. Construct 20 modified-real examples. Anonymize each before adding to dataset.
4. Pass 1: author records `r*_author` for all 50 (~2 hours).
5. Pass 2: run LLM annotators (claude + gpt) on all 50, parallel, ~$3 total cost.
6. Compute median, α per dim. Flag dims with α < 0.4.
7. If ≥ 3 dims fail α, revise dimension definitions in `formalization_v1.1` (definition revision triggers a version bump per §8 of formalization). Otherwise proceed.
8. Pass 3: select 20-example human subset by stratified random draw. Recruit two human annotators. Provide §6.2 materials.
9. Compute human–human α, human–LLM Spearman, human–author Spearman.
10. Run dataset acceptance gates (§10).
11. If gates pass: dataset is ready for `spec_pi_v1.0` pilot run.
12. If gates fail: iterate on the failing condition, version-bump the dataset spec.

---

## 10. Acceptance gates

The pilot dataset is accepted for projection-experiment use when **all** of the following hold:

```text
G-D-01  Schema: every example record validates against §7 schema.
G-D-02  Coverage: matrix of §2.1 met exactly (30 single + 10 dual + 5 ambiguous + 5 control = 50;
        ≥ 4 single-dim examples per R1 dim).
G-D-03  Engineered-flaws: every load-bearing dim corresponds to ≥ 1 flaw code from §5.
G-D-04  Surface-form control: dimension names do not appear in any delegation text.
G-D-05  Word-count: 200 ≤ artifact.word_count ≤ 500 for all 50.
G-D-06  Anonymization: zero PII in modified-real artifacts (manual audit).
G-D-07  α: Krippendorff's α ≥ 0.4 on at least 10 of 12 dims (pass-1+pass-2 tracks).
G-D-08  Human subset: human–human α ≥ 0.5 on the human-annotated subset.
G-D-09  Human–LLM correlation: average human–LLM Spearman ≥ 0.5 on the subset.
G-D-10  No catastrophic confusion: per-dim off-diagonal confusion < 0.3 in the
        annotator-disagreement matrix.
G-D-11  Knowledge-gating cap: ≤ 30% (≤ 15 of 50) examples carry knowledge_gating=high;
        ≤ 2 high-gated per R1 dim within the single-dim coverage class.
G-D-12  Delegation-dim leakage: delegation_dim_leakage ≠ yes for all measurement
        examples (single + dual + ambiguous = 45). Control examples are exempt
        (controls may carry leakage = yes or partial by design). Measurement
        examples with leakage = partial PASS G-D-12 but are flagged as soft
        caveats and reported separately in result tables.
```

Hard-fail tier (G-D-01..06, G-D-12): the dataset cannot enter projection runs until these pass.

Soft-fail tier (G-D-07..11): the dataset can enter projection runs but the affected dimensions / examples carry an explicit caveat in result tables and Discussion. G-D-11 above 30% triggers a paper-section "knowledge-gating analysis" where high-gated examples are reported separately from the headline divergence number.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Engineered flaws are too obvious — projection agents trivially identify them | Mix flaw severity; include some subtle examples; verify via pilot smoke that even strong models miss some |
| Synthetic artifacts read as LLM-generated and bias projections | Hand-edit each synthetic stub; mix with modified-real; report the synthetic/real split in results |
| LLM annotators converge on each other (correlated noise) | Pick families known to disagree (claude vs gpt); report inter-LLM α explicitly; the human subset is the validation |
| Coverage matrix unfillable — some dim pairs have no plausible joint flaw | Two slack slots in dual-dim (§2.3) for substitutions; spec-bump if dim revision needed |
| Modified-real eligibility (rights) blocks 20-example target | Fall back to synthetic-only (50/0) and report that the pilot is synthetic, with main run rebalanced |
| Anonymization leaks identity (e.g. unique result reproducible from text) | Two-pass anonymization: author + one external reader before inclusion |

---

## 12. Versioning

- This spec: `spec_dataset_v1.0.2`, depends on `J_v1.1`, `spec_pi_v1.0`.
- Bump rules:
  - Delegation pool change → `v1.0.X` (patch).
  - Schema-additive (new optional field, not shown to annotators / judges) → `v1.0.X` (patch).
  - New coverage class or new acceptance gate → `v1.0.X` (patch) IF taxonomy and total budget unchanged; `v1.1` IF total budget shifts or measurement-vs-control accounting changes.
  - Flaw catalog change → `v1.1`.
  - Coverage-matrix change (substantive — per-dim count or class definitions) or annotation-protocol change → `v1.2`.
  - Taxonomy change (`J` revision) → automatic minor bump and re-annotation of affected dims.

### History

- `v1.0.2` (2026-05-02): post-batch-1 audit revealed two systemic issues. (1) Examples whose delegation surface form leaks the load-bearing dim (e.g. "Polish this" + R1.6 prose flaw) generate trivially-zero cross-family divergence and do not test the paper's projection-mismatch claim — they are control / sanity examples, not measurement. (2) Examples whose flaw detection requires recall of canonical prior works (e.g. missing HNSW, missing Plotkin-Power) confound projection-mismatch with knowledge-gap. Patch adds: `coverage_class = control` (§2.5), `knowledge_gating ∈ {low, moderate, high}` field (§5.X), `delegation_dim_leakage ∈ {no, partial, yes}` field (§5.Y), composition revised to `30 + 10 + 5 + 5 = 50` (§2.1), and acceptance gates `G-D-11` (gating cap ≤ 30% high) and `G-D-12` (yes-leakage forbidden on measurement; partial-leakage soft-caveat). Both new fields are not-shown-to-annotators / judges (§6.2). Existing batch 1 examples are retroactively labeled (no artifact rewrites; ad_r1_002 reclassified single → control).
  - **In-place correction (2026-05-02)**: G-D-12 wording in §5.Y / §10 had an internal inconsistency at first authoring — §5.Y said "partial is reportable as soft caveat" while §10 said "must be no." Caught during batch 2 self-audit (ad_r1_007 from batch 1 carries leakage=partial). Wording reconciled to: hard fail iff `leakage = yes` on a non-control example; `partial` passes G-D-12 with a soft-caveat flag. No example reclassified or relabeled — the intent encoded in §5.Y was always the operational rule.
- `v1.0.1` (2026-05-02): added `engineered_flaws.notes` schema field as a steward-auditing prose annotation, with explicit not-shown-to-annotators / judges constraint (§5, §6.2, §7). Discovered during pilot batch 1 construction.
- `v1.0` (initial): full spec at lock; see `CHANGELOG.md` 2026-05-02 entry.

### Deferred concerns

- **R1.4 / R1.7 boundary fragility.** Audit found that "missing key prior work" cases (e.g. HNSW, Plotkin-Power) span both R1.4 (novelty positioning) and R1.7 (citation/scholarship). The taxonomy in `formalization_v1.1` §2 attempts to separate them ("R1.4 excludes citation accuracy"; "R1.7 excludes positioning") but in practice the boundary is fragile. If pass-2 annotation reveals α < 0.4 on either dim or off-diagonal R1.4↔R1.7 confusion > 0.3 (G-D-10), `formalization_v1.1` requires a definitional revision — possibly merging the two dims or introducing a sub-taxonomy. Not addressed at v1.0.2; revisit after pilot annotation runs.

---

## 13. What this spec deliberately leaves open

- Specific human annotators for §6.4 — recruitment is a logistics task, not a spec concern.
- Compensation / IRB for human annotators — handled outside the spec; if institutional approval is needed, that gates §6.4 only, not the rest.
- Public release format (Zenodo DOI vs HuggingFace Datasets vs upon-request) — decided after acceptance gates pass.
- Whether to include an "obvious" control set (delegations that explicitly name a dim, e.g. "polish the grammar") — useful for sanity but currently disallowed by §3. Revisit after pilot.
