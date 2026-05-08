# R1.7 sb1 invitation messages — for Prolific message panel

> Send via Prolific researcher dashboard → R1.1 sb2 → Submissions → click rater → "Message participant".
> Each rater gets the COMMON intro + their individual specific note.
> Refine wording as needed.

---

## Common intro (send to all 3)

```
Thank you again for your work on the R1.1 (Conceptual Reconstruction) study.

I'm the researcher running this pilot, and I really appreciated the care and thoughtfulness in your previous responses. Based on that, I’ve opened a new small sub-batch on a different dimension: R1.7 (Citation and Scholarship).

This is a single 6-rating session, expected to take around 45 minutes, with a £9 reward. I’ve added you to the custom allowlist for this batch.

One important note: R1.7 uses different anchor verbs from R1.1. In particular:

s=1 — No citation-level engagement
s=3 — Flags one missing or wrong citation
s=5 — Audits every load-bearing citation against the source. Flags missing key works in the relevant cluster. Suggests insertions with bibliographic precision.

Please re-read the anchor carefully on each rating page, since the citation rubric is quite different from the conceptual reconstruction rubric
Thanks again — I’d be very happy to have your input on this next round.
```

---

## Individual specific notes

### To 697a707c07e72a894f55e3b8
```
One specific note: I appreciated that your R1.1 rationales were closely tied to the anchor descriptions.

For R1.7, please add one extra step: quote specific phrases from the agent output in your rationale whenever possible. The anchor verbs for this task — “audits,” “flags,” and “suggests insertions” — are quite precise, so quoting the exact agent phrasing helps clarify borderline cases.

For example:

“The agent flags ‘Anonymous Authors et al., 2021’ as a placeholder citation, which matches the s=3 anchor. However, it does not audit the other load-bearing claims against their sources or suggest insertions with full author/year/venue precision, so the s=5 anchor is not fully met. Score: 3.5.”

Thanks again — this would be very helpful for interpreting the ratings.
```

---

### To 6928a36e509f66538a9dc672
```
Specific note for you: your R1.1 rationales identified deep technical contradictions, such as the lock-free vs. pthread inconsistency and the policy-gradient REINFORCE method being described under a “value-based” label. That was exactly the kind of careful reading I was hoping to see.

For R1.7, please apply the same level of attention to citations. In particular, please flag specific citations the agent missed or attributed incorrectly, using author/year/venue precision when possible.

If the agent claims novelty for a mechanism that prior work already established, please identify the missing work and explain why it matters. This may fall under the s=5 anchor for “flags missing key works in the relevant cluster.”
```

---

### To 69809013aa657927169c5b0f
```
Specific note for you: your R1.1 rationales were structured and diagnostic — your comment that one response was “primarily diagnostic, offering general suggestions without reconstruction” was a sharp distinction.

R1.7 uses a similar discriminating logic. The s=5 anchors focus on whether the agent audits load-bearing citations and suggests insertions with bibliographic precision.

Please focus on substantive citation engagement rather than surface-level formatting. If the agent only comments on commas, italics, en-dashes, or other formatting issues without identifying missing, incorrect, or unsupported citations, that should generally be treated as a lower-anchor case.

Thanks again — I’d be glad to have your judgment on this round.
```

---

## Sending checklist

- [ ] R1.7 sb1 study published (currently UNPUBLISHED — publish first)
- [ ] Confirm reward £9 + custom_allowlist with 3 PIDs (already patched)
- [ ] Send common intro + individual note to each of 3 raters
- [ ] Wait for Prolific platform review (12–24h) → study goes live → 3 raters notified

## Estimated cost

- 3 raters × £9 reward × 1.33 fee + VAT (~20%) ≈ **£43** out of pocket
- Compared to original 5-rater plan (~£60): saves ~£17 + higher quality data
