# R1.7 v2 — 5-rater qualitative corroboration analysis (2026-05-07 / 2026-05-08)

> Standalone analysis of the 5 responses to the R1.7 v2 co-annotation form,
> partitioned into a *pre-protocol* group (raters submitted before the
> `rater_protocol_v1.md` document was distributed to them) and a
> *post-protocol* group (raters who received the protocol doc separately
> and re-evaluated the same 6 packages).
>
> This is the source doc behind the strengthened §VI #4 finding in
> `paper_master_v1.3.md`.
>
> Note: this is not a controlled trial. All 5 submissions used the **same**
> v2 form; the partition is by the rater's natural exposure to the protocol
> document, not by an experimental manipulation. We treat it as qualitative
> corroboration evidence, not as an inferential test.

## Form metadata

- Form ID: `1VpgZMt4wNlWD9Y8k-5fhuSZVUI5ifoAEgIRKzB640po`
- Responder URL: `https://docs.google.com/forms/d/e/1FAIpQLSffp-nBA3UaYoY7sOJ-Tjc9_jysJCodS48GT6QUZT3csXKB0Q/viewform`
- Packages: 6 (R1_7_v2_pkg_01..06)
- Anchor: sharpened citation-event-count decision tree (form description) +
  `event_count` (0–10) field per page.

## Raters (anonymized; chronological)

| label | submitted | role-field input | language | protocol exposure | notes |
|---|---|---|---|---|---|
| **rater A** | 2026-05-07 06:37 | `author` (matched dropdown) | KO | none — protocol doc not yet drafted | paper author's own first self-test; pkg_01 was excluded from primary alignment because rater A had consulted with the paper assistant on pkg_01 before scoring |
| **rater B** | 2026-05-07 08:22 | free-text label outside dropdown | KO | none — form-embedded anchor only | peer pass 1 |
| **rater C** | 2026-05-07 10:18 | mis-picked `author` from dropdown | EN | none — form-embedded anchor only | peer pass 2 |
| **rater D** | 2026-05-07 12:21 | free-text label outside dropdown | KO+EN | **rater_protocol_v1.md sent to rater before this submission** | post-protocol pass; rationales use protocol-specific markers `(a)/(c)` |
| **rater E** | 2026-05-08 03:05 | mis-picked `author` from dropdown | EN | **rater_protocol_v1.md sent to rater before this submission** | post-protocol pass; matches anchor table including the s=5 row (event_count=4 → score 5.0 on pkg_05) |

> rater A = paper author (one person); raters B, C, D, E = anonymized peers.
> The rater→identity map between B/C/D/E pairs (i.e., which post-protocol
> rater corresponds to which pre-protocol rater, if any) is **not asserted**.
> The findings below do not depend on resolving this.
>
> Personally identifying information (e.g., academic role written in free
> text) was stripped during anonymization.

## Score / event_count comparison (all 6 packages, all 5 raters)

| pkg | example | rater A | rater B | rater C | rater D | rater E | anchor reference |
|---|---|---|---|---|---|---|---|
| 01 | DrugDock priority claim (cluster-as-1 case; rater A excluded due to consultation) | 1 / 1.0 | 5 / 4.5 | 3 / 4.0 | 0 / 1.0 | 1 / 3.0 | 1 → s=3 |
| 02 | SentiBridge | 2 / 2.0 | 6 / 4.5 | 4 / 4.0 | 2 / 4.0 | 2 / 4.0 | 3 → s=4 |
| 03 | V2G/Lagrangian | 2 / 2.5 | 4 / 4.0 | 5 / 4.5 | 2 / 4.0 | 2 / 4.0 | 2 → s=4 |
| 04 | PINN — agent says *"did not... touch citations"* | **0 / 1.0** | **5 / 4.0** | **2 / 4.5** | **0 / 1.0** | **0 / 1.0** | **0 → s=1** |
| 05 | ANN/FastNav (s=5 case) | 5 / 4.0 | 6 / 4.0 | 6 / 4.0 | 3 / 4.5 | **4 / 5.0** | 5 → s=5 |
| 06 | GraphFlow (R-GCN/CompGCN/HGT cluster) | 0 / 1.5 | 5 / 4.0 | 4 / 4.0 | 1 / 3.0 | 1 / 2.0 | 1 → s=3 |

Bold cells are the pkg_04 zero-event stress test (raters A, D, E pass; raters B, C fail) and rater E's pkg_05 score (the only s=5 score across the full table — matches the anchor table's "4+ events → s=5" row).

## Findings

### F1. pkg_04 stress test — pre-protocol 1/3, post-protocol 2/2

The PINN package contains an agent output with the explicit disclaimer:
*"I did not restructure sections, add or remove technical claims, or touch
citations."* This is a definitional zero-event case under the sharpened
anchor.

