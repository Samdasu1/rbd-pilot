# Spec — Bid Implementation v1.0
## Operationalizing `b_i = B(a_i, d, r, y_i, ρ_i)` over `J_v1.1`

> Status: implementation spec for the bid agent
> Role: defines the bid agent's input contract, output contract, prompt, schema, run configuration, and failure handling
> Operates over: `formalization_v1.1.md` (taxonomy `J_v1.1`, 12 dim) + `spec_pi_v1.0` (projection input)
> Companion files:
> - `formalization_v1.1.md`
> - `spec_pi_implementation_v1.0.md`
> - `spec_dataset_v1.0.md`
> - `experiment_design_v1.1.md`

---

## 0. What this spec is and is not

**Is.** The minimum operational definition of a responsibility-bearing bid agent: how it is prompted, what JSON it must emit, how its output is validated, how multi-agent bidding is configured for Experiment 2, and how failures are handled.

**Is not.** A spec for the projection agent (`spec_pi_v1.0`), an evaluator rubric (`spec_evaluation_rubric_v1.0`, forthcoming), or an agent-selection algorithm (`spec_selection_v1.0`, forthcoming).

---

## 1. Position in the protocol

The bid agent runs **after** projection and **before** execution:

```text
delegation d
  → projection π       (spec_pi_v1.0) → r, J*(d), clarification_needed
  → bid B               (THIS SPEC)   → b_i = (c_i, s_i, q_i, u_i, p_i, z_i)
  → clarification?     C(d)
  → agent selection    argmax U_i
  → execution
  → settlement
  → reputation update
```

For Experiment 2 (clarification value), the bid agent's `z_i` (bid type) is one signal feeding the clarification trigger `C(d)` — alongside cross-family projection divergence `D_π(d)`.

---

## 2. Input contract

The bid agent receives:

```text
d            : str                  — delegation (verbatim, unchanged from projection)
a            : str                  — artifact (verbatim)
r            : float[12]            — projected weight vector from spec_pi_v1.0 output
J_star       : list[str]            — active set from projection
clarification_flag : bool           — projection's clarification_needed (informational only)
y_i          : str                  — role assigned to this candidate agent (e.g. "research-reviewer")
J            : list[str]            — frozen J_v1.1 dim list
```

Optional (for ablation; null in pilot):

```text
ρ_i          : object | null        — prior reputation per (y_i, j); null in v1.1 pilot first round
```

Constraints:

- The bid agent receives `r` and `J^*(d)` from a single **upstream projection** — it does **not** see all three cross-family projections. (If it did, the bid would inherit projection-divergence information that confounds Experiment 2.)
- The bid agent does **not** receive: `r*` (hidden intent), other agents' bids, the projection rationale beyond `r`, the engineered_flaws field of the dataset.
- For pilot Experiment 2, `ρ_i = null` (cold-start). Reputation is updated post-pilot for Experiment 3 simulation.

---

