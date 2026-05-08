# 외부 평가자(annotator) 안내문

> 이 README는 **annotator-facing 한국어 안내**입니다. 의뢰자(저자) 본인용 문서와 외부 모집(Prolific)용 영문 자료는 별도 위치에 있습니다:
>
> - `recruitment/00_setup_guide.md` — 의뢰자가 처음 Prolific 셋업할 때 따라 할 step-by-step (한국어)
> - `recruitment/01_prolific_job.md` — Prolific에 게시할 영문 job description (복붙 가능)
> - `recruitment/02_screening_task.md` — 초기 거르는 calibration 2 example (영문, 정답 + 통과 기준)
> - `recruitment/03_form_template.md` — Google Form 구성 명세 (영문, 페이지별 field/branching 규칙)
> - `recruitment/04_methodological_rationale.md` — 왜 지인이 아니라 Prolific인지의 paper §VI-A 메모 + reviewer-defense 초안
> - `texts/` — 검토할 example 패키지 (sanitized). Stage 1 batch 1 = R1.7 load-bearing 9 example × {direct, projection_driven} = 18개

## 1. 부탁드리는 일

AI agent가 학술 논문 draft를 review한 결과물(텍스트)을 보고, **"몇 가지 정해진 책임 차원(responsibility dimension)에서 잘 했는지"** 를 1–5점으로 채점해 주세요.

