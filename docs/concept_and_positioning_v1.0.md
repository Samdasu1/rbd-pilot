# Concept and Positioning v1.0
## Reframing Responsibility-Bearing Delegation Against Adjacent Prior Work

> Status: reconstructed positioning document  
> Role: concept clarification + related-work differentiation  
> Companion files:
> - `paper_master_reconstruction_v1.0.md`
> - `formalization_v1.0.md`
> - `experiment_design_v1.0.md`
> - `reviewer_risk_and_writing_plan_v1.0.md`

---

## 0. Core repositioning

The project began from a strong intuition:

> Multi-agent LLM orchestration should be treated like a responsibility-bearing process, not merely as output generation.

After reviewing the expanded prior work, this intuition must be made narrower and more technical.

The final conceptual move is:

```text
Natural-language delegation is ambiguous not only because words have multiple meanings,
but because the delegated responsibility boundary is under-specified.
```

This produces a failure mode:

```text
Projection mismatch:
the agent commits to the wrong responsibility structure before execution.
```

This is distinct from:

```text
- task ambiguity,
- underspecified input,
- model confidence miscalibration,
- behavioral variance,
- post-hoc failure modes,
- poor aggregation,
- poor model selection.
```

Those phenomena are related, but they are not identical to responsibility projection.

---

## 1. Why “responsibility projection” is the right core object

A user request like:

```text
Improve this draft.
```

does not merely ask for an output. It implicitly delegates responsibility for some subset of:

```text
- conceptual reconstruction
- logical consistency
- novelty assessment
- evidence-claim alignment
- writing polish
- structural reorganization
- uncertainty disclosure
- overclaim avoidance
```

A capable agent may still fail if it chooses the wrong subset.

Example:

```text
User intended:
    conceptual reconstruction + reviewer-risk assessment

Agent projected:
    grammar polish + flow improvement

Observed output:
    fluent, useful, but wrong task

Failure:
    not low capability, but projection mismatch
```

This is why “responsibility projection” should be treated as a first-class pre-execution object.

---

## 2. Relationship to Task-Aware Delegation Cues

### What the prior work does

`Task-Aware Delegation Cues for LLM Agents` proposes a task-aware collaboration signaling layer. It uses semantic clustering of prompts, derives task-conditioned capability profiles from pairwise preference data, and uses coordination-risk cues such as disagreement/tie-rate to drive delegation decisions.

Its loop can be summarized as:

```text
task typing
→ capability profile
→ coordination-risk cue
→ routing / auditor decision
→ rationale disclosure
→ accountability logging
```

### Why it is close

It shares several commitments:

```text
- delegation should be visible and auditable;
- users need reliability cues;
- task-conditioned competence matters;
- disagreement/uncertainty can trigger intervention;
- collaboration requires accountability.
```

### Key distinction

Task-aware delegation cues answer:

```text
Given a task type, which model or routing mode is reliable?
```

Responsibility-bearing delegation asks:

```text
Before choosing a model, what responsibility structure is being assigned?
```

The difference is the object being typed:

| Dimension | Task-aware cues | Responsibility-bearing delegation |
|---|---|---|
| Primary object | task cluster | responsibility vector |
| Main signal | task-conditioned win-rate / tie-rate | responsibility projection / mismatch |
| Intervention | route, add auditor, disclose rationale | clarify, bid, settle, update responsibility reputation |
| Accountability | log routing and rationale | settle claimed responsibility by dimension |
| Risk | poor model-task match | wrong responsibility commitment |

### How to cite/position

Use the prior work as the nearest “delegation” paper, then differentiate:

> Task-aware delegation cues make model reliability visible at the task-type level. Our protocol instead makes the responsibility structure of the delegation itself explicit before execution.

---

## 3. Relationship to CLAMBER

### What the prior work does

CLAMBER is a benchmark for identifying and clarifying ambiguous information needs. It defines a taxonomy of ambiguous queries with three primary dimensions:

```text
- Epistemic Misalignment
- Linguistic Ambiguity
- Aleatoric Output
```

