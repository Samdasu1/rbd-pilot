# Calibration Screening Task

> 2 calibration examples shown at the start of the Google Form before any rating tasks. Annotator must score each within ±1.5 of the expected score; otherwise study ends with partial payment.

> Purpose: filter out annotators who cannot interpret the rubric anchors, before they pollute the main ratings.

---

## How it appears in the form

After Section 1 (intro + agreement), Section 2 has two pages:

- Page 2.1 — **Calibration A** (expected to score very low: ~1)
- Page 2.2 — **Calibration B** (expected to score very high: ~5)

Each page has the same fields as a real rating page:

```
example_id  : (cal_A or cal_B)
condition   : calibration
dim         : R1.7
score       : ___       (1.0–5.0, 0.5 increments)
rationale   : ___       (12–600 chars)
confidence  : ___       (0.0–1.0)
```

After Page 2.2 submission, the form silently calculates `|score_A - 1| + |score_B - 5|`. If either |error| > 1.5, the form skips Section 3 (main ratings) and routes directly to a "thank you, partial payment" page.

If both pass: Section 3 (main ratings) opens.

---

## Calibration A — expected score ~ 1

### Delegation

```
Review this section.
```

### Artifact (verbatim)

```
We propose NeuralCompress, a learned compression algorithm for image
streams. Our method uses a transformer-based encoder paired with an
arithmetic coder. We train on the JPEG-AI dataset (Anonymous Authors
et al., 2023) and evaluate on the Kodak dataset.

Our experimental results demonstrate that NeuralCompress achieves
state-of-the-art compression ratios. Specifically, we obtain bits-per-
pixel of 0.42 on Kodak, outperforming JPEG2000 by 18% and HEVC by 11%.
The model has 240M parameters and runs at 120 FPS on an A100 GPU.

We position NeuralCompress as a step toward practical neural
compression deployment.
```

### Agent output (verbatim)

```
**Summary:** Reviewed and lightly polished the section.

The writing flows well overall. Here are some suggestions:

- The phrasing "step toward practical neural compression deployment"
  could be tightened to "a practical neural compression method."
- The numerical results section reads cleanly but could benefit from
  a leading topic sentence.
- The transition between paragraphs 2 and 3 is slightly abrupt.

The contribution is clearly stated and the experimental claims appear
well-supported within the paper's scope. Overall this is a solid draft.
```

### R1.7 anchor (the active set)

```
s=1  No citation-level engagement.
s=3  Flags one missing or wrong citation.
s=5  Audits every load-bearing citation against the source. Flags
     missing key works in the relevant cluster. Suggests insertions
     with bibliographic precision.
```

### Expected score

**~ 1.0** (acceptable range: **1.0 to 2.5**)

### Why

The agent output makes zero citation-level engagement. It comments on phrasing, transitions, and topic sentences. It does not flag the "Anonymous Authors et al., 2023" placeholder, does not note the missing JPEG2000/HEVC baseline citations, and does not suggest any insertions. Per anchor s=1: "No citation-level engagement." This is a clear 1.

A score of 2 would be defensible if the annotator argues that the closing sentence ("experimental claims appear well-supported within the paper's scope") loosely touches on evidence-citation alignment — but that's a stretch for R1.7 specifically.

A score of ≥ 3 indicates the annotator did not read the anchor. → reject.

---

## Calibration B — expected score ~ 5

### Delegation

```
Review this section.
```

### Artifact (verbatim)

```
We introduce DeepFold, a graph neural network for protein structure
prediction that operates on amino acid sequence input. Our architecture
combines a transformer-based sequence encoder with an SE(3)-equivariant
graph refinement module.

Compared to AlphaFold2 (Jumper et al., 2021), DeepFold achieves
comparable accuracy on CASP15 targets while using 40% fewer parameters.
On the held-out test set, we obtain a mean GDT-TS of 0.81, which is
within 2% of AlphaFold2's reported 0.83.

We position DeepFold as a more parameter-efficient alternative for
protein structure prediction tasks.
```

### Agent output (verbatim)

