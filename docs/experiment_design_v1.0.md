# Experiment Design v1.0
## Controlled Evaluation for Responsibility-Bearing Delegation

> Status: reconstructed experiment design  
> Role: dataset, hypotheses, metrics, baselines, ablations, and pilot protocol  
> Companion files:
> - `paper_master_reconstruction_v1.0.md`
> - `concept_and_positioning_v1.0.md`
> - `formalization_v1.0.md`
> - `reviewer_risk_and_writing_plan_v1.0.md`

---

## 0. Experimental goal

The experiments should not attempt to prove a universal theory of delegation.

They should support a narrower claim:

> Ambiguous natural-language delegations induce measurable pre-execution responsibility-projection mismatch, and a responsibility-bearing delegation protocol can reduce mismatch, unnecessary execution, overclaiming, and repeated misassignment compared with routing, clarification, selection, and scalar-reputation baselines.

---

## 1. Core experimental claims

### Claim 1 — Projection mismatch exists

The same natural-language delegation produces different responsibility projections across agents/model families.

This mismatch is measurable in a closed responsibility space.

### Claim 2 — Projection mismatch is not just stochastic variance

Cross-family projection divergence should exceed within-model stochastic projection divergence.

This is critical because otherwise the paper collapses into “LLMs are stochastic.”

### Claim 3 — Clarification reduces costly mismatch when triggered selectively

Clarification should reduce downstream settlement loss and rework when projection uncertainty is high, but unnecessary clarification should be penalized.

### Claim 4 — Responsibility-level settlement improves future assignment

Responsibility-conditioned reputation should outperform scalar reputation for repeated delegation.

### Claim 5 — The protocol adds value beyond existing baselines

The method should be compared against:

```text
- direct execution
- task-aware routing
- ambiguity clarification
- underspecification clarification
- generate-then-select aggregation
- scalar reputation
- within-model stochastic baseline
```

---

## 2. Dataset: AmbiguousDelegation-300

### 2.1 Dataset size

Main dataset:

```text
5 task categories × 12 delegation templates × 5 hidden-intent variants = 300 examples
```

Pilot dataset:

```text
50 examples = 10 per category
```

### 2.2 Categories

```text
R1 Paper draft / research writing
R2 Code review / bug-fix
R3 Result interpretation
R4 Proposal improvement
R5 Technical summarization for decision-making
```

### 2.3 Dataset unit

Each example:

```json
{
  "delegation_id": "ad_r1_001",
  "category": "R1",
  "delegation": "Improve this paper draft.",
  "artifact": "<short text/code/table/report>",
  "artifact_meta": {
    "type": "paper_section",
    "length_words": 450,
    "domain": "machine_learning"
  },
  "hidden_intent": {
    "weights": {
      "R1.1": 0.9,
      "R1.2": 0.8,
      "R1.4": 0.7,
      "R1.6": 0.1,
      "RX.1": 1.0,
      "RX.2": 1.0,
      "RX.3": 1.0,
      "RX.4": 1.0,
      "RX.5": 1.0
    }
  },
  "acceptable_outputs_summary": "Conceptual reconstruction and reviewer-risk critique.",
  "bad_outputs_summary": "Grammar-only rewrite or generic contribution polishing."
}
```

### 2.4 Hidden-intent annotation

Procedure:

```text
1. Three annotators independently assign 0–1 weights over 38 dimensions.
2. Median weight becomes r*.
3. Krippendorff's α is computed per dimension.
4. Dimensions with α < 0.4 are flagged.
5. If many dimensions fail, revise taxonomy before main experiment.
```

Important:

```text
r* is operational annotation, not true mental intent.
```

---

## 3. Projection protocol

Each projection agent receives:

```text
- delegation d
- artifact a
- closed taxonomy J
- instruction: do not execute; only project responsibility
```

Required JSON:

```json
{
  "weights": {"R1.1": 0.9, "...": 0.0},
  "active_set": ["R1.1", "R1.2", "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"],
  "category_focus": "R1",
  "clarification_needed": true,
  "clarification_question": "Do you want conceptual review or wording polish?",
  "rationale": {
    "R1.1": "The request implies possible conceptual revision."
  }
}
```