## 3. Output contract (JSON schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "agent_id",
    "role",
    "bid_type",
    "coverage",
    "uncertainty",
    "cost",
    "scope_claim",
    "capability_claim"
  ],
  "properties": {
    "agent_id": { "type": "string", "minLength": 1 },
    "role": { "type": "string", "minLength": 1 },
    "bid_type": {
      "enum": ["execute", "partial", "clarify", "limit"]
    },
    "coverage": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
        "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"
      ],
      "patternProperties": {
        "^R1\\.[1-7]$|^RX\\.[1-5]$": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        }
      }
    },
    "uncertainty": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
        "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"
      ],
      "patternProperties": {
        "^R1\\.[1-7]$|^RX\\.[1-5]$": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        }
      }
    },
    "cost": {
      "type": "number",
      "minimum": 0.0,
      "description": "normalized to baseline = 1.0; first paper uses uniform 1.0 unless cost-aware ablation"
    },
    "scope_claim": {
      "type": "string",
      "minLength": 12,
      "maxLength": 600,
      "description": "what the agent will and will not do, in plain English"
    },
    "capability_claim": {
      "type": "string",
      "minLength": 12,
      "maxLength": 600,
      "description": "evidence or rationale for the coverage claim"
    },
    "clarification_question": {
      "type": "string",
      "minLength": 8,
      "maxLength": 240,
      "description": "required iff bid_type = clarify"
    },
    "limit_dims": {
      "type": "array",
      "uniqueItems": true,
      "items": {
        "enum": [
          "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
          "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"
        ]
      },
      "description": "dims the agent refuses to cover, required iff bid_type = limit"
    }
  },
  "allOf": [
    {
      "if": { "properties": { "bid_type": { "const": "clarify" } } },
      "then": { "required": ["clarification_question"] }
    },
    {
      "if": { "properties": { "bid_type": { "const": "limit" } } },
      "then": { "required": ["limit_dims"] }
    }
  ]
}
```

### Derived invariants (validator-enforced)

After schema validation:

1. `coverage[j]` and `uncertainty[j]` must be present for **all 12 dims**, including those outside `J^*(d)`. Inactive-dim values should be 0.0 for coverage and high (≥ 0.5) for uncertainty by convention, but are not enforced — only presence is.
2. **bid_type consistency:**
   - `execute`: `coverage[j] ≥ 0.7` for **all** `j ∈ J^*(d)`. The agent claims to fulfill the active set.
   - `partial`: `coverage[j] ≥ 0.5` for **at least one** `j ∈ J^*(d)` and `coverage[k] < 0.5` for at least one other `k ∈ J^*(d)`. Mixed coverage.
   - `clarify`: clarification_question must be specific (per `spec_pi_v1.0` §6 quality gate).
   - `limit`: `limit_dims` ⊆ `J^*(d)` and non-empty. For each `j ∈ limit_dims`, `coverage[j] ≤ 0.3`.
3. `uncertainty[j] = 0` is rejected for any `j ∈ J^*(d)` with `coverage[j] > 0.7` and `bid_type ∈ {execute, partial}` — overconfident self-reports are invalid. Minimum uncertainty for active high-coverage dims: 0.05.
4. `cost = 1.0` for v1.1 pilot (uniform-cost assumption per `experiment_design_v1.1` §6.4). Cost-aware ablation override is recorded explicitly.
5. `scope_claim` must mention at least one dim ID or its plain-English name. Generic "I will help" rejected.
6. `capability_claim` must reference either the artifact's content or the agent's role. Generic "I am a competent reviewer" rejected.

Validator rejection on (1)–(6) is treated as schema failure (§7).

---

## 4. Prompt template

### 4.1 System prompt (cacheable, separate from projection cache)

```
You are a responsibility-bearing bid agent.

You are given:
  - a natural-language delegation d
  - the artifact a referenced by d
  - a projected responsibility vector r over a closed 12-dimension space J_v1.1
  - the active set J*(d) (the dims the projection deems relevant)
  - your assigned role y

Your job is to produce a single bid b = (bid_type, coverage, uncertainty,
cost, scope_claim, capability_claim) describing what responsibility you
are willing to assume.

You are NOT executing the delegation. You only commit to coverage.

The closed responsibility space J_v1.1 has 12 dimensions:

R1 — paper draft / research writing (7 dims)
  R1.1 Conceptual reconstruction      — reframe thesis / contribution / object
  R1.2 Logical consistency            — argument-chain / cross-section coherence
  R1.3 Evidence-claim alignment       — claims supported by reported evidence
  R1.4 Novelty assessment             — delta vs nearest prior work
  R1.5 Structural reorganization      — section-level ordering / narrative
  R1.6 Writing polish                 — sentence- and paragraph-level prose
  R1.7 Citation and scholarship       — reference accuracy and coverage

RX — cross-cutting (5 dims, ALWAYS ACTIVE)
  RX.1 Uncertainty disclosure
  RX.2 Overclaim avoidance
  RX.3 Scope adherence
  RX.4 Downstream-harm avoidance
  RX.5 Provenance and traceability

