# Reviewer Risk and Writing Plan v1.0
## Defensive Framing and Section-by-Section Paper Construction

> Status: reconstructed reviewer-risk and writing plan  
> Role: anticipated objections, responses, and paper drafting guide  
> Companion files:
> - `paper_master_reconstruction_v1.0.md`
> - `concept_and_positioning_v1.0.md`
> - `formalization_v1.0.md`
> - `experiment_design_v1.0.md`

---

## 0. Overall reviewer-risk profile

This paper is conceptually strong but exposed to several “this is just X” objections.

The paper must avoid sounding like it independently discovered:

```text
- task-aware routing
- ambiguity clarification
- underspecification
- uncertainty calibration
- behavioral variance
- MAS failure modes
- output selection
```

Those are already covered by adjacent work.

The defensive strategy is:

```text
acknowledge each adjacent literature early,
then define the missing object:
pre-execution responsibility projection and settlement.
```

---

## 1. Risk: “This is just task-aware routing.”

### Why reviewer may think this

The protocol includes agent selection, capability profiles, cost, and reputation. Task-aware delegation work already uses task typing, capability profiles, coordination-risk cues, and routing.

### Response

Routing assumes the task object is already operationally defined. Our protocol first asks what responsibility structure the delegation implies.

### Paper sentence

> Task-aware routing estimates which model is reliable for a task type; responsibility-bearing delegation estimates what responsibility structure the request has assigned before deciding who should act.

### Experiment defense

Include task-aware routing baseline:

```text
task cluster → best historical model → execute
```

Show that responsibility projection improves scope alignment and settlement loss.

---

## 2. Risk: “This is just ambiguity clarification.”

### Why reviewer may think this

The paper uses clarification and ambiguous natural-language requests.

### Response

Ambiguity clarification benchmarks focus on ambiguous information needs. We focus on ambiguous responsibility boundaries in delegated work.

### Paper sentence

> A clarification question in our protocol is not merely a request to disambiguate a word or missing entity; it is a request to fix the responsibility boundary before an agent commits to execution.

### Experiment defense

Include generic ambiguity clarification baseline:

```text
ambiguity detector → clarify if ambiguous → execute
```

Compare against responsibility-specific clarification.

---

## 3. Risk: “LHAW already handles underspecification and clarification cost.”

### Why reviewer may think this

LHAW is close: long-horizon tasks, missing information, clarification behavior, cost-sensitive questions.

### Response

LHAW studies missing task information along Goal/Constraint/Input/Context. We study delegated responsibility projection.

### Paper sentence

> Underspecification asks what information is missing for task completion; responsibility projection asks what obligation the agent believes it has assumed.

### Experiment defense

Include LHAW-like baseline:

```text
classify missing Goal/Constraint/Input/Context → clarify
```

Show cases where no information is missing, but responsibility boundary is still ambiguous.

Example:

```text
"Improve this draft" contains enough text to act on,
but not enough responsibility specification to know whether to polish, reconstruct, or review novelty.
```

---

## 4. Risk: “Mehta already showed interpretation is the bottleneck.”

### Why reviewer may think this

Consistency Amplifies states that interpretation accuracy matters more than execution consistency and reports consistent wrong interpretation.

### Response

Use Mehta as motivation. Our paper formalizes the pre-execution responsibility commitment that Mehta diagnoses indirectly through trajectories.

### Paper sentence

> Prior work shows that interpretation failures can dominate execution variance. We make this failure mode directly measurable before execution by representing interpretation as responsibility projection over a closed taxonomy.

### Experiment defense

Measure projection before execution, not action-sequence variance.

Include within-model stochastic baseline.

---

## 5. Risk: “Cui & Alexander already showed same prompt leads to different outcomes.”

### Why reviewer may think this

They show reproducibility problems in data analysis across 480 LLM executions.

### Response

They measure outcome divergence after execution. We measure responsibility-projection divergence before execution.

### Paper sentence

> Outcome divergence studies show that LLM analyses can follow different analytical pathways. Our framework measures whether such divergence is already visible in the responsibility structure agents project before taking those pathways.

### Experiment defense

R3 result-interpretation category should include data-analysis-like artifacts and show projection divergence before analysis.

---

## 6. Risk: “MAST already has a MAS failure taxonomy.”

### Why reviewer may think this

MAST includes failure modes such as disobey task specification, disobey role specification, fail to ask clarification, and incomplete verification.

### Response

MAST is post-hoc diagnostic. Our protocol is pre-execution governance plus settlement.

### Paper sentence

> Failure taxonomies label what went wrong in completed traces; responsibility-bearing delegation governs what is projected and claimed before execution, then uses settlement evidence after execution.

### Experiment defense

Optional: map MAST labels to settlement evidence, not to projection dimensions.

---

## 7. Risk: “This is just uncertainty calibration.”

### Why reviewer may think this

The protocol includes uncertainty disclosure, overclaim penalties, and confidence.

### Response

Uncertainty is one dimension of responsibility accounting, not the whole method.

### Paper sentence

> We do not train a calibrated confidence reporter; we evaluate whether an agent’s uncertainty disclosure was appropriate for the responsibility it claimed.

