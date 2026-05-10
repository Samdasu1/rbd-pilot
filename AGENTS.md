# AGENTS.md — paper-6 (RBD pilot) 작업 헌법

> 이 디렉토리는 paper "When Responsibility Guidance Hurts: A Pilot Study of Pre-Execution Projection in LLM Agents" (Hwang & Han, KNU EE, 2026)의 source + data + scripts다. 모든 sub-agent / Claude 세션은 호출 직전 본 문서를 읽고 §1의 critical invariants를 인지해야 한다.

---

## 0. 프로젝트 상태 (2026-05-10 기준)

- **Manuscript**: `paper/main.pdf` v1.4 (21 pp., IEEE format, hidelinks, pastel heatmap tables)
- **Submission**: TMLR via OpenReview (제출 완료, rolling review 6-8주)
- **Public repo**: https://github.com/Samdasu1/rbd-pilot (CC BY 4.0)
- **Citable archive**: Zenodo DOI [10.5281/zenodo.20088555](https://doi.org/10.5281/zenodo.20088555)
- **Authors**: Younggyu Hwang (first), Sekyung Han (corresponding) — both KNU EE
- **현재 진행**: main run n=300 (50 pilot + 250 새 generated 2026-05-09); Exp 1 projection (cross+within) done; Exp 2 judge (Phase C) 진행 예정 (codex 주간 토큰 회복 후)

---

## 1. Critical invariants (위반 시 abort)

| ID | 규칙 |
|---|---|
| **R-PAPER** | `paper/sections/*.tex` 의 numerical claim (R=14.4, paired diff -0.132, etc.) 은 `data/pilot_v1.1/stats/` 의 산출 결과와 정합해야 함. number 변경 전 반드시 산출 재현 가능 여부 확인. |
| **R-DATA** | `data/pilot_v1.1/stats/*` 직접 overwrite 금지. analysis script 돌리기 전에 기존 stats 파일 백업 (`cp` to `_backup_<date>/`). 어떤 stats가 paper에 cite됐는지 모르면 grep first. |
| **R-PANEL** | `data/pilot_v1.1/spec_models_panel.json`이 현재 model panel single source of truth. cross-family = `gpt-5 / gemini-2.5-pro / grok-4`, within-model = `gpt-5` (현재). 단 paper §V.2의 R=14.4는 **구 panel (claude-sonnet-4.5 within)** 산출이며 methodology drift 존재. 재현 작업 진행 중 (sonnet-4-6 subscription path). |
| **R-SUBSCRIPTION** | LLM 호출은 subscription 먼저: claude executor = Claude CLI, gpt-5 = codex CLI. API fallback은 `CODEX_QUOTA_STRATEGY=wait_5h` 환경에서 5h bucket 회복 대기로 우회 가능. |
| **R-LICENSE** | 모든 산출물 CC BY 4.0. `reference/`, `reference2/`, `reference3/` PDF 60개는 저작권 사유로 public push 금지 (이미 `.gitignore`). |

---

## 2. 입구 — 작업 시작 전 반드시 읽을 파일 (load-bearing first)

```
docs/CHANGELOG.md              # 결정 로그 reverse-chrono. 최근 entry부터.
paper/main.pdf                 # 현재 deliverable (21p)
paper/sections/{abstract,introduction,results,conclusion}.tex   # paper의 numerical claim 위치
data/pilot_v1.1/spec_models_panel.json   # 현재 model panel
docs/spec_dataset_v1.0.md      # dataset 구성 + r* annotation protocol
```

추가로 수정 작업 종류별:
- **paper editing**: `_submission/main.pdf`, `_submission/metadata.md` (TMLR 제출 본 동기화 필요)
- **dataset 추가**: `scripts/gen_examples_main.py` + `scripts/build_topic_seeds.py`, output to `data/pilot_v1.1/examples/` + `data/main_v1.0/topic_seeds.jsonl`
- **projection 실행**: `scripts/exp1_projection.py --mode {cross|within|both} --ids ...`
- **claude within-model 재실행** (paper R=14.4 재현용): `scripts/exp1b_claude_within.py --ids-range 1 310 --reps 5` (Claude CLI subscription, 무료)
- **judge 실행 (Phase C)**: `scripts/exp2_run.py` + `scripts/exp2_aggregate.py` — 시작 전 `CODEX_QUOTA_STRATEGY=wait_5h` env 켜기

---

## 3. 일관성 점검 — paper의 헤드라인 클레임과 데이터

| paper 위치 | 클레임 | 산출 위치 | 현재 상태 |
|---|---|---|---|
| abstract / intro / §V.2 | R(d) median = 14.4, "approximately 17×" | `data/pilot_v1.1/stats/exp1_per_example.json` | 구 panel (claude-sonnet-4.5 within) 산출. 현재 데이터 (gpt-5 within)로는 R≈3-4. claude-sonnet-4-6 subscription 재실행 중. |
| §V.4 / §V.5 | weighted-R1 settlement loss diff = -0.132 [-0.164, -0.101] | `data/pilot_v1.1/stats/exp2_aggregate.json` | v1.3 12-judge panel 기준. 그대로 유효. |
| §VI #4 | anchor specifiability boundary | `human_annotation/recruitment/r17_v2_5_rater_analysis.md` | Stage 1 closure, n=5 rater. |

paper의 number 수정 전 — 반드시 (a) 어느 stats 파일에서 산출됐는지 `grep`, (b) 산출 path 재실행 시 같은 number 나오는지 확인.

---

## 4. 자주 하는 실수 (avoid)

- ❌ `exp1_analyze.py` 무지성 실행 → 기존 `exp1_per_example.json` overwrite. 이 스크립트는 v1.0 시절 const (`FAMILIES = ["claude", "gpt", "gemini"]`)가 박혀있어 현재 v1.3 panel과 미스매치.
- ❌ paper의 number 직접 수정 → 데이터 산출과 desync.
- ❌ subscription-first 약속 어기고 OpenAI/Anthropic API 직접 호출 → 비용 폭발 (Phase A+B 사례: $67 over $5 estimate).
- ❌ public push 시 `reference*/` PDF 포함 → 저작권 위반.

---

## 5. 외부 review 사이클 (모든 non-trivial 변경)

`feedback_external_review_iterations.md` 메모리 규칙: 모든 non-trivial doc/code는 codex review **≥ 2-3 iter** 거쳐야 "done". paper-6은 7 사이클 (27 iter 누적) 수행한 사례. 현재 수정도 같은 discipline 적용.

---

## 6. 변경 이력 (이 문서 자체)

- 2026-05-10: 작성. paper TMLR 제출 + main run n=300 expansion 시점 baseline.
