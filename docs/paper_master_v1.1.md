# Paper Master v1.1
## Sync Patch on `paper_master_reconstruction_v1.0` for the First-Cycle (R1 + RX) Scope

> Status: narrowed master plan for first paper cycle
> Role: re-states the v1.0 master plan under the operational scope of `J_v1.1`, defers R2–R5 and main-300 work to later cycles
> Companion files:
> - `paper_master_reconstruction_v1.0.md` (parent — unchanged)
> - `formalization_v1.1.md`
> - `concept_and_positioning_v1.0.md`
> - `experiment_design_v1.1.md`
> - `spec_pi_implementation_v1.0.md`
> - `spec_dataset_v1.0.md`

---

## 0. What changed from v1.0

The thesis, vocabulary, and contribution structure of `paper_master_reconstruction_v1.0` are unchanged. v1.1 narrows the **operational scope** of the first paper cycle:

- The taxonomy used in experiments is `J_v1.1` (12 dim: R1.1–R1.7 + RX.1–RX.5), not the full 38-dim `J` of v1.0. v1.0's taxonomy remains the long-term target.
- Categories R2–R5 (code review, result interpretation, proposal improvement, technical summarization) are **deferred** to later cycles. The first paper studies R1 + RX only.
- The main 300-example dataset is **deferred**. The first paper reports the 50-example pilot (`AmbiguousDelegation-50-R1`) plus a within-model stochastic baseline; a follow-up paper or extended version reports the 300-example main run.
- Reviewer-defensibility is moved from "broad coverage of delegation" to "narrow but well-controlled measurement on a single category".

What does **not** change:

- The thesis (incomplete delegation, projection mismatch as pre-execution failure mode).
- The protocol layers (projection → bid → clarification → execution → settlement → reputation).
- The conceptual vocabulary in §4 of v1.0.
- The four contributions in §5 of v1.0, in spirit. Contribution 4 narrows in scope (see §5 below).
- The "what this paper is not" disclaimers in §6 of v1.0.
- The positioning against prior-work clusters in §8 of v1.0.

---

## 1. Final one-sentence thesis (unchanged)

> Multi-agent LLM orchestration is not merely a problem of routing, aggregation, ambiguity detection, or post-hoc failure diagnosis; it is an incomplete delegation problem in which agents must project, claim, clarify, execute, and settle responsibility under natural-language ambiguity.

The thesis is identical to v1.0 §1. The narrowed scope is an empirical scope, not a thesis scope.

---

## 2. Narrowed empirical scope

The first paper makes the thesis empirically defensible **for one task category** (R1, paper-research delegation) and the cross-cutting RX dimensions. The paper claims:

```text
On R1 paper-research delegations:
  - projection mismatch is measurable and exceeds within-model stochasticity;
  - clarification, when triggered by responsibility-projection uncertainty, reduces settlement loss;
  - dimension-level settlement and reputation outperform scalar baselines on simulated repeated assignment.
```

The paper does **not** claim:

```text
- generalization to R2–R5 (those are explicitly future work);
- production readiness;
- a universal taxonomy of delegation;
- that the protocol replaces existing routing or aggregation methods.
```

The narrowed-scope version of the gap statement (v1.0 §12) is:

> Existing work has made task type, ambiguity, underspecification, confidence, behavioral variance, aggregation quality, and post-hoc failure modes measurable. What remains under-specified is the agent's pre-execution responsibility commitment. We provide a closed 12-dimension responsibility taxonomy for paper-research delegation and a protocol that makes commitment, clarification, and settlement measurable on this taxonomy.

---

## 3. Final paper object (unchanged structure, narrowed instantiation)

Protocol layers per v1.0 §3 are unchanged. The instantiation:

```text
delegation              : R1-category natural-language requests (10 surface templates)
responsibility space    : J_v1.1 (12 dim)
projection agent        : per spec_pi_v1.0
bid / clarification     : per spec_bid_v1.0 (forthcoming)
agent set               : 3 model families × mid-tier
evidence sources        : LLM judges + 20-example human subset
settlement              : per-dim s_ij ∈ {1..5}, v_ij = (s_ij-1)/4
reputation update       : additive EMA per (agent, role, dim, task)
```