### Experiment defense

Include scalar confidence baseline or no-uncertainty ablation.

---

## 8. Risk: “Tool-use calibration already shows evidence tools vs verification tools.”

### Why reviewer may think this

The protocol uses evidence collection and provenance.

### Response

Tool calibration informs evidence reliability, but our object is settlement over responsibility dimensions.

### Paper sentence

> Tool outputs enter our framework as settlement evidence with different reliability profiles; they are not themselves the unit of delegation.

### Experiment defense

In settlement, separate deterministic/harness evidence from LLM/human/retrieval evidence.

---

## 9. Risk: “Selection bottleneck already explains multi-agent performance.”

### Why reviewer may think this

The protocol includes choosing agents and may use judges.

### Response

Selection bottleneck concerns post-generation aggregation. We govern pre-generation responsibility assignment.

### Paper sentence

> Selection-based aggregation chooses among completed outputs; responsibility-bearing delegation determines what should be claimed and clarified before outputs are generated.

### Experiment defense

Include generate-then-select baseline.

---

## 10. Risk: “Responsibility taxonomy is arbitrary.”

### Why reviewer may think this

The 38 dimensions could appear hand-designed.

### Response

Do not claim universality. Claim operational closure for reproducible experiments.

### Paper sentence

> The taxonomy is not a universal ontology of responsibility; it is a closed operational index space that makes projection, annotation, comparison, settlement, and reputation update reproducible.

### Experiment defense

Report inter-annotator agreement and revise poor dimensions after pilot.

---

## 11. Risk: “Hidden intent is not observable.”

### Why reviewer may think this

`r*` may appear artificial.

### Response

Use controlled hidden intent only for evaluation. In deployment, approximate through clarification and feedback.

### Paper sentence

> Hidden responsibility profiles are used only for controlled evaluation. In deployment, intended responsibility is treated as partially observable and updated through clarification, user feedback, and repeated settlement.

### Experiment defense

Use annotator agreement and stratified analysis.

---

## 12. Risk: “LLM-as-judge is unreliable.”

### Why reviewer may think this

Rubric scoring may use LLM judges.

### Response

Use multiple LLM judges, human subset, agreement reporting, and deterministic/harness evidence where available.

### Paper sentence

> Settlement evidence may include LLM judges, but the protocol does not depend on them alone; deterministic harnesses and human ratings are used where available, and agreement is reported.

### Experiment defense

Report:

```text
LLM–LLM agreement
human–human agreement
human–LLM correlation
```

---

## 13. Risk: “Clarification increases cost and annoys users.”

### Response

Agree. Clarification is selective and cost-sensitive.

### Paper sentence

> Clarification is not treated as universally beneficial; it is triggered only when expected mismatch loss exceeds clarification cost.

### Experiment defense

Report cost-adjusted gain and unnecessary clarification rate.

---

## 14. Risk: “The method is too abstract.”

### Response

Keep algorithm, schemas, dataset, metrics, baselines, and ablations central.

### Paper must include

```text
- notation table
- closed taxonomy summary
- algorithm block
- JSON schemas
- concrete examples
- pilot agreement
- baseline comparison
```

---

## 15. Risk: “This is too much for one paper.”

### Response

Scope down.

Main paper:

```text
- projection mismatch
- clarification value
- settlement/reputation mechanism
```

Appendix:

```text
- full taxonomy
- schemas
- extended baselines
- additional risk discussion
```

Do not overload the main text with every adjacent literature detail.

---

# Part II — Writing Plan

---

## 16. Target paper title options

### Recommended

**Responsibility-Bearing Delegation: Pre-Execution Responsibility Projection and Settlement for Multi-Agent LLM Orchestration**

### Shorter

**Responsibility-Aware Delegation for Multi-Agent LLM Orchestration**

### More contrastive

**Before Agents Act: Responsibility Projection and Settlement in Multi-Agent LLM Systems**

### Avoid

Titles that sound only like routing, ambiguity, or calibration.

---

## 17. Abstract plan

The abstract should be 180–220 words.

Required structure:

```text
1. Multi-agent LLMs perform delegated work.
2. Existing methods focus on routing, aggregation, ambiguity, uncertainty, or post-hoc failure.
3. Problem: natural-language delegation leaves responsibility boundaries ambiguous.
4. Proposal: responsibility projection, bid/clarification, settlement, reputation.
5. Evaluation: controlled experiments with closed taxonomy.
6. Claim: pre-execution responsibility projection makes mismatch measurable and correctable.
```

Draft skeleton:

```text
Multi-agent LLM systems increasingly perform delegated work such as coding, reviewing, research assistance, and document editing. Existing orchestration methods often frame this as routing, aggregation, clarification, or output evaluation. However, real delegations are expressed in natural language and often leave the responsibility boundary underspecified. An agent may therefore fail not because it lacks capability, but because it commits to the wrong responsibility before execution.

We formulate this as incomplete delegation under natural-language ambiguity and introduce a responsibility-bearing delegation protocol. The protocol projects a delegation into a closed responsibility space, solicits responsibility-bearing bids, triggers clarification when projection uncertainty is high, settles execution ex post by responsibility dimension, and updates role- and responsibility-conditioned reputation.

We propose controlled experiments measuring projection mismatch, cross-family versus within-model projection divergence, clarification value, and settlement-based reputation improvement. The framework complements prior work on task-aware routing, ambiguity clarification, underspecification, calibration, behavioral variance, and MAS failure taxonomies by making the agent’s pre-execution responsibility commitment explicit and measurable.
```