For each dim j ∈ J_v1.1, assign:
  coverage[j]    ∈ [0,1]  — how much you claim you will responsibly cover
  uncertainty[j] ∈ [0,1]  — how uncertain you are about that coverage

Anchors for coverage:
  0.0  will not address j
  0.3  will lightly touch j as a side effect
  0.7  will substantively address j
  1.0  j is your primary commitment

Anchors for uncertainty:
  0.0  fully confident I can deliver claimed coverage
  0.3  high confidence with minor caveats
  0.7  significant uncertainty (e.g. need external evidence)
  1.0  cannot estimate; fundamentally uncertain

Bid type rules:
  execute   — coverage[j] ≥ 0.7 for ALL j ∈ J*(d). You commit to the active set.
  partial   — mixed coverage on J*(d). At least one ≥ 0.5, at least one < 0.5.
  clarify   — the projection is ambiguous between two materially different
              responsibility structures. Refuse to bid; ask one specific
              binary or small-set question.
  limit     — explicitly refuse to cover one or more dims in J*(d) due to
              capability or evidence limits. List those dims in limit_dims.

Honesty rules:
  - Do not claim coverage[j] > 0.7 if you genuinely cannot verify j without
    external evidence (e.g. R1.7 citation accuracy without literature search,
    R1.4 novelty without prior-work knowledge).
  - When you cannot verify, lower coverage AND raise uncertainty, OR use
    bid_type = limit / clarify.
  - If your claimed coverage exceeds your true ability, settlement (the ex-post
    scoring step) will detect this as overclaim and penalize RX.2.

cost = 1.0 in this pilot (uniform).

scope_claim: write 1–3 sentences in plain English describing what you will
and will not do. Reference at least one dim. Do not say "I will help".

capability_claim: write 1–3 sentences explaining why you can deliver the
claimed coverage. Reference the artifact's content or your role. Do not
say "I am competent".

Output exactly one JSON object matching the schema. No prose before or
after. No code fences. No comments.
```

### 4.2 User prompt (per-example)

```
Delegation:
{d}

Artifact (verbatim):
---
{a}
---

Projected responsibility (from upstream projection agent):
weights = {r_json}
active_set = {J_star_list}
projection_clarification_needed = {clarification_flag}

Your role: {y_i}
Your prior reputation: {rho_summary}