The paper does not propose a new agent framework. The harness (`rbd-harness`) is the reference implementation, released with the paper.

---

## 4. Final conceptual vocabulary (unchanged)

The vocabulary table in v1.0 §4 is reused verbatim. No term is added or removed at v1.1. Future cycles may add R2–R5-specific terms; those will not displace v1.1 terms.

---

## 5. Contributions (narrowed)

### Contribution 1 — Problem formulation (unchanged)

We formulate multi-agent LLM orchestration as **incomplete delegation under natural-language ambiguity**, identifying **projection mismatch** as a pre-execution failure mode.

### Contribution 2 — Protocol (unchanged in description, narrowed in instantiation)

We introduce a responsibility-bearing delegation protocol with the layers in §3. The protocol is described in full generality; the implementation and evaluation are scoped to R1 + RX in this paper.

### Contribution 3 — Settlement and reputation (narrowed scope)

We define the ex-post settlement mechanism over `J_v1.1` and update role- and responsibility-conditioned reputation using additive EMA. Reputation updates are computed only on the 12 dimensions of `J_v1.1`; extension to the full 38-dim taxonomy is future work.

### Contribution 4 — Controlled evaluation framework (narrowed scope)

We propose and run controlled experiments on the 50-example `AmbiguousDelegation-50-R1` pilot:

```text
- cross-family vs within-model projection divergence (Experiment 1 + 1B);
- projection-intent mismatch (Experiment 1);
- clarification value vs cost on pilot subset (Experiment 2, scaled-down);
- settlement-based reputation simulation (Experiment 3, simulated agents);
- comparison against direct-execution and generate-then-select baselines (Experiment 4, narrowed).
```

The Experiment 5 (uncertainty / overclaim calibration) of v1.0 is reported as analysis, not as a primary experiment, in the first paper.

---

## 6. What this paper is not (unchanged + one addition)

All disclaimers in v1.0 §6 are retained. Add:

```text
This is not a multi-category benchmark.
The first paper studies one category (R1) with five cross-cutting dimensions.
Generalization to R2–R5 is reserved for follow-up work.
```

---

## 7. Updated paper architecture

The architecture in v1.0 §7 is reused. Section-level changes:

### Abstract

Add an explicit scope sentence:

> We instantiate and evaluate the protocol on paper-research delegation (R1) over a closed 12-dimension taxonomy; extension to other delegation categories is reserved for future work.

### 1. Introduction

Logic in v1.0 §7.Introduction is unchanged. The contributions list at the end of the Introduction must use the v1.1 versions (§5 above).

### 2. Related Work

Unchanged section structure. The "ambiguity" and "underspecification" subsections may add a sentence noting that v1.1 evaluates only one task category, with future work covering more.

### 3. Problem Formulation

Use `formalization_v1.1` notation. The text should:

```text
- introduce J as a closed responsibility space, |J|=12 in this paper;
- note that the long-term taxonomy is larger (38 dim) and cite formalization_v1.0 / appendix A for the full enumeration if appendix space allows.
```

### 4. Protocol

Use `formalization_v1.1` §10's seven equations. Algorithmic description follows v1.0 §16, restricted to `J_v1.1` for the running example.

### 5. Experiments

Restructure to match `experiment_design_v1.1`:

```text
5.1 Dataset: AmbiguousDelegation-50-R1 (defer to spec_dataset_v1.0 for full)
5.2 Experiment 1: cross-family projection mismatch on 50 examples
5.3 Experiment 1B: within-model stochastic baseline
5.4 Experiment 2: clarification value (scaled-down)
5.5 Experiment 3: settlement-based reputation (simulated repeated assignment)
5.6 Baselines and ablations (narrowed list)
5.7 Metrics
```

### 6. Results

To be filled after the pilot run completes. Result claims must be phrased as observations on the pilot, with explicit "we do not generalize beyond R1" caveats.

### 7. Discussion

