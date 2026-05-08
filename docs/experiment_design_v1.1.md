# Experiment Design v1.1
## Sync Patch on `experiment_design_v1.0` for the First-Cycle (R1 + RX) Scope

> Status: narrowed experiment plan for first paper cycle
> Role: re-states the v1.0 experiment design under `J_v1.1`, scales to the 50-example pilot, defers main-300 work
> Companion files:
> - `experiment_design_v1.0.md` (parent — unchanged)
> - `formalization_v1.1.md`
> - `paper_master_v1.1.md`
> - `spec_pi_implementation_v1.0.md`
> - `spec_dataset_v1.0.md`

---

## 0. What changed from v1.0

The five experimental claims in v1.0 §1 are unchanged in spirit but **narrowed in evidence**:

- All experiments operate on `AmbiguousDelegation-50-R1` (50 R1 examples) instead of the full 300.
- Hidden-intent annotation uses one author + two LLM annotators with a 20-example human validation subset (not three humans on every example).
- The taxonomy in all metrics is `J_v1.1` (12 dim) instead of the full 38.
- Experiment 4 (generate-then-select) is included but at reduced scale (10 examples).
- Experiment 5 (uncertainty / overclaim calibration) is reported as analysis, not as a standalone experiment.
- Operational details (prompts, schemas, dataset construction) defer to the `spec_*_v1.0` documents rather than being re-stated here.

What does **not** change:

- The five claims (projection mismatch exists; cross-family > within-model; clarification has cost-sensitive value; per-dim reputation > scalar; protocol > baselines on R1).
- The hypothesis structure for Experiment 1B (`R(d) = d_C / d_W > 1`).
- The dataset acceptance gates (now formalized in `spec_dataset_v1.0` §10).
- The statistical-test choices (paired bootstrap CI, Wilcoxon signed-rank, etc.).

---

## 1. Core experimental claims (narrowed evidence)

| Claim | v1.0 evidence | v1.1 evidence (this paper) |
|---|---|---|
| C1: projection mismatch exists | 300 examples × 3 families | 50 examples × 3 families |
| C2: not just stochasticity | 300 + 1500 within-model runs | 50 + 250 within-model runs |
| C3: clarification has cost-sensitive value | full 300 | 50, with smaller per-claim CIs |
| C4: per-dim reputation > scalar | full simulation | reduced simulation, same protocol |
| C5: protocol > baselines | 5 baselines on 300 | 4 baselines on 50 |

The paper must report the reduced-scale CIs honestly. Significance claims must survive at n=50 or be downgraded to "consistent with H but underpowered".

---

## 2. Dataset (defer to spec_dataset_v1.0)

The pilot dataset is defined in `spec_dataset_v1.0`. Summary that the paper's §5.1 must include:

```text
Total examples:      50
Categories:          R1 only
Source mix:          30 synthetic + 20 modified-real (option C)
Coverage:            35 single-dim + 10 dual-dim + 5 ambiguous
Delegation pool:     10 generic surface forms (no dim names)
Hidden-intent:       author + 2 LLM annotators on all 50
                     + 2 humans on 20-example stratified subset (option D)
Acceptance gates:    G-D-01..10 (spec_dataset_v1.0 §10)
```

Operational fields (per-example schema, flaw catalog, build order) live in `spec_dataset_v1.0`. The paper's §5.1 cites the spec by name and includes the summary table only.

---

## 3. Projection protocol (defer to spec_pi_v1.0)

The projection prompt, schema, run configuration, retry policy, and recording format live in `spec_pi_implementation_v1.0`. Paper §5.2 cites the spec and includes:

- Prompt overview (one paragraph, not the verbatim prompt).
- Output schema reference (Appendix B).
- Cross-family run config table (3 families × 1 run, T=0).
- Within-model run config table (1 fixed model × 5 runs, T=0.5).
- `unprojected` rate as a quality metric.

---

## 4. Experiment 1 — Cross-Family Projection Mismatch

### 4.1 Setup

