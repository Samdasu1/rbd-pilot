# Review Feedback v1.0
## Pre-code-modification Critical Review of Paper Direction and Theory

> Status: critical review of v1.0 + v1.1 + v1.2 document set, prior to code modification
> Role: surfaces structural risks in paper direction and theoretical formalization, with explicit decision items
> Reviewed documents:
> - `paper_master_reconstruction_v1.0`, `paper_master_v1.1`, `paper_master_v1.2`
> - `formalization_v1.0`, `formalization_v1.1`
> - `experiment_design_v1.0`, `experiment_design_v1.1`, `experiment_design_v1.2`
> - `concept_and_positioning_v1.0`, `reviewer_risk_and_writing_plan_v1.0`
> - `paper_section_5_draft_v1.0` (pilot v1 measurement layer)
> - `spec_pi_implementation_v1.0`, `spec_dataset_v1.0`, `spec_evaluation_rubric_v1.0`, `spec_bid_v1.0`, `spec_models_v1.0`
> - `CHANGELOG.md`

---

## 0. Headline finding

The paper is currently positioned to make two coupled claims, but the pilot evidence supports them asymmetrically:

```
T1 (measurability)  — projection commitment is computable and family-attributable
                      → STRONG evidence (Exp 1 + 1B; cross-family ~17× within-model)

T2 (actionability)  — knowledge of projection commitment improves execution outcome
                      → INCONCLUSIVE/CONTRARY evidence (Exp 2; CI includes 0; dual class reverses)
```

The pilot's Exp 2 mechanism analysis (§5.5 of `paper_section_5_draft_v1.0`) decomposes the failure into four protocol-level mechanisms — format coupling, active-set propagation bias, self-claim drift, RX attention boost — each of which signals immaturity in the protocol *design*, not insufficient sample size. v1.2 model-panel redesign and n=300 main run will not by themselves repair these mechanisms.

**Most defensible repositioning:** keep T1 as the strong claim, demote T2 to "single projection-injection is insufficient — protocol design space is non-trivial," and use the four mechanisms as the paper's *finding* rather than its weakness.

---

# Part I — Paper Direction Review

## 1. Adversarial reviewer simulation (SA-1)

The single reject-coding sentence this paper is most exposed to:

> "Your thesis claims pre-execution responsibility projection improves outcome, but Experiment 2 has CI including 0 at n=50, and projection-driven is *worse* than direct on the dual-class subset (Δ=−0.032). Headline claim and measurement disagree."

The §5.5 decomposition into 4 mechanisms is honest and actually strengthens the paper *if* repositioned. Currently it reads as a confession; it should read as a finding: "naive projection injection is insufficient; we identify and characterize the four protocol-design factors that mediate execution."

## 2. Conceptual coherence (SA-2)

The thesis as stated couples T1 (measurability) and T2 (actionability) into a single claim. They are theoretically distinct: measurability is necessary but not sufficient for actionability. Recommend explicit decoupling in §3 or §4 introduction:

```
We introduce two distinct propositions:
  P1 (measurability)  — projection commitment is computable and family-distinguishable.
  P2 (actionability)  — knowledge of projection commitment can be used to improve execution.

This paper's evidence is strong on P1 (Exp 1/1B), suggestive but inconclusive on P2 (Exp 2),
and we explicitly identify protocol-design factors (§5.5) that mediate the gap.
```

## 3. Prior-work positioning (SA-3)

