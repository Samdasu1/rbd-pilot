# Main Run Findings (n=310)

> Status: **paper at TMLR review (2026-05-09)** — findings below are for the follow-up / v2 paper, NOT for the submitted manuscript. Do not retroactively rewrite `paper/sections/*.tex` while review is in progress.

---

## 0. Why this document exists

The pilot manuscript currently under TMLR review cites numbers derived from the v1.0/v1.1 panel (claude-sonnet-4.5 within-model, 25/50 zero-d_W examples, R(d) median = 14.4). The main run scaled to n=310 examples with a closer-but-not-identical within-model panel (claude-sonnet-4-6 via Claude Code subscription, no `temperature` exposed). The headline magnitude shifts; the directional claim ("cross-family > within-family stochasticity") survives intact. This file captures the as-measured numbers so the v2/follow-up paper can cite them without needing to re-run.

---

## 1. Dataset

| Quantity | Pilot v1.1 | Main run v1.0 (this) |
|---|---|---|
| n | 50 (32 synthetic + 18 modified-real) | **310** (50 inherited + 260 new synthetic, topic-seeded from `references.bib` titles) |
| coverage_class | 30 single + 10 dual + 5 ambiguous + 5 control | 190 single + 62 dual + 31 ambiguous + 27 control |
| knowledge_gating | 90% low, 4% moderate, 6% high | 66% low, 23% moderate, 12% high |
| delegation_dim_leakage = no | 88% | 91% |
| ISSUES | 0 | 0 |

Generated via `scripts/gen_examples_main.py` using Claude Code subscription (free), seeded by `data/main_v1.0/topic_seeds.jsonl` (63 titles, 44 with PDF abstract).

---

## 2. Projection — cross-family (Exp 1) + within-model (Exp 1B)

### Setup

- Cross-family: gpt-5 / gemini-2.5-pro / grok-4 at T=0 (one run each per example).
- Within-model (new — re-run 2026-05-11..05-12 via Claude Code subscription): claude-sonnet-4-6, nominal T=0.5, 5 runs per example.
- Within-model under paper's panel was claude-sonnet-4.5 via API at T=0.5; that panel is no longer reachable (model retired / API behavior shifted). claude-sonnet-4-6 is the closest available match.

### Headline R(d) (controls excluded)

| | pilot (1-50) | new (51-310) | **combined (1-310)** | paper claim (v1.0 panel) |
|---|---|---|---|---|
| usable n | 45 | 229 | **274** | 25 finite of 50 |
| d_C cos median | 0.0857 | 0.0786 | 0.0804 | — |
| d_W cos median | 0.0164 | 0.0160 | **0.0161** | ~0.001 with 50% zero |
| **R_cos median (finite)** | 5.85 | 5.07 | **5.11** | **14.4** |
| R_cos mean | 9.69 | 9.19 | 9.28 | 17.99 |
| R_cos 95% bootstrap CI | — | — | **[4.53, 5.74]** | — |
| R_jac median | 1.84 | 1.75 | 1.76 | — |
| R_cos > 1 | 100% | 96% | **97%** | 100% |
| R_cos > 1.2 | 98% | 95% | **95%** | 100% |
| R_cos > 10 | 27% | 23% | 24% | — |
| zero-d_W (excluded) | 0 | 1 | 1 | 25 of 50 |
| Paired (d_C − d_W) mean | — | — | **0.0823** | 0.099 |
| Paired 95% CI excludes 0 | — | — | **[0.0734, 0.0921]** ✓ | [0.088, 0.112] |
| Wilcoxon dC > dW p | — | — | **9 × 10⁻⁴⁷** | < 0.0001 |

### All 5 hypotheses pass on the main run data

| H | claim | result |
|---|---|---|
| H1.1 | (d_C − d_W) 95% CI excludes 0 | PASS [0.0734, 0.0921] |
| H1B.1 | median R(d) > 1 | PASS (5.11) |
| H1B.2 | R 95% CI excludes 1 | PASS [4.53, 5.74] |
| H1B.3 | Wilcoxon p < 0.05 | PASS (p = 9 × 10⁻⁴⁷) |
| H1B.4 | median R ≥ 1.2 (strong claim) | PASS (5.11 ≫ 1.2) |

### Magnitude shift explanation

The paper's R=14.4 came from a within-model panel (claude-sonnet-4.5 via API at T=0.5) that produced d_W = 0 in 25 of 50 pilot examples — i.e., the model produced bit-identical projection vectors across 5 independent runs at T=0.5. The current claude-sonnet-4-6 via Claude Code subscription is non-deterministic at the projection-vector level (only 1 of 274 example showed d_W = 0). Median d_W therefore rises from ~0.001 to 0.0161 (10×), and R = d_C / d_W falls from 14.4 to 5.11 (~3×).

Three regimes:

| within-model panel | per-call deterministic? | d_W median | R_cos median |
|---|---|---|---|
| claude-sonnet-4.5 API T=0.5 (paper) | 50% bit-identical | ~0.001 | 14.4 |
| **claude-sonnet-4-6 Claude Code subscription (this)** | rarely identical | 0.0161 | **5.11** |
| gpt-5 API T=0.5 (Phase A+B) | never identical | 0.022 | 3.86 |

The headline magnitude ("17×") is panel-specific. The directional claim ("cross-family > within-family") holds across all three panels.

### Pilot↔new consistency

Pilot and new sets give nearly identical R medians (5.85 vs 5.07) and per-quantile breakdowns. Scaling 6× via topic-seeded synthetic examples did not introduce a structural shift in projection-mismatch — the synthetic generation procedure does not appear to collapse cross-family disagreement (which had been a methodological concern).

---

## 3. Cost (cumulative through 2026-05-12)

| Stage | calls | cost | notes |
|---|---|---|---|
| Dataset generation (250 synth) | 250 | $0 | Claude Code subscription |
| Exp 1 cross + 1B within (Phase A+B, gpt-5 mostly API fallback) | 2496 | $67.79 | overshot ~$5 estimate because codex throttle |
| Exp 1B within rerun (claude-sonnet-4-6 subscription) | 1525 | $0 | included 25 smoke + 1500 main |
| **Cumulative** | — | **$67.79** | — |

Budget cap: $1000. Spent so far ~$204 (pilot $136 + main $68). Remaining ~$796. Phase C (Exp 2 judge) expected to add ~$10-15.

---

## 4. Open items