```text
3 model families (claude, gpt, gemini)
Per-family model: mid-tier of each family at run time (recorded)
1 projection run per (model, example)
Temperature: 0.0
50 R1 examples × 3 families = 150 projection calls
```

### 4.2 Metrics (`J_v1.1` instantiation of v1.0 §4)

#### Cross-family projection distance

```math
d_C^{\cos}(d) = \frac{1}{\binom{3}{2}} \sum_{m<n} (1 - \cos(r^{(m)}, r^{(n)}))
```

```math
d_C^{\text{jac}}(d) = \frac{1}{\binom{3}{2}} \sum_{m<n} \big(1 - \frac{|J^*_m \cap J^*_n|}{|J^*_m \cup J^*_n|}\big)
```

#### Projection-intent mismatch

```math
M_i(d) = \Delta(r_i, r^*) \quad \text{per } formalization\_v1.1\ §5
```

with components: cosine, Jaccard on `J^*`, under-projection, over-projection.

#### Under-projection / over-projection (R1 dims only — RX is always active)

```math
\text{UnderProjection}_i(d) = \frac{|\{j \in R1 : r_{i,j} \le 0.3 \land r^*_j > 0.7\}|}{|\{j \in R1 : r^*_j > 0.7\}|}
```

```math
\text{OverProjection}_i(d) = \frac{|\{j \in R1 : r_{i,j} > 0.3 \land r^*_j \le 0.2\}|}{|\{j \in R1 : r_{i,j} > 0.3\}|}
```

(RX is excluded from these because it is always active by construction; including it would inflate the denominator.)

#### Clarification tendency

```math
\text{ClarRate}_i = \frac{|\{d : r_i.\text{clarification\_needed} = \text{true}\}|}{50}
```

### 4.3 Reporting

Per-family table with `d_C^{cos}, d_C^{jac}, M_i, \text{Under}_i, \text{Over}_i, \text{ClarRate}_i`. Paired bootstrap 95% CI on `d_C - d_W` (cross v within, see §5).

### 4.4 Hypotheses (n=50)

```text
H1.1  Median d_C^cos > 0 with paired bootstrap 95% CI > 0
H1.2  Mean projection-intent cosine ≥ 0.6 (above chance) per family
H1.3  Cross-family Jaccard distance distinguishable from random partition
```

H1.1 is the load-bearing claim. H1.2 and H1.3 protect against the "everyone is just bad" objection.

---

## 5. Experiment 1B — Within-Model Stochastic Baseline

### 5.1 Setup

```text
1 fixed model (default: claude mid-tier)
5 projection runs per example
Temperature: 0.5
50 R1 examples × 1 model × 5 runs = 250 projection calls
```

### 5.2 Metrics

```math
d_W^{\cos}(d) = \frac{1}{\binom{5}{2}} \sum_{m<n} (1 - \cos(r^{(m)}, r^{(n)}))
```

```math
d_W^{\text{jac}}(d) = \frac{1}{\binom{5}{2}} \sum_{m<n} (1 - \text{Jaccard}(J^*_m, J^*_n))
```

```math
R(d) = d_C^{\cos}(d) / d_W^{\cos}(d)
```

### 5.3 Hypotheses (n=50)

```text
H1B.1  median R(d) > 1                 (point estimate)
H1B.2  paired bootstrap 95% CI on R    excludes 1
H1B.3  Wilcoxon signed-rank on R > 1   p < 0.05
H1B.4  median R ≥ 1.2                  (pilot gate from spec_dataset §10)
```

### 5.4 Pilot gate (spec_dataset_v1.0 §10 G-D-soft)

If pilot median `R ≤ 1.2`:

```text
- pause main-run planning
- revise projection prompt or taxonomy
- consider whether the pilot delegation pool is too disambiguated by the artifact
- versioned re-run before any further claims
```

If pilot median `1.0 < R < 1.2`:

```text
- claim is reportable but underpowered;
- paper must say "consistent with H1B but does not establish significance at n=50";
- main-run extension required for the strong claim.
```

### 5.5 Why the within-model uses T=0.5 while cross-family uses T=0

This asymmetry is intentional and disclosed in the paper's Discussion:

```text
Cross-family at T=0 captures family-attributable divergence under deterministic
decoding. Within-model at T=0.5 captures the upper bound of stochastic
decoding variance. If d_C(T=0) > d_W(T=0.5), the cross-family signal exceeds
even an inflated stochasticity baseline. This makes the comparison
conservative against the "you're just measuring noise" objection.
```

---

## 6. Experiment 2 — Clarification vs Direct Execution (scaled-down)

### 6.1 Setup

```text
30 examples drawn from the 50-pilot, stratified:
  - 12 single-dim (covering all 7 R1 dims)
  - 10 dual-dim
  - all 5 ambiguous (clarification-expected)
  - 3 single-dim controls (clarification-not-expected)
```

This 30-example subset is the clarification experiment scope. The full 50 is preserved for Experiment 1/1B; Experiment 2 uses 30 to fit the cost cap.

### 6.2 Conditions

```text
A. Direct execution         (no projection, no clarification)
B. Task-aware routing       (route by surface-form heuristic, no clarification)
C. Generic clarification    (CLAMBER-like: ambiguity classifier, generic Q)
D. Proposed protocol        (J_v1.1 projection → clarify-if-trigger → execute)
```

LHAW-style underspecification clarification (v1.0 §6 Baseline D) is **deferred** to the main run — it requires a separate prompt and adds operational scope without distinguishing v1.1's claim. Reported in paper §5 as "deferred to main run" with citation of `experiment_design_v1.0` Appendix D.

### 6.3 Metrics (defer rubric details to spec_evaluation_rubric_v1.0)

```text
- final settlement loss L_i  (per-dim, weighted by w_j; see formalization_v1.1 §13)
- projection-intent cosine after clarification
- number of clarification turns (in {0, 1, 2})
- clarification efficiency CE(d) = (L_direct - L_clarified) / clarification_cost
- overclaim rate (q_ij > v_ij + 0.2)
- scope adherence (RX.3)
```

### 6.4 Cost model

```text
clarification_cost = 1 turn  (uniform first-paper assumption)
```

Sensitivity analysis with `cost ∈ {0.5, 1, 2}` reported in appendix.

### 6.5 Hypotheses (n=30)

```text
H2.1  D mean L < A mean L on ambiguous + dual-dim subset (n=15)
H2.2  D mean L within 0.05 of A on single-dim controls (no harm done)
H2.3  D's CE(d) > 0 on the 5 clarification-expected examples
H2.4  D's overclaim rate ≤ A's overclaim rate
```

H2.1 is the load-bearing claim. H2.2 protects against "clarification always helps" being true trivially.

---

## 7. Experiment 3 — Settlement-Based Reputation (simulated)

### 7.1 Setup

The reputation experiment in the first paper is **simulated**, not run on real LLM agents. Reasons:

```text
- repeated assignment requires T rounds × N agents × N delegations of execution;
- at pilot cost budget this is not feasible;
- the claim (per-dim reputation > scalar) is most cleanly tested in simulation
  with controlled agent fulfillment profiles.
```

Simulated agents have known fulfillment vectors `v_ij ~ Beta(α_ij, β_ij)` per dim. The simulation runs T = 200 rounds, N_agents = 6, drawing delegations from the pilot template pool.

### 7.2 Conditions

```text
A. Scalar reputation                ρ_i           (one number per agent)
B. Task-category reputation         ρ_{i,t}       (one per agent × task; v1.1 has only R1, so reduces to A)
C. Role-conditioned reputation      ρ_{i,y}       (per agent × role)
D. Role + dim reputation (proposed) ρ_{i,y,j}     (per agent × role × dim)
E. Oracle upper bound               (knows true v profiles)
```

For v1.1, B reduces to A because t=R1 for all examples; the comparison is effectively A vs C vs D vs E.

### 7.3 Metrics

```text
- assignment accuracy (fraction of rounds where best-suited agent selected)
- cumulative settlement loss over T rounds
- regret vs E (oracle)
- time-to-specialization (rounds until ρ_{i,y,j} stable within ε)
```

