# Full Paper Reconstruction v1.0
## Responsibility-Bearing Delegation under Ambiguity, Calibration, and Multi-Agent Failure Evidence

> Status: condensed reconstruction document  
> Purpose: Re-align the paper concept, contributions, formulation, experiments, and reviewer-defense strategy after incorporating the internal development chain and the newly reviewed adjacent literature.  
> Working title: **Responsibility-Bearing Delegation: A Settlement Protocol for Multi-Agent LLM Orchestration under Natural-Language Ambiguity**  
> Use: This document should replace the scattered v0.2–v0.9 planning notes as the next working master document before drafting `paper_draft_v1.0.md` or converting to LaTeX.

---

## 0. Executive Summary

The paper should no longer be framed as merely proposing a new routing method, benchmark, or agent-evaluation harness. After incorporating the adjacent literature, the defensible core is narrower and stronger:

> **Multi-agent LLM orchestration fails not only because agents execute poorly, but because ambiguous natural-language delegations are first projected into the wrong responsibility structure. Existing work measures ambiguity, uncertainty, behavioral variance, task-specific reliability, or post-hoc failures; this paper formalizes the pre-execution responsibility commitment itself and introduces a protocol for clarifying, bidding, settling, and updating responsibility over repeated delegation.**

The key shift is from:

```text
old framing:
    agent routing + ex-post settlement inspired by electricity markets

new framing:
    responsibility projection + clarification + settlement as a governance layer
    for ambiguous delegation before, during, and after execution
```

The most important conceptual distinction is temporal:

```text
Before execution:
    What responsibility does the agent believe it is being asked to bear?
    Should this projection be clarified before commitment?

During execution:
    Which agent executes, verifies, or audits under the agreed responsibility scope?

After execution:
    Did the agent fulfill the responsibility it claimed, disclose uncertainty,
    avoid overclaiming, and preserve traceability?
```

The paper should claim a **protocol-level contribution**, not a universal theory of intent. Its target is controlled evidence that responsibility projection mismatch is measurable, that clarification can reduce costly mismatch, and that responsibility-conditioned settlement improves repeated delegation relative to scalar reputation or routing-only baselines.

---

## 1. Reconstructed Core Problem

### 1.1 Incomplete delegation

The central problem is **incomplete delegation**.

> **Incomplete delegation** is the setting in which a user or orchestrator assigns complex work to an LLM agent through natural language while the task-specific capability, scope boundary, responsibility dimension, and evaluation criterion remain only partially specified before execution.

This setting is common in real workflows:

```text
Improve this paper draft.
Review this code.
Check whether this result makes sense.
Make this proposal stronger.
Prepare this for submission.
Fix this implementation.
Summarize this report for decision-making.
```

These are not empty prompts. They contain rich intent. However, they are operationally under-specified: the request may imply writing polish, conceptual reconstruction, novelty assessment, mathematical verification, regression-risk review, uncertainty disclosure, or decision-relevant summarization.

The failure mode is not simply poor output quality. A capable agent can fail by doing a high-quality version of the wrong responsibility.

### 1.2 Projection mismatch

> **Projection mismatch** occurs when an ambiguous natural-language delegation is mapped into responsibility dimensions that differ from the responsibility structure intended, preferred, or later endorsed by the delegator.

Example:

```text
Delegation:
    "Improve this paper draft."

User intended responsibility:
    conceptual reconstruction + contribution logic + reviewer-risk assessment

Agent projected responsibility:
    sentence polish + title refinement + smoother transitions

Failure:
    output may be fluent and locally useful, but it solves the wrong delegation problem.
```

This paper should emphasize that projection mismatch is distinct from:

```text
- execution error
- benchmark failure
- tool failure
- low model capability
- post-hoc failure taxonomy label
- within-model stochastic variance
- final-output reproducibility variance
```

The paper's object of measurement is the **pre-execution projected responsibility vector**.

---

## 2. Positioning Against Newly Reviewed Literature

The newly reviewed papers do not eliminate the contribution. They force the paper to become more precise.

### 2.1 Task-aware delegation cues

**Task-Aware Delegation Cues for LLM Agents** proposes a collaboration signaling layer that derives task-conditioned capability profiles and coordination-risk cues from preference data. It uses semantic clustering over prompts, task-conditioned win rates, and tie rates as coordination-risk priors. Its loop includes task typing, routing, rationale disclosure, and accountability logging.