Pre-protocol pass:
- **rater A** (author baseline, pre-protocol): 0 events / s=1 ✓
- **rater B**: 5 events / s=4.0 ✗ (counted prose-cleanup actions as events)
- **rater C**: 2 events / s=4.5 ✗ (counted retention of Wang et al. 2021 as
  an event — protocol §3 explicitly excludes "praise of existing citations")

Post-protocol pass:
- **rater D**: 0 events / s=1.0 ✓
- **rater E**: 0 events / s=1.0 ✓

Pass rate: pre-protocol 1/3, post-protocol 2/2. The two peers in the
post-protocol group both pass the pkg_04 zero-event stress test that the
two pre-protocol peers failed.

### F2. score–event mapping — pre-protocol decoupled, post-protocol monotonic

Submitted event-count vs submitted score, per rater across the 6 packages:

- **rater A** (pre-protocol baseline, author): submitted counts span 0–5;
  scores are near-monotonic (0→1.0–1.5; 2→2.0–2.5; 5→4.0). Anchor table
  values are reached at the low-count rows but the high-count rows score
  one step below the table (5 events → score 4.0 instead of 5.0).
- **rater B** (pre-protocol peer): submitted counts span 4–6; scores
  cluster at 4.0–4.5 across all packages. *Decoupled.*
- **rater C** (pre-protocol peer): submitted counts span 2–6; scores
  cluster at 4.0–4.5 across all packages, including the pkg_04 case where
  the anchor reference count is 0. *Decoupled.*
- **rater D** (post-protocol peer): submitted counts span 0–3; scores
  span 1.0–4.5. Score-event mapping is monotonic: 0→1.0 (twice),
  1→3.0, 2→4.0 (twice), 3→4.5. Closely matches the anchor table.
- **rater E** (post-protocol peer): submitted counts span 0–4; scores
  span 1.0–5.0. Mapping: 0→1.0, 1→2.0–3.0, 2→4.0, 4→**5.0**. Matches
  the anchor table including the s=5 row that no other rater reached.

The two post-protocol raters are the only raters whose score-event
mapping is monotonically aligned with the anchor table at both the low
end (zero-event → s=1) and the high end (4+ events → s=5).

### F3. cluster-vs-item counting (pkg_01, pkg_06)

- **pkg_01 (DrugDock)**: anchor cluster-as-1 rule → 1 event.
  - rater A = 1 (consistent with cluster-as-1, but pkg_01 was excluded
    due to prior consultation; reported here only for completeness)
  - rater B = 5 (item-as-each: counted DeepDTA / GNINA / DiffDock /
    EquiBind / RoseTTAFold-AA as 5 separate events)
  - rater C = 3 (intermediate)
  - **rater D = 0** (post-protocol; under-credited the cluster — applied
    the §3 borderline rule too strictly)
  - **rater E = 1** (post-protocol; cluster-as-1 applied correctly)

- **pkg_06 (GraphFlow R-GCN/CompGCN/HGT)**: anchor cluster-as-1 → 1
  borderline event (no author/year given for the missing comparators).
  - rater A = 0 (didn't credit; protocol §3 borderline rule treats this
    as 0–0.5)
  - rater B = 5; rater C = 4 (over-inclusive)
  - **rater D = 1** (post-protocol; counted the cluster, score = 3.0 →
    s=3 per anchor table)
  - **rater E = 1** (post-protocol; counted the cluster but identified
    the no-author/year flaw, score = 2.0 → s=2 per anchor table's
    borderline row — this is the protocol §3 borderline rule applied
    correctly)

The two post-protocol raters disagree with each other on the cluster
count for pkg_01 (D=0, E=1) but agree on pkg_06 (both =1). This
suggests cluster-as-1 is itself a borderline call that the protocol's
v1 §3.2 list correctly anticipated as "v1 does NOT yet resolve."

### F4. high-density agreement (pkg_05)

The ANN/FastNav package is the s=5 ground-truth case (4 clear events +
1 borderline insertion suggestion).

- rater A: 5 events / s=4.0
- rater B: 6 events / s=4.0
- rater C: 6 events / s=4.0
- rater D: 3 events / s=4.5
- **rater E: 4 events / s=5.0** ← only s=5 score across all 5 raters

The pre-protocol group (A, B, C) all submitted high event counts (5–6)
but capped scores at 4.0. Only the post-protocol rater E reached the
s=5 row of the anchor table. Rater D submitted a lower count (3) and a
corresponding 4.5 score, also closer to the anchor table than the
pre-protocol raters.

### F5. (NEW) Protocol-reading effect on score-event alignment

This is the central finding for §VI #4 strengthening.

Compared to the pre-protocol peer pass (raters B and C):

- **pkg_04 zero-event stress test pass rate**: 0/2 → 2/2 in post-protocol
  pass (raters D, E both pass).
