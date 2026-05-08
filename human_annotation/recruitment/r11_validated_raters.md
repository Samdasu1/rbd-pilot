# R1.1 Prolific salvage — validated rater allowlist (2026-05-07)

> Closed allowlist of Prolific raters who passed quality screening on R1.1 sub-batches sb1 and sb2 of the v1.3 Stage 1 plan. Used as the default invitee pool for any future R1.x Prolific stage that requires R1.1-style scoring. Established as part of the 2026-05-07 Stage 1 closure (CHANGELOG entry of that date).

## Pool summary

| metric | value |
|---|---|
| total rater attempts (sb1 + sb2) | 9 |
| validated (added to closed allowlist) | **3** (697a707c, 6928a36e, 69809013) |
| approved-but-not-allowlisted | 1 (69fb482a — submission accepted, but rationale style was not strong enough to be re-invited for higher-stakes work) |
| rejected (Prolific reject) | 3 (699f458a, 69f01b94, 69e8fcc1) — see reject taxonomy below |
| dropped out / timed out | 2 (no submission; no record kept) |
| pass rate (validated / total attempts) | **3 / 9 ≈ 33%** |
| out-of-pocket cost | ~£100 (all of which is recorded as Stage 1 actual spend in `experiment_design_v1.3` §3) |

The 33% pass rate is the empirical input to the §VI #4 cost-projection caveat in `paper_master_v1.3` (the planned 270-rating breadth would imply ~£550–800 gross recruitment exposure under the same pass rate, vs. the v1.3 plan's ~$300 estimate that did not condition on pass rate).

## Validated raters (closed allowlist)

These 3 raters are the closed pool to invite for future R1.x Prolific stages:

| Prolific ID | strengths observed (from R1.1 rationale review) |
|---|---|
| `697a707c07e72a894f55e3b8` | rationales were closely tied to the anchor descriptions; consistent dim-anchor application |
| `6928a36e509f66538a9dc672` | identified deep technical contradictions (e.g., lock-free vs. pthread inconsistency; policy-gradient REINFORCE described under a "value-based" label) |
| `69809013aa657927169c5b0f` | rationales were structured and diagnostic; the "primarily diagnostic, offering general suggestions without reconstruction" framing was a sharp distinction call |

> Per-rater allowlist rationale notes are reproduced verbatim from `stage1_r17_invitation_messages.md` (which was the operational invitation template generated when R1.7 sb1 was being prepared, before that batch was withdrawn as part of the 2026-05-07 Stage 1 closure).

## Approved-but-not-allowlisted

| Prolific ID | reason for non-allowlist |
|---|---|
| `69fb482a...` | sb2 submission was accepted on Prolific (full reward paid), but rationale quality was below the bar for future invitations. Recorded here for traceability; will not be invited for higher-stakes work. |

## Reject taxonomy (3 rejected raters)

The 3 rejections follow the Prolific reject category set we adopted in the v1.3 plan (FAILED_INSTRUCTIONS / MALINGERING / LOW_EFFORT). The dominant patterns observed:

| Prolific ID | category | observed signature |
|---|---|---|
| `699f458a...` | FAILED_INSTRUCTIONS or MALINGERING (AI-assisted suspicion) | rationales had AI-assistant register + low typo count + uniform score distribution |
| `69f01b94...` | LOW_EFFORT or MALINGERING | very short rationales not tied to specific agent output spans; time-on-task ~15 min for a session designed at 45 min |
| `69e8fcc1...` | LOW_EFFORT | rationales essentially restated the form question without engaging the agent output |

Per-rater specific reject messages were composed and sent through the Prolific dashboard at the time of rejection; they are not reproduced here verbatim (the dashboard retains them).

## Drop-outs / time-outs

2 raters initiated a session but did not complete (no Prolific submission). No record retained beyond Prolific's own log; not relevant for allowlist purposes.

## Provenance

- v1.3 plan called for R1.1 sb1, sb2, sb3 (each 5 raters × 9 examples × 2 conditions = 90 ratings) for ~$300 total spend. Actual: only sb1 and sb2 were run before the closure; sb3 was deleted (Prolific draft + Google Form deleted 2026-05-07).
- Rater allowlist was established on the way to preparing R1.7 sb1 invitations (before R1.7 Prolific arm was itself withdrawn as part of the closure). The R1.7 sb1 study was patched to use this allowlist + £9 reward + 3-slot capacity, then deleted unpublished as part of the 2026-05-07 cleanup.
- Validation was done by author manual review of every submitted rationale across the 9 attempts. No automated scoring; the bar was "rationale references specific agent output spans + score-rationale consistency under the dim's anchor."

## Use policy

If a future R1.x stage needs Prolific-anchored ratings on R1.1 (or, conservatively, on dims with similar anchor structure to R1.1):

1. Default invitee pool = the 3 PIDs above.
2. New raters can be added but only after author review of a sample of their pilot submissions on a calibration set.
3. Re-invitation cost: same per-rating cost as the v1.3 plan (~$15 per dim batch per rater + 33% Prolific fee + 20% VAT).

## See also

- `docs/CHANGELOG.md` 2026-05-07 entry — Stage 1 closure context.
- `docs/paper_master_v1.3.md` §VI #4 — boundary-condition finding that the 33% pass rate informs.
- `human_annotation/recruitment/stage1_r17_invitation_messages.md` — original invitation copy (R1.7 sb1 was deleted; this file is retained for the per-rater rationale notes used above).
