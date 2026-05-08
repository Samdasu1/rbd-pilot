# Google Form Structure Template

> Use this when building the form in forms.google.com. Each `[H2]` is a Google Form section break (page break).

---

## [H2] Section 1 — Introduction & Agreement

### Form section title

```
Welcome — Please read before starting
```

### Section description (shown to annotator)

```
Thank you for accepting this study. Below is what you will do, what we
ask of you, and what you will be paid. Please read fully before clicking
"Next."

WHAT YOU WILL DO

You will read 18 short outputs (~600 words each) produced by AI agents
that were asked to review academic paper sections. For each output, you
will assign a score on a single dimension — citation quality (R1.7) —
on a 1.0 to 5.0 scale (in 0.5 increments).

Before the main ratings, you will complete 2 short calibration tasks
(~10 minutes total) so we can verify the rubric is being interpreted
consistently. If your calibration scores are too far off, the study
ends early with partial payment (USD 3 instead of USD 15).

Total time: ~90 minutes. Reward: USD 15.

WHAT YOU MUST NOT DO

  - Do not share the texts, agent outputs, or rubric anchors outside
    this study (this is pre-publication internal research material).
  - Do not consult external sources to "look up" what the right answer
    should be. We need YOUR judgment based on the rubric anchors only.
  - Do not copy/paste the same rationale across ratings. Each rationale
    must specifically reference the agent output you are scoring.
```

### Required field

| Type | Required | Label |
|---|---|---|
| Checkbox | ✅ | "I have read the above and agree to these conditions." |

### Required field (for cross-checking with Prolific)

| Type | Required | Label |
|---|---|---|
| Short text | ✅ | "Your Prolific ID (24 chars, copy-paste from Prolific)" |

---

## [H2] Section 2.1 — Calibration A

### Form section title

```
Calibration 1 of 2
```

### Section description

```
Below is one example. Read the artifact (the original paper section)
and the agent output, then score the agent's output on dimension R1.7
using the anchor text shown.

This calibration ensures we share an interpretation of the rubric
before you start the main ratings.
```

### Embedded content (paste verbatim from `02_screening_task.md` "Calibration A")

- Delegation
- Artifact
- Agent output
- R1.7 anchor

### Required fields (same per-rating format)

| Type | Required | Label | Validation |
|---|---|---|---|
| Dropdown | ✅ | "Score (1.0 to 5.0, 0.5 increments)" | options: `1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0` |
| Long text | ✅ | "Rationale (must quote or paraphrase the agent output)" | min 12 chars, max 600 chars |
| Dropdown | ✅ | "Confidence (0.0 to 1.0)" | options: `0.0, 0.1, 0.2, ..., 1.0` |
| Short text | optional | "Blockers (only if output is empty/wrong language/adversarial)" | max 240 chars |

---

## [H2] Section 2.2 — Calibration B

Same structure as Section 2.1, with content from `02_screening_task.md` "Calibration B".

---

## [H2] Section 2.3 — Calibration result routing (HIDDEN LOGIC)

This is not a visible section — it's a Google Form **conditional branching** rule.

In Google Form: go to the score field of Calibration A and B → "Add section based on answer"

| If | Action |
|---|---|
| `Cal_A score > 2.5` OR `Cal_A score < -0.5` (impossible — clamp to 0) | Route to Section 4 (early-end thank-you) |
| `Cal_B score < 3.5` | Route to Section 4 (early-end thank-you) |
| Otherwise | Continue to Section 3 |

**Note**: Google Form's conditional logic is limited (single-question branching). For the AND/OR combination above, you may need either:
- (a) Use **Apps Script** to compute branching after submission of Section 2.2, OR
- (b) Simplify to: "If `Cal_A score ≥ 3` → end" AND "If `Cal_B score ≤ 3` → end" using two separate single-question branches in series.

Option (b) is simpler. The pass criteria become:
- Cal_A score ≤ 2.5 (i.e., annotator scored A correctly low)
- Cal_B score ≥ 3.5 (i.e., annotator scored B correctly high)

---

## [H2] Section 3 — Main rating loop

