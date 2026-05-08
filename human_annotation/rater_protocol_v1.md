# Rater Protocol v1 — single-dim anchor application for R1.7 (Citation and scholarship)

> Skill / training document for human raters of Stage 1 packages.
>
> **Status**: v1, derived from Stage 1 pilot findings (2026-05-07).
> **Scope**: R1.7 (Citation and scholarship). The two-axis structure generalizes
> to other R1 dims, but worked examples and counting conventions are R1.7-specific.
> **Written for**: author + 1–2 peers (closed allowlist). General Prolific
> crowdworkers are out of scope for v1 — see §6.

---

## 1. Why this document exists

Two pilot rounds (Prolific R1.1 sb1+sb2 with 9 raters; author self-test on 18
R1.7 packages) surfaced **two failure modes** that can not be fixed by
recruiting more raters:

1. **Rater regression to a generic "is the output good overall?" lens** when
   the anchor is short (`s=1/3/5` text) and the artifact is dim-irrelevant
   (no citation events to act on). This is the *dim–data mismatch* failure.
2. **Spec-specifiability ceiling** — even when the data is dim-relevant and
   the rater understands the anchor, two further ambiguities remain:
   - **Counting**: is "DeepDTA, GNINA, DiffDock-family, EquiBind, RoseTTAFold-AA"
     ONE event (a cluster of missing comparators) or FIVE events (each a
     separate work)?
   - **Correctness**: is the agent's flag ("Achiam 2017 = CPO; CPO does not
     concern per-step reachability") *factually right*? Judging this requires
     domain knowledge the rater may not have.

This protocol does not eliminate those ambiguities — they are inherent. It
**fixes a convention** so two raters who follow the protocol arrive at the
same count even on borderline cases, and it **decouples** "did the agent take
a citation action?" (any rater can score) from "was it correct?" (expert
rater only).

---

## 2. Counting convention

### Rule

**One *intent* per event.** When the agent makes ONE rhetorical move that
groups N citations into a single argumentative point, count **1 event**, not
N.

Examples of one-intent moves:

- *Cluster-as-1*: "Several existing methods (DeepDTA, GNINA, DiffDock-family,
  EquiBind, RoseTTAFold-AA) make 'first ML method' implausible without
  qualification." → **1 event** of type (b). The intent is "name a missing
  comparator cluster"; the cluster is one intent regardless of how many works
  the agent enumerates.
- *Audit-as-1*: "Verify DiskANN's venue/year — some bibliographies list NeurIPS
  2019, others differ." → **1 event** of type (c). The intent is "audit one
  citation"; multiple suggestions inside the same audit are one event.

Examples of two-intent moves (count separately):

- "Achiam et al. 2017 is mis-cast (it is CPO, not per-step safety). Separately,
  Chen et al. 2025 is unverifiable from the passage." → **2 events** of type
  (a). Two distinct citations, two distinct moves.
- "ScaNN is mis-classified as graph-based (it is a quantization method).
  Also, HNSW (Malkov & Yashunin, 2018) is conspicuously absent." → **2 events**:
  one (a), one (b).

Rule of thumb: **count agent paragraphs/bullets that target distinct
citations or distinct work clusters, not the works inside them**.

### Why this convention

Counting works inside a cluster inflates events for citation-rich domains
(intros, related-work) and deflates events for citation-sparse domains
(method, results). Counting intents normalizes across artifact types.

---

## 3. The four event types (with R1.7-specific examples)

| Type | Definition | Example from pilot package |
|---|---|---|
| **(a)** | Flags a specific citation as missing, wrong, mis-attributed, or mis-classified | "ScaNN is described as a graph-based approach. This is incorrect; ScaNN is a quantization+partitioning method." (pkg_05, ANN intro) |
| **(b)** | Names a specific work the artifact omits and explains why it matters | "HNSW (Malkov & Yashunin, 2018) is the most widely used graph-based ANN baseline and is conspicuously absent." (pkg_05) |
| **(c)** | Audits a specific citation's venue / year / authorship against the source | "DiskANN is Subramanya et al., 2019 in the text — please verify against the published record." (pkg_05) |
| **(d)** | Suggests a specific insertion with bibliographic precision (author + year + venue, or DOI-level detail) | "Consider citing Bentley 1975 and Dasgupta & Freund 2008 if you cite the others." (pkg_05; borderline — has author+year but no venue) |

