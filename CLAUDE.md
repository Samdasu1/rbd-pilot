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

## 3.5. 장기 background 작업 health-check 규약

긴 background 작업 (≥ 30분 예상: dataset generation, projection batch, exp2 judge 등) 돌릴 때는 watcher 하나만 믿지 말고 **자체 10-30분 cadence로 health-check 능동 수행**. 이유: watcher (Bash run_in_background)는 max ~10분 timeout이라 1-3일 long-run을 끝까지 못 봄. 그리고 silent failure (subprocess.TimeoutExpired uncaught, 메모리 부족 OOM, network drop 등)는 watcher가 잡지 못 함 — 진짜 처음으로 알아채는 건 ledger/파일 카운트가 멈춘 시점.

**health-check 4점 체크리스트** (사용자 ping 들어올 때 항상 + 자발적으로 30분 주기):

```bash
# 1. process 살아있나
ps aux | grep <script_name> | grep -v grep | head -1
# 2. output 파일 수 증가하나
ls <output_dir>/ | grep <pattern> | wc -l
# 3. ledger 최근 entry 시간이 최근 N분 안인가
tail -3 <ledger.jsonl>
# 4. log에 traceback / error 있나
tail -50 <log_file> | grep -iE "error|traceback|timeout|fail"
```

발견되는 silent failure 패턴:
- **subprocess.TimeoutExpired 처리 안 됨**: 한 call이 timeout_s 초과 → uncaught → script 죽음. 모든 subprocess.run은 try/except로 감싸고 retry/skip 로직 필요.
- **ledger entry 시간 stale**: 30분간 새 entry 없으면 hang. process 살아있어도 의심해야 함.
- **log stdout buffered**: nohup으로 띄운 Python의 print는 buffered. 진짜 진행은 ledger.jsonl과 output 파일 mtime로 확인.

작업 시작 시 추정 시간 X 줬으면, X/4 또는 X/8 시점에 한 번씩 점검 (예: 20시간 추정이면 2.5시간 또는 5시간마다).



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
