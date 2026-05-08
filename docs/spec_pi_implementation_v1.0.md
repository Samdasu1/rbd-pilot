# Spec — Projection Implementation v1.0
## Operationalizing `π(d,u,t,a) → r` over `J_v1.1`

> Status: implementation spec for first pilot
> Role: defines the projection agent's input contract, output contract, prompt, schema, run configuration, and failure handling
> Operates over: `formalization_v1.1.md` (taxonomy `J_v1.1`, 12 dim)
> Companion files:
> - `formalization_v1.1.md`
> - `experiment_design_v1.0.md`
> - `paper_master_reconstruction_v1.0.md`

---

## 0. What this spec is and is not

**Is.** The minimum operational definition of a projection agent: how it is prompted, what JSON it must emit, how its output is validated, how cross-family and within-model runs are configured, and how failures are handled.

**Is not.** A bid implementation (covered later under `spec_bid_v1.0`), an evaluator rubric (covered under `spec_evaluation_rubric_v1.0`), or an agent-selection algorithm (covered under `spec_selection_v1.0`).

---

## 1. Input contract

The projection agent receives:

```text
d  : str              — natural-language delegation
u  : str | null       — user identifier or null in anonymous mode
t  : str | null       — task category hint or null (the projection should not depend on it)
a  : str              — the artifact text (paper draft, section, abstract, etc.)
J  : list[str]        — frozen list of 12 dimension IDs from J_v1.1
```

Constraints:

- `d` length: ≤ 200 words. Longer delegations are truncated and the truncation is logged.
- `a` length: ≤ 1500 words for v1.1. Pilot artifacts must respect this cap.
- `t` is **deliberately ignored** by the prompt. v1.1 is R1-only; the projection agent must not be told the category in advance, otherwise the projection-mismatch experiment is contaminated.
- `J` is passed in literally (not paraphrased) so prompt-template drift cannot silently change the taxonomy.

The agent does **not** receive:

- the hidden intent `r*`
- other agents' projections
- the user's name or persona
- prior reputation

These exclusions are load-bearing for the cross-family experiment.

---

## 2. Output contract (JSON schema)

The agent must emit a single JSON object matching this schema. No prose before or after.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "weights",
    "active_set",
    "category_focus",
    "clarification_needed",
    "rationale"
  ],
  "properties": {
    "weights": {
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
    "active_set": {
      "type": "array",
      "uniqueItems": true,
      "minItems": 5,
      "maxItems": 12,
      "items": {
        "enum": [
          "R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6", "R1.7",
          "RX.1", "RX.2", "RX.3", "RX.4", "RX.5"
        ]
      }
    },
    "category_focus": { "const": "R1" },
    "clarification_needed": { "type": "boolean" },
    "clarification_question": {
      "type": "string",
      "minLength": 8,
      "maxLength": 240
    },
    "rationale": {
      "type": "object",
      "additionalProperties": false,
      "patternProperties": {
        "^R1\\.[1-7]$|^RX\\.[1-5]$": {
          "type": "string",
          "minLength": 8,
          "maxLength": 400
        }
      }
    }
  },
  "allOf": [
    {
      "if": { "properties": { "clarification_needed": { "const": true } } },
      "then": { "required": ["clarification_question"] }
    }
  ]
}
```

### Derived invariants (validator-enforced)

These rules are checked *after* schema validation passes:

1. `active_set ⊇ {RX.1, RX.2, RX.3, RX.4, RX.5}` — the five RX dims are always active.
2. `active_set ⊇ {j ∈ R1 : weights[j] > 0.3}` — R1 active membership is exactly the threshold rule.
3. `active_set ⊆ {j ∈ R1 : weights[j] > 0.3} ∪ J_X` — no dim outside the threshold rule may be in `active_set`.
4. For every `j ∈ active_set`, `rationale[j]` must exist.
5. `rationale[j]` for inactive dimensions is permitted but not required.
6. `category_focus = "R1"` is fixed in v1.1.
7. If `clarification_needed = true`, the question must be specific (not "what do you want?" — see §6 anchors).

Validator rejection on any of (1)–(7) is treated identically to a schema failure (see §7).

---

## 3. Prompt template

### 3.1 System prompt (cacheable)

```
You are a responsibility-projection agent.

Your job is to read a natural-language delegation d and the artifact a it
refers to, and to project the delegation onto a closed responsibility space.

You must NOT execute the delegation. You must NOT rewrite, edit, summarize,
critique, or otherwise act on the artifact. You only produce a projection.

The closed responsibility space J_v1.1 has exactly 12 dimensions.

R1 — paper draft / research writing (7 dimensions)
  R1.1 Conceptual reconstruction
       Reframe the thesis, gap statement, or contribution claim. Above the
       sentence level. Excludes novelty evaluation against named prior works.
  R1.2 Logical consistency
       Verify the argument chain — premises, intermediates, conclusions.
       Excludes claim-evidence linkage and citation accuracy.
  R1.3 Evidence-claim alignment
       Are claims supported by the experiments / tables / figures as reported?
       Excludes whether the experiments are well-designed.
  R1.4 Novelty assessment
       Estimate delta vs the nearest prior work. Excludes scholarship audit.
  R1.5 Structural reorganization
       Section-level / subsection-level ordering and narrative arc.
       Excludes paragraph-internal flow.
  R1.6 Writing polish
       Sentence- and paragraph-level grammar, flow, register, conciseness.
       Excludes anything above the sentence level.
  R1.7 Citation and scholarship
       Reference accuracy, coverage of the relevant literature, attribution.
       Excludes contribution-vs-prior-work positioning.