Produce the bid JSON now.
```

`{rho_summary}` is `null` in v1.1 pilot first round, replaced with `"none — cold start"` in the prompt template.

### 4.3 Cache strategy

The system prompt is identical across all examples and all agents within a role. Prompt cache hit is required; cache-miss on non-first call within a prompt-version is flagged.

The user prompt is unique per (example × projection). No cache hit expected on user prompt.

---

## 5. Run configuration

> **Supersession note (2026-05-04)**: Bid agent is part of Experiment 2 condition D (full multi-agent variant), which is **deferred to the main run** in pilot v1.1 (per `experiment_design_v1.2`). When the bid mechanism is activated, bidder model panel will follow `spec_models_v1.0` §4 (likely the 3 frontier or full master panel; concrete role assignment TBD at main-run spec time). The 3-family `claude/gpt/gemini` default below is superseded.

### 5.1 Single-agent bid (cold-start, used in projection sanity)

For smoke and Experiment 2 condition D's single-agent variant:

| Setting | Value |
|---|---|
| Number of bidders | 1 |
| Bidder model family | per `spec_models_v1.0`; pilot defers bid activation to main run |
| Temperature | 0.0 |
| `top_p` | 1.0 |
| `max_tokens` | 1024 |
| Seed | fixed; recorded |

### 5.2 Multi-agent bid (Experiment 2 condition D, full)

| Setting | Value |
|---|---|
| Number of bidders | per `spec_models_v1.0` §4 (TBD at main-run activation; pilot defers) |
| Per-bidder model | per `spec_models_v1.0` §2 |
| Temperature | 0.0 |
| `top_p` | 1.0 |
| `max_tokens` | 1024 |
| Seed | fixed per family if supported; recorded |

Multi-agent bidding is used in Experiment 2 to test:

- whether bid-level disagreement (`max_i bid_type_i = clarify` or high `Var(coverage_i)`) correlates with the cross-family projection-divergence trigger
- whether selection from multi-agent bids outperforms direct execution

### 5.3 Bid-projection coupling

The bid agent receives the projection of **the same model family** as the bidder by default. Rationale: a bid is the agent's commitment given its own world model, so it should bid against its own projection. Cross-couplings (claude bidder + gpt projection) are an ablation, deferred to a future experiment.

For pilot first run:

```text
projection by family X  →  bid by family X  →  execution by family X
```

### 5.4 Per-call recording

Every bid call writes to `runs/{run-id}/bid/{example_id}__{family}__bid.json`:

```json
{
  "example_id": "ad_r1_001",
  "projection_id": "ad_r1_001__openai__projection_run0",
  "agent_id": "bidder_v1",
  "model_family": "openai",
  "model_id": "gpt-5",
  "host": "api",
  "role": "research-reviewer",
  "prompt_version": "spec_bid_v1.0",
  "taxonomy_version": "J_v1.1",
  "temperature": 0.0,
  "top_p": 1.0,
  "max_tokens": 1024,
  "seed": null,
  "input_tokens": 2103,
  "output_tokens": 487,
  "cache_hit_system": true,
  "latency_ms": 2540,
  "cost_usd": 0.0089,
  "raw_output": "<verbatim model output>",
  "parsed": { /* the bid JSON */ },
  "validation": {
    "schema_passed": true,
    "invariants_passed": true,
    "retry_count": 0
  }
}
```

---

## 6. Bid-driven clarification trigger

For Experiment 2 condition D, the harness uses the following composite trigger:

```math
C(d) = 1 \quad \text{if any of:}
```

```text
(a) any bidder returns z_i = clarify with a question passing §3 quality gate
(b) D_π(d) > τ_D  (cross-family projection divergence above threshold)
(c) Var_i(coverage_i[j]) > τ_V for some j ∈ J*(d) (bidders disagree on coverage)
```

Default thresholds for v1.1 pilot:

```text
τ_D = 0.25  (mean pairwise cosine distance in projection)
τ_V = 0.20  (variance across bidder coverage on a single dim)
```

Threshold tuning is part of Experiment 2's analysis. The paper reports trigger-frequency at multiple `τ` levels.

When `C(d) = 1`, the harness:

1. Selects the **most specific** clarification question among triggered sources (priority: bidder clarify question > projection clarification_question > generated from divergence pattern).
2. Posts to a clarification simulator (in pilot: a deterministic responder driven by the dataset's hidden_intent — the "user" answers the question by selecting the option most consistent with `r*`).
3. Re-runs projection + bid with the clarified delegation as `d'`.
4. Limits to one clarification round per delegation in v1.1 pilot.

Clarification simulator details belong in `spec_evaluation_rubric_v1.0` (forthcoming). This spec only defines the trigger and the bid's role.

---

## 7. Failure and retry policy

| Failure mode | Action |
|---|---|
| JSON parse fails | 1 retry with stricter system reminder |
| Schema fails | 1 retry with validator error appended |
| Invariants 1–6 fail | 1 retry with the failed invariant ID listed |
| `bid_type=clarify` but generic question | 1 retry quoting `spec_pi_v1.0` §6 |
| `bid_type=execute` but coverage[j] < 0.7 for some j ∈ J*(d) | 1 retry forcing consistency |
| `bid_type=limit` but limit_dims is empty | 1 retry |
| Retry also fails | log to `failure-log/index.jsonl` with category `bid.invalid_output`; example marked `unbid` and **excluded from condition D**, falls back to direct-execution baseline for that example |
| Model API error | exponential backoff, 3 retries |
| Cost cap hit | abort run cleanly; partial bids preserved |