Our paper should explicitly acknowledge this as the closest delegation-oriented prior work.

Structural difference:

```text
Task-aware delegation cues:
    task type → capability profile / coordination risk → routing or auditing cue

Responsibility-bearing delegation:
    natural-language delegation → responsibility projection → responsibility-bearing bid
    → clarification / execution → settlement → dimension-conditioned reputation
```

Their unit is **task-conditioned reliability**. Our unit is **responsibility-conditioned commitment**.

The critical distinction:

> A task type can tell which model tends to win on similar prompts, but it does not specify what responsibility the agent is claiming to bear on this particular ambiguous delegation.

### 2.2 Ambiguity and clarification benchmarks

**CLAMBER** introduces a taxonomy and benchmark for identifying and clarifying ambiguous information needs, with three broad dimensions and eight fine-grained categories such as unfamiliar entities, contradictions, lexical ambiguity, semantic ambiguity, and missing WHO/WHEN/WHERE/WHAT output elements.

This is highly relevant because it establishes that LLMs struggle to identify and clarify ambiguity even with prompting strategies.

Structural difference:

```text
CLAMBER:
    ambiguous information need → ambiguity identification → clarifying question quality

Responsibility-bearing delegation:
    ambiguous delegated work → responsibility projection → bid / clarification
    → responsibility settlement and reputation update
```

CLAMBER evaluates whether a query is ambiguous and whether a clarifying question is good. Our protocol evaluates whether the **responsibility scope of delegated work** has been projected, claimed, clarified, executed, and settled.

### 2.3 Controllable underspecification in long-horizon tasks

**LHAW** generates controllably underspecified variants of long-horizon workflow tasks by removing information across four dimensions: Goal, Constraint, Input, and Context. It empirically validates whether variants are outcome-critical, divergent, or benign by running agent trials, and introduces clarification-efficiency analysis such as performance gain per question.

This is directly relevant to the clarification-cost argument.

Structural difference:

```text
LHAW:
    well-specified task → remove Goal/Constraint/Input/Context information
    → empirical agent trials → classify underspecification severity

Responsibility-bearing delegation:
    naturally ambiguous delegation → project onto closed responsibility taxonomy
    → ask whether responsibility commitment itself should be clarified
```

LHAW studies missing information required for long-horizon task success. Our paper studies responsibility mismatch even when all surface inputs may be present.

### 2.4 Metacognition and uncertainty communication

**Improving Metacognition and Uncertainty Communication in Language Models** shows that uncertainty communication is trainable, but task-specific: single-question confidence estimation and pairwise confidence comparison do not automatically transfer, while multitask training yields broader gains.

This supports our RX.1 uncertainty-disclosure dimension, but it is not the same contribution.

Structural difference:

```text
Metacognition paper:
    Can the model communicate its confidence about answer correctness?

Responsibility-bearing delegation:
    Can the agent disclose uncertainty about the responsibility it claims,
    the scope it assumes, and the evidence supporting fulfillment?
```

The relevant distinction is **answer confidence** versus **responsibility-scope uncertainty**.

### 2.5 Tool-use calibration and confidence dichotomy

**The Confidence Dichotomy** shows that tool type changes calibration dynamics: evidence tools such as web search can induce severe overconfidence because retrieved information is noisy, whereas verification tools such as code interpreters provide deterministic grounding and can mitigate miscalibration.

This should reshape the settlement section. Evidence should not be treated as a uniform object.

Add to protocol:

```text
Evidence reliability depends on evidence type:
    verification evidence: deterministic, execution-grounded, low ambiguity
    evidence-tool evidence: noisy, retrieved, potentially overconfidence-inducing
    judge evidence: rubric-based, useful but bias-prone
    human evidence: expensive but high-value for ambiguous responsibility dimensions
```

This maps naturally to RX.1 uncertainty disclosure and RX.5 provenance/traceability.

### 2.6 Behavioral variance and reproducibility

**Same Prompt, Different Outcomes** shows that repeated LLM-generated data analysis can yield different results under the same task, data, and settings; variation often arises in data-preparation steps and propagates into final estimates.

This supports the need to inspect upstream commitments rather than only final outputs.

Structural difference:

```text
Same Prompt, Different Outcomes:
    same task/data/settings → multiple executions → output variance in analysis results

Responsibility-bearing delegation:
    same delegation/artifact → multiple projections → responsibility-vector divergence
    before execution begins
```

Their finding is downstream evidence. Our mechanism predicts one upstream source of such divergence: different responsibility projections.