The differentiation against the 9 cited works in `concept_and_positioning_v1.0` is generally solid. One residual risk: the **CLAMBER** distinction (information-need ambiguity vs responsibility ambiguity) is conceptually clean but operationally hard to distinguish — both are measured as "different LLMs interpret the same prompt differently." A direct measurement-level comparison (e.g., does the same artifact under CLAMBER's 8-category scheme produce a different active set than under J_v1.1?) is needed at least in appendix.

## 4. Pilot-evidence reality check (SA-4)

Mapping paper claims to pilot evidence:

| paper claim | pilot evidence | strength |
|---|---|---|
| C1 problem formulation | theoretical prose | OK (theoretical) |
| C2 protocol | Exp 2 mixed | **weak** — no working prototype demonstrated |
| C3 settlement+reputation | Exp 3 simulated only | **very weak** — zero real-agent evidence |
| C4 controlled evaluation | Exp 1/1B strong, Exp 2 weak | partial |

**C3 is effectively a simulation-only contribution.** Recommend demoting to: "Conditional on dimension-level fulfillment heterogeneity, scalar reputation underperforms in simulation; empirical confirmation in real agents is future work." Currently presenting it as a co-equal main contribution invites the "two papers stitched together" reject vector.

## 5. Scope appropriateness (SA-5)

The narrowing v1.0 → v1.1 → v1.2 (5→1 categories, 38→12 dim, 300→50 examples) is reasonable but creates a thesis-evidence asymmetry. Current thesis claims "multi-agent LLM orchestration" (general) but evidence is R1-only.

**Decision required (one of two):**
- **Option A (conservative, recommended):** narrow thesis sentence to "paper-research delegation requires pre-execution responsibility projection over a closed taxonomy."
- **Option B (aggressive):** add 1–2 spot-check examples per R2–R5 demonstrating that the closed-taxonomy approach generalizes structurally (different dim list, same protocol).

Option A pairs well with the v1.2 cost increase and is more defensible at pilot scale.

---

# Part II — Theoretical Formalization Review

## 6. Formalization rigor (SA-6)

### Weakness 1 — settlement loss weighting

Current `formalization_v1.0` §13:

```
L_i = Σ_{j ∈ J*(d)} w_j^(u,t) ℓ_ij
```

In the pilot (`paper_section_5_draft_v1.0` §5.4) the headline uses **uniform weight over J*(d)**, with weighted-by-r* as supplementary only. This is theoretically weak: r*_j (∈ [0,1]) carries information about how load-bearing each dimension is, and discarding it via a binary active-set membership wastes signal.

**Recommendation:** define both versions and report both:

```
L_i^uniform  = mean over J*(d) of ℓ_ij                (current headline)
L_i^weighted = Σ r*_j · ℓ_ij / Σ r*_j                 (theoretically more aligned)
```

Promote `L_i^weighted` to headline; relegate uniform to ablation. This partially mitigates the active-set propagation bias mechanism (§5.5.2): peripheral dims enter at weight ~0.3 instead of weight 1.0, so they no longer dilute load-bearing dim evaluation.

### Weakness 2 — clarification trigger second OR-clause

`formalization_v1.0` §9:

```
C(d) = 1 if D_π(d) > τ_D OR E[L_direct(d)] - E[L_clarified(d)] > Cost_clarify(d)
```

The second clause is **operationally unmeasurable in deployment** — there is no way to know `E[L_clarified]` without first running clarification. Pilot uses only the first clause. Recommend: in §3 keep the second clause as theoretical motivation, but in §4 (protocol) explicitly state that practical implementation uses only the first clause (or a learned surrogate). Reserve the second clause as future-work meta-controller objective.

## 7. r* hidden-intent justification (SA-7) — single greatest theoretical risk

`formalization_v1.0` §5 disclaims that r* is "operational target for controlled evaluation, not metaphysical truth" — good but insufficient.

**The deeper problem:** r* is itself LLM-derived (median of author + 2/3 LLM annotators). This means:

- "Projection-intent mismatch" Δ(r, r*) is mathematically equivalent to "executor-LLM projection diverges from annotator-LLM-panel projection."
- Cross-family divergence (Exp 1) at root measures **LLM-LLM disagreement structure**, not "responsibility commitment" in any external sense.

Stage 1 5-human anchor on R1.7 (18 ratings) is a partial mitigation but covers **one dim of one aspect**. `spec_models_v1.0` §6.4 acknowledges this; relying on §VI Limitations alone is insufficient at submission grade.

**Strong recommendation:**
1. Extend Stage 1 human anchor to R1.4 (novelty) and R1.1 (conceptual reframing) — 2 additional dims × 5 raters × ~9 examples × 2 conditions ≈ ~$200 additional Prolific cost.
2. For human-anchored dims, re-report Exp 1 cross-family divergence on those dims specifically. If divergence persists with human-anchored r*, the LLM-LLM-disagreement objection is empirically blocked.
3. R1.7-only is not enough — that dim was the worst-α (0.219) in v1.0 pilot, so the human anchor there reads as "fixing a known weak spot," not "validating the rubric."

## 8. Taxonomy closure (SA-8)

The 12-dim partition (R1.1–R1.7 + RX.1–RX.5) is operationally clean (anchors at s=1/3/5 are well-defined) but theoretically under-justified. Closure rests on:
- Author's peer-review experience (one human's intuition).
- R1.4↔R1.7 boundary test in pilot showing 0/50 swap cases (weak but positive).
- Stage 1 R1.7 human anchor (one dim).