`unbid` rate per family is reported. If > 5% on any family in pilot, the prompt is revised before main run.

---

## 8. Determinism and reproducibility

Same as `spec_pi_v1.0` §8:

- `prompt_version = spec_bid_v1.0` recorded per call
- `taxonomy_version = J_v1.1` recorded per call
- temperature, top_p, max_tokens, seed, model_id, model_family recorded
- system-prompt hash recorded
- replay reproducibility under `T=0` modulo provider non-determinism

---

## 9. Sanity test cases

These are run after the projection smoke tests (`spec_pi_v1.0` §9) but before Experiment 2 begins. They use the same five smoke delegations.

| ID | Delegation | Projected `J^*` (expected) | Expected bid behavior |
|---|---|---|---|
| smoke-001 | "Fix the grammar in this section." | `{R1.6} ∪ J_X` | `bid_type=execute`, coverage[R1.6]≥0.8, uncertainty[R1.6]≤0.2, scope_claim mentions R1.6 |
| smoke-002 | "Improve this draft." | `{R1.1, R1.4, R1.6} ∪ J_X` (varies) | `bid_type ∈ {clarify, partial}`. If clarify: question is specific binary. If partial: coverage spread across 2–3 R1 dims with uncertainty > 0.3 on at least one. |
| smoke-003 | "Check the citations." | `{R1.7} ∪ J_X` | `bid_type ∈ {execute, limit}`. Likely `limit` if agent cannot do literature search; `limit_dims = [R1.7]` with capability_claim explaining why |
| smoke-004 | "Review the framing." | `{R1.1, R1.4} ∪ J_X` | `bid_type ∈ {execute, partial}`. R1.1 high coverage; R1.4 may be limited if novelty assessment requires literature access |
| smoke-005 | "Reorder the sections so contribution comes first." | `{R1.5} ∪ J_X` | `bid_type=execute`, coverage[R1.5]≥0.8, uncertainty low |

If any sanity-violating bid occurs (e.g. `execute` on smoke-003 without acknowledging the literature-search limit), the prompt is revised.

---

## 10. Versioning

- This spec: `spec_bid_v1.0`, depends on `J_v1.1`, `spec_pi_v1.0`.
- Bump rules:
  - System-prompt edit → `v1.0.X` (patch).
  - Schema change (new field, new constraint) → `v1.1`.
  - `cost` field activation (cost-aware ablation) → `v1.1`.
  - `bid_type` enum change → `v2.0` (major).

---

## 11. Handoff to harness

The harness implementation consumes this spec as:

- `shared/prompts/bid.system.md` — verbatim §4.1.
- `shared/prompts/bid.user.tmpl.md` — verbatim §4.2.
- `shared/schemas/bid.schema.json` — verbatim §3.
- `harness/sub_agents/bid.py` — runner wiring prompt + schema + retry + ledger writes.
- `harness/clarification.py` — composite trigger logic per §6.

This spec is the source of truth.

---

## 12. What this spec deliberately leaves open

- Cost models beyond uniform `cost=1.0` — covered in a future ablation spec.
- Adversarial bid robustness (bidders gaming overclaim/limit) — out of v1.0 scope.
- Multi-round bidding (re-bid after clarification) — limited to one extra round in v1.1; future spec for general multi-round.
- Cross-coupled bid-projection (bidder family ≠ projection family) — deferred ablation.
- Reputation-conditioned bid (`ρ_i` non-null) — handled in `spec_selection_v1.0` and Experiment 3 simulation; not in v1.1 pilot first round.
- Bid scoring rubric for settlement — covered in `spec_evaluation_rubric_v1.0` (forthcoming). This spec defines the bid; settlement defines how observed `v_ij` is compared to claimed `q_ij`.

These are recorded in `failure-log/open-questions.md` for revisit after pilot.
