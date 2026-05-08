# RBD Pilot — Pre-Execution Responsibility Projection in Multi-Agent LLM Orchestration

Pilot replication package for **"Measuring Pre-Execution Responsibility Projection in Multi-Agent LLM Orchestration"** (Hwang, Geum, Han — Kyungpook National University, 2026).

> arXiv: *(link added on submission)*

## What's here

| path | content |
|---|---|
| `paper/` | LaTeX source for the manuscript (IEEE format, 21 pp.). `main.tex` is the entry point. |
| `data/pilot_v1.1/` | 50-example pilot dataset and per-step outputs: `examples/` (artifacts + hidden $r^*$), `projection/` (cross-family responsibility projections), `execution/` (3-condition outputs), `judge/` (12-judge panel scores), `annotations*/` (rater data), `stats/` (Experiment 1 / 1B / 2 aggregates). |
| `scripts/` | Experiment runners (`exp1_*.py`, `exp2_*.py`, `pass2_*.py`) and analysis. `_clients.py` is the unified per-host LLM client; `_models.py` is the panel loader. |
| `docs/` | Versioned specs (concept, formalization, experiment design, paper master). The latest revisions reflect the v1.4 paper. |
| `human_annotation/` | Rater protocol v1, packaged texts, and Prolific recruitment artifacts for the closed Stage 1 R1.7 corroboration. |
| `review/` | Pre-code-modification critical reviews (v1.0 review feedback, additional prior-work mapping). Kept for transparency on the research process. |

## What's *not* here

- **`reference/`, `reference2/`, `reference3/`** (60 PDFs) are excluded from this repository for copyright reasons. Citation entries live in `paper/references.bib`.
- API keys and provider credentials (`.env`) are excluded.

## Reproducibility

The pilot used a fixed model panel (`data/pilot_v1.1/spec_models_panel.json`) at $T = 0$ for projection and a 12-judge Anthropic-excluded tier-stratified panel for execution scoring. To rerun:

```bash
# 1. install deps (Python 3.10+)
python -m venv .venv && source .venv/bin/activate
pip install openai anthropic google-generativeai

# 2. set API keys (one-time)
cp .env.example .env       # then fill in keys
# ANTHROPIC_API_KEY=...
# OPENAI_API_KEY=...
# GOOGLE_API_KEY=...
# XAI_API_KEY=...
# (Ollama, if used, runs locally)

# 3. rerun any stage from data/
python scripts/exp1_projection.py    # cross-family projection (Exp 1)
python scripts/exp2_run.py           # 3-condition execution (Exp 2)
python scripts/exp2_aggregate.py     # judge-panel aggregation
python scripts/exp1_analyze.py       # paired-bootstrap statistics
```

Estimated total cost at panel pricing (2026-05): ≈ \$130 (within the $1{,}000 study cap reported in §V).

## Citation

```bibtex
@article{hwang2026rbd,
  title   = {Measuring Pre-Execution Responsibility Projection in Multi-Agent LLM Orchestration},
  author  = {Hwang, Younggyu and Geum, Seungho and Han, Sekyung},
  journal = {arXiv preprint},
  year    = {2026},
  note    = {arXiv:XXXX.XXXXX}
}
```

## License

Code, data, and documentation are released under [CC BY 4.0](LICENSE). Reference PDFs are not redistributed; cite the original publishers.

## Contact

- **Younggyu Hwang** (first author) — `treu4644@knu.ac.kr`
- **Sekyung Han** (corresponding) — `skhan@knu.ac.kr`
