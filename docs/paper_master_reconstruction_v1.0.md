# Paper Master Reconstruction v1.0
## Responsibility-Bearing Delegation for Multi-Agent LLM Orchestration

> Status: reconstructed master plan  
> Role: top-level paper architecture and conceptual commitment  
> Companion files:
> - `concept_and_positioning_v1.0.md`
> - `formalization_v1.0.md`
> - `experiment_design_v1.0.md`
> - `reviewer_risk_and_writing_plan_v1.0.md`

---

## 0. What changed after the expanded prior-work review

The original project framed multi-agent LLM orchestration as a **responsibility-bearing delegation** problem rather than a simple routing problem. That framing remains valid, but the nearby literature is now crowded enough that the paper must be sharpened.

The key update is:

> The paper should no longer claim novelty merely from “delegation,” “ambiguity,” “clarification,” “uncertainty,” “agent variance,” or “failure taxonomy.”  
> Those are now occupied by adjacent works.  
> The paper’s defensible space is the **pre-execution projection of delegated responsibility into a closed operational responsibility space, followed by responsibility-bearing bid, clarification, ex-post settlement, and responsibility-conditioned reputation update**.

In other words, the core novelty is not:

```text
LLMs are ambiguous.
Agents need clarification.
Agents are miscalibrated.
Multi-agent systems fail.
Different agents produce different outputs.
Task-aware routing helps.
```

Those are all supported by prior work.

The paper’s narrower claim is:

```text
Ambiguous natural-language delegation creates a responsibility-projection problem before execution.
This projected responsibility can be represented in a closed operational space,
used for pre-execution bidding and clarification,
settled after execution,
and accumulated as role- and responsibility-conditioned reputation.
```

---

## 1. Final one-sentence thesis

> Multi-agent LLM orchestration is not merely a problem of routing, aggregation, ambiguity detection, or post-hoc failure diagnosis; it is an incomplete delegation problem in which agents must project, claim, clarify, execute, and settle responsibility under natural-language ambiguity.

---

## 2. Expanded thesis

Real user requests are usually not fully specified operational tasks. They are delegated through natural language:

```text
Improve this paper draft.
Review this code.
Check whether this result makes sense.
Make this proposal stronger.
Prepare this for submission.
```

Such requests are semantically rich but operationally ambiguous. A request may imply surface editing, conceptual reconstruction, methodological review, citation checking, mathematical verification, risk assessment, or some combination of these.

Existing systems often answer one of the following questions:

```text
Which model should handle this prompt?
Is the query ambiguous?
Should the agent ask a clarification question?
Did the final output succeed?
Which failure mode occurred after execution?
Which candidate output should be selected?
How confident is the model?
```

This paper asks a different question:

```text
What responsibility structure has the agent projected from the user’s delegation before acting,
what responsibility does it claim to assume,
should that projection be clarified,
and how should fulfillment or failure update future delegation?
```

The distinction is temporal and structural:

```text
Prior work often measures ambiguity, uncertainty, variance, or failure after or around execution.
This paper makes the pre-execution responsibility commitment itself measurable.
```

---

## 3. Final paper object

The paper proposes a protocol:

```text
natural-language delegation
→ responsibility projection
→ responsibility-bearing bid / clarification bid
→ agent-role assignment
→ execution
→ evidence collection
→ ex-post settlement
→ user-feedback calibration
→ responsibility-conditioned reputation update
```

This should be described as a **protocol-level governance layer**, not as a benchmark, not as a new agent framework, and not as a universal theory of intent.

---

## 4. Final conceptual vocabulary