### 2.7 Behavioral consistency and interpretation bottleneck

**Consistency Amplifies** argues that interpretation accuracy matters more than execution consistency. Consistency can amplify correct or incorrect outcomes; a major failure mode is repeated wrong interpretation.

This should be absorbed as motivation, not treated as competition.

Structural difference:

```text
Consistency Amplifies:
    execution trajectories reveal that consistent wrong interpretation causes failures

Responsibility-bearing delegation:
    responsibility projection makes that interpretation commitment explicit before execution
```

The sentence to preserve:

> We share the diagnosis that interpretation quality is central, but reframe interpretation as a delegation problem: before an agent acts, it has already committed to a responsibility structure.

### 2.8 Multi-agent failure taxonomies

**MAST / Why Do Multi-Agent LLM Systems Fail?** provides an empirically grounded taxonomy of 14 MAS failure modes across system design issues, inter-agent misalignment, and task verification, based on 1600+ traces with high inter-annotator agreement.

This is essential for reviewer defense.

Structural difference:

```text
MAST:
    post-hoc taxonomy over completed MAS execution traces

Responsibility-bearing delegation:
    pre-execution governance protocol plus ex-post settlement
```

MAST labels can become settlement evidence, especially for:

```text
- Disobey task specification
- Disobey role specification
- Fail to ask for clarification
- No or incomplete verification
- Incorrect verification
- Information withholding
```

But MAST does not by itself determine whether the agent should have clarified before commitment, nor does it update future responsibility-conditioned reputation.

### 2.9 Selection bottleneck in multi-agent pipelines

**When Agents Disagree** argues that the benefit of diverse multi-agent teams depends on selector quality. Diverse candidate pools help only when the selector can identify the best output; synthesis can waste diversity.

This is relevant but orthogonal.

Structural difference:

```text
Selection bottleneck:
    candidate generation diversity + selector quality → output quality

Responsibility-bearing delegation:
    responsibility projection + bid + clarification + settlement → accountable delegation
```

However, the selection-bottleneck model suggests a useful baseline:

```text
generate-then-select baseline:
    multiple agents execute immediately; judge selects best output

proposed protocol:
    multiple agents project/bid first; clarification happens before execution; settlement updates reputation
```

The proposed protocol should outperform generate-then-select especially when wrong responsibility projections produce superficially polished but misaligned outputs.

---

## 3. Reconstructed Thesis and Contributions

### 3.1 Core thesis

> Multi-agent LLM orchestration is not merely a problem of routing, selection, clarification, or post-hoc failure diagnosis. It is an incomplete delegation problem under natural-language ambiguity, where the first critical commitment is the projection of a request into responsibility dimensions before execution begins.

### 3.2 Expanded thesis

Natural-language delegations are semantically rich but operationally ambiguous. Existing systems often respond by selecting a model, decomposing a task, running a tool, asking a generic clarification, or evaluating the final output. These mechanisms are useful but incomplete because they do not explicitly represent what responsibility the agent believes it is assuming.

A responsibility-bearing delegation protocol makes this commitment explicit. It projects the delegation into a closed responsibility space, allows agents to bid on responsibility coverage or request clarification, executes under the agreed scope, settles fulfillment against responsibility dimensions, and updates role- and responsibility-conditioned reputation.

### 3.3 Contributions

#### Contribution 1 — Pre-execution responsibility projection

We formulate ambiguous multi-agent LLM orchestration as **responsibility projection** over a closed operational taxonomy.

This differs from prior work because the measured object is:

```text
- pre-execution, not post-hoc trace-based;
- responsibility-dimensional, not only task-type-based;
- vector-valued, not only categorical ambiguity labels;
- commitment-oriented, not only final-output variance.
```

#### Contribution 2 — Responsibility-bearing bid and clarification protocol

We introduce a delegation protocol in which agents submit bids specifying:

```text
- claimed capability,
- claimed scope,
- claimed responsibility coverage,
- uncertainty about each responsibility dimension,
- bid type: execute / clarify / partial / limit,
- cost.
```

This extends task-aware routing and clarification benchmarks by making the agent's responsibility claim explicit before execution.

#### Contribution 3 — Settlement loss and responsibility-conditioned reputation

We define ex-post settlement over the same responsibility dimensions used at projection time. Settlement combines:

```text
- category-specific fulfillment,
- uncertainty disclosure,
- overclaim avoidance,
- scope adherence,
- downstream-harm avoidance,
- provenance and traceability.
```