```
**Summary:** Audited all load-bearing citations against the literature
and identified two critical scholarship gaps. Provided specific
bibliographic suggestions.

## Citation audit

The section cites only AlphaFold2 (Jumper et al., 2021) as a
comparison point. This is a load-bearing claim because the paper
positions itself as a "more parameter-efficient alternative." For
this claim to hold, the related work must include the canonical
parameter-efficient and equivariant predecessors:

1. **MISSING — RoseTTAFold** (Baek et al., Science 376:871, 2021).
   Equivalent in scope to AlphaFold2 and frequently cited as a
   smaller-architecture alternative. Should be inserted alongside
   AlphaFold2 in paragraph 2. Suggested citation:
     Baek M, et al. "Accurate prediction of protein structures and
     interactions using a three-track neural network." Science 376
     (6557): 871-876, 2021.

2. **MISSING — ESMFold** (Lin et al., Science 379:1123, 2023).
   Specifically a parameter-efficient alternative to AlphaFold2 (15B
   parameters but no MSA dependency). Directly competes with the
   paper's positioning claim. Should be in paragraph 1 or 2.
   Suggested citation:
     Lin Z, et al. "Evolutionary-scale prediction of atomic-level
     protein structure with a language model." Science 379 (6637):
     1123-1130, 2023.

3. **REVIEW — Jumper et al., 2021 attribution**. The paper attributes
   GDT-TS 0.83 to AlphaFold2 without specifying which CASP iteration.
   AlphaFold2's CASP14 results are 0.92 GDT-TS; CASP15 results are
   reported separately by the AlphaFold team in a follow-up
   (Jumper et al., 2022 ICML workshop paper). Citation should
   distinguish.

4. **REVIEW — SE(3)-equivariance lineage**. The architecture
   description claims SE(3)-equivariant graph refinement but does not
   cite Fuchs et al., 2020 (SE(3)-Transformers, NeurIPS) or
   Satorras et al., 2021 (E(n)-Equivariant GNN, ICML), which
   originated this design pattern. Required for novelty positioning.

## Recommended insertions

Paragraph 2, after "(Jumper et al., 2021)":
  "...AlphaFold2 (Jumper et al., 2021) and the parameter-efficient
  ESMFold (Lin et al., 2023) and RoseTTAFold (Baek et al., 2021)..."

Methods section (where SE(3)-equivariant module is described):
  Add citations to Fuchs et al., 2020 and Satorras et al., 2021.

## Summary of impact

Without ESMFold and RoseTTAFold citations, the "more parameter-
efficient alternative" claim is unsupported — the natural readers
(structural biologists) will immediately identify these as the
standard parameter-efficient comparisons.
```

### R1.7 anchor

```
s=1  No citation-level engagement.
s=3  Flags one missing or wrong citation.
s=5  Audits every load-bearing citation against the source. Flags
     missing key works in the relevant cluster. Suggests insertions
     with bibliographic precision.
```

### Expected score

**~ 5.0** (acceptable range: **3.5 to 5.0**)

### Why

The agent output satisfies all three s=5 verbs:

- **Audits every load-bearing citation against the source**: the existing AlphaFold2 citation is cross-referenced against actual GDT-TS values, and the SE(3)-equivariant claim is checked against the canonical literature.
- **Flags missing key works in the relevant cluster**: ESMFold and RoseTTAFold are flagged as canonical missing baselines; SE(3)-Transformers and E(n)-EGNN are flagged for the architecture lineage.
- **Suggests insertions with bibliographic precision**: full bibliographic format is given (author, title, journal, volume, pages, year) for both ESMFold and RoseTTAFold.

A score of 4 would be defensible if the annotator argues that not every load-bearing claim in the section has been audited (e.g., the "40% fewer parameters" comparison was not examined). That's a fair partial-deduction.

A score of ≤ 3 indicates the annotator did not read either the output or the anchor. → reject.

---

## Pass / fail computation

```python
# pseudocode
err_A = abs(score_A - 1.0)
err_B = abs(score_B - 5.0)

if err_A > 1.5 or err_B > 1.5:
    route_to_partial_payment_page()
    # Annotator paid USD 3 instead of USD 15
else:
    route_to_section_3_main_ratings()
```

---

## What annotator sees on the partial-payment page

```
Thank you for participating.

Your calibration scores were outside the expected range, which suggests
the rubric anchors may not have been interpreted as we expected. The
study ends here for you, but you will receive partial payment (USD 3)
for the calibration time.

Please enter this completion code on Prolific to receive your partial
payment: [CALIBRATION_CODE]

We appreciate your time.
```

(`CALIBRATION_CODE` is a separate Prolific code distinct from the main completion code, so the researcher can distinguish full vs partial submissions in Prolific's dashboard.)

---

## Why these specific calibration examples

- **A scores low**: tests whether annotator reads the anchor literally. The output is not "bad" overall — it gives reasonable polish suggestions — but it does NOT engage with citations. An annotator who scores it 3+ is using a holistic "is this a good review?" heuristic instead of the dim-specific anchor. We need anchor-specific scoring.

- **B scores high**: tests whether annotator can recognize all three s=5 verbs being satisfied. An annotator who scores it 3 is treating "flagging citations" as the highest possible behavior, missing that "bibliographic precision" and "audit every claim" are additional anchor requirements.

These two examples cover the most common failure modes: (1) ignoring the anchor and using global judgment, (2) capping at "intermediate" and not recognizing exemplary work.

---

## Maintenance

If the calibration pass rate drops below 50% across batches:
- Re-examine whether the anchors themselves are too ambiguous (R1.7 dim's known α=0.219 problem)
- Loosen pass criteria from ±1.5 to ±2.0
- Add a third calibration example targeting a 3.0 score to better train the middle range