| Term | Final definition |
|---|---|
| Natural-language delegation `d` | A user request that assigns work without fully specifying operational responsibility. |
| Responsibility projection `r = π(d,u,t)` | A pre-execution mapping from delegation to a closed vector of responsibility dimensions. |
| Projection mismatch | Difference between projected responsibility and intended or later-preferred responsibility. |
| Responsibility-bearing bid `b_i` | An agent’s pre-execution claim about coverage, uncertainty, limits, cost, and willingness to assume responsibility. |
| Clarification bid | A bid that refuses premature execution because responsibility structure is underdetermined. |
| Settlement | Ex-post scoring of whether the agent fulfilled the responsibility it claimed or should have claimed. |
| Responsibility-conditioned reputation `ρ_{i,y,j,t}` | Historical fulfillment estimate indexed by agent, role, responsibility dimension, and task type. |

---

## 5. Final contribution set

### Contribution 1 — Problem formulation

We formulate multi-agent LLM orchestration as **incomplete delegation under natural-language ambiguity**, identifying **projection mismatch** as a pre-execution failure mode.

The key novelty is that projection mismatch is:

```text
- pre-execution, unlike post-hoc failure taxonomies;
- responsibility-structured, unlike generic ambiguity labels;
- vector-valued over a closed taxonomy, unlike open-ended interpretation descriptions;
- actionable, because it can trigger clarification before commitment.
```

### Contribution 2 — Protocol

We introduce a **responsibility-bearing delegation protocol** that converts ambiguous delegations into responsibility vectors, solicits responsibility-bearing bids, triggers clarification under projection uncertainty, and assigns agents based on responsibility-adjusted utility rather than scalar competence alone.

### Contribution 3 — Settlement and reputation

We define an **ex-post settlement mechanism** over responsibility dimensions and update role- and responsibility-conditioned reputation using additive EMA. This distinguishes execution quality, overclaiming, uncertainty disclosure, scope adherence, downstream harm, and provenance.

### Contribution 4 — Controlled evaluation framework

We propose controlled experiments measuring:

```text
- cross-agent and cross-family projection divergence;
- projection-intent mismatch;
- clarification value versus clarification cost;
- settlement-based reputation improvement;
- robustness against within-model stochasticity and task-aware routing baselines.
```

---

## 6. What this paper is not

This disclaimer must appear early, probably in Introduction or Scope.

```text
This is not a complete theory of user intent.
This is not a replacement for ambiguity benchmarks.
This is not merely a model router.
This is not a general MAS failure taxonomy.
This is not a tool-use calibration method.
This is not a multi-agent debate or synthesis architecture.
This is not an electricity-market isomorphism.
```

The electricity-market analogy can remain as intuition for **bid → commitment → settlement**, but the final paper should avoid over-relying on the market metaphor.

---

## 7. Updated paper architecture

### Abstract

Must mention:

```text
- incomplete delegation
- natural-language ambiguity
- pre-execution responsibility projection
- closed responsibility taxonomy
- bid / clarification
- settlement
- reputation update
- controlled experiments
```

### 1. Introduction

Recommended logic:

```text
1. LLM agents increasingly perform delegated work.
2. Existing orchestration often focuses on routing, aggregation, benchmarks, or post-hoc failure.
3. Recent work shows interpretation, ambiguity, uncertainty, and variance matter.
4. But those works still leave open what an agent commits to before acting.
5. Introduce projection mismatch.
6. Present responsibility-bearing delegation protocol.
7. List contributions.
```

### 2. Related Work

Organize by contrast, not by chronological literature review.

```text
2.1 Task-aware routing and delegation cues
2.2 Ambiguity identification and clarification
2.3 Underspecification in long-horizon tasks
2.4 Uncertainty communication and calibration
2.5 Behavioral variance and reproducibility
2.6 MAS failure taxonomies
2.7 Multi-agent aggregation and selection bottlenecks
```

### 3. Problem Formulation

Define:

```text
d, u, t, A, y
J = closed responsibility dimension set
π(d,u,t) → r ∈ [0,1]^|J|
r*
projection mismatch Δ(r,r*)
```

### 4. Protocol

Subsections:

```text
4.1 Responsibility projection
4.2 Responsibility-bearing bids
4.3 Clarification trigger
4.4 Agent selection
4.5 Execution and evidence collection
4.6 Settlement loss
4.7 Reputation update
```

### 5. Experiments

Subsections:

```text
5.1 Dataset: AmbiguousDelegation-300
5.2 Experiment 1: projection mismatch
5.3 Experiment 2: clarification value
5.4 Experiment 3: settlement/reputation update
5.5 Baselines and ablations
5.6 Metrics
```

### 6. Results

To be filled after running experiments.

Expected result claims should be phrased as hypotheses until measured.

### 7. Discussion

Discuss:

```text
- Why responsibility projection is different from task typing
- Why clarification is not always good
- How settlement evidence can use harnesses, LLM judges, and human ratings
- Why taxonomy closure matters
- Deployment implications
```

### 8. Limitations

Must include:

```text
- responsibility taxonomy is operational, not universal
- hidden intent labels are artificial / annotation-dependent
- LLM judges may be biased
- experiments are controlled, not full production deployment
- user feedback calibration requires longitudinal interaction
```

### Appendix A — Responsibility Taxonomy

38 dimensions.

### Appendix B — Projection and bid schemas

JSON schemas.

### Appendix C — Evaluation rubrics

Per-dimension rubric.

### Appendix D — Baseline protocol details

Task-aware routing, ambiguity clarification, LHAW-like underspecification, selection bottleneck, stochastic baseline.

---

## 8. Final positioning against major prior-work clusters

| Prior-work cluster | What it does | Our distinction |
|---|---|---|
| Task-aware delegation cues | Task-conditioned capability and coordination-risk signals | We model responsibility structure, not only task type or model win-rate. |
| Ambiguity clarification benchmarks | Identify ambiguous queries and generate clarifying questions | We evaluate delegated responsibility across roles and settlement, not only information need ambiguity. |
| Long-horizon underspecification | Remove Goal/Constraint/Input/Context information and test clarification | We model responsibility projection and claimed responsibility, not only missing task information. |
| Metacognition / calibration | Improve confidence reporting and uncertainty communication | We make uncertainty one settlement dimension within responsibility accounting. |
| Tool-use calibration | Tool type affects confidence calibration | We treat evidence reliability and provenance as settlement evidence, not as the main object. |
| Behavioral variance | Same task can produce different traces or outcomes | We measure divergence before execution in responsibility-projection space. |
| MAS failure taxonomy | Classifies failures after execution traces | We provide pre-execution governance and post-execution settlement. |
| Selection bottleneck | Aggregator quality determines whether diversity helps | We compare selection baselines but our object is delegated responsibility, not only output selection. |

---

## 9. Minimum viable paper scope

To keep the paper defensible, the first version should avoid trying to build a universal system.

Minimum viable scope:

```text
- 5 task categories
- 38 responsibility dimensions
- 300 controlled examples
- 50-example pilot
- 3 model families for projection
- 3 LLM judges + small human subset
- 4–5 strong baselines
- settlement/reputation simulation
```

The paper should not claim production readiness.

---

## 10. Recommended next workflow

```text
Step 1. Finalize these five reconstructed md files.
Step 2. Write `spec_pi_implementation_v1.0.md`.
Step 3. Write `spec_evaluation_rubric_v1.0.md`.
Step 4. Build 50-example pilot dataset.
Step 5. Run pilot projection and annotation.
Step 6. Revise taxonomy if κ/α is poor.
Step 7. Run main 300-example experiment.
Step 8. Draft paper v1.0.
Step 9. Convert to LaTeX.
```

---

## 11. Final current status

The project is no longer at “idea exploration.”

It is at:

```text
pre-experiment paper architecture locked enough for pilot construction
```

The next bottleneck is not prose.  
The next bottleneck is operationalization:

```text
projection prompt
schema enforcement
dataset construction
annotation protocol
baseline implementation
pilot agreement
```