The discussion in v1.0 §7.Discussion is reused, with one addition:

```text
- Why this paper studies R1 only; what would change for R2–R5
- What the within-model baseline does and does not rule out
- How the pilot-scale annotation protocol (one author + two LLM annotators + 20-example human subset) affects the strength of α and Spearman claims; main-run improvements
```

### 8. Limitations

v1.0 §7.Limitations is reused. Add:

```text
- Pilot scale: 50 examples, R1 only, may not generalize to other delegation categories.
- Hidden-intent annotation in pilot uses LLM annotators with human validation on 20 examples; main run uses three independent human annotators per example.
- Modified-real artifacts are derived from author-owned drafts; representativeness across domains is limited.
- Within-model baseline uses one fixed mid-tier model; conclusions about stochasticity are conditional on this choice.
```

### Appendix A — Responsibility Taxonomy

`J_v1.1` (12 dim) full enumeration with definitions and score anchors. The full v1.0 38-dim taxonomy is referenced as the long-term target, with one paragraph explaining the deferral rationale.

### Appendix B — Projection and bid schemas

Use the strict JSON schemas from `spec_pi_v1.0` §2 and `spec_bid_v1.0` (forthcoming).

### Appendix C — Evaluation rubric

Per-dim rubric for `J_v1.1` from `spec_evaluation_rubric_v1.0` (forthcoming).

### Appendix D — Baseline protocol details

Narrowed list per `experiment_design_v1.1` §10.

### Appendix E — Annotation protocol and validation

Hidden-intent annotation as in `spec_dataset_v1.0` §6, with the 20-example human subset validation results (human–LLM Spearman, human–human α).

---

## 8. Final positioning against prior-work clusters (unchanged)

v1.0 §8 table is reused verbatim. The positioning sentences are agnostic to the empirical scope and remain valid for v1.1.

---

## 9. Minimum viable paper scope (revised for first paper)

Replaces v1.0 §9. The first paper's MVP:

```text
- 1 task category (R1)                    — instead of 5
- 12 responsibility dimensions (J_v1.1)   — instead of 38
- 50 controlled examples                  — instead of 300
- author + 2 LLM annotators per example   — instead of 3 humans
- 20-example human validation subset      — for α and Spearman defense
- 3 model families for projection         — same as v1.0
- 3 LLM judges for output scoring         — same as v1.0
- 4 baselines (direct, task-aware routing, generic clarification, generate-then-select)
- settlement/reputation simulation on simulated agents
```

The paper claims **scoped** rather than **production-ready**.

---

## 10. Recommended next workflow (current status)

Replaces v1.0 §10. The roadmap as of this v1.1 sync:

```text
[done]   formalization_v1.1            (12-dim taxonomy)
[done]   spec_pi_implementation_v1.0   (projection prompt + schema)
[done]   spec_dataset_v1.0             (pilot dataset construction)
[done]   paper_master_v1.1             (this document)
[done]   experiment_design_v1.1        (sync patch)
[next]   spec_evaluation_rubric_v1.0   (judge rubric prompt + schema)
[next]   spec_bid_v1.0                 (bid prompt + schema, for Experiment 2)
[next]   build pilot dataset           (spec_dataset_v1.0 §9 build order)
[then]   pilot projection runs         (smoke + cross-family + within-model)
[then]   pilot annotation              (LLM passes + human subset)
[then]   acceptance gate check         (per spec_dataset_v1.0 §10)
[then]   pilot judge runs              (after spec_evaluation_rubric exists)
[then]   draft paper sections          (after pilot results stable)
[then]   convert to LaTeX
```

---

## 11. Status

The project state at v1.1 lock:

```text
[done]   pre-experiment paper architecture locked (v1.0 + v1.1 patches)
[done]   first-cycle taxonomy and operational specs locked (formalization_v1.1, spec_pi_v1.0, spec_dataset_v1.0)
[blocking next milestone]   build the 50-example pilot dataset
```

Next bottleneck: pilot dataset construction (spec_dataset_v1.0 §9). After that, the projection experiment (Experiment 1 + 1B) can run end-to-end.