and eight fine-grained categories such as unfamiliar entities, contradiction, lexical ambiguity, semantic ambiguity, and missing WHO/WHEN/WHERE/WHAT elements.

It evaluates whether LLMs can:

```text
1. identify whether a query is ambiguous;
2. generate a useful clarifying question.
```

### Why it is close

It directly addresses clarification under ambiguity. It also shows that CoT/few-shot prompting may not reliably solve ambiguity identification, and may induce overconfidence in some settings.

### Key distinction

CLAMBER focuses on **ambiguous information needs**.

Our paper focuses on **ambiguous delegated responsibility**.

Example difference:

```text
CLAMBER-style ambiguity:
    "When did he land on the moon?"
    Problem: unclear referent "he"

Responsibility-delegation ambiguity:
    "Improve this paper draft."
    Problem: unclear responsibility boundary
    Is the agent responsible for grammar, novelty, logic, experiments, citations, or reviewer risk?
```

### Positioning sentence

> Ambiguity benchmarks such as CLAMBER evaluate whether a model recognizes and clarifies ambiguous user queries. Our work addresses a different ambiguity: the responsibility boundary implied by delegated work, where several valid task interpretations may correspond to different responsibilities, roles, and settlement consequences.

---

## 4. Relationship to LHAW

### What the prior work does

LHAW generates controllably underspecified long-horizon tasks by removing information along four dimensions:

```text
- Goal
- Constraint
- Input
- Context
```

It validates underspecified variants empirically through agent trials and classifies them as:

```text
- outcome-critical
- divergent
- benign
```

It also studies clarification efficiency using metrics such as gain per question.

### Why it is close

LHAW is highly relevant because it treats clarification as costly and evaluates when agents should ask questions in long-horizon workflows. This overlaps with our clarification trigger.

### Key distinction

LHAW studies **missing task information**.

Our paper studies **responsibility projection under delegated work**.

The two can overlap, but they are not the same.

Example:

```text
LHAW underspecification:
    "Use the latest dataset."
    Missing input: which dataset?

Responsibility projection:
    "Check whether this result makes sense."
    Missing responsibility boundary:
        numerical correctness?
        statistical validity?
        causal claim adequacy?
        plot-claim correspondence?
        overclaim risk?
```

### Important incorporation

LHAW strengthens our experiment design in two ways:

1. Clarification must be cost-sensitive.
2. Ambiguity should be validated by behavioral consequences, not only linguistic intuition.

Therefore, our clarification experiment should include:

```text
ClarificationValue(d) = reduction in expected settlement loss after clarification
ClarificationEfficiency(d) = loss reduction / number or cost of clarification turns
```

### Positioning sentence

> LHAW operationalizes underspecification by removing outcome-critical task information. Our protocol instead operationalizes delegated responsibility by projecting ambiguous work requests into responsibility dimensions, allowing clarification when the responsibility structure—not merely missing input—is uncertain.

---

## 5. Relationship to metacognition and uncertainty communication

### What the prior work does

`Improving Metacognition and Uncertainty Communication in Language Models` studies whether LLMs can communicate confidence more reliably. It evaluates:

```text
- single-question confidence estimation
- pairwise confidence comparison
```

and measures calibration/discrimination across domains. It finds that uncertainty communication is trainable but task-specific, with broader generalization requiring multitask fine-tuning.

### Why it is close

Our protocol includes uncertainty disclosure as a cross-cutting responsibility dimension.

### Key distinction

Metacognition work asks:

```text
Can the model accurately express how likely its answer is correct?
```

Our paper asks:

```text
Did the agent disclose uncertainty about the responsibility it claimed to assume,
and should its future responsibility reputation be updated based on settlement?
```

This is not merely answer confidence. It is responsibility-scope confidence.

Example:

```text
Agent says:
    "I can polish the writing, but I cannot verify novelty without literature search."

This is not just confidence = 0.7.
It is a bid-level limitation and uncertainty disclosure over dimensions.
```

### Incorporation

The metacognition literature should inform:

```text
RX.1 Uncertainty disclosure
q_ij claimed responsibility coverage
u_ij uncertainty vector
overclaim penalty
calibration metrics between claimed q/u and observed fulfillment
```