### 7.4 Hypotheses

```text
H3.1  D regret < A regret over T=200 rounds
H3.2  D specializes faster than C
H3.3  Effect strongest when agents have within-dim heterogeneity (e.g., A_strong-on-R1.1
      but A_weak-on-R1.4)
```

### 7.5 What v1.1 explicitly does not claim

```text
- generalization to real LLM agents over T=200 rounds (cost-prohibitive);
- that simulated agent profiles match real LLM fulfillment distributions;
- that reputation update converges in adversarial regimes.
```

These are explicit limitations in the paper.

---

## 8. Experiment 4 — Generate-then-Select Baseline (narrowed)

### 8.1 Setup

```text
10 examples drawn from the 30-Exp2-subset, stratified across coverage classes
3 agents (one per family) execute directly without projection
1 LLM judge selects best output
```

### 8.2 Comparison

Compare D (proposed) vs the generate-then-select baseline on these 10 examples:

```text
- selected output settlement loss
- total execution cost (proposed avoids redundant generation)
- judge disagreement rate
- overclaim instances visible to settlement but invisible to output selection
```

### 8.3 Hypotheses (n=10, exploratory)

```text
H4.1  Proposed total cost < generate-then-select total cost  (because clarification reduces wrong-scope generations)
H4.2  Proposed scope adherence (RX.3) > select baseline scope adherence
```

n=10 is too small for significance claims; reported as observational with effect-size estimates and explicit "exploratory" framing.

---

## 9. Experiment 5 — Uncertainty / Overclaim Calibration (analysis only)

The bid `b_i = (q_i, u_i, p_i, z_i)` records claimed coverage `q_ij` and uncertainty `u_ij`. Settlement gives `v_ij`. The paper reports as analysis (not as a standalone experiment):

```text
- ECE_q  (calibration error between q_ij and v_ij)
- ECE_u  (calibration error between 1-u_ij and v_ij)
- Overclaim rate  OCR = mean 1[q_ij > v_ij + 0.2]
- Honest-limitation rate  (z_i = limit + settlement confirms)
```

These metrics are reported in Discussion, not as separate hypotheses. Reason: with the v1.1 protocol, the bid mechanism is observed across Experiments 1–4 anyway; carving out a separate experiment for it inflates the paper's claim count without adding evidence.

---

## 10. Baseline summary (narrowed)

| Baseline | Prior-work connection | Used in | Reason for inclusion / deferral |
|---|---|---|---|
| Direct execution | standard assistant baseline | Exp 2, Exp 4 | Required floor |
| Task-aware routing | Task-Aware Delegation Cues | Exp 2 | Closest delegation paper |
| Generic ambiguity clarification | CLAMBER | Exp 2 | Ambiguity-vs-responsibility distinction |
| LHAW-like underspecification clarification | LHAW | **deferred** | Adds prompt overhead without distinguishing v1.1 claim |
| Generate-then-select | Selection bottleneck | Exp 4 (n=10) | Tests "select after vs govern before" |
| Within-model stochastic | behavioral variance | Exp 1B | Defends against noise objection |
| Scalar reputation | ordinary memory | Exp 3 | Simulated only |
| No settlement | benchmark-only eval | Exp 3 | Implicit in comparison |

---

## 11. Ablation design (narrowed)

The full v1.0 §11 ablation list is preserved as future work. v1.1 reports a focused subset:

```text
A0  No projection (= Direct execution baseline; covered by Exp 2 condition A)
A1  Projection only, no clarification     (Exp 2 variant: D minus clarification)
A2  No overclaim penalty                  (Exp 5 analysis)
A3  Scalar reputation instead of dim      (Exp 3 condition A)
A4  Open-vocabulary projection            (deferred — requires separate prompt; future work)
```

A4 (open-vocabulary projection) is explicitly deferred. The first paper does not include the empirical result that closed-taxonomy outperforms open-vocabulary; instead, the paper argues the closure case theoretically (in Discussion) and reserves the empirical comparison for a follow-up.

---

