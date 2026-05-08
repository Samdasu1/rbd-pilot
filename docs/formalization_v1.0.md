# Formalization v1.0
## Mathematical and Algorithmic Reconstruction for Responsibility-Bearing Delegation

> Status: reconstructed formalization  
> Role: method notation, equations, protocol, and implementation-facing definitions  
> Companion files:
> - `paper_master_reconstruction_v1.0.md`
> - `concept_and_positioning_v1.0.md`
> - `experiment_design_v1.0.md`
> - `reviewer_risk_and_writing_plan_v1.0.md`

---

## 0. Design constraints after prior-work review

The formalization must satisfy five constraints:

1. **Closed responsibility space**  
   Open-vocabulary responsibility projection is too unstable. All responsibility dimensions must belong to a fixed index set `J`.

2. **Pre-execution measurability**  
   The main object must be computed before execution, otherwise the paper collapses into post-hoc failure analysis.

3. **Clarification as cost-sensitive intervention**  
   Clarification is not always good. It must be triggered by expected reduction in mismatch or settlement loss.

4. **Settlement as evidence-weighted, dimension-level scoring**  
   Output quality alone is insufficient. Settlement must score each active responsibility dimension.

5. **Reputation must recover**  
   Multiplicative reputation decay is deprecated because it only decreases. Additive EMA is the default.

---

## 1. Notation

| Symbol | Meaning |
|---|---|
| `d` | natural-language delegation |
| `u` | user / delegator |
| `t` | task context or task category |
| `a` | artifact supplied with delegation |
| `A = {a_1, ..., a_n}` | candidate agent set |
| `y_i` | role assigned to agent `i` |
| `J` | closed responsibility dimension set, `|J| = 38` |
| `J_X` | cross-cutting responsibility dimensions RX.1–RX.5 |
| `J*(d)` | active responsibility set for delegation `d` |
| `π` | responsibility projection function |
| `r` | projected responsibility vector |
| `r*` | hidden or later-preferred responsibility vector |
| `b_i` | responsibility-bearing bid of agent `i` |
| `q_i` | claimed coverage vector |
| `u_i` | uncertainty vector |
| `z_i` | bid type |
| `p_i` | cost claim |
| `C(d)` | clarification trigger |
| `o_i` | output produced by agent `i` |
| `E_i` | evidence set for evaluating agent `i` |
| `s_ij` | rubric score on dimension `j`, integer 1–5 |
| `v_ij` | normalized fulfillment score on dimension `j` |
| `ℓ_ij` | loss on dimension `j` |
| `L_i` | total settlement loss |
| `ρ_{i,y,j,t}` | reputation of agent `i` in role `y` on dimension `j` and task context `t` |

---

## 2. Closed responsibility space

Let:

```text
J = J_R1 ∪ J_R2 ∪ J_R3 ∪ J_R4 ∪ J_R5 ∪ J_X
```

where:

```text
R1: paper draft / research writing
R2: code review / bug-fix
R3: result interpretation
R4: proposal improvement
R5: technical summarization
RX: cross-cutting dimensions
```

with:

```text
|J| = 38
|J_X| = 5
J_X = {RX.1, RX.2, RX.3, RX.4, RX.5}
```

The cross-cutting dimensions are:

```text
RX.1 Uncertainty disclosure
RX.2 Overclaim avoidance
RX.3 Scope adherence
RX.4 Downstream-harm avoidance
RX.5 Provenance and traceability
```

All vectors indexed by `j` use `j ∈ J`.

This avoids the open-vocabulary problem:

```text
No free-form "responsibility labels" are allowed in experiments.
Projection is multi-label classification + weight prediction over J.
```

---

## 3. Natural-language delegation

A user provides:

```math
d ∈ D
```

with context:

```math
(u, t, a)
```

where:

```text
u = user
t = task category or context
a = artifact to be acted on
```

The delegation is incomplete because it does not fully specify:

```text
- responsibility dimensions,
- priority weights,
- role boundaries,
- evidence requirements,
- acceptable uncertainty,
- downstream risk tolerance.
```

---

## 4. Responsibility projection

The projection function maps:

```math
π(d,u,t,a) → r ∈ [0,1]^{|J|}
```