RX — cross-cutting (5 dimensions, ALWAYS ACTIVE)
  RX.1 Uncertainty disclosure
  RX.2 Overclaim avoidance
  RX.3 Scope adherence
  RX.4 Downstream-harm avoidance
  RX.5 Provenance and traceability

For each dimension j ∈ J_v1.1, assign a weight r_j ∈ [0,1]:
  0.0  not requested; out of scope
  0.3  peripheral; nice-to-have
  0.7  central expected responsibility
  1.0  load-bearing; failure invalidates the delegation

Active set rule:
  active_set = {j ∈ R1 : r_j > 0.3} ∪ {RX.1, RX.2, RX.3, RX.4, RX.5}

Clarification rule:
  Set clarification_needed = true only when the delegation admits at least
  two materially different responsibility structures that the artifact alone
  cannot disambiguate. Do not ask for clarification merely because the
  request is short. The clarification_question must propose a concrete
  binary or small-set choice, not "what do you want?".

Output exactly one JSON object matching the schema. No prose before or
after. No code fences. No comments.
```

### 3.2 User prompt (per-example)

```
Delegation:
{d}

Artifact (verbatim):
---
{a}
---

Produce the projection JSON now.
```

### 3.3 Cache strategy

The system prompt is **identical across all examples and all runs**. Prompt cache hit on the system prompt is required. The ledger logs `cache_hit: true` for the system-prompt cache; first-call cache-miss is acceptable. If `cache_hit: false` on a non-first call within the same prompt-version, the run is flagged for investigation.

---

## 4. Run configuration

> **Supersession note (2026-05-04)**: Model identities (family list, per-family model id, host) for all roles are now canonical in `spec_models_v1.0.md`. The settings below are the *configuration shape* (T, top_p, max_tokens, runs); for actual model assignments see `spec_models_v1.0` §2 (master panel) and §4 (role assignments). The previously stated `claude / gpt / gemini` list with `claude-sonnet-4-6` example is superseded by the Anthropic-excluded 12-model panel.

### 4.1 Cross-family run (Experiment 1, formalization v1.0 §4)

| Setting | Value |
|---|---|
| Model families | per `spec_models_v1.0` §4.2 (3 frontier: gpt-5, gemini-2.5-pro, grok-4) |
| Per-family model | exact ids in `spec_models_v1.0` §2; recorded per call |
| Runs per (model, example) | 1 |
| Temperature | 0.0 |
| `top_p` | 1.0 (or family default) |
| `max_tokens` | 1024 (output cap) |
| Seed | fixed per run if family supports; recorded otherwise |

Rationale for `T=0`: cross-family divergence must not be confounded by within-model stochasticity. Any divergence observed at `T=0` is family-attributable.

### 4.2 Within-model stochastic baseline (Experiment 1B, formalization v1.0 §5)

| Setting | Value |
|---|---|
| Model | one fixed model per `spec_models_v1.0` §4.2 (gpt-5) |
| Runs per example | 5 |
| Temperature | 0.5 |
| `top_p` | 1.0 |
| `max_tokens` | 1024 |
| Seed | varied per run; recorded |

Rationale for `T=0.5`: this is the upper bound of stochastic variance under typical deployment. Any cross-family signal that exceeds this baseline survives the "you're just measuring noise" objection.

### 4.3 Per-call recording

Every projection call writes to `runs/{run-id}/projection/{example_id}__{family}__{run_idx}.json`:

```json
{
  "example_id": "ad_r1_001",
  "model_family": "openai",
  "model_id": "gpt-5",
  "host": "api",
  "prompt_version": "spec_pi_v1.0",
  "taxonomy_version": "J_v1.1",
  "temperature": 0.0,
  "top_p": 1.0,
  "max_tokens": 1024,
  "seed": null,
  "input_tokens": 1834,
  "output_tokens": 412,
  "cache_hit_system": true,
  "latency_ms": 2103,
  "cost_usd": 0.0078,
  "raw_output": "<verbatim model output>",
  "parsed": { /* the projection JSON itself */ },
  "validation": {
    "schema_passed": true,
    "invariants_passed": true,
    "retry_count": 0
  }
}
```

The harness's existing `cost-ledger` and `failure-log` are reused unchanged.

---

## 5. Token and cost budget (pilot)

Per-call budget:

```text
input  ≤ 2500 tokens (system prompt + delegation ≤ 200 words + artifact ≤ 1500 words)
output ≤ 1024 tokens
```

Pilot total (50 examples):

```text
Cross-family:    50 × 3 families × 1 run  = 150 calls
Within-model:    50 × 1 model    × 5 runs = 250 calls
Total:                                     400 calls
```

Estimated cost at mid-tier rates: ≤ $15 for projection alone. This fits the harness's per-run cap (R-05: $8/run); the pilot is split into two runs (`pilot-cross-family-001`, `pilot-within-model-001`) so each run respects the cap.

---

## 6. Clarification-question quality gate

A `clarification_question` is **acceptable** if it satisfies all of:

1. Names two or more concrete alternatives or asks for a specific bit of information.
2. References the artifact or delegation directly (not generic).
3. Is answerable in ≤ 1 sentence by the user.

Examples (acceptable):

- "Do you want conceptual reframing of the thesis, or sentence-level polish of the existing draft?"
- "Should I check the citations for accuracy, or audit the related-work cluster for missing key papers?"
- "Is the goal to tighten the contribution claim, or to restructure the section ordering?"

Examples (rejected):

- "What do you want?" — generic.
- "Could you clarify your request?" — generic.
- "Please specify." — generic.

Rejected clarification questions count as a schema failure for retry purposes (§7).

---

## 7. Failure and retry policy

| Failure mode | Action |
|---|---|
| JSON parse fails | 1 retry with stricter system reminder appended |
| Schema fails | 1 retry with the validator error appended to the user prompt |
| Invariant 1–7 fails | 1 retry with the failed invariant ID listed |
| Clarification-question gate fails | 1 retry with §6 rules quoted |
| Retry also fails | log to `failure-log/index.jsonl` with category `projection.invalid_output`; example marked `unprojected` and **excluded** from divergence statistics |
| Model API error (5xx, timeout) | exponential backoff, 3 retries, then `failure-log` |
| Cost cap hit mid-run | abort run cleanly; partial outputs preserved |

`unprojected` rate is itself a metric: if it exceeds 5% of pilot examples for any model family, the prompt is revised before the main run.

---

## 8. Determinism and reproducibility

- The prompt-version string `spec_pi_v1.0` is recorded in every output. Any prompt edit increments this string.
- The taxonomy-version string `J_v1.1` is recorded. Any change to dimension IDs or counts increments it.
- `temperature`, `top_p`, `max_tokens`, `seed`, `model_id`, `model_family`, and the verbatim system prompt hash are recorded per call.
- Replay: given the same `(prompt_version, taxonomy_version, model_id, temperature=0, seed)`, replays must match modulo provider non-determinism. Mismatches are logged but do not block the run.

---

## 9. Sanity test cases (not gold labels)

These five toy examples are run before the pilot to verify the prompt and validator work end-to-end. They are **not** gold labels for the experiment; they are smoke tests.

| ID | Delegation | Expected (informal sketch) |
|---|---|---|
| smoke-001 | "Fix the grammar in this section." | R1.6 dominant (~0.9); R1.1–R1.5 ≤ 0.3; clarification_needed=false |
| smoke-002 | "Improve this draft." | High variance expected: at least two of R1.1, R1.4, R1.6 ≥ 0.5; clarification_needed=true with concrete binary |
| smoke-003 | "Check the citations." | R1.7 dominant; R1.6, R1.4 low; clarification_needed=false |
| smoke-004 | "Review the framing." | R1.1 ≥ 0.7; R1.4 ≥ 0.5; R1.6 ≤ 0.3; clarification_needed possibly true |
| smoke-005 | "Reorder the sections so the contribution comes first." | R1.5 ≥ 0.7; R1.1 moderate; clarification_needed=false |

If any model family produces a sanity-violating output on any smoke-* example (e.g., R1.6 ≥ 0.7 on smoke-005), the prompt is revised before pilot.

---

## 10. Versioning

- This spec: `spec_pi_v1.0`, depends on `J_v1.1`.
- Bump rules:
  - System-prompt edit → `spec_pi_v1.0.X` (patch).
  - Schema change (new field, new constraint) → `spec_pi_v1.1`.
  - Taxonomy change → already covered by `J_v1.1` → `J_v1.2` etc., this spec rebinds.
- Every run records `(spec_pi_version, taxonomy_version)` so historical projections remain interpretable after future bumps.

---

## 11. Handoff to harness

The harness implementation (`rbd-harness`) consumes this spec as:

- `shared/prompts/projection.system.md` — verbatim §3.1.
- `shared/prompts/projection.user.tmpl.md` — verbatim §3.2.
- `shared/schemas/projection.schema.json` — verbatim §2.
- `harness/sub_agents/projection.py` — the runner that wires prompt + schema + retry policy + ledger writes.
- `harness/runs.py` — the per-call output writer per §4.3.

This spec is the **source of truth**; the harness files are derived. Any change starts here and propagates downstream.

---

## 12. What this spec deliberately leaves open

- Which mid-tier model is used per family — recorded at run time, not fixed here, because models deprecate.
- The exact `seed` strategy when a family does not expose seeds — provider-dependent.
- Human-in-the-loop projection (a sixth run mode) — out of scope for v1.0.
- Adaptive prompt versions per family — out of scope; the same system prompt is used everywhere.

These are recorded in `failure-log/open-questions.md` and revisited after the pilot.