## 12. Evaluation rubric (defer to spec_evaluation_rubric_v1.0)

The per-dim rubric prompt and schema for LLM and human judges live in `spec_evaluation_rubric_v1.0` (forthcoming). Paper §5.7 cites the spec and reports:

```text
- LLM-LLM α per dim
- human-human α per dim (on Exp 2 + Exp 4 outputs that received human scoring)
- human-LLM Spearman per dim
```

Judges score only on `j ∈ J^*(d)` and do not see hidden intent, model identity, or other agents' outputs (per v1.0 §12).

---

## 13. Statistical tests

| Test | Used in | Reason |
|---|---|---|
| Paired bootstrap 95% CI | Exp 1 (`d_C - d_W`), Exp 2 (`L_A - L_D`) | Robust to non-normal distributions |
| Wilcoxon signed-rank | Exp 1B (`R(d) > 1`) | Median test for paired ratios |
| Krippendorff's α | Annotation, judge agreement | Multi-rater categorical |
| Spearman correlation | Human-LLM judge correlation | Rank-based, robust |
| Cumulative regret curves | Exp 3 | Standard reputation eval |

Effect sizes (Cohen's d or rank-biserial) reported alongside p-values.

---

## 14. Pilot protocol (now operational, not aspirational)

The pilot in v1.0 §14 is now formalized in `spec_dataset_v1.0` §9 (build order) and §10 (acceptance gates). Paper §5.1.X reports:

```text
- whether all 10 acceptance gates passed (G-D-01..10)
- per-dim α achieved
- coverage matrix actually realized
- list of any dim that failed α with explanation
- list of any acceptance gate failure that was waived (with reason)
```

Failures must be reported, not hidden.

---

## 15. Expected tables (narrowed)

| Table | Content | n |
|---|---|---|
| T1 | Dataset composition (50 examples) | 50 |
| T2 | Projection divergence: cross-family vs within-model | 50 |
| T3 | Projection-intent mismatch by dim | 50 × 12 |
| T4 | Clarification results (Exp 2) | 30 |
| T5 | Baseline comparison (Exp 2) | 30 |
| T6 | Reputation simulation (Exp 3) | T=200 rounds |
| T7 | Judge agreement (LLM-LLM, human-human, human-LLM) | 20 + Exp 2 |
| T8 | Generate-then-select (Exp 4) | 10 |

---

## 16. Expected figures (narrowed)

```text
F1  Protocol diagram (delegation → projection → bid/clar → exec → settle → reputation)
F2  Three model families' projections on a single example (qualitative)
F3  Boxplots: d_C^cos vs d_W^cos, by coverage class
F4  Scatter: clarification value vs projection uncertainty (Exp 2)
F5  Heatmap: agent × dim reputation over T rounds (Exp 3)
F6  Bar chart: settlement loss by condition (Exp 2)
```

F2 (qualitative example) is load-bearing for reader intuition; reserve a full page if needed.

---

## 17. Risk and recovery

The central risk in v1.0 §19 is preserved:

> Projection divergence may be small or not meaningfully different from within-model stochasticity.

v1.1 recovery plan, in order:

```text
1. If R(d) median ∈ [1.0, 1.2], paper reports "consistent with H but underpowered";
   does not claim significance.
2. If R(d) median ≤ 1.0, prompt or taxonomy is revised before any claim is published.
3. If revision still fails, the paper repositions to "we provide a closed taxonomy
   and a measurement framework; empirical divergence claim is deferred to extension".
4. The paper does not hide the result.
```

---

## 18. Final recommendation (current cycle)

The first paper prioritizes:

```text
1. Experiment 1 + 1B  (projection mismatch, must succeed for paper to exist)
2. Experiment 2        (clarification value, the protocol's killer feature)
3. Experiment 3        (reputation, simulated; cheap; high theoretical leverage)
4. Experiment 4        (generate-then-select, exploratory; n=10)
5. Experiment 5        (calibration analysis, no separate experiment)
```

If time/cost forces further reduction, drop Experiment 4 first, then trim Experiment 3's T to 100. Keep 1, 1B, and 2.