### Borderline rules

- **Method-name only** (e.g., "R-GCN, CompGCN, HGT-style models") with no
  author/year: count as (b) **only if** the agent simultaneously explains why
  the omission matters in concrete terms ("the draft compares only against
  the authors' own GraphFlow-v1; without these comparators the contribution
  looks larger than it is"). Otherwise count as **0.5 event** and report it
  as such in `event_count` (no rounding). The 0.5 reporting value maps to
  s=2 in §4 (one borderline half-event).
- **"Please double-check your references"** without naming any specific
  citation: **NOT an event**. This is generic citation hand-waving; the
  anchor explicitly excludes it.
- **Praise of existing citations** ("the Wang et al. 2021 reference is
  appropriate"): **NOT an event** — the dim measures audit/insertion behavior,
  not endorsement.
- **Anonymized placeholder citations** ("Anonymous Authors et al., 2021")
  are a special case. If the agent **flags** the placeholder as a citation
  problem, count as (a). If the agent uses the placeholder as if it were a
  real reference without flagging, count as 0 events for that citation
  (the agent missed an obvious audit target — note this in rationale).

### Known borderline cases v1 does NOT yet resolve (be explicit in rationale)

These are unresolved by v1; raters should pick a position and *cite which
position they took* in the rationale field. v2 will fix the most common
disagreements after we observe peer data.

- **Many actions in one bullet**: a single bullet ("ScaNN mis-classified;
  HNSW absent; NSG description loose; DiskANN venue uncertain") could be 1
  intent-event (under cluster-as-1) or 4 distinct events (under
  bullet-action splitting). v1 default: count distinct *citations targeted*
  inside one bullet as separate events when each names a different work.
  Cluster-as-1 applies when one rhetorical move groups several works under
  one *argument* (e.g., "missing comparators"), not when it sequentially
  audits several works.
- **Family vs subfamilies**: "DiffDock-family methods" — is this one missing
  family (1 event) or several missing subfamilies (multiple)? v1 default:
  count as 1, since the agent named the family, not its members.
- **Author+year without venue as type (d)**: bibliographic-precision
  threshold for (d) is "author + year + venue, *or* DOI-level detail." v1
  treats author+year alone as 0.5 of (d), not full (d).
- **Citation-format flags vs scholarship audit**: agent flags "italics on
  *J. ACM* missing" or "use en-dash for page ranges." v1 default: NOT an
  R1.7 event (these are R1.6 writing-polish concerns). R1.7 measures
  *what* is cited and whether it is right, not how it is typeset.
- **"Cannot verify X" — type (a), (c), or uncertainty?** v1 default: count
  as 0.5 of type (c) if the agent named the specific citation. If the agent
  said "I cannot verify the references in this section" without naming any,
  it is NOT an event (anchor explicitly excludes generic hand-waving).
- **Axis-2 `wrong` vs `unverifiable_by_me`**: only mark `wrong` when you
  can cite the contradicting source by author+year. Absence of evidence
  ("I haven't read X") is `unverifiable_by_me`, not `wrong`.

---

## 4. The two-axis score (decoupled)

### Why decouple

Anchor `s=5` says "audits *every load-bearing citation against the source*."
Verifying "against the source" requires the rater to know the cited
literature. Most raters (including the author on most dims) lack this for
dims outside their specialty. Coupling action and correctness in one score
means an inexpert rater either (a) refuses to score, or (b) silently scores
"action only" and pretends correctness is verified — neither is sound.

We split the score into two axes:

- **Axis 1: Citation engagement (any rater can score)** — counts events under
  §2–§3 conventions. Anchor table below.
- **Axis 2: Correctness (expert rater only)** — for each event, was the agent
  *right*? Reported as a separate field, may be left blank.

### Axis 1 anchor table — *operational engagement score* (events → score)

> This table produces an **operational engagement score**, not a verdict on
> the original R1.7 anchor's "audits every load-bearing citation against the
> source" criterion. The Axis-1 score is a count-based proxy for whether the
> agent engaged the citation layer at all; verifying "against the source"
> belongs to Axis 2.

| event_count | score | description |
|---|---|---|
| 0 | **s=1** | No citation-level engagement. The output may be excellent on writing/method/claim-evidence, but it does not touch the citation layer. |
| 0.5 (borderline) | **s=2** | One ambiguous half-event (e.g., method-name listing without "why it matters"). |
| 1 clear | **s=3** | Exactly one clear event of type (a)/(b)/(c)/(d). |
| 1 clear + 1 borderline (= 1.5) | **s=3 by default; s=4 only if the borderline event is substantive** | When mixing clear and borderline, the score is set by the *clear* count (1 → s=3 row), not by the half-event sum. Escalate to s=4 only if the borderline event independently meets the "specific work + reason it matters" bar. Default = s=3. |
| 2–3 clear | **s=4** | Two or three clear events. |
| 4+ clear | **s=5** | Four or more events; reads as a citation audit covering the artifact's load-bearing citations. |

The rater *should* match this table mechanically, not eyeball "how good was
the citation review overall." If you find yourself scoring lower because a
high count "didn't feel like s=5," log that in the rationale and *still*
follow the table. Calibration drift is a known v1 issue (see §7) and we want
the table value, not the eyeball value.

### Axis 2 — correctness (optional, expert-gated)

For each event, mark one of:

- `correct` — the agent's flag/insertion is right; you have read the cited
  literature and can verify
- `wrong` — the agent's flag/insertion is provably wrong (e.g., the agent
  claims "HNSW absent" but HNSW is in fact cited two paragraphs later)
- `unverifiable_by_me` — the event is plausible but you lack the domain
  knowledge to confirm

Axis 2 is **post-hoc**. Submit Axis 1 immediately; Axis 2 can be filled in
later by a domain-expert pass over the same packages.

### How the two axes combine for paper reporting

The paper reports:
- `score_axis1` per (rater, package) — primary
- `correctness_rate` per (rater, dim) = fraction of events marked `correct`
  out of (`correct` + `wrong`); `unverifiable_by_me` excluded
- A package's "anchor-validated score" is reported only if at least one rater
  has axis-2 coverage on that package

This protects against the v1 failure where a high `score_axis1` could be
"the agent confidently invented a citation flag and the rater believed it."

---

## 5. Worked examples

### Example A — clean s=1 (pkg_04, PINN)

Agent output: "Light prose cleanup of the existing text — tightened sentences,
fixed minor awkwardness... I did not restructure sections, add or remove
technical claims, **or touch citations**."

- **Events**: 0 (the agent explicitly disclaims citation engagement)
- **Axis 1**: s=1
- **Axis 2**: N/A (no events to verify)
- **Rationale skeleton**: "Agent disclaims citation work ('did not... touch
  citations'). 0 events."

### Example B — clean s=5 (pkg_05, ANN intro / FastNav)

Agent output (excerpts):
1. "DiskANN is Subramanya et al., 2019 in the text — verify against the
   published record." → 1 event of (c)
2. "ScaNN... is described as a 'graph-based approach.' This is incorrect.
   ScaNN is a quantization+partitioning method." → 1 event of (a)
3. "HNSW (Malkov & Yashunin, 2018/2020) is the most widely used graph-based
   ANN baseline and is conspicuously absent." → 1 event of (b)
4. "NSG's contribution is typically described as constructing a Monotonic
   Relative Neighborhood Graph approximation with bounded out-degree, not
   'theoretical guarantees on graph navigability' in a generic sense.
   Tighten the description." → 1 event of (a)
5. "Consider citing Bentley 1975 and Dasgupta & Freund 2008 if you cite the
   others." → 1 borderline event of (d) (author+year, no venue)

- **Events**: 5 (4 clear + 1 borderline)
- **Axis 1**: s=5
- **Axis 2**: requires ANN literature knowledge to verify each. An ML
  retrieval researcher could fill this in; a non-specialist marks all as
  `unverifiable_by_me`.

### Example C — 1 clear + 1 borderline event (pkg_03, V2G/Lagrangian)

Agent output (excerpts):
1. "Citation of Achiam et al. (2017) appears miscast. The well-known Achiam
   et al. 2017 paper is *Constrained Policy Optimization* (CPO). CPO is itself
   a Lagrangian/trust-region method for CMDPs; it does not 'formalize
   horizon-invariant hard constraint enforcement.'" → **1 clear event of (a)**.
   Specific work named, specific mis-attribution argued.
2. "Citation of Chen et al. (2025) cannot be verified from the passage and
   the framing risks overclaim." → **0.5 borderline event of (c)**. The
   agent flags a verification need but does not complete the audit; this is
   a request for audit, not an audit.

- **event_count**: 1.5 (1 clear + 1 borderline)
- **Axis 1**: **s=3**. Rationale: §4 row "1 clear + 1 borderline (= 1.5)"
  maps to s=3 by default (the integer clear count is 1 → s=3 row). The
  borderline event does not meet the "substantive" bar to escalate to s=4.
- **Axis 2**: a constrained-RL researcher can verify event 1 (Achiam 2017
  IS CPO; the agent's flag is `correct`). Event 2 is `unverifiable_by_me`
  since the cited 2025 paper may not exist; the rater should NOT mark it
  `wrong` on absence-of-evidence alone.

### Example D — cluster-as-1 disagreement (pkg_01, DrugDock)

Agent output: "There is a sizable existing literature on ML-based binding
affinity prediction (DeepDTA, GNINA, DiffDock-family methods, EquiBind,
RoseTTAFold-AA, etc.), so 'first' is almost certainly false."

- Under §2 cluster-as-1 rule: **1 event** of (b). The intent is "name a
  missing comparator cluster," and the five works listed are all part of one
  rhetorical move.
- A naive item-as-each rater might count 5. The rationale **must explicitly
  cite the cluster-as-1 rule** if you choose this convention.

This package also illustrates the §3 placeholder-citation case: the artifact
contains "Anonymous Authors et al., 2021/2022" placeholder references and
the agent does not flag them. Note this in rationale ("agent missed obvious
placeholder-citation flag at lines X–Y").

---

## 6. When you cannot apply this protocol

This protocol is **insufficient** when:

- **The artifact has no citation events to act on** (cite=0, e.g., a method
  description or a scaling-result paragraph). In these cases every well-formed
  Axis-1 score will be `s=1`, which is correct but uninformative for r\*
  validity. The Stage 1 sample selection (§ Sample selection in
  `experiment_design_v1.3` §2.6) must filter for citation density ≥1 in the
  artifact; this is a *data-side* fix, not a protocol fix.
- **The rater has zero domain knowledge** of the artifact's literature. Axis
  1 is still applicable (counting events does not require expertise). Axis 2
  must be left blank; the rater should record this honestly rather than
  guess.
- **The dim is not R1.7**. The two-axis structure (action / correctness)
  generalizes to R1.4 (Novelty assessment) and R1.3 (Evidence-claim
  alignment), but the (a)/(b)/(c)/(d) event types are R1.7-specific. v2 of
  this protocol will provide per-dim event taxonomies.

---

## 7. Known limits of v1 (do not silently work around)

- **Score-event mapping calibration.** The author's pilot pass on the v2
  R1.7 form (6 packages) showed event counts aligned with §4's table, but
  scores systematically one step below the table value (5 events → score
  4.0 instead of 5.0; 2 events → score 2.0–2.5 instead of 4.0). v1 of this
  protocol asks raters to **follow the table mechanically**; we collect
  rater scores AND mechanical-table scores and report the gap.
- **Borderline (b) — method-name only**. The author and a hypothetical peer
  may disagree on whether "R-GCN, CompGCN, HGT" without author/year counts
  as (b). v1 fixes this with the §3 borderline rule (count as 0.5 event if
  "why it matters" is articulated; 0 otherwise). v2 may revise after peer
  data.
- **Axis 2 coverage will be sparse.** Most papers' R1.7 packages will have
  Axis 2 coverage on at most 1–2 events per package. We do not promise
  Axis-2 coverage as part of Stage 1 deliverables; it is a *separate*
  expert-pass deliverable.
- **Form-embedded anchor is empirically insufficient** *(2026-05-07/08
  finding, corroborated by 5-rater pre/post-protocol pass)*. The pre-
  protocol pass (rater A = paper author baseline + raters B, C = peers
  with form-embedded anchor only) showed score-event decoupling: peers
  B and C scored 4.0–4.5 across submitted event counts 2–6, including
  the pkg_04 case where the anchor reference count is 0; both failed
  the zero-event stress test. The post-protocol pass (raters D, E =
  peers who received this document separately and re-evaluated the
  same 6 packages) showed monotonic score-event alignment with the
  anchor table; both passed pkg_04 (s=1) and rater E reached the s=5
  row on pkg_05 — the only such score across the 5-rater set.
  **Implication for protocol use**: this document appears more
  reliably applied in this small post-protocol pass when read
  separately before the rating session than when only the form-embedded
  anchor is provided. Stronger claims would require a controlled trial. The
  form-embedded layer and the protocol-document layer are separable
  protocol-design moves. Candidate v2 mitigations are: (a) a 1–2 page
  handout summarising §2 and §3, sent ahead of the form link; (b) a
  1-package worked-example pre-rating step. The post-protocol pass
  also surfaced residual specifiability gaps (raters D, E disagree on
  cluster-as-1 application: pkg_01 D=0 vs E=1; both followed the
  protocol but diverged on its borderline rule), validating the §3.2
  "v1 does NOT yet resolve" subsection as forecasting real
  disagreement. See `human_annotation/recruitment/r17_v2_5_rater_analysis.md`
  F1–F5 for the empirical pattern this addresses.
- **Form-instruction-level mislabeling (secondary observation, layer-
  independent).** Across the 5-rater pre/post-protocol pass, 4 of 5
  raters did not match the form's `author/peer1/peer2` role dropdown,
  with mis-handling persisting from pre-protocol (rater B free-text;
  rater C mis-picked `author`) into post-protocol (rater D free-text
  again; rater E mis-picked `author` again); only rater A handled it
  correctly. Reading the dim-anchor
  protocol does NOT fix the form-instruction-level mislabeling — the
  two specifiability gaps live at different layers. This is secondary
  form-design evidence, not core to the boundary-condition claim.
  Candidate v2 form control: a closed role dropdown with no text-entry
  fallback, validated before the rating pages unlock.

These limits are documented in paper §VI rather than treated as TODOs.

---

## 8. Submission checklist

Before submitting Axis 1 for a package:

- [ ] You re-read the anchor on §3/§4 of THIS document (not just the form's
      embedded anchor) at least once during the session.
- [ ] Your `event_count` matches the cluster-as-1 rule of §2.
- [ ] Your `score` matches the §4 table value for your `event_count`.
- [ ] Your `rationale` quotes or paraphrases the agent output for at least
      one event (12–600 chars).
- [ ] If you applied a borderline rule from §3, you cited the rule explicitly
      in your rationale.
- [ ] If you skipped Axis 2, you noted "Axis 2 deferred — `unverifiable_by_me`"
      somewhere in the rationale.