Use structured outputs or strict schema. Free-form JSON parsing should not be allowed.

---

## 4. Experiment 1 — Projection Mismatch Measurement

### Objective

Show that ambiguous delegations induce measurable responsibility-projection divergence.

### Conditions

```text
3 model families × 1 projection run per example
```

Optional:

```text
strong / medium / small models per family
```

### Metrics

#### Cross-family projection distance

```math
d_C^cos(d) = mean pairwise cosine distance across model-family projections
```

```math
d_C^jac(d) = mean pairwise Jaccard distance across active sets
```

#### Projection-intent mismatch

```math
M_i(d) = Δ(r_i, r^*)
```

#### Under-projection

Omission of high-importance hidden-intent dimensions.

#### Over-projection

Inclusion of low-importance dimensions.

#### Clarification tendency

Fraction of examples where agents request clarification.

### Expected result

The expected result should be phrased cautiously:

```text
We expect substantial cross-family projection divergence, especially in R1, R3, and R4 tasks where responsibility boundaries are less deterministic.
```

Do not claim until measured.

---

## 5. Experiment 1B — Within-Model Stochastic Baseline

### Purpose

Defend against the objection:

```text
Your cross-model projection diversity is just stochastic variance.
```

### Setup

For each example:

```text
1 fixed model M
5 independent projection runs
temperature = 0.5
```

Compute:

```math
d_W^cos(d) = mean within-model cosine distance over 10 pairs
```

```math
d_W^jac(d) = mean within-model Jaccard distance over 10 pairs
```

Compare with cross-family distance:

```math
R(d) = d_C(d) / d_W(d)
```

### Hypotheses

```text
H1: median R(d) > 1
H2: 95% CI excludes 1
H3: direction holds in all five categories
H4: target median R ≥ 1.5 for a strong claim
```

### Pilot gate

If pilot median R ≤ 1.2:

```text
pause main experiment
revise projection prompt or taxonomy
```

This makes the claim falsifiable and reviewer-defensible.

---

## 6. Experiment 2 — Clarification vs Direct Execution

### Objective

Test whether responsibility-aware clarification reduces settlement loss and rework.

### Conditions

#### Baseline A — Direct execution

```text
d → agent executes immediately
```

#### Baseline B — Task-aware routing

```text
d → task type → select historically strong model → execute
```

This approximates task-aware delegation cues.

#### Baseline C — Ambiguity clarification

```text
d → generic ambiguity detector → ask clarification if ambiguous → execute
```

This approximates CLAMBER-style clarification but without responsibility dimensions.

#### Baseline D — Underspecification clarification

```text
d → classify missing Goal/Constraint/Input/Context → ask clarification → execute
```

This approximates LHAW-style underspecification handling.

#### Proposed — Responsibility-bearing delegation

```text
d → responsibility projection → bid/clarify → execute → settle
```

### Metrics

```text
final settlement loss L
projection-intent similarity after clarification
number of clarification turns
clarification efficiency = loss reduction / clarification cost
user correction turns
overclaim rate
scope adherence
final satisfaction proxy
```

### Clarification cost

Use a simple cost model:

```math
Cost_clarify = c_turn + c_latency + c_user_burden
```

For first experiment:

```text
Cost_clarify = 1 per question
```

and report sensitivity.

### Expected result

The proposed method should win mainly where responsibility ambiguity is high.

It may not win for simple, well-specified tasks. That is acceptable and should be stated.

---

## 7. Experiment 3 — Settlement-Based Reputation Update

### Objective

Test whether dimension-level reputation improves repeated assignment.

### Setup

Create repeated delegation rounds:

```text
T rounds
multiple agents with different strengths
task categories mixed
hidden-intent profiles vary
```

Agents have simulated or measured fulfillment profiles by dimension.

### Conditions

```text
A. scalar reputation
B. task-category reputation
C. role-conditioned reputation
D. role + responsibility-conditioned reputation (proposed)
E. oracle upper bound
```

### Update rule

```math
ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t} + λv_{ij}
```

### Metrics

```text
assignment accuracy
cumulative settlement loss
regret vs oracle
overclaim frequency
time-to-specialization
catastrophic reassignment rate
```