---

## 6. Relationship to tool-use calibration and the Confidence Dichotomy

### What the prior work does

`The Confidence Dichotomy` argues that tool type affects calibration:

```text
- evidence tools such as web search can induce overconfidence because retrieved evidence is noisy;
- verification tools such as code interpreters can ground reasoning through deterministic feedback.
```

### Why it is close

Our settlement step uses evidence. Some evidence is deterministic; some is noisy.

### Key distinction

Tool-use calibration is about confidence dynamics under tools.

Our paper treats tool outputs as **settlement evidence** whose reliability depends on source type.

### Incorporation

The formalization should distinguish evidence source reliability:

```text
e ∈ E_i
type(e) ∈ {deterministic, harness, human, LLM-judge, retrieval/evidence-tool}
reliability(e) ∈ [0,1]
```

This can affect settlement:

```text
v_ij = aggregate_e reliability(e) · score_ij(e)
```

In the first paper, this can stay simple:

```text
deterministic/harness evidence gets priority when available;
LLM/human judgment is used for dimensions without deterministic evidence;
retrieval-based evidence must be provenance-tracked under RX.5.
```

---

## 7. Relationship to behavioral variance and reproducibility

### Same Prompt, Different Outcomes

This work shows that LLM-generated data analysis can vary substantially even under the same task/data/settings. It evaluates 480 attempts across models, prompting strategies, and temperatures. It finds that data preparation differences can propagate into different analytical conclusions.

### Why it is close

It supports the premise that one execution is insufficient and that variance matters.

### Key distinction

It measures **output and pipeline variance after execution**.

Our paper measures **responsibility projection variance before execution**.

### Conceptual bridge

Their finding can be interpreted as downstream evidence of upstream divergence:

```text
Different data-preparation choices may reflect different implicit responsibility projections:
    prioritize reproducibility?
    include all records?
    clean missing values conservatively?
    match human analysis?
    produce executable code only?
```

But the prior work does not measure this projection directly.

### Positioning sentence

> Outcome-reproducibility studies show that identical prompts can lead to different analytical conclusions. We move one step earlier by measuring whether agents project different responsibility structures before execution begins.

---

## 8. Relationship to Consistency Amplifies

### What the prior work does

`Consistency Amplifies` measures behavioral consistency in SWE-bench-style agents. It reports that consistency correlates with accuracy across models, but consistency can amplify wrong interpretations. A key result is that many failures are “consistent wrong interpretation.”

### Why it is close

This is one of the closest papers conceptually because it states that interpretation quality matters more than execution consistency.

### Key distinction

It diagnoses interpretation failure from repeated execution trajectories.

Our paper directly models the pre-execution responsibility commitment.

### Reframing

Use this prior work as motivation, not as a competitor to avoid.

```text
Consistency Amplifies:
    interpretation accuracy matters more than execution consistency.

Our paper:
    interpretation failure is often a responsibility-projection failure,
    and can be measured before execution in a closed responsibility space.
```

### Required contribution wording

Contribution 1 should explicitly say:

> We make interpretation failure measurable as pre-execution responsibility projection, separating it from action-sequence variance and post-hoc trajectory analysis.

---

## 9. Relationship to MAST

### What the prior work does

MAST builds a multi-agent system failure taxonomy from annotated execution traces. It includes 14 failure modes across:

```text
- system design issues
- inter-agent misalignment
- task verification
```

Examples include:

```text
- disobey task specification
- disobey role specification
- fail to ask for clarification
- no or incomplete verification
- incorrect verification
```

### Why it is close

MAST contains several failure modes that overlap with our protocol’s concerns.

### Key distinction

MAST is **post-hoc diagnostic**.

Our protocol is **pre-execution governance + post-execution settlement**.

MAST asks:

```text
What went wrong in the completed trace?
```

Our protocol asks:

```text
What responsibility was projected, claimed, and clarified before execution,
and how should the result be settled afterward?
```

### Integration

MAST labels can serve as settlement evidence or failure-mode tags in our experiment, but they are not the same as the responsibility projection itself.