---

## 18. Introduction writing plan

### Paragraph 1 — Context

LLM agents are now delegated complex work.

Mention:

```text
coding
reviewing
summarization
research support
document editing
long-horizon workflows
```

### Paragraph 2 — Existing framing

Existing methods treat orchestration as:

```text
routing
task typing
aggregation
clarification
benchmarking
failure analysis
confidence calibration
```

Acknowledge this is valuable.

### Paragraph 3 — Missing object

Introduce:

```text
pre-execution responsibility commitment
```

Use example:

```text
"Improve this paper draft."
```

Show multiple possible responsibilities.

### Paragraph 4 — Projection mismatch

Define projection mismatch.

Emphasize:

```text
not low capability;
wrong responsibility.
```

### Paragraph 5 — Relation to recent work

Mention recent work has shown:

```text
interpretation matters,
same prompts produce different outcomes,
agents fail to clarify,
MAS failures include role/specification failures.
```

Then pivot:

```text
We move one step earlier.
```

### Paragraph 6 — Proposed protocol

Summarize pipeline.

### Paragraph 7 — Contributions

Use final contribution list.

---

## 19. Related work writing plan

Do not write a broad survey. Write contrastive related work.

Each subsection should have:

```text
what this literature does
why it is related
what it does not capture
how our paper differs
```

Recommended order:

```text
2.1 Task-aware routing and delegation cues
2.2 Ambiguity clarification and underspecification
2.3 Uncertainty communication and calibration
2.4 Behavioral variance and reproducibility
2.5 MAS failure taxonomies
2.6 Aggregation and selection
```

The paper should not spend too much space on old general agent frameworks unless needed.

---

## 20. Method writing plan

### 3.1 Problem setup

Define:

```text
d, u, t, a, A
```

### 3.2 Responsibility taxonomy

Introduce:

```text
J, |J|=38
R1–R5 and RX
```

Full taxonomy goes appendix.

### 3.3 Projection

Define:

```text
r = π(d,u,t,a)
J*(d)
projection mismatch
```

### 3.4 Bid

Define:

```text
b_i = (q_i, u_i, p_i, z_i)
```

### 3.5 Clarification

Define cost-sensitive trigger.

### 3.6 Settlement

Define:

```text
s_ij, v_ij, ℓ_ij, L_i
```

### 3.7 Reputation

Define additive EMA.

### 3.8 Algorithm

One algorithm block.

---

## 21. Experiment writing plan

### 4.1 Dataset

AmbiguousDelegation-300.

### 4.2 Exp 1

Projection mismatch.

### 4.3 Exp 1B

Within-model stochastic baseline.

### 4.4 Exp 2

Clarification.

### 4.5 Exp 3

Reputation.

### 4.6 Baselines

List all.

### 4.7 Metrics

Define all.

---

## 22. Discussion writing plan

Key discussion points:

```text
- why responsibility projection is not task typing
- when clarification helps
- why closed taxonomy matters
- how settlement evidence should be interpreted
- how this could integrate with task-aware routing and MAS failure taxonomies
```

---

## 23. Limitations writing plan

Must include:

```text
1. Taxonomy is operational and limited.
2. Hidden intent is annotated, not directly observed.
3. Experiments are controlled.
4. LLM judges have bias.
5. User-feedback calibration is not fully validated.
6. Longitudinal deployment remains future work.
```

---

## 24. Rebuttal-ready one-liners

### If reviewer says “routing”

> Routing chooses an agent for a task; our protocol first determines what responsibility the task delegates.

### If reviewer says “ambiguity”

> Ambiguity benchmarks clarify information needs; our protocol clarifies responsibility boundaries.

### If reviewer says “LHAW”

> LHAW removes missing task information; we project responsibility even when the task input is complete but the delegated role is ambiguous.

### If reviewer says “MAST”

> MAST diagnoses completed traces; our protocol governs pre-execution commitment and then settles fulfillment.

### If reviewer says “Mehta”

> Mehta shows interpretation is the bottleneck; we operationalize interpretation as measurable pre-execution responsibility projection.

### If reviewer says “Cui”

> Cui and Alexander measure outcome variance; we measure responsibility-projection variance before outcomes are produced.

### If reviewer says “selection bottleneck”

> Selection chooses among generated outputs; our protocol decides what should be generated and under which responsibility claim.

---

## 25. Final writing priority

Do not start LaTeX yet.

Write in this order:

```text
1. spec_pi_implementation_v1.0.md
2. spec_evaluation_rubric_v1.0.md
3. full paper outline v0.9
4. pilot dataset
5. experiment scripts
6. paper draft v1.0
7. LaTeX conversion
```

The paper is conceptually ready, but experimentally not yet locked.
