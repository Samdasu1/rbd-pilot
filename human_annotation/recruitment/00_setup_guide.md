# Stage 1 Recruitment 셋업 가이드 (사용자용)

> 본인(작업 의뢰자)이 처음 Prolific을 셋업할 때 따라 할 step-by-step. 한 번 셋업하면 다음 batch는 30분.

---

## 0. 사전 준비 (5분)

- 결제 수단 (신용카드 또는 PayPal)
- Google 계정 (Form + Sheet — 답변 수집용)
- GitHub 계정 (Gist로 패키지 호스팅) — 선택, Google Drive view-only 도 OK

**예상 총 셋업 시간 (1차)**: 약 2.5–3시간. 다음 batch부터 30–60분.

---

## 1. Prolific researcher 계정 생성 (10분)

1. https://www.prolific.com → "Sign up" → "I want to use Prolific as a researcher"
2. 학교/회사 이메일 권장 (개인 이메일도 가능, 신원 확인 1–2일 더 걸릴 수 있음)
3. Workspace 생성 (이름 자유)
4. Payment method 등록 — 카드 또는 PayPal
5. **첫 잔액 충전 minimum: $50**. 한 번 넣으면 여러 study에 분할 사용 가능

---

## 2. 패키지 호스팅 (15분)

Annotator가 markdown 패키지를 볼 수 있어야 함. 옵션 3개:

| 옵션 | 무료 | 장점 | 단점 |
|---|---|---|---|
| **GitHub Gist (secret)** | ✅ | URL 모르면 접근 X, 검색엔진 X | GitHub 계정 필요 |
| Google Drive view-only | ✅ | 익숙함 | "공유받은 모든 사람"이 검색 가능 (link-only로 설정 필수) |
| Notion 공개 페이지 | ✅ | 예쁘게 렌더링 | URL 노출 주의 |

**권장: GitHub Gist (secret)**.

작업:
1. `texts/` 폴더의 markdown 파일 각각을 secret gist로 업로드 (gist.github.com → "Create secret gist")
2. URL 정리해서 본인 보관 (예: `https://gist.github.com/{user}/{hash}`)
3. annotator는 이 URL로 접근

---

## 3. Google Form 만들기 (1시간)

`03_form_template.md` 의 구조대로 form 작성.

대략 4 section:

- Section 1 — Intro + 동의 (NDA-like checkbox)
- Section 2 — Calibration screening (2 example, `02_screening_task.md` 참조). 통과 못하면 마지막 thank-you 페이지로 redirect
- Section 3 — Main rating loop (한 rating = 한 page 권장)
- Section 4 — Completion code 표시 ("이 코드를 Prolific에 입력하세요")

**필수 설정**:
- "응답 자동으로 Sheet에 저장" 활성화
- "이메일 수집" 비활성화 (annotator 익명성 유지)
- "응답 수정 허용" 비활성화 (제출 후 수정 X)

---

## 4. Prolific Study 생성 (30분)

`01_prolific_job.md` 의 텍스트 거의 그대로 복붙.

### 4.1 Study 기본 정보

| Field | 값 (1차 batch — R1.7만) |
|---|---|
| Title | "Score AI agent paper-review outputs on a citation-quality rubric" |
| Description | `01_prolific_job.md` Description 섹션 복붙 |
| External study URL | (위에서 만든 Google Form URL) |
| Estimated completion time | 90 minutes |
| Reward | $15 (= ~$10/h) |
| N participants | **5** |

### 4.2 Pre-screen filter (Prolific UI에서 설정)

| Filter | 값 |
|---|---|
| First language | English |
| Highest education | Master's degree or higher |
| Approval rate | ≥ 95% |
| Studies completed | ≥ 50 |
| Subject area (선택) | Computer Science / AI / Data Science |
| Country (선택) | US, UK, CA, AU 권장 (영어 native 풀) |

**중요**: filter가 너무 좁으면 annotator pool이 작아서 study가 늦어짐. 위 조합으로 보통 24–48h 내 완료.

### 4.3 Completion code mechanism

- Prolific에서 random completion code 생성 (예: `C1A2B3D4`)
- 이 코드를 Google Form 마지막 페이지에 표시
- Annotator가 코드를 Prolific submit 페이지에 입력 → 우리가 Prolific에서 approve 누르면 결제

### 4.4 Per-participant cost 계산

| 항목 | 금액 |
|---|---|
| 1인 reward | $15 |
| Prolific service fee (33%) | $5 |
| 1인 합 | $20 |
| **5명 합** | **$100** |

→ **$1000 budget 안에서 1차 batch 안전**.

---

## 5. Study 게시

1. "Submit for review" → Prolific 자체 review (보통 12–24h)
2. Approved되면 자동 게시
3. Annotator pool에 task 노출. 보통 24–48h 내 5명 완료

**중간에 무엇이라도 잘못된 것 같으면**: study 일시 중지 가능 (이미 시작한 사람은 끝까지 진행).

---

## 6. 답변 수집 (24–48h)

- Google Sheet에 자동 누적
- Prolific submission 검토 — completion code 입력자만 표시됨
- 각 submission: approve / reject / partial-payment 선택
  - **Approve**: 정상 답변. 결제 진행
  - **Reject**: spam, calibration 통과 못함, blank 등. 결제 X
  - **Partial payment**: 일부는 했지만 미흡. 일부 결제

**Reject 정책 (사전 안내 필수)**:
- Calibration 점수 정답 ±1 벗어남 → reject
- Rationale 12자 미만 또는 generic ("good job" 등) → partial / reject
- 답변 시간이 제시 시간의 30% 미만 → spam 의심, reject

---

## 7. 분석으로 넘김

이 batch 끝나면:
- Sheet export → CSV
- 다음 세션에서 Krippendorff α 계산 (외부 5명 + author + 3 LLM judges 조합별)
- Spearman per dim — human vs LLM
- 결과 따라 R1.7 dim의 운명 결정 (살림 / split / paper에서 빼기)

---

## 8. 다음 batch 진행 (R1.1 + R1.3, 선택)

1차 R1.7 process 검증되면 같은 셋업으로 R1.1 + R1.3 batch 진행. 같은 annotator pool 재사용하려면 Prolific의 "custom whitelist" 기능 활용 (1차 통과자만 2차 초대).

추가 비용 ~$200–250 (R1.1 + R1.3 합쳐서, 5명, ~3h × $10/h × 5 + fee).

---

## 9. 예상 총 비용 정리 (Stage 1만)

| Batch | 내용 | n | 비용 |
|---|---|---|---|
| 1차 | R1.7 18 ratings | 5 | $100 |
| 2차 (선택) | R1.1 + R1.3 합산 ~30 ratings | 5 | $200 |
| 예비 (재시작 등) | — | — | $50 |
| **Stage 1 총** | | | **$200–350** |

→ Budget $1000에서 Stage 1 최대 $350. 잔액 $650으로 Stage 2 + Exp 2 main run.

---

## 10. 셋업하면서 막히면

- Prolific researcher help: https://researcher-help.prolific.com
- Google Form auto-Sheet 연동 안 됨 → Form 우상단 "Responses" 탭 → Sheet 아이콘 클릭
- Gist 텍스트 너무 길어서 안 올라감 → 잘라서 여러 gist로
- Calibration filter가 너무 빡빡하다 싶으면 → 정답 ±1.5로 완화