- Phase C (Exp 2 executor) — **done 2026-05-12**. 780/780 new examples × 3 conditions = 930 total exec files. Subscription path (claude-opus-4-7 via Claude CLI), $0 actual cost (API leak incident on first attempt — see §7).
- Phase C (Exp 2 judge) — **partial 2026-05-12, ~5% done before server shutdown**. See §8.
- Codex weekly bucket recovers **2026-05-16 Saturday 00:00 KST**; Claude weekly recovers **2026-05-14 Thursday 00:00 KST**. Phase C executor (claude-opus) is fine — Anthropic subscription has headroom after sonnet within-model run finished. Judge calls via codex (gpt-5) are gated by 5h bucket (`wait_5h`) and weekly bucket. 
- Anchor specifiability ceiling (P3 / §VI #4) — Stage 1 closure unchanged; future rater_protocol_v2 work deferred to v2 paper.

---

## 5. Provenance

- Examples: `data/pilot_v1.1/examples/ad_r1_001.yaml` ... `ad_r1_310.yaml`
- Projections: `data/pilot_v1.1/projection/{eid}__{gpt-5|gemini-2.5-pro|grok-4|claude}__t{0.0|0.5}_run{0..5}.json`
- Ledger: `data/pilot_v1.1/stats/exp1_cost_ledger.jsonl`
- Topic seeds: `data/main_v1.0/topic_seeds.jsonl`
- Analysis: re-run any time via the inline python in this file (see "headline R(d)" computation in §2). No script depends on the stats file being current.

---

## 6. Changelog of this document

- 2026-05-12: created. Captures n=310 R(d) median 5.11 finding (vs paper's 14.4 from v1.0 panel). Paper at TMLR review — kept manuscript untouched per submission discipline.

---

## 7. Incident — Phase C executor accidental API billing (2026-05-12)

### Symptom

Anthropic dashboard (console.anthropic.com/usage):

| Time (UTC) | opus-4-7 | haiku |
|---|---|---|
| 2026-05-11 17:00 | 1,240,000 tokens | 65,000 |
| 2026-05-11 18:00 | 1,730,000 tokens | 86,000 |

= ~3M opus tokens (haiku ~150k overhead from Claude Code CLI internal routing) during the first ~2h of Phase C executor.

### Cause

`scripts/exp2_run.py` `_call_claude_cli_executor` (and `scripts/exp1b_claude_within.py` `call_claude_cli`) built subprocess env via `env = {**os.environ, "HARNESS_NO_RECURSE": "1"}`. This inherited `ANTHROPIC_API_KEY` from `.env`. Despite the Claude Code session being OAuth-logged into a Max subscription (`~/.claude/.credentials.json` shows `subscriptionType: max`), some CLI code paths preferred the API key over the OAuth session, billing the calls against the API account.

### Fix (commit `cf059b3`)

1. Both `.env` files (`~/paper/6. agent/.env` and `~/research-harness/.env`) had `ANTHROPIC_API_KEY=...` commented out:
   `# DISABLED 2026-05-12 to prevent CLI fallback to API mode: ...`
2. Both subprocess-env constructions in `exp2_run.py` and `exp1b_claude_within.py` now strip `ANTHROPIC_API_KEY` explicitly:
   `env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}`

### Verification

Smoke re-run after fix (`ad_r1_051 × 3 conditions` via `--executor-mode claude_cli`): 3/3 pass, `cost_usd = 0` per ledger. Subsequent Phase C calls should not appear on `console.anthropic.com` usage; if they do, the patch failed and the run must be killed again.

### Pre-patch sunk cost

The 152 executor calls completed before the kill (ad_r1_051..~ad_r1_102, partial) are valid outputs we kept on disk; they were billed to API at unknown amount (user to verify on dashboard). They are not re-run; the script's existing-file-check skips them on restart.

### Lesson (added to AGENTS.md / CLAUDE.md if recurring)

When invoking CLI tools that have multiple auth modes (subscription OAuth + API key), do not assume env inheritance is safe. Explicitly strip auth env that you don't want the CLI to use, or set `--bare` / equivalent flag to force a specific mode.

---

## 8. Phase C judge — partial progress at 2026-05-12 server shutdown

Server was scheduled to power off at 2026-05-12 21:30 KST. Two judge processes were running in parallel and gracefully stopped at 20:45 KST.

### What ran

| process | PID | judges | started | stopped |
|---|---|---|---|---|
| frontier 3 | 2604828 | gpt-5 (codex sub), gemini-2.5-pro (API), grok-4 (API) | 12:23 | 20:45 (SIGTERM) |
| ollama 9 | 2799360 | llama-3.1-70b/8b, qwen-2.5-72b/7b, mistral-large-2/7b, deepseek-v3-70b, gemma-9b, phi-3-medium-14b | 15:03 | 20:45 (SIGTERM) |

Both were launched as `python scripts/exp2_run.py --mode judge ...` with `CODEX_QUOTA_STRATEGY=wait_5h`. Frontier had `--judge-workers 3`, Ollama had `--judge-workers 2`. ANTHROPIC_API_KEY and OPENAI_API_KEY env disabled (see §7), so any unexpected fallback would have failed-closed rather than charged.

### Coverage achieved (new examples only, ad_r1_051..310)

| metric | value |
|---|---|
| (eid, condition) pairs touched | 38 / 780 (4.9%) |
| pairs with full 12-judge coverage | 29 |
| pairs with frontier-3 complete | 29 |
| pairs with ollama-9 complete | 37 |
| total NEW judge calls written | ~410 |
| total NEW judge files on disk | 424 |
| actual cost (API/codex sum) | $0.70 (gemini $0.27 + grok $0.43 + gpt-5 codex $0; ollama 9 all $0) |

Pilot 50 examples × 3 conditions × 12 judges = 1800 judge files are intact from earlier runs (paper-cited). Total judge dir size: 2224 files.

### Resumption commands (post-power-on)

Both scripts have `if p.exists(): return True, 0.0` skip logic at the run_judge entry, so re-launching the same commands will pick up where they left off without duplicating work.

```bash
# enable defensive env (do NOT re-enable ANTHROPIC_API_KEY or OPENAI_API_KEY
# in .env unless you have a specific reason)
export CODEX_QUOTA_STRATEGY=wait_5h

# frontier 3 — ~17-20h remaining at ~65s per (eid, cond)
cd "/home/treu46/paper/6. agent"
nohup ~/research-harness/.venv/bin/python scripts/exp2_run.py \
  --mode judge --judges gpt-5 gemini-2.5-pro grok-4 --judge-workers 3 \
  > /tmp/exp2_judge_frontier.log 2>&1 &

# ollama 9 — ~3-5 days remaining at --judge-workers 2 (40% GPU target)
# launch separately so the two phases progress independently
nohup ~/research-harness/.venv/bin/python scripts/exp2_run.py \
  --mode judge \
  --judges llama-3.1-70b-instruct qwen-2.5-72b-instruct mistral-large-2-2407 \
           deepseek-v3-distill-70b llama-3.1-8b-instruct qwen-2.5-7b-instruct \
           gemma-2-9b-it phi-3-medium-14b-instruct mistral-7b-instruct-v0.3 \
  --judge-workers 2 \
  > /tmp/exp2_judge_ollama.log 2>&1 &
```

The `r_star_median.json` fallback to `hidden_intent.weights` (commit `cf059b3` family — see also `get_active_set` patch in `exp2_run.py`) is required for the new examples to be judgeable; this is already in the script.

### Open items at shutdown

- Frontier 3 still has ~96% (~750 pairs) of new judge work to do.
- Ollama 9 still has ~95% (~743 pairs) to do.
- Once the judge phase reaches ≥95% coverage (e.g., ≥741 of 780 new pairs with at least 9-of-12 judges), run `scripts/exp2_aggregate.py` to compute settlement loss and per-tier breakdowns. Output should write to `data/main_v1.0/stats/` not `data/pilot_v1.1/stats/` to preserve paper-cited pilot stats.
- After aggregate stats land, this file's §2-style block will be added for the executor/judge headline numbers under the v2-paper section.