The settlement signal updates role- and responsibility-conditioned reputation via additive EMA rather than scalar global reputation.

#### Contribution 4 — Controlled experimental framework

We propose a controlled experimental suite that measures:

```text
1. projection mismatch across model families;
2. clarification value under high projection uncertainty;
3. settlement-based reputation improvement over scalar routing;
4. whether cross-family projection divergence exceeds within-model stochastic variance;
5. whether responsibility-aware clarification beats task-aware routing, ambiguity-only clarification,
   generate-then-select, and post-hoc failure-diagnosis baselines.
```

This contribution should be framed as a first controlled framework, not a complete benchmark.

---

## 4. Reconstructed Formalization

### 4.1 Delegation and context

Let:

```text
d ∈ D       natural-language delegation
u           user or delegator
t           task context or task family
a           artifact to be acted on
A           candidate agent set {a_1, ..., a_n}
y_i         role assigned to agent i
```

A delegation is not evaluated directly. It is first projected into a responsibility space.

### 4.2 Closed responsibility space

Let:

```text
J = {1, ..., 38}
```

be the closed index space defined by the responsibility taxonomy.

The taxonomy contains:

```text
R1 Paper draft / research writing       7 dimensions
R2 Code review / bug-fix                7 dimensions
R3 Result interpretation                6 dimensions
R4 Proposal improvement                 7 dimensions
R5 Technical summarization              6 dimensions
RX Cross-cutting                        5 dimensions
```

The cross-cutting dimensions are:

```text
RX.1 Uncertainty disclosure
RX.2 Overclaim avoidance
RX.3 Scope adherence
RX.4 Downstream-harm avoidance
RX.5 Provenance and traceability
```

### 4.3 Responsibility projection

Projection maps a delegation and artifact to a responsibility-weight vector:

```math
r = π(d, a, u, t) ∈ [0,1]^|J|
```

where `r_j` is the projected importance of responsibility dimension `j`.

The active set is:

```math
J^*(d) = {j ∈ J : r_j > τ_r} ∪ J_X
```

where `τ_r = 0.3` by default and `J_X = {RX.1, ..., RX.5}`.

Important stance:

> `π` is not claimed to recover true user intent. It is an operational projection that makes responsibility assumptions measurable, comparable, clarifiable, and revisable.

### 4.4 Projection mismatch

Let `r*` denote the hidden, annotated, clarified, or later user-endorsed responsibility profile.

Projection mismatch is:

```math
M(d,u,t) = Δ(r, r^*)
```

where `Δ` can be cosine distance, Jaccard distance over active sets, or a weighted combination:

```math
M = α_1 M_miss + α_2 M_extra + α_3 M_priority + α_4 M_role
```

Interpretation:

```text
M_miss      important responsibility dimensions omitted
M_extra     unnecessary responsibility dimensions included
M_priority  wrong importance ordering
M_role      wrong role interpretation
```

### 4.5 Responsibility-bearing bid

Each agent submits:

```math
b_i = (c_i, s_i, q_i, u_i, p_i, z_i)
```

where:

```text
c_i   capability claim
s_i   scope claim
q_i   responsibility coverage vector in [0,1]^|J|
u_i   uncertainty vector in [0,1]^|J|
p_i   cost claim
z_i   bid type ∈ {execute, clarify, partial, limit}
```

A bid is not a generic confidence score. It is a task-conditioned commitment to responsibility dimensions.

### 4.6 Clarification trigger

Clarification is triggered when expected mismatch loss exceeds clarification cost.

Minimal rule:

```math
C(d)=1 \quad \text{if} \quad H(P(r|d,a)) > τ_H
```

or:

```math
C(d)=1 \quad \text{if} \quad E[L_{mismatch} | d,a] > κ_{clarify}
```

A more explicit form:

```math
C(d)=1 \quad \text{if} \quad
λ_M \widehat{M}(d) + λ_D D_{agents}(d) + λ_U \bar{u}(d) > κ_Q
```

where:

```text
M_hat(d)     estimated projection mismatch risk
D_agents(d)  disagreement among projected responsibility vectors
u_bar(d)     average uncertainty over active dimensions
κ_Q          clarification cost threshold
```

This connects to LHAW's cost-sensitive clarification setting but applies to responsibility mismatch rather than only missing information.

### 4.7 Agent selection

The selected agent maximizes responsibility-adjusted utility:

```math
i^* = \arg\max_i U_i
```

with:

```math
U_i = \sum_{j ∈ J^*(d)} w_j^{(u,t)} q_{ij} ρ_{i,y,j,t}
      - β p_i
      - γ \sum_{j ∈ J^*(d)} u_{ij}
      - ζ R_i^{overclaim}
```

Selection should prefer an agent that:

```text
- covers the important responsibility dimensions,
- has good role- and dimension-conditioned reputation,
- discloses uncertainty honestly,
- has acceptable cost,
- does not overclaim.
```

### 4.8 Evidence collection

Evidence is not homogeneous. The protocol should classify evidence by reliability type:

```text
D  deterministic evidence: tests, schema checks, numerical verification
X  tool/harness evidence: linter, unit tests, code interpreter, external checker
R  retrieval/evidence-tool evidence: web search, RAG, API output; noisy and overconfidence-prone
J  judge evidence: LLM-as-judge or panel evaluation
H  human evidence: annotator or user feedback
```

Evidence type matters because tool-use calibration studies show that evidence tools and verification tools affect confidence differently.

### 4.9 Settlement loss

For agent `i`, settlement loss is:

```math
L_i = \sum_{j ∈ J^*(d)} w_j^{(u,t)} \ell_{ij}
```

where:

```math
\ell_{ij} = 1 - v_{ij}
```

and:

```math
v_{ij} = \frac{s_{ij}-1}{4}, \quad s_{ij} ∈ {1,2,3,4,5}
```

The decomposition is:

```math
L_i = L_i^{cat} + L_i^{X}
```

with:

```math
L_i^{cat} = \sum_{j ∈ J^*(d) \setminus J_X} w_j^{(u,t)} \ell_{ij}
```

```math
L_i^{X} = \sum_{j ∈ J_X} w_j^{(u,t)} \ell_{ij}
```

The RX dimensions replace ad hoc symbolic loss terms:

```text
RX.1 → uncertainty-disclosure loss
RX.2 → overclaim loss
RX.3 → scope-adherence loss
RX.4 → downstream-harm loss
RX.5 → provenance / attribution / traceability loss
```

### 4.10 Overclaim coupling

Overclaim is penalized when claimed responsibility exceeds demonstrated fulfillment:

```math
\ell_{i,RX.2} \propto
\sum_{j ∈ J^*(d) \setminus J_X}
\mathbb{1}[q_{ij} > v_{ij} + δ_{oc}]
```

where `δ_oc` is a tolerance, default `0.2`.

### 4.11 Reputation update

Use additive EMA:

```math
ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t} + λv_{ij}
```

with neutral initialization:

```math
ρ_{i,y,j,0} = 0.5
```

This replaces the multiplicative update because multiplicative decay cannot recover after penalty.

Optional overclaim-sensitive variant:

```math
ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t}
+ λ(v_{ij} - μ_{oc} \mathbb{1}[q_{ij} > v_{ij}+δ_{oc}])
```

with clipping to `[0,1]`.

---

## 5. Reconstructed Experiment Plan

The experiments should be redesigned around one main hypothesis and four support hypotheses.

### 5.1 Main hypothesis

> Ambiguous natural-language delegations induce measurable pre-execution responsibility projection divergence, and responsibility-bearing delegation reduces mismatch, rework, overclaiming, and repeated misassignment compared with routing-only, clarification-only, and post-hoc selection baselines.

### 5.2 Dataset: AmbiguousDelegation-300

Minimum dataset:

```text
5 categories × 12 delegation types × 5 hidden-intent variants = 300 examples
```

Categories:

```text
R1 paper draft / research writing
R2 code review / bug-fix
R3 result interpretation
R4 proposal improvement
R5 technical summarization
```

Each example contains:

```json
{
  "delegation_id": "ad_writing_001",
  "category": "R1",
  "delegation": "Improve this paper draft.",
  "artifact": "<short artifact>",
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
  }
}
```

Hidden intent should be annotated by three annotators and represented in the same 38-dimensional space.

### 5.3 Pilot first

Before the full 300-example experiment, run a 50-example pilot.

Pilot checks:

```text
1. Krippendorff's α for hidden-intent labels per dimension.
2. Distribution of active-set size |J*(d)|.
3. Malformed JSON rate under structured output.
4. LLM-judge agreement on rubric scoring.
5. Whether cross-family projection divergence exceeds within-model stochastic divergence.
6. Cost per example.
```

