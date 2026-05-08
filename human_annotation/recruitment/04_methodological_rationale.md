# Methodological Rationale — Why blind paid annotation, not in-network volunteers

> Internal note for the paper §VI-A "Annotation reliability" subsection. Records the reasoning behind choosing Prolific paid annotation over recruiting acquaintances/colleagues. Use this as the source for the reviewer-defense paragraph in v2.0.

---

## The decision

Stage 1 (R1.7 reliability rescue) uses **5 Prolific-recruited annotators with screening-task qualification**, not in-network volunteers (colleagues, students, the author's lab).

---

## Why this matters for paper §VI-A

The original paper's pass-3 plan was "20 stratified examples × 2 humans" (CHANGELOG entry, 2026-05-03). The most natural execution is "ask 1–2 colleagues." The reviewer Critical-6 in `review/main_paper_review_1st.md` already flagged that the author was 1 of 3 raters in pass-1, creating ground-truth leakage. Substituting "colleague-rater" for "author-rater" partially addresses this, but introduces a different and equally exploitable confound: **social-relational bias**.

---

## Three confounds that in-network annotation introduces

### 1. Social-relational bias (impossible to disclose)

A colleague who knows the author is asked to score a subjective dimension like R1.7. The colleague has incentive to converge with the author's expected scoring distribution — not because of bad faith, but because of unconscious calibration to "what would my friend think is reasonable."

This bias is **not measurable**. The author cannot declare "I asked my friend who scored independently of our relationship" and expect a reviewer to accept it. The very act of asking introduces the bias.

### 2. Rubric-question paralysis (asymmetric clarification)

When a colleague reads the anchor and is unsure, they ask the author: "what did you mean by 'bibliographic precision' here?" The author answers, and the colleague's score becomes a function of the author's clarification — not of the anchor as written. This breaks the load-bearing property of the spec (`spec_evaluation_rubric_v1.0` §6.3): "Human annotators do not see r*."

Paid blind annotators **cannot ask the author**. They must rely on the anchor text alone. This is exactly the test we want — does the anchor stand on its own, or does it require live disambiguation? If it requires live disambiguation, the dim is not a stable measurement instrument and should not anchor a paper claim.

### 3. Sample-size and distributional bias

Korean-speaking annotators with the requisite English fluency, ML background, and willingness to score 60+ ratings is a pool of ~5 individuals known to the author. This is a small, non-random, professionally-overlapping sample. Any α from such a sample reflects the consensus of that specific subculture, not a property of the rubric.

Prolific filtered pool (English first language, Master's+, ML background, approval rate ≥95%, ≥50 prior studies) is at least 1–2 orders of magnitude larger and is randomly assigned to the study. The α calculated on this pool generalizes to "what trained but external English-speaking annotators agree on."

---

## What the paper §VI-A v2.0 should say (draft text)

> **Annotation reliability validation.** To address the concern that
> author involvement in pass-1 annotation (§VI-A2) introduces ground-
> truth leakage [reviewer concern, internal review], pass-3 was
> conducted with five external annotators recruited via Prolific
> (https://www.prolific.com), filtered for English first language,
> Master's degree or higher, and ≥95% prior approval rate. Annotators
> were blind to: r*, engineered_flaws, agent identity, prior LLM judge
> scores, and the dataset author's identity. Each annotator passed a
> two-task calibration screening (one expected-low, one expected-high
> example) before scoring; submissions failing calibration (|error| >
> 1.5 on either example) received partial payment and were excluded
> from analysis.
>
> This recruitment design prevents three confounds that in-network
> annotation would otherwise introduce: social-relational bias toward
> the author's expected scoring distribution, asymmetric clarification
> in which the annotator can resolve rubric ambiguity by asking the
> author, and small-sample distributional bias in the author's
> immediate professional network. Krippendorff's α is reported across
> three rater configurations: external-only (n=5), external + author
> (n=6), and external + 3 LLM judges (n=8); cross-configuration
> agreement is examined for stability.

---

## What the paper §VII (limitations) should add

> The Prolific recruitment choice introduces its own limitation: paid
> annotators have weaker domain expertise than would-be domain experts.
> For the R1.1 (conceptual reconstruction) and R1.4 (novelty) dimensions
> in particular, this may reduce the ceiling of achievable α regardless
> of rubric quality. Pass-4 in main run will sub-stratify a 5-example
> subset for domain-expert annotation (recruited from the relevant
> conference's reviewer pool) to test whether the Prolific-vs-expert
> α gap is dim-dependent.

---

## What this implies for §VIII (conclusion)

The decision to validate reliability with blind paid annotators rather than colleague volunteers should be presented as a **methodological strength**, not a workaround. Specifically: it is the only design that allows R1.7's α to be reported as a property of the rubric anchor rather than a property of the author's social network.

A short sentence in §VIII conclusion:

> The reliability validation in §VI-A, in particular, demonstrates that
> R1.7's reliability gap (α = ...) is a property of the dimension's
> anchor text and not of the specific raters involved — a distinction
> that in-network annotation could not have established.

---

## What goes in supplementary material (for reviewers who want full transparency)

- The Prolific job description (`recruitment/01_prolific_job.md`)
- The screening calibration task and pass criteria (`recruitment/02_screening_task.md`)
- The full Google Form structure (`recruitment/03_form_template.md`)
- Distribution of annotator backgrounds (Prolific provides anonymized demographic summary post-study)
- Per-annotator α decomposition (which annotator's exclusion/inclusion most changes α — sensitivity analysis)

These supplementary files exist as the recruitment kit in `human_annotation/recruitment/`.

---

## Why this matters more than just defending one paper

This methodology — using paid blind annotation with calibration screening for sub-rubric reliability validation — is itself a small contribution. The dominant pattern in the LLM-judge-evaluation literature is either (a) pure LLM panels with no human ground truth, or (b) author-recruited expert annotators. The Prolific + calibration-screening design occupies a middle ground that is reproducible across labs and does not depend on the author's professional network.

If this design becomes the methodological backbone of the paper's reliability arguments, it generalizes beyond R1.7 — any future researcher applying `J_v1.1` to a new artifact domain can replicate the reliability validation step exactly.

---

## Cross-reference

- Strategic decision recorded in: `docs/CHANGELOG.md` (entry to be added when Stage 1 completes)
- Recruitment kit: `recruitment/` (this folder)
- Sanitized example packages: `texts/`
- Original spec: `docs/spec_evaluation_rubric_v1.0.md` §6.3 (will be bumped to v1.1 to reflect half-step grid + Prolific protocol when Stage 1 ramps up)