where:

```math
r_j = projected importance of responsibility dimension j.
```

Default active set:

```math
J^*(d) = {j ∈ J : r_j > τ_r} ∪ J_X
```

with:

```text
τ_r = 0.3 default
```

Cross-cutting dimensions are always active because uncertainty, overclaim, scope, harm, and provenance apply to all delegated work.

---

## 5. Projection mismatch

Let:

```math
r^* ∈ [0,1]^{|J|}
```

be a hidden, annotated, clarified, or later-preferred responsibility vector.

Projection mismatch is:

```math
M(d,u,t) = Δ(r, r^*)
```

Recommended components:

```math
Δ(r,r^*) =
α_cos · (1 - cos(r,r^*))
+ α_jac · Jaccard(J^*(r), J^*(r^*))
+ α_under · UnderProjection(r,r^*)
+ α_over · OverProjection(r,r^*)
```

Where:

```math
UnderProjection =
Σ_j 1[r_j ≤ τ_r ∧ r^*_j > τ_high] / Σ_j 1[r^*_j > τ_high]
```

```math
OverProjection =
Σ_j 1[r_j > τ_r ∧ r^*_j ≤ τ_low] / Σ_j 1[r_j > τ_r]
```

Defaults:

```text
τ_high = 0.7
τ_low = 0.2
```

Important: `r*` is not assumed to be metaphysical true intent. It is an operational target for controlled evaluation.

---

## 6. Multiple candidate projections

For ambiguous delegations, several projections may be plausible:

```math
R(d) = {r^(1), ..., r^(M)}
```

Projection uncertainty can be measured by:

```math
H_π(d) = entropy over active-set distributions
```

or by disagreement among projection agents:

```math
D_π(d) = mean_{m<n} Δ(r^(m), r^(n))
```

This matters because clarification should be triggered by high uncertainty or high expected loss, not by ambiguity labels alone.

---

## 7. Responsibility-bearing bid

Each candidate agent submits:

```math
b_i = B(a_i, d, r, y_i, ρ_i)
```

with:

```math
b_i = (c_i, s_i, q_i, u_i, p_i, z_i)
```

| Component | Meaning |
|---|---|
| `c_i` | capability claim |
| `s_i` | scope claim |
| `q_i ∈ [0,1]^|J|` | claimed responsibility coverage |
| `u_i ∈ [0,1]^|J|` | uncertainty about fulfilling each responsibility |
| `p_i` | cost |
| `z_i` | bid type |

Bid types:

```text
execute  : claims ability to execute under projected responsibility
clarify  : claims responsibility structure is underdetermined
partial  : claims some dimensions but not all
limit    : refuses or limits scope due to missing evidence, unsafe assumptions, or insufficient capability
```

---

## 8. Coverage and uncertainty calibration

A key distinction:

```text
q_ij = what the agent claims it can responsibly cover
u_ij = how uncertain the agent is about that coverage
v_ij = what settlement later observes
```

Overclaim occurs when:

```math
q_{ij} > v_{ij} + δ_oc
```

where:

```text
δ_oc = 0.2 default
```

Uncertainty hiding occurs when:

```math
q_{ij} high, u_{ij} low, but v_{ij} low
```

A simple uncertainty-calibration loss can be defined as:

```math
ℓ^{cal}_{ij} = |(1-u_{ij}) - v_{ij}|
```

This can optionally contribute to RX.1.

For the first paper, keep this as an auxiliary metric unless it complicates the main settlement.

---

## 9. Clarification trigger

Clarification is a pre-execution intervention:

```math
C(d) ∈ {0,1}
```

Baseline rule:

```math
C(d)=1 if D_π(d) > τ_D
       or E[L_direct(d)] - E[L_clarified(d)] > Cost_clarify(d)
```

A more practical first-paper rule:

```math
C(d)=1 if:
    mean pairwise projection distance > τ_D
    OR max_j uncertainty over responsibility importance > τ_U
    OR any agent submits z_i = clarify with high rationale score
```

Clarification value:

```math
CV(d) = L_direct(d) - L_after_clarification(d)
```

Clarification efficiency:

```math
CE(d) = CV(d) / Cost_clarify(d)
```