### Section title

```
Main rating tasks (18 total)
```

### Section description (shown once at top)

```
You passed calibration. The remaining 18 ratings each follow the same
format as the calibration tasks.

For each rating:
  1. Read the artifact and agent output (linked at the top of each page).
  2. Score on R1.7 using the anchor.
  3. Write a rationale that quotes or paraphrases the agent output.
  4. Estimate your confidence.

You may take breaks between ratings (Google Form preserves your
progress). When you finish all 18, you will see your completion code
on the final page.
```

### Per-rating page structure (replicate 18 times — one page per rating)

| Field | Type | Required | Notes |
|---|---|---|---|
| (display only) | Header | — | "Rating 3 of 18 — example_id: ad_r1_026 / condition: direct" |
| (display only) | Link | — | "Open the package (read-only): [GitHub Gist URL]" |
| (display only) | Image or text | — | (Optional) embed the active set + R1.7 anchor again for convenience |
| Score | Dropdown | ✅ | `1.0, 1.5, ..., 5.0` |
| Rationale | Long text | ✅ | min 12 chars, max 600 chars |
| Confidence | Dropdown | ✅ | `0.0, 0.1, ..., 1.0` |
| Blockers | Short text | optional | max 240 chars |

**The R1.7 anchor text should be visible on every rating page** — annotators must not flip back to remember it. Either embed it in the page text or use a Google Form image of the anchor block.

---

## [H2] Section 4 — Completion (full payment OR early-end partial payment)

### If main ratings completed (18/18):

```
Thank you for completing the study.

Your full completion code is:

   ┌─────────────────────┐
   │   {COMPLETION_CODE} │
   └─────────────────────┘

Please copy this code and paste it on the Prolific submission page to
receive your full payment of USD 15.

We will manually review your submissions before approving payment
(usually within 48 hours). If you have any questions, contact:
{researcher_email}
```

### If routed from Calibration failure:

```
Thank you for participating.

Your calibration scores were outside the expected range, so the study
ends here for you. You will be paid USD 3 (partial payment) for the
calibration time.

Your partial completion code is:

   ┌─────────────────────┐
   │   {CALIBRATION_CODE}│
   └─────────────────────┘

Please paste this code on the Prolific submission page to receive
partial payment.

We appreciate your time.
```

---

## Google Sheet column structure (auto-populated)

When responses come in, Google Form automatically pushes to a linked Sheet with these columns (each row = one annotator's full response):

```
Timestamp | Prolific ID | Cal_A score | Cal_A rationale | Cal_A confidence | Cal_B score | Cal_B rationale | Cal_B confidence | Rating_1_score | Rating_1_rationale | Rating_1_confidence | Rating_1_blockers | ... (× 18) | Completion_code
```

For analysis, this wide-format sheet should be melted to long format:

```
prolific_id | example_id | condition | dim | score | rationale | confidence | blockers | timestamp
```

A short Python script (pandas melt) can do this in 5 lines. Optional: add this script to `recruitment/05_response_processing.py` after first batch.

---

## Form-building checklist

Before publishing the form:

- [ ] All 18 main ratings have unique `example_id` and `condition` in the page header
- [ ] All 18 main ratings link to the correct Gist URL (test each link)
- [ ] R1.7 anchor visible on every rating page
- [ ] Conditional branching from calibration → tested with mock answers
- [ ] Both completion codes (full + partial) embedded correctly in Section 4
- [ ] Auto-Sheet linked
- [ ] Email collection DISABLED
- [ ] Response editing DISABLED
- [ ] Form set to "Anyone with link" (no Google login required)
- [ ] Test the entire form yourself end-to-end before posting on Prolific

---

## Time estimates per section

| Section | Annotator time |
|---|---|
| 1 — Intro + agreement | 3 min |
| 2 — Calibration (2 examples) | 10 min |
| 3 — Main ratings (18 × ~4 min) | 72 min |
| 4 — Completion | 1 min |
| **Total** | **~86 min** |

Reward USD 15 → ~$10/hour. Within Prolific's recommended range.