### Expected result

Responsibility-conditioned reputation should especially improve cases where an agent is strong in one dimension but weak in another.

Example:

```text
Agent A: strong writing polish, weak novelty assessment
Agent B: strong method critique, weak prose polish
Agent C: strong uncertainty disclosure, weak direct execution
```

Scalar reputation hides these differences.

---

## 8. Experiment 4 — Generate-then-Select Baseline

### Purpose

Address the selection bottleneck literature.

### Baseline

```text
multiple agents execute directly
judge selects best output
```

Variants:

```text
- homogeneous team + judge selection
- diverse team + judge selection
- diverse team + synthesis
- diverse team + majority/consensus if applicable
```

### Proposed comparison

```text
responsibility projection + assignment + execution + settlement
```

### Key question

Does governing responsibility before generation outperform selecting among outputs after generation?

### Metrics

```text
selected output settlement loss
cost
number of generated outputs
judge disagreement
overclaim not visible to output-only selection
```

### Expected advantage of proposed method

The proposed method may be cheaper and more scope-aligned because it avoids generating multiple wrong-scope outputs.

---

## 9. Experiment 5 — Uncertainty / Overclaim Calibration

### Purpose

Connect to metacognition and confidence-calibration work.

### Setup

For each bid:

```text
q_ij = claimed coverage
u_ij = uncertainty
v_ij = observed fulfillment
```

### Metrics

#### Coverage calibration

```math
ECE_q = calibration error between q_ij and v_ij
```

#### Uncertainty calibration

```math
ECE_u = calibration error between 1-u_ij and v_ij
```

#### Overclaim rate

```math
OCR = mean 1[q_ij > v_ij + δ_oc]
```

#### Honest limitation rate

Fraction of cases where `z_i = limit` or `partial` and settlement confirms that limitation was appropriate.

### Baselines

```text
- no uncertainty field
- scalar confidence only
- pairwise confidence comparison
- responsibility-specific uncertainty vector
```

This experiment can be optional if the paper becomes too large. At minimum, keep the metrics as analysis.

---

## 10. Baseline summary

| Baseline | Prior-work connection | What it tests |
|---|---|---|
| Direct execution | standard assistant behavior | effect of no projection |
| Task-aware routing | Task-Aware Delegation Cues | task type vs responsibility vector |
| Generic ambiguity clarification | CLAMBER | ambiguity detection vs responsibility clarification |
| Underspecification clarification | LHAW | missing info vs responsibility boundary |
| Generate-then-select | Selection bottleneck | output selection vs pre-execution responsibility governance |
| Within-model stochastic | Mehta behavioral variance | cross-family signal beyond stochasticity |
| Scalar reputation | ordinary routing memory | dimension-level reputation value |
| No settlement | benchmark-only evaluation | value of ex-post responsibility accounting |

---

## 11. Ablation design

Proposed full protocol:

```text
projection + bid + clarification + settlement + responsibility reputation
```

Ablations:

```text
A0 No projection
A1 Projection only, no clarification
A2 Projection + clarification, no settlement
A3 Settlement with scalar loss only
A4 No overclaim penalty
A5 No uncertainty disclosure
A6 No user-feedback weight calibration
A7 Scalar reputation instead of responsibility reputation
A8 Open-vocabulary projection instead of closed taxonomy
```

A8 is especially useful to show why the 38-dim taxonomy matters.

---

## 12. Evaluation rubric

Each output is scored only on active dimensions:

```text
j ∈ J*(d)
```

Evaluator sees:

```text
- delegation
- artifact
- active dimension list
- per-dimension rubric
- agent output
```

Evaluator does not see:

```text
- hidden intent r*
- other agents' outputs
- model identity
```

Score:

```text
s_ij ∈ {1,2,3,4,5}
v_ij = (s_ij - 1)/4
ℓ_ij = 1 - v_ij
```

Judges:

```text
- 3 LLM judges for all examples
- 3 human annotators on 60-example stratified subset
```

Report:

```text
- LLM judge agreement
- human agreement
- human–LLM Spearman correlation
```

---

## 13. Statistical tests

### Projection divergence