Gating criterion:

```text
If key dimensions have α < 0.4 or projection output is unstable,
revise taxonomy/prompt before main experiment.
```

### 5.4 Experiment 1 — Projection mismatch measurement

Objective:

> Show that the same delegation produces different responsibility projections across model families and that these projections differ from hidden-intent profiles.

Procedure:

```text
For each delegation d:
    provide d + artifact + closed taxonomy
    ask each model to output a 38-dim responsibility vector
    do not allow execution
```

Metrics:

```text
- cosine distance between projected vector and hidden intent
- Jaccard distance over active sets
- under-projection rate
- over-projection rate
- cross-family projection distance
- within-model projection distance
```

Key addition from v0.5.2:

```text
B0: Within-model stochastic baseline
    fixed model M, N=5 projection runs at temperature 0.5
    compare d_C(d) / d_W(d)
```

Main statistic:

```math
R(d) = d_C(d) / d_W(d)
```

Claim requires:

```text
median R(d) > 1, ideally ≥ 1.5,
with stable direction across R1–R5.
```

### 5.5 Experiment 2 — Clarification vs direct execution

Objective:

> Test whether responsibility-aware clarification reduces downstream mismatch and rework.

Conditions:

```text
A. Direct execution
B. Scalar routing only
C. Task-aware routing baseline
D. Ambiguity-only clarification baseline
E. Underspecification clarification baseline
F. Generate-then-select baseline
G. Proposed responsibility-bearing delegation
H. Oracle upper bound
```

Important baselines:

```text
Task-aware routing baseline:
    uses task type / capability profile style signals but no responsibility vector.

Ambiguity-only clarification baseline:
    asks clarification when query ambiguity is detected but does not project responsibility dimensions.

Underspecification baseline:
    asks clarification for missing Goal/Constraint/Input/Context information.

Generate-then-select baseline:
    multiple agents execute immediately; judge selects the best output.
```

Metrics:

```text
- final responsibility alignment
- user correction turns
- rework cost
- clarification count
- clarification efficiency: Δalignment per question
- settlement loss
- overclaim rate
- downstream harm score
```

Expected result:

```text
Responsibility-bearing delegation should ask fewer but more targeted clarifications
than generic ambiguity clarification, and should reduce costly wrong execution
relative to direct execution or routing-only baselines.
```

### 5.6 Experiment 3 — Settlement-based reputation update

Objective:

> Test whether responsibility-conditioned reputation improves future agent assignment compared with scalar reputation.

Simulation:

```text
Round 1..T:
    sample delegation d_t
    select agent under policy
    execute / evaluate
    compute settlement loss
    update reputation
```

Policies:

```text
- scalar global reputation
- task-category reputation
- responsibility-conditioned reputation
- responsibility + role-conditioned reputation
- oracle assignment
```

Metrics:

```text
- cumulative settlement loss
- assignment accuracy
- repeated misassignment rate
- overclaim recurrence
- recovery after prior failure
```

Expected result:

```text
Responsibility-conditioned reputation should avoid penalizing or rewarding an agent globally
for dimension-specific performance.
```

### 5.7 Experiment 4 — Evidence reliability and calibration

This is optional but valuable if scope allows.

Objective:

> Test whether settlement evidence type affects overclaiming and uncertainty disclosure.

Evidence conditions:

```text
- deterministic verification evidence
- noisy retrieval evidence
- LLM judge evidence
- human evidence subset
```

Metrics:

```text
- calibration error between claimed confidence and fulfillment
- uncertainty-disclosure score RX.1
- provenance score RX.5
- overclaim score RX.2
```

This experiment directly connects to tool-use calibration literature.

---

## 6. Revised Related Work Structure

The Related Work section should not be a list. It should be organized by **what object each prior work measures**.

### 6.1 Task-conditioned capability and routing

Covers:

```text
- task-aware delegation cues
- model routing
- capability profiles
- preference-derived routing
```

Our distinction:

```text
They measure task-conditioned model reliability;
we measure responsibility-conditioned pre-execution commitment.
```

### 6.2 Ambiguity identification and clarification

Covers:

```text
- CLAMBER
- ClariQ / AmbigQA style clarification work
- LHAW underspecification
```

Our distinction:

```text
They identify ambiguous or underspecified information;
we identify responsibility projection mismatch in delegated work.
```

### 6.3 Metacognition, uncertainty, and calibration

Covers:

```text
- uncertainty communication
- confidence calibration
- tool-use calibration
```