### Positioning sentence

> MAS failure taxonomies diagnose completed traces; responsibility-bearing delegation governs the pre-execution responsibility commitment that may prevent some such failures before they appear in traces.

---

## 10. Relationship to When Agents Disagree / Selection Bottleneck

### What the prior work does

This work argues that diverse multi-agent teams help only when the aggregation/selection mechanism is strong enough. It defines a selector-quality threshold and shows judge-based selection can outperform synthesis-style aggregation.

### Why it is close

Our protocol also selects agents and may use reviewers/judges.

### Key distinction

Selection bottleneck work asks:

```text
Given candidate outputs, which output should be selected?
```

Our paper asks:

```text
Before output generation, which responsibility should be projected, claimed, clarified, and assigned?
```

### Incorporation

It should become a baseline or comparison condition:

```text
Generate-then-select baseline:
    several agents execute directly;
    judge selects final answer;
    no responsibility projection or bid.
```

If our protocol outperforms this baseline, the contribution is stronger because it shows value beyond output selection.

### Positioning sentence

> Selection-based aggregation can exploit output diversity after generation. Our protocol instead governs the responsibility commitment before generation, and settlement can later use selection or judging as one evidence source.

---

## 11. Final conceptual map

```text
Ambiguity literature:
    asks whether user query is ambiguous.

Underspecification literature:
    asks what missing information prevents task completion.

Calibration literature:
    asks whether model confidence matches correctness.

Behavioral variance literature:
    asks whether agents behave or conclude consistently.

MAS failure taxonomy:
    asks what failed after execution.

Selection bottleneck literature:
    asks how to pick the best generated output.

Responsibility-bearing delegation:
    asks what responsibility the agent projected and claimed before execution,
    whether clarification should occur,
    and how fulfillment should be settled by responsibility dimension.
```

---

## 12. Final “gap” statement

The clearest gap statement is:

> Existing work has made task type, ambiguity, underspecification, confidence, behavioral variance, aggregation quality, and post-hoc failure modes measurable. What remains under-specified is the agent’s pre-execution responsibility commitment: what responsibility it believes it has been delegated, what it claims it can assume, whether it should clarify that commitment, and how the commitment should be settled after execution.

This should be the intellectual center of the paper.

---

## 13. Recommended related-work section skeleton

### 2.1 Task-aware delegation and routing

- Task-conditioned capability profiles
- Coordination-risk cues
- Difference: task type vs responsibility vector

### 2.2 Ambiguity and clarification

- CLAMBER
- ClariQ / AmbigQA if needed
- Difference: information need ambiguity vs delegated responsibility ambiguity

### 2.3 Underspecification in long-horizon workflows

- LHAW
- Difference: missing Goal/Constraint/Input/Context vs responsibility projection

### 2.4 Uncertainty communication and calibration

- Metacognition
- Confidence Dichotomy
- Difference: confidence reporting vs responsibility-bearing uncertainty disclosure

### 2.5 Behavioral variance and reproducibility

- Same Prompt, Different Outcomes
- Consistency Amplifies
- Difference: post-execution variance vs pre-execution projection divergence

### 2.6 MAS failure diagnosis

- MAST
- Difference: post-hoc taxonomy vs pre-execution governance and settlement

### 2.7 Aggregation and selection

- When Agents Disagree
- MoA/Self-MoA if needed
- Difference: output selection vs responsibility assignment

---

## 14. Terms to avoid or use carefully

Avoid overusing:

```text
accountability
intent
ground truth responsibility
optimal agent
guarantee
causal
universal taxonomy
```

Use instead:

```text
operational responsibility
projected responsibility
later-preferred responsibility
controlled evaluation
settlement evidence
responsibility-conditioned reputation
pre-execution commitment
```

---

## 15. Final conceptual recommendation

The paper should be written as:

```text
A protocol paper with controlled experiments
```

not as:

```text
A benchmark paper
A theory paper
A routing paper
A clarification paper
A calibration paper
A MAS failure taxonomy paper
```

The winning framing is:

> We introduce the missing pre-execution layer between natural-language delegation and agent execution.