This connects to long-horizon underspecification work where clarification has real interruption cost.

---

## 10. Agent selection

The system selects agent-role assignments:

```math
x_i ∈ {0,1}
```

A responsibility-adjusted utility can be:

```math
U_i =
Σ_{j ∈ J^*(d)} w_j^{(u,t)}
[
q_{ij} · ρ_{i,y,j,t}
- β_u u_{ij}
- β_oc OC_{ij}
]
- β_p p_i
```

where:

```text
w_j^{(u,t)} = user/task-conditioned weight
ρ_{i,y,j,t} = prior reputation
u_ij = uncertainty
p_i = cost
OC_ij = expected overclaim risk
```

Select:

```math
i^* = argmax_i U_i
```

But if `C(d)=1`, clarification occurs before final assignment.

---

## 11. Evidence model

After execution, each agent output `o_i` is evaluated with evidence set:

```math
E_i = {e_1, ..., e_m}
```

Evidence types:

```text
D = deterministic check
X = external harness / tool
H = human rating
J = LLM judge
R = retrieval/evidence-tool source
```

Each evidence item has reliability:

```math
κ(e) ∈ [0,1]
```

Recommended reliability hierarchy:

```text
deterministic/harness evidence > human rubric > multi-judge LLM rubric > retrieval-only evidence
```

For first implementation:

```text
- use deterministic/harness evidence when available;
- otherwise use 3 LLM judges;
- use human subset for validation;
- track provenance under RX.5.
```

---

## 12. Fulfillment score and loss

Evaluator score:

```math
s_{ij} ∈ {1,2,3,4,5}
```

Normalize:

```math
v_{ij} = (s_{ij} - 1)/4
```

Loss:

```math
ℓ_{ij} = 1 - v_{ij}
```

If multiple evidence sources exist:

```math
v_{ij} = Σ_{e ∈ E_{ij}} κ(e) v_{ij}^{(e)} / Σ_{e ∈ E_{ij}} κ(e)
```

For first paper, this can be simplified to median over judges or deterministic override.

---

## 13. Settlement loss

Total settlement loss:

```math
L_i = Σ_{j ∈ J^*(d)} w_j^{(u,t)} ℓ_{ij}
```

Decomposition:

```math
L_i = L_i^cat + L_i^X
```

where:

```math
L_i^cat = Σ_{j ∈ J^*(d) \ J_X} w_j^{(u,t)} ℓ_{ij}
```

```math
L_i^X = Σ_{j ∈ J_X} w_j^{(u,t)} ℓ_{ij}
```

Cross-cutting interpretation:

```text
RX.1 → uncertainty-disclosure loss
RX.2 → overclaim loss
RX.3 → scope-adherence loss
RX.4 → downstream-harm loss
RX.5 → provenance/traceability loss
```

Overclaim coupling:

```math
ℓ_{i,RX.2} =
min(1, γ_oc Σ_{j ∈ J^*(d)\J_X} 1[q_{ij} > v_{ij} + δ_oc])
```

Scope adherence:

```math
ℓ_{i,RX.3}
```

penalizes work outside claimed or clarified scope, especially if it damages required dimensions.

---

## 14. User-feedback weight calibration

User feedback:

```math
F ∈ [-1,1] or structured per dimension
```

Weight update:

```math
w_j^{(u,t)} ← normalize(w_j^{(u,t)} + η · g_j(F,d,o))
```

where `g_j` maps feedback to dimension weights.

Example:

```text
User says:
    "I did not ask for grammar polish; I wanted the conceptual issue fixed."

Update:
    increase R1.1 Conceptual reconstruction
    decrease R1.6 Writing polish
```

First paper should not overclaim this as solved. It can be shown in simulation.

---

## 15. Reputation update

Default additive EMA:

```math
ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t} + λv_{ij}
```

with:

```text
ρ ∈ [0,1]
λ = 0.2 default
ρ_{i,y,j,0} = 0.5
```

Properties:

```text
- can increase and decrease;
- converges to repeated fulfillment;
- stable under noise;
- avoids irreversible multiplicative decay.
```

Overclaim-sensitive variant:

```math
ρ_{i,y,j,t+1}
= clip_{[0,1]}((1-λ)ρ_{i,y,j,t} + λ(v_{ij} - μ_oc · 1[q_{ij} > v_{ij}+δ_oc]))
```

Use variant only in ablation or appendix.

---

## 16. Algorithm

```text
Algorithm: Responsibility-Bearing Delegation

Input:
    delegation d
    user u
    context t
    artifact a
    candidate agents A
    responsibility taxonomy J
    prior reputation ρ

1. Project responsibility:
       r = π(d,u,t,a)

2. Construct active responsibility set:
       J*(d) = {j : r_j > τ_r} ∪ J_X

3. Solicit bids:
       for each agent a_i:
           b_i = (c_i, s_i, q_i, u_i, p_i, z_i)

4. Estimate projection uncertainty:
       D_π(d), H_π(d), or bid-level clarification signals

5. Clarification decision:
       if C(d)=1:
           ask clarification question
           update d or r
           return to step 1 or 2

6. Select agent:
       compute U_i
       choose i* = argmax_i U_i

7. Execute:
       o_i* = execute(a_i*, d, r, scope)

8. Collect evidence:
       E_i* = harness / deterministic checks / LLM judges / human ratings

9. Settle:
       compute s_ij, v_ij, ℓ_ij, L_i

10. Update reputation:
       ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t} + λv_ij

11. Optionally update user weights:
       w_j^(u,t) using feedback F

Output:
       final answer, settlement record, updated reputation
```

---

## 17. Minimum equations for the main paper

The main paper should include only these equations:

```math
r = π(d,u,t,a), \quad r ∈ [0,1]^{|J|}
```

```math
J^*(d) = {j ∈ J : r_j > τ_r} ∪ J_X
```

```math
M(d,u,t) = Δ(r,r^*)
```

```math
b_i = (q_i,u_i,p_i,z_i)
```

```math
C(d)=1 \;\text{if}\; D_π(d) > τ_D \;\text{or}\; E[L_direct-L_clarified] > Cost_clarify
```

```math
L_i = Σ_{j ∈ J^*(d)} w_j^{(u,t)}ℓ_{ij}
```

```math
ρ_{i,y,j,t+1} = (1-λ)ρ_{i,y,j,t} + λv_{ij}
```

Everything else can go into appendix.

---

## 18. Implementation schemas

### Projection output

```json
{
  "weights": {
    "R1.1": 0.90,
    "R1.2": 0.75,
    "RX.1": 1.00
  },
  "active_set": ["R1.1", "R1.2", "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"],
  "category_focus": "R1",
  "rationale": {
    "R1.1": "The user asks to improve the draft at a conceptual level.",
    "R1.2": "The argument chain may require consistency checking."
  },
  "clarification_needed": true,
  "clarification_question": "Do you want surface editing or conceptual/reviewer-risk revision?"
}
```

### Bid output

```json
{
  "agent_id": "agent_research_reviewer",
  "bid_type": "partial",
  "coverage": {
    "R1.1": 0.9,
    "R1.2": 0.8,
    "R1.4": 0.6,
    "R1.6": 0.2
  },
  "uncertainty": {
    "R1.1": 0.2,
    "R1.4": 0.5
  },
  "scope_claim": "Can review conceptual framing and argument logic; cannot verify full novelty without literature search.",
  "cost": 1.0
}
```

### Settlement record

```json
{
  "delegation_id": "ad_writing_001",
  "agent_id": "agent_research_reviewer",
  "active_set": ["R1.1", "R1.2", "R1.4", "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"],
  "scores": {
    "R1.1": 4,
    "R1.2": 5,
    "R1.4": 3,
    "RX.1": 4,
    "RX.2": 5
  },
  "settlement_loss": 0.21,
  "overclaim_flags": ["R1.4"],
  "evidence_sources": ["human_rubric", "llm_judge_panel"]
}
```

---

## 19. What not to formalize in v1.0

Do not over-formalize:

```text
- full causal attribution graph
- complete game-theoretic bid equilibrium
- learned user intent model
- RL training objective
- legal accountability
- production deployment governance
```

Those will distract reviewers.

The first paper should keep the formalism operational and experimentally testable.