Our distinction:

```text
They calibrate confidence in answer correctness or tool-use success;
we require uncertainty disclosure about responsibility scope and evidence sufficiency.
```

### 6.4 Behavioral variance and reproducibility

Covers:

```text
- same prompt different outcomes
- consistency amplifies
- within-model and cross-model variance
```

Our distinction:

```text
They measure variance in execution trajectories or final outputs;
we measure variance in pre-execution responsibility projections.
```

### 6.5 Multi-agent failure diagnosis

Covers:

```text
- MAST
- agent failure taxonomies
- LLM-as-judge trace labeling
```

Our distinction:

```text
They diagnose what went wrong after execution;
we govern what responsibility was projected, claimed, and clarified before execution.
```

### 6.6 Multi-agent selection and aggregation

Covers:

```text
- Mixture-of-Agents
- Self-MoA
- judge-based selection
- selection bottleneck
```

Our distinction:

```text
They ask how to aggregate candidate outputs;
we ask whether agents should execute before responsibility commitment is clarified.
```

---

## 7. Reviewer Risk Reframing

### Risk A — “This is just task-aware routing.”

Response:

```text
Routing selects a model for a presumed task type.
Responsibility-bearing delegation first asks what responsibility the task implies.
```

### Risk B — “This is just ambiguity clarification.”

Response:

```text
Ambiguity clarification asks what the user means.
Responsibility-bearing delegation asks what responsibility an agent is willing to bear,
what uncertainty it has about that responsibility, and how fulfillment is settled.
```

### Risk C — “LHAW already handles underspecification.”

Response:

```text
LHAW removes Goal/Constraint/Input/Context information and validates terminal divergence.
Our protocol handles responsibility mismatch even when the required artifact and inputs are present.
```

### Risk D — “Mehta already showed interpretation matters.”

Response:

```text
Mehta diagnoses interpretation failures from execution trajectories.
We represent the interpretation commitment directly as a pre-execution responsibility vector.
```

### Risk E — “Cui & Alexander already showed output variance.”

Response:

```text
They show final data-analysis outcomes diverge.
We measure an upstream cause: divergent responsibility projections before execution.
```

### Risk F — “MAST already gives a MAS failure taxonomy.”

Response:

```text
MAST labels completed traces.
Our protocol can use MAST-like labels as settlement evidence, but the core mechanism is pre-execution projection and clarification.
```

### Risk G — “Selection bottleneck already explains multi-agent gains.”

Response:

```text
Selection bottleneck explains how to choose among generated outputs.
Our protocol reduces the chance that all generated outputs solve the wrong responsibility.
```

### Risk H — “The taxonomy is arbitrary.”

Response:

```text
The taxonomy is operational, not universal.
The paper tests whether a closed responsibility space improves measurement and settlement
relative to open-vocabulary projection and scalar scoring.
```

---

## 8. Recommended Paper Outline v1.0

### Abstract

Should include:

```text
- problem: ambiguous natural-language delegation in multi-agent LLM workflows
- failure mode: projection mismatch
- method: responsibility projection, bids, clarification, settlement, reputation
- experiments: projection mismatch, clarification value, reputation update, baseline comparisons
- distinction: pre-execution responsibility commitment, not routing or post-hoc failure taxonomy
```

### 1. Introduction

Core flow:

```text
1. LLM agents increasingly perform delegated work.
2. Existing orchestration frames: routing, selection, benchmarking, clarification, failure diagnosis.
3. But real delegation is ambiguous at the responsibility level.
4. Projection mismatch explains why competent agents can fail by solving the wrong problem.
5. Recent literature supports the broader diagnosis: ambiguity, underspecification,
   calibration, variance, and failure taxonomies all point to upstream interpretation problems.
6. Our contribution: pre-execution responsibility projection + settlement protocol.
```

### 2. Related Work

Use the object-of-measurement structure in Section 6.

### 3. Problem Formulation

Define:

```text
- incomplete delegation
- responsibility projection
- projection mismatch
- closed responsibility space J
- hidden intended profile r*
```

### 4. Responsibility-Bearing Delegation Protocol

Include:

```text
- projection π
- bid b_i
- clarification trigger C(d)
- selection utility U_i
- evidence collection
- settlement loss L_i
- reputation update ρ
```

### 5. Experimental Design

Include:

```text
- AmbiguousDelegation-300
- projection collection
- hidden-intent annotation
- baselines
- metrics
- pilot criteria
```