- **Score-event monotonicity**: decoupled (B, C plateau at 4.0–4.5) →
  monotonic (D, E both close to anchor table).
- **s=5 row reached**: 0/3 pre-protocol (raters A, B, C) → 1/2 post-protocol
  (rater E pkg_05); 1/5 overall.
- **Rationale style change**: pre-protocol raters write generic praise
  /critique prose without invoking protocol categories; post-protocol
  raters use protocol-specific markers ("**1. (c):** 인용 오류" — rater
  D pkg_05; "no full citations (no authors or years)" — rater E pkg_06
  invoking the §3 borderline rule by name).

Caveats:
- n=2 in each group; not inferential. We report the *pattern*, not a
  hypothesis test.
- The post-protocol pass was not a controlled trial. Raters were sent
  the protocol document and asked to redo; they self-selected when to
  read and how thoroughly. The rater→rater identity map between
  pre/post pairs is not asserted.
- Score scaling remains imperfect even post-protocol: rater D's pkg_05
  is 3/4.5 (could be argued either way against the anchor table's 2–3
  → s=4 row); rater D's pkg_01 is 0 (applied cluster-as-1 too
  strictly, contradicting rater E who applied it correctly).

## Implications for paper §VI #4

The morning §VI #4 framing said:

> The pilot of [the planned 3-dim Prolific extension] surfaced a binding
> constraint that the plan itself did not anticipate.

The 2026-05-08 5-rater framing extends this:

> The boundary-condition is **partially mitigated by separately reading
> the rater_protocol_v1 document before the rating session**, not by
> the form-embedded sharpened anchor alone. Two post-protocol peers
> produced anchor-aligned score-event mappings on the same 6 packages
> where the two pre-protocol peers had decoupled. This supports — but
> does not inferentially validate — the v1 known-limit hypothesis that
> the form-embedded anchor is insufficient and a separately-read
> protocol document appears necessary in this small pass for reliable
> application.

Three load-bearing claims now in §VI #4:

1. **Specifiability ceiling at the form layer**: form-embedded anchor
   alone is insufficient (pre-protocol pass evidence).
2. **Specifiability partial mitigation at the protocol layer**:
   separately-read protocol document closes a substantial part of the
   gap (post-protocol pass evidence).
3. **Residual specifiability gap remains even after protocol-reading**:
   rater D vs rater E disagree on cluster-as-1 application (pkg_01:
   D=0, E=1). v2 of the protocol would need to sharpen the §3.2
   borderline list more prescriptively. Domain-expertise ceiling
   (Axis-2 correctness verification) is unresolved across all 5
   raters.

## Implications for `rater_protocol_v1.md`

The 5-rater data confirms two of the §7 known limits:

- **Form-embedded anchor is empirically insufficient** (now corroborated
  by pre/post-protocol contrast, n=2 each).
- **Form-instruction-level mislabeling** continues: 4 of 5 raters
  mis-handled the role dropdown across the 5 raters, with the
  mis-handling persisting from pre-protocol (rater B free-text; rater C
  mis-picked `author`) into post-protocol (rater D free-text again;
  rater E mis-picked `author` again); only rater A handled the dropdown
  correctly (matching it as `author`, which is also their actual role). Reading the dim-anchor protocol
  did **not** fix the form-instruction-level mislabeling, suggesting
  the two specifiability gaps are at different layers.

The §3.2 borderline list ("v1 does NOT yet resolve") is partially
empirically validated:
- Cluster-vs-item (pkg_01): post-protocol raters disagree (D=0, E=1).
- Method-name-only (pkg_06): post-protocol raters agree on count (1)
  but score differently (D=3.0, E=2.0) — protocol §3 borderline rule
  was applied differently. v2 should sharpen this.

## Implications for `experiment_design_v1.3.md` §2.6.3

The §2.6.3 reporting form (3-rater table) should be replaced with the
5-rater table above and the F1–F5 findings. Concrete numbers:

| reporting item | concrete value |
|---|---|
| pkg_04 zero-event-stress-test pass rate, pre-protocol | 1/3 (only rater A) |
| pkg_04 zero-event-stress-test pass rate, post-protocol | 2/2 (raters D, E) |
| Score-event monotonicity, pre-protocol peers | decoupled (rater B, rater C; scores plateau 4.0–4.5) |
| Score-event monotonicity, post-protocol peers | monotonic (rater D, rater E; close to anchor table) |
| s=5 score reached | 1/5 raters (only rater E pkg_05, post-protocol) |
| cluster-as-1 disagreement (pkg_01) | rater A=1, B=5, C=3, D=0, E=1 |
| Form-instruction-level role mis-handling | 4/5 raters (B free-text; C mis-picked `author`; D free-text; E mis-picked `author`; only A handled correctly — matched dropdown to actual role) |