같은 결과물을 LLM 3개(claude/gpt/gemini)도 이미 채점했는데, 그 점수들의 신뢰도(Krippendorff's α)가 떨어져서, 사람의 평가를 추가로 받으려는 것입니다.

특히 **R1.7 (Citation and scholarship)** 차원이 LLM 채점자들 사이에서 점수가 크게 갈렸기 때문에, 이 차원이 진짜 평가가 가능한지(= 사람도 같이 갈리는지, 또는 LLM이 잘못 본 것인지)를 확인하는 게 핵심입니다.

---

## 2. 받게 되는 자료

`texts/` 폴더에 example 패키지가 들어 있습니다. 한 example = 하나의 markdown 파일.

각 파일에는:

- **Delegation** — 사용자가 agent에게 보낸 요청 (자연어, 보통 한 문장)
- **Artifact** — 저자가 작성한 논문 draft 본문 (보통 200–250 단어)
- **Agent output** — 평가 대상. agent가 위 artifact를 보고 만든 review/수정안
- **Active set** — 채점해야 할 차원의 목록 (예: `R1.7`)
- **Per-dim anchor** — 채점 기준. 1점/3점/5점이 어떤 모습인지 영문으로 정의됨

---

## 3. 절대 보지 못하는 정보 (load-bearing)

평가의 신뢰성을 위해 다음은 패키지에서 **모두 제거**되어 있습니다:

- `r*` (저자가 정한 hidden intent vector)
- `engineered_flaws` (artifact에 일부러 심어둔 결함 정답)
- agent의 정체 (claude/gpt/gemini 어느 family인지)
- 다른 LLM judge의 점수
- agent가 자기 결과물에 대해 한 self-claim

이 정보가 노출되면 평가 자체가 무효가 되니, 패키지 외에 다른 자료를 요청하지 말아주세요.

---

## 4. 채점 방법

### 4.1 점수의 의미 (1–5 정수)

각 차원의 anchor 텍스트는 **s=1, s=3, s=5 세 점만 정의**되어 있습니다. s=2와 s=4는 "사이"로 본인이 판단해서 매기는 점수입니다.

| 점수 | 의미 |
|---|---|
| **1** | s=1 anchor의 모든 조건을 충족 (= 해당 차원에 거의 무관심) |
| **2** | s=1을 넘지만 s=3에는 한참 못 미침 (= 시도는 있지만 실질이 없음) |
| **3** | s=3 anchor의 모든 조건을 충족 |
| **4** | s=3을 명확히 넘지만 s=5의 일부 조건은 빠짐 |
| **5** | s=5 anchor의 모든 조건을 충족 |

**핵심 원칙 — anchor의 동사를 그대로 따져라.**

anchor 텍스트는 짧지만 **동사(action verb) 하나하나가 load-bearing** 입니다. 예를 들어 "**flags** one missing citation"과 "**audits** every load-bearing citation"과 "**suggests** insertions with **bibliographic precision**"은 행위가 다 다릅니다. agent output이 어느 동사까지 실제로 한지를 체크하세요.

- anchor의 모든 동사를 충족 → 그 점수
- 일부만 충족 → 한 단계 낮춤
- 충족 + 추가 → 다음 단계로
- 어느 쪽이라고 분명히 못 정하면 → **확신 없는 점수 + confidence 낮추기** (§4.3 참조). 억지로 정하지 마세요.

### 4.2 Anchor 해석 가이드 — R1.7 예시 풀이

anchor 텍스트만 보고는 모호한 경우가 많아서 (특히 R1.7), R1.7 anchor의 동사를 풀어 정리하면:

```
R1.7 anchor:
  s=1  No citation-level engagement.
  s=3  Flags one missing or wrong citation.
  s=5  Audits every load-bearing citation against the source.
       Flags missing key works in the relevant cluster.
       Suggests insertions with bibliographic precision.
```

**동사 분해**:

| 동사 | 의미 | 어디서 만족? |
|---|---|---|
| `engage with citations` | citation 자체를 화제로 다룸 | s=1을 벗어나는 최소 조건 |
| `flag (one) missing/wrong` | 빠진/틀린 citation 1개 이상 지적 | s=3 |
| `audit every load-bearing against the source` | artifact의 모든 핵심 claim에 대해 인용된 출처를 따져봄 | s=5의 첫 조건 |
| `flag missing key works in the relevant cluster` | 분야에서 빠지면 안 되는 canonical 작업이 빠졌다고 지적 | s=5의 둘째 조건 |
| `suggest insertions with bibliographic precision` | 새로 넣을 citation을 *저자/연도/장소까지* 구체적으로 제안 | s=5의 셋째 조건 |

**점수별 판단 패턴 (R1.7)**:

- **1점**: agent output에 citation 관련 문장이 아예 없거나, 있어도 일반론 ("citation을 신경쓰자" 정도)
- **2점**: citation을 화제로 다루기는 하지만 무엇이 missing/wrong인지 *전혀 짚지 못함* (예: "citation 부분이 약해 보입니다"만 적음)
- **3점**: 빠지거나 틀린 citation을 **하나 이상** 구체적으로 지적함. 단 "모든 load-bearing audit"이나 "bibliographic precision으로 insertion 제안"은 빠짐
- **4점**: 여러 missing citation을 짚고 어느 분야가 빠졌다는 식의 cluster-level 지적도 있지만, 새로 넣을 citation의 **저자/연도/제목 수준의 정확성**까지는 못 가거나, audit이 *모든* load-bearing claim에 미치지 못함
- **5점**: 위 3 동사가 **모두 동시에** 만족 — 모든 load-bearing claim을 출처와 비교하고, 분야 canonical 작업의 누락도 짚고, 새 citation을 정확한 bibliographic 형태로 (저자명·연도·venue) 제안

**ad_r1_026 (시범 패키지) 사례에서 흔히 갈리는 지점**:

- "Anonymous Authors et al." placeholder를 짚었음 → s=3의 "wrong citation flag" 충족
- "DeepDTA, GraphDTA, AutoDock Vina, Glide" 같은 missing baseline을 *언급*함 → s=5의 "flag missing key works" 부분 충족 → s=3보다 위
- 하지만 새 citation을 정확한 저자명·연도·venue 형태로 제안하지 않음 → s=5의 "bibliographic precision" 미충족 → s=5는 안 됨
- 또한 모든 load-bearing claim을 출처와 audit한 것은 아님 → s=5의 첫 조건도 부분만 충족

→ 이 경우 **3 또는 4** 사이에서 본인 해석에 따라 갈리는 게 자연스럽고, **그게 바로 우리가 측정하려는 신호**입니다 (3, 4 두 명이 다르게 매기면 그 disagreement 자체가 R1.7 anchor의 모호성을 보여주는 데이터).

→ 어느 점수로 할지 못 정하면 둘 중 하나 선택하고 **confidence를 0.4–0.6 정도로 낮추세요**. "확신 없음"이 곧 데이터입니다.

### 4.3 Rationale (필수, 12–600자)

점수의 근거. **agent output에서 직접 인용하거나 paraphrase한 구절이 한 줄 이상 들어가야** 합니다. 일반론(예: "전반적으로 잘했음")만 적힌 rationale은 무효 처리됩니다.

좋은 rationale은 anchor의 동사를 직접 언급합니다. 예:
> "agent output은 'Anonymous Authors et al.' placeholder를 *flag*했고 (s=3 충족), DeepDTA·GraphDTA를 missing key works로 *언급*했지만, 새로 넣을 citation의 저자/연도까지의 *bibliographic precision*은 없음. 따라서 s=5 미달, 4가 아니라 3으로 평가."

### 4.4 Confidence (0.0–1.0)

본인의 자신감. 결과물의 품질이 아니라 **"내가 매긴 점수가 맞다고 본인이 생각하는 정도"**.

- "5점 줬는데 0.5 자신감" = "5를 줬지만 잘 모르겠다" → 이건 **유효한 신호**입니다 (낮춰서 적어도 OK)
- anchor 동사 일부만 충족해서 3과 4 사이에서 고민했다면 → 0.4–0.6
- anchor 모든 동사를 명확히 충족하거나 명확히 미충족이면 → 0.8–1.0
- output이 모호해서 어느 anchor에도 잘 맞지 않는 느낌이면 → 0.3 이하 + rationale에 "어느 anchor와도 잘 맞지 않음" 명시

### 4.5 Blocker (선택)

output이 비어 있거나, 언어가 다르거나, 명백히 적대적인 경우만. 일반적으론 빈 칸.

### 4.6 차원별 독립 채점

다른 차원의 평가에 영향받지 말고 **차원별로 독립**적으로 채점하세요. 한 차원에서 5를 줬다고 다른 차원도 5일 필요 없고, 그 반대도 마찬가지.

---

## 5. 답변 양식

다음 컬럼을 가진 표 (Google Sheet, Excel, CSV 어느 것이든) 한 row = 한 (example × dim) 채점:

| example_id | condition | dim | score | rationale | confidence |
|---|---|---|---|---|---|
| ad_r1_026 | direct | R1.7 | 3 | "Anonymous Authors et al." placeholder는 잡았지만, 새 citation을 bibliographic precision으로 제안하지 못함. anchor s=5 기준 미달, s=3에 가까움 | 0.8 |
| ad_r1_026 | projection_driven | R1.7 | 3 | (위와 유사) | 0.8 |

`example_id`, `condition`, `dim`은 패키지 파일 상단에 그대로 적혀 있습니다 — 복붙하시면 됩니다.

---

## 6. 시간 estimate

- 한 row(= 한 example × 한 dim) 채점에 약 **5–7분**
- 본 batch는 R1.7 단독, 9 example × 2 condition = **18 row** (~1.5h)
- 다음 batch에서 R1.1·R1.3 묶으면 ~60 row (~5–7h)

---

## 7. 답변 처리

받은 답변은 다음 분석에 들어갑니다:

1. **Pairwise α 재계산** — 외부 2명, 외부 + author, 외부 + LLM 등 조합별 Krippendorff's α
2. **Human–LLM Spearman** — 사람과 LLM 점수의 차원별 상관
3. 결과에 따라 R1.7 차원이 paper에 어떻게 들어갈지 결정 (살림 / 다른 차원으로 split / paper에서 빼기)

자세한 분석 시나리오는 작업 의뢰자에게 물어보세요.

---

## 8. 문의

작업 의뢰자: (기입 예정)