### 6. Results

Planned tables:

```text
Table 1: Taxonomy overview
Table 2: Projection mismatch by category and model family
Table 3: Cross-family vs within-model projection divergence
Table 4: Clarification vs direct execution / baselines
Table 5: Settlement and reputation update results
Table 6: Ablation results
```

Planned figures:

```text
Figure 1: Responsibility-bearing delegation protocol
Figure 2: Difference from prior work by temporal stage
Figure 3: Projection vectors for same delegation across model families
Figure 4: Clarification value vs cost
Figure 5: Reputation update trajectories by responsibility dimension
```

### 7. Discussion

Include:

```text
- why responsibility projection is not intent recovery
- when clarification is useful vs costly
- role of evidence reliability
- how MAST-like post-hoc labels can support settlement
- how task-aware routing can be combined with responsibility-aware delegation
```

### 8. Limitations

Must state:

```text
- taxonomy is operational and non-universal
- hidden intent is approximated by annotation or clarification
- experiments are controlled, not full deployment
- LLM judges require agreement checks
- user-specific weights are not fully learned in the first paper
- responsibility settlement is not legal accountability
```

### 9. Conclusion

Final message:

```text
The paper moves orchestration from selecting agents to governing responsibility.
```

---

## 9. What to Keep, Change, and Drop

### Keep

```text
- incomplete delegation
- responsibility projection
- projection mismatch
- responsibility-bearing bid
- clarification trigger
- settlement loss
- RX cross-cutting dimensions
- additive EMA reputation update
- AmbiguousDelegation-300
- B0 within-model stochastic baseline
```

### Change

```text
- Do not over-emphasize electricity-market analogy.
- Treat task-aware delegation cues as the closest prior, not as a minor citation.
- Add evidence reliability classification.
- Add generate-then-select and task-aware-routing baselines.
- Make contribution explicitly pre-execution and responsibility-vector based.
```

### Drop or move to appendix

```text
- broad philosophical claims about accountability
- claims of universal intent recovery
- excessive electricity market isomorphism
- open-vocabulary responsibility labels
- multiplicative reputation update
- too many speculative future mechanisms
```

---

## 10. Minimal Next Work Order

```text
Step 1: Write paper_draft_v1.0.md using this document as the master.
Step 2: Write spec_pi_implementation_v1.0.md.
Step 3: Write spec_evaluation_rubric_v1.0.md.
Step 4: Build 50-example pilot dataset.
Step 5: Run projection-only pilot.
Step 6: Check annotation agreement and R(d)=d_C/d_W.
Step 7: Revise taxonomy or prompts if needed.
Step 8: Run full AmbiguousDelegation-300 experiments.
Step 9: Insert results and move to LaTeX.
```

---

## 11. One-Paragraph Paper Identity

This paper introduces **responsibility-bearing delegation**, a protocol for governing multi-agent LLM orchestration under natural-language ambiguity. Rather than treating orchestration as only routing, output selection, clarification, or post-hoc failure diagnosis, the protocol represents the agent's first commitment: how an ambiguous delegation is projected into responsibility dimensions before execution. Agents then bid on responsibility coverage, request clarification when projection uncertainty is high, execute under an explicit scope, and are settled ex post against the same responsibility dimensions. The resulting settlement signal updates role- and responsibility-conditioned reputation. The framework is evaluated through controlled experiments measuring projection mismatch, clarification value, and repeated delegation improvement across five task categories using a closed 38-dimensional responsibility taxonomy.

---

## 12. Short Continuation Prompt

```text
We are preparing a paper titled "Responsibility-Bearing Delegation: A Settlement Protocol for Multi-Agent LLM Orchestration under Natural-Language Ambiguity." The current master document is `full_paper_reconstruction_v1.0.md`. The central claim is that multi-agent orchestration is an incomplete delegation problem: ambiguous natural-language requests must first be projected into responsibility dimensions before execution. The method uses a closed 38-dimensional responsibility taxonomy, responsibility-bearing bids, clarification triggers, settlement loss over active dimensions, and additive EMA reputation updates. The paper must distinguish itself from task-aware delegation cues, CLAMBER, LHAW, uncertainty/metacognition work, tool-use calibration, behavioral variance studies, MAST failure taxonomy, and selection-bottleneck work. The next task is to draft `paper_draft_v1.0.md` with a full abstract, introduction, related work, method, and experiment design based on this reconstruction.
```