```text
paired bootstrap CI for d_C - d_W
Wilcoxon signed-rank for R(d) > 1
category-stratified analysis
```

### Clarification experiment

```text
paired comparison by delegation
effect size on settlement loss
cost-adjusted improvement
```

### Reputation simulation

```text
cumulative regret curves
paired comparison over random seeds
```

### Judge agreement

```text
Krippendorff's α per dimension
Spearman human–LLM agreement
```

---

## 14. Pilot protocol

Before main experiment:

```text
50 examples
10 per category
3 model families
within-model stochastic baseline on fixed model
3 annotators for hidden intent
3 LLM judges for output scoring
```

Pilot checks:

```text
1. Projection JSON validity ≥ 98%
2. Median active-set size between 4 and 12
3. Hidden-intent agreement α ≥ 0.4 for most active dimensions
4. Cross-family / within-model ratio median R > 1.2
5. Clarification questions are specific, not generic
6. Cost per example within budget
7. No dimension is systematically confused with another
```

If failure:

```text
revise taxonomy, prompts, or active threshold before main run
```

---

## 15. Expected tables

### Table 1 — Dataset composition

Category, examples, average artifact length, active dimensions.

### Table 2 — Projection divergence

Cross-family distance, within-model distance, R ratio.

### Table 3 — Projection-intent mismatch

Under-projection, over-projection, cosine similarity by category.

### Table 4 — Clarification results

Settlement loss, clarification turns, cost-adjusted gain.

### Table 5 — Baseline comparison

Direct, task-aware routing, generic clarification, LHAW-like clarification, generate-then-select, proposed.

### Table 6 — Reputation update

Scalar vs responsibility-conditioned cumulative loss and assignment accuracy.

### Table 7 — Judge agreement

LLM–LLM, human–human, human–LLM.

---

## 16. Expected figures

### Figure 1 — Protocol diagram

Delegation → projection → bid/clarification → execution → settlement → reputation.

### Figure 2 — Responsibility projection examples

Same delegation, different model-family projections.

### Figure 3 — Cross-family vs within-model divergence

Boxplots by category.

### Figure 4 — Clarification value vs projection uncertainty

Scatter plot.

### Figure 5 — Reputation specialization over rounds

Heatmap of agent × responsibility reputation.

### Figure 6 — Baseline comparison

Settlement loss by condition.

---

## 17. Practical implementation plan

### Phase 1 — Build specs

```text
spec_pi_implementation_v1.0.md
spec_evaluation_rubric_v1.0.md
spec_baseline_protocols_v1.0.md
```

### Phase 2 — Build pilot dataset

```text
50 examples
manual hidden-intent annotation
artifact collection
bad/good output summaries
```

### Phase 3 — Run projection calls

```text
structured outputs
3 model families
within-model 5-run baseline
```

### Phase 4 — Run execution and scoring

```text
baselines
proposed protocol
judge scoring
human subset
```

### Phase 5 — Analyze

```text
projection divergence
clarification value
settlement loss
reputation simulation
```

---

## 18. Minimum viable experiment if time is short

If the full suite is too large, run:

```text
Pilot 50 only
Experiment 1 + 1B
Small clarification experiment on 50 examples
No full reputation simulation
```

This still supports the core conceptual claim:

```text
pre-execution responsibility projection is measurable and nontrivial.
```

Then present settlement/reputation as protocol design plus smaller simulation.

---

## 19. Main experimental risk

The central risk is:

```text
Projection divergence may be small or not meaningfully different from within-model stochasticity.
```

This is why the B0 baseline and pilot gate are essential.

If this happens, possible recovery:

```text
- sharpen delegation templates
- increase ambiguity in hidden-intent variants
- improve taxonomy definitions
- distinguish category-specific vs cross-cutting dimensions
- focus paper on taxonomy/protocol rather than empirical divergence magnitude
```

But do not hide the result.

---

## 20. Final experiment recommendation

The first full paper should prioritize:

```text
1. Projection mismatch measurement
2. Cross-family vs within-model divergence
3. Clarification value
4. Settlement/reputation simulation
```

The uncertainty calibration and generate-then-select baselines are valuable but can be reduced if page limits are tight.