**RX always-active decision** has a measurability cost: zero variance → α undefined. This should be repositioned in §3 from "measurement dimension whose α we cannot compute" to "cross-cutting design constraint enforced by protocol, not a measurement target." The current paper text leaves this slightly ambiguous.

**Recommendation:** §3 should explicitly state J_v1.1 closure as "operational closure for one task category in one paper" and not as a closure claim about responsibility-bearing delegation in general. §5.1 should foreground the R1.4↔R1.7 boundary test result as the small-but-real closure evidence.

## 9. Construct validity (SA-9) — deepest unresolved issue

`spec_models_v1.0` §6.2 acknowledges construct validity as a residual limit. The R1.7 α=0.219 is the surface symptom; the underlying question is whether each anchor (s=1/3/5 wording) is a one-dimensional projection of a multi-dimensional latent factor.

**Reportable evidence the pilot can already supply (no new annotation needed):**
- Inter-dimension correlation matrix on r*_median across 50 examples.
- If R1.1 and R1.4 correlate at r > 0.7, the two dims are likely fronting one latent factor.
- Honest disclosure in §5.1 with effect on subsequent claims.

This won't fix the issue but transforms it from hidden weakness to declared limitation with effect-size evidence.

## 10. Pre-execution measurability vs actionability (SA-10)

Theoretical decoupling of P1 / P2 (per §2 above) should be added to §3 problem formulation as an explicit two-proposition framing. This single paragraph is the highest-leverage single edit available — it pre-empts the SA-1 reject vector and reframes the paper around its strongest evidence.

---

# Part III — Decision Items Required Before Code Modification

| # | Item | Recommended decision | Priority |
|---|---|---|---|
| 1 | Thesis sentence | Decouple P1 (measurability) and P2 (actionability); strong on P1, suggestive on P2 with mechanism analysis | **P0** |
| 2 | Paper scope | Option A — narrow to "paper-research delegation," scoped not universal, from abstract onward | **P0** |
| 3 | C3 (settlement+reputation) | Demote to conditional/simulation-only; future work for real-agent confirmation | P1 |
| 4 | L_i definition | Promote weighted (`Σ r*_j ℓ_ij / Σ r*_j`) to headline; uniform → ablation | P1 |
| 5 | Clarification trigger | Theoretical 2-clause definition retained; practical 1-clause explicitly disclosed | P2 |
| 6 | r* human anchor | Extend Stage 1 to R1.4 + R1.1 (~$200 extra); re-report Exp 1 on anchored dims | **P0** |
| 7 | Construct validity | Add inter-dim correlation matrix to §5.1; honest disclosure of factor-correlation pairs | P1 |
| 8 | RX role | Reposition as "cross-cutting design constraint, not measurement target" in §3 | P2 |
| 9 | Exp 2 mechanism analysis | Reposition from weakness-confession to finding ("naive projection injection is insufficient") | **P0** |

P0 items must be decided before code modification. P1/P2 can be decided during writing.

---

# Part IV — Honest summary

The pilot does *not* support "this protocol works." It supports two narrower but still publishable claims:

1. **Pre-execution responsibility commitment is family-attributable and measurable.** (Exp 1/1B; strong.)
2. **Naive projection injection does not improve execution; protocol design space is non-trivial, with four identifiable mechanisms.** (Exp 2 + §5.5; mixed-but-informative.)

A "measurement paper + mechanism analysis paper" framing is more defensible than a "complete protocol" paper. This reframing changes priority of code-modification work: extending Stage 1 human anchor to additional dims (P0) becomes more important than re-running Exp 3 simulated reputation. The current code-modification queue should be re-prioritized accordingly after these decisions are made.
