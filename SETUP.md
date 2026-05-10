# SETUP.md — Per-User Configuration for Replication

This file lists everything a clone of `rbd-pilot` needs to configure **per machine / per user account**. The repo itself is reproducible from the LaTeX source + `data/` + `scripts/`, but the runtime depends on credentials and account-specific subscription anchors that don't belong in version control.

> **Policy**: Anything in this list is your responsibility to set up after `git clone`. The repo will not auto-create them.

---

## 1. Python environment (required for any script run)

```bash
# Python 3.10+ recommended (zoneinfo, modern type hints)
python -m venv .venv
source .venv/bin/activate
pip install openai anthropic "google-genai" xai_sdk python-dotenv pyyaml numpy
```

Optional (analysis): `pip install pandas pyarrow scipy matplotlib`.

---

## 2. API keys (`.env`) — required for non-subscription paths

Copy the template and fill in your provider keys:

```bash
cp .env.example .env
# Edit .env:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
#   GOOGLE_API_KEY=...
#   XAI_API_KEY=...
```

**Which keys you actually need depends on what you rerun**:

| Pipeline stage | Required keys |
|---|---|
| Exp 1 cross-family projection | `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` (or codex CLI subscription instead of OpenAI) |
| Exp 1B within-model variance | `OPENAI_API_KEY` (default), or Claude CLI subscription if using `scripts/exp1b_claude_within.py` |
| Exp 2 executor | `ANTHROPIC_API_KEY` (only if not using Claude CLI subscription) |
| Exp 2 judge panel (12 models) | All four (frontier + mid via API), plus Ollama for the 5 local models |

`.env` is git-ignored. Never commit it.

---

## 3. CLI tools (optional, but recommended for cost reduction)

### Codex CLI (ChatGPT subscription)

```bash
npm install -g @openai/codex   # or follow your distribution's path
codex login                     # browser flow
```

Used by `_clients.py` for `gpt-5` calls when `CODEX_PREFER_API` is *not* set. Drops Exp 1 projection cost from ~$170 to near-zero.

### Claude CLI (Anthropic subscription)

```bash
# Install per https://claude.com/claude-code, then:
claude login
```

Used by `scripts/exp1b_claude_within.py` for free within-model variance with `claude-sonnet-4-6`.

### Ollama (open-weight judges, all local)

```bash
# Install per https://ollama.com, then pull the panel:
ollama pull llama3.1:70b-instruct-q4_K_M
ollama pull qwen2.5:72b-instruct-q4_K_M
ollama pull mistral-large:123b-instruct-2407-q4_K_M
ollama pull deepseek-r1:70b-distill-q4_K_M
ollama pull llama3.1:8b-instruct
ollama pull qwen2.5:7b-instruct
ollama pull gemma2:9b-instruct
ollama pull phi3:medium-14b-instruct
ollama pull mistral:7b-instruct-v0.3
```

Five of these populate the "light" tier of the 12-judge panel; the rest are part of the "mid" tier. Total VRAM at full load ~120 GB; you can prune to a subset if you only want the headline metric.

---

## 4. Codex weekly-quota config (only if using `CODEX_QUOTA_STRATEGY=wait_weekly`)

`_clients.py`'s `wait_weekly` strategy waits until the next ChatGPT subscription weekly bucket reset before retrying — this avoids OpenAI API fallback when the codex subscription is exhausted. **The reset weekday is account-specific** (anchored to your subscription start date). Drop a YAML at `~/.config/codex_quota.yaml`:

```yaml
weekly_reset:
  weekday: SAT       # MON|TUE|WED|THU|FRI|SAT|SUN — your account's reset day
  hour_local: 0      # 0..23 in tz below
  tz: Asia/Seoul     # IANA timezone string
```

If the file is missing, `wait_weekly` falls back to a generic 24-hour poll (correct, just less precise). Default strategy if `CODEX_QUOTA_STRATEGY` env is unset is `fallback` (immediate API switch on rate-limit), which costs money but doesn't wait.

How to discover your reset weekday: when you next hit "weekly limit reached" from codex CLI, note the timestamp; whenever it starts answering again, note that too. The day-of-week of the second timestamp is your `weekday`.

---

## 5. Reference PDFs (optional, for full citation context)

The 60 reference PDFs that informed `paper/references.bib` are excluded from this repo for copyright reasons. To rebuild your local PDF library:

- Open `paper/references.bib` and pull each entry from arXiv / publisher venue.
- Place under `reference/`, `reference2/`, `reference3/` (any organization works; `scripts/build_topic_seeds.py` matches by fuzzy title).

The reference PDFs are not strictly required for replication of the experiments — just for `scripts/build_topic_seeds.py` (used during dataset expansion) and for verifying citation accuracy.

---

## 6. Quick sanity check

After steps 1+2, this should succeed:

```bash
source .venv/bin/activate
python scripts/exp1_projection.py --mode cross --ids ad_r1_001 --limit 1
```

Expected output: three projection JSONs in `data/pilot_v1.1/projection/` (one per family), and one ledger entry in `data/pilot_v1.1/stats/exp1_cost_ledger.jsonl`. If any provider returns an auth error, that key in `.env` is wrong.

---

## 7. What this repo will NOT do for you

- Install Python, npm, Ollama, or any system packages.
- Create API accounts or fund them.
- Configure `~/.config/codex_quota.yaml` from your subscription history.
- Re-download reference PDFs.
- Provision GPU memory for Ollama models.

Each of these is per-user / per-machine and out of the repo's scope.
