# CLAUDE.md — paper-6 Claude 운영 가이드

> Claude Code / Anthropic SDK 통해 본 디렉토리에서 호출된 Claude 인스턴스용. **본 파일 직전 또는 직후 `AGENTS.md` 반드시 로드** (충돌 시 AGENTS.md 우선).

## 본 문서의 역할 — session 재시작 회피

대화 세션을 끝내고 새 세션으로 다시 시작하는 것은 비효율적이다 — 사용자가 같은 prompt를 반복 입력하고, 모델은 cold-start로 컨텍스트를 재학습해야 한다. 그 대신 본 문서 + `AGENTS.md`가 매 turn system context로 자동 로드되도록 둔다. **자동 압축(compaction) 후에도 본 문서들은 보존**되므로, 새 prompt로 같은 정보를 반복하는 것보다 token 사용량이 적다. 따라서 사용자가 paper-6 작업 중 컨텍스트가 길어져도 (a) 새 세션 열 필요 없고, (b) 압축이 일어나도 critical invariant 잃지 않는다.

---

## 0. 매 호출 직전 자가 확인

1. `AGENTS.md` §1 critical invariants 5개 (R-PAPER / R-DATA / R-PANEL / R-SUBSCRIPTION / R-LICENSE) 인지했나?
2. 작업이 paper number 수정인가? → AGENTS.md §3 일관성 표 먼저 확인
3. 작업이 stats 파일 write인가? → 기존 파일 백업 (`cp data/pilot_v1.1/stats/{file} _backup_$(date +%Y%m%d).json`)
4. 작업이 LLM 호출인가? → subscription 경로 (`claude --model ...` 또는 `codex exec`) 우선

---

## 1. 사용자 톤 (R-06 conformance, paper-6 specific)

- **카카오톡 톤**: "~거든", "~네", "~인 것 같아"
- **직설적**. 사용자 지적 사항 윤색 금지 (원문 톤 보존)
- **메타 추론 선호**: 결론보다 reasoning pattern 자체에 가치
- **table 좋아함**: 비교/옵션 제시는 \| | column | format | 으로
- **응답 길이**: 단답이 가능하면 단답. 5-7줄 넘어가면 헤더로 구획. 100줄 넘으면 사용자가 짜증 냄.

---

## 2. paper-6 작업 시 자주 쓰는 패턴

### LaTeX recompile
```
cd "/home/treu46/paper/6. agent/paper"
pdflatex -interaction=nonstopmode main.tex > /tmp/c1.log 2>&1
bibtex main > /tmp/b.log 2>&1
pdflatex -interaction=nonstopmode main.tex > /tmp/c2.log 2>&1
pdflatex -interaction=nonstopmode main.tex > /tmp/c3.log 2>&1
pdfinfo main.pdf | grep -E "Pages|File size"
grep -c "Overfull" /tmp/c3.log    # 반드시 0이어야 submission-ready
```

### projection / judge 실행 (subscription-first)
```
# wait_5h 켜고 시작 (codex throttle 시 5h 대기, API fallback 회피)
CODEX_QUOTA_STRATEGY=wait_5h \
  ~/research-harness/.venv/bin/python scripts/exp1_projection.py --mode both --ids ...
```

### data 수정 후 paper 동기화
```
1. analysis 재실행 → stats 파일 update
2. paper §V의 number grep + 수정
3. recompile + 0 overfull 확인
4. _submission/ 동기화 (main.pdf + source-bundle.tar.gz)
5. git commit + push (단, public-safe 검증)
```

---

## 3. Python 환경

- system python3 (`/usr/bin/python3`): yaml, json만 — 빠른 분석용
- **venv** (`~/research-harness/.venv/bin/python`): paper-6 scripts 돌릴 때 — openai/anthropic/google.genai/xai_sdk/dotenv 다 있음
- venv는 paper-6에 자체 venv가 없어서 harness venv를 공유 중 (의도적)

---

## 4. 외부 review iter 규칙

`feedback_external_review_iterations.md` 메모리: 모든 non-trivial 변경은 codex review **≥ 2-3 iter**. 작은 변경(typo / wording fix)은 1 iter OK. paper §V number / 데이터 산출 / dataset spec 변경은 minimum 2 iter.

---

## 5. 자주 하는 실수 (avoid)

- ❌ `exp1_analyze.py` 무지성 실행 — v1.0 panel const 박혀있음. 실행 전 FAMILIES, WITHIN_MODEL 확인.
- ❌ paper number 즉시 수정 — 산출 path 추적 후. AGENTS.md §3 표 참조.
- ❌ smoke 없이 batch 250+ 실행 — quality drift 못 잡음.
- ❌ subscription throttle 무시하고 API 자동 fallback — Phase A+B에서 \$67 cost over 학습.

---

## 6. 응답 끝맺음

- 다음 결정이 필요하면 **옵션 표 + 추천 + 1-line 질문** 으로 마무리
- 백그라운드 task 돌리면 PID + 예상 시간 명시
- "다 됐어" 같은 일반적 확인 외에는 raw output dump 금지 (사용자가 직접 grep 안 해도 되게)

---

## 7. 변경 이력

- 2026-05-10: 작성. AGENTS.md와 동시 baseline.
