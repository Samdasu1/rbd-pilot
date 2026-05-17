# Defense Memo: Responsibility Projection Paper

## 0. 목적

이 문서는 현재 제출한 기존 논문에 대해, review 의견을 받기 전에 미리 준비해야 할 **defense 방향**을 정리한 문서다.

특히 핵심 쟁점은 다음이다.

> Responsibility projection은 측정 가능하지만, projection vector를 executor prompt에 직접 주입했을 때 일부 차원에서 성능이 악화되었다.  
> 이 결과를 어떻게 논문의 약점이 아니라, 논문의 중요한 발견으로 방어할 것인가?

이 문서는 review response, rebuttal, discussion 보강, limitation 보강, 추가 ablation 설계에 바로 사용할 수 있도록 작성한다.

**사용 정책**: 본 문서는 예상 리뷰 의견 기반 defense 초안이다. paper-6 v1.4의 manuscript는 현 시점에서 *수정하지 않는다*. 실제 reviewer comment가 도착했을 때 본 문서의 해당 attack 항목 (Attack 1~5 또는 Q&A Q1~Q5)을 바로 활용해 rebuttal 작성. v1.5 framing 보강이 정식 결정되면 §14 checklist를 살릴 것.

---

## 1. 가장 중요한 defense frame

### 핵심 방어 문장

> Our result should not be read as a failure of responsibility projection itself. Rather, it shows that responsibility projection and execution guidance are different operations: a projection can be measurable and diagnostically useful even when naive prompt-level injection harms execution.

한국어:

> 이 결과는 responsibility projection 자체가 실패했다는 뜻이 아니다.  
> 오히려 projection을 측정하는 것과, 그 projection을 executor prompt에 직접 넣어 실행 지시로 사용하는 것은 서로 다른 문제라는 점을 보여준다.

즉, 논문의 방어 방향은 다음과 같다.

```text
나쁜 defense:
projection을 넣었는데 성능이 떨어졌지만 그래도 의미 있다.

좋은 defense:
projection은 측정 가능한 diagnostic object이고,
그것을 naive execution instruction으로 쓰는 것이 별도의 실패 모드임을 발견했다.
```

---

## 2. Reviewer가 공격할 가능성이 큰 지점

### Attack 1. Projection을 넣었는데 성능이 나빠졌다면, 방법이 실패한 것 아닌가?

예상 reviewer comment:

> If injecting the responsibility projection into the executor prompt degrades performance, why is responsibility projection useful?

대응 방향:

> The paper does not claim that naive projection injection is the correct use of projection. The key contribution is to show that responsibility projection can be measured and that model families disagree systematically beyond stochastic variance. The negative injection result is an empirical warning: explicit responsibility guidance does not automatically translate into better execution.

강조할 점:

- projection의 목적은 첫째로 **measurement / diagnosis**임.
- execution improvement는 별도의 downstream use case임.
- projection injection condition은 proposed deployment가 아니라 **stress test / probing condition**에 가깝다.
- 결과가 나빴기 때문에 오히려 "projection ≠ instruction"이라는 중요한 결론이 나옴.

---

### Attack 2. Projection이 틀려서 executor가 나빠진 것 아닌가?

예상 reviewer comment:

> The degradation may simply be caused by inaccurate projected responsibilities.

대응 방향:

맞는 지적이다. 다만 이 경우에도 논문 주장은 유지된다.

가능한 답변:

> We agree that projection error may contribute to degradation. This is why we avoid claiming that projection injection is an execution-improving intervention. Instead, our analysis separates the measurability of projection from the downstream use of projection. Projection error, attention dilution, and resource mismatch are all plausible mechanisms, and identifying them is an important implication of our findings.

추가로 논문에 넣으면 좋은 문장:

> A poor projection can misdirect execution, whereas even a correct projection may still overload the prompt or shift the model toward surface-level compliance. Our results therefore motivate treating projected responsibility as a diagnostic signal rather than a direct instruction.

---

### Attack 3. 그냥 prompt가 길어져서 성능이 떨어진 것 아닌가?

예상 reviewer comment:

> The projection condition may degrade because it consumes context/output budget or distracts the model.

대응 방향:

이 공격은 오히려 방어에 유리하다.

답변 방향:

> This is precisely one of the failure modes we aim to surface. Responsibility information is not free. Adding explicit responsibility guidance can consume attention, shift priorities, or displace task-specific reasoning. Thus, our result cautions against assuming that more explicit instruction always improves execution.

추가 실험 가능:

```text
A. direct prompt
B. projection injection prompt
C. length-matched control prompt
D. compressed projection prompt
E. top-1 / top-2 responsibility only
```

이 실험을 지금 당장 못 하더라도 limitation/future work에 넣을 수 있음.

---

### Attack 4. R1.4 / R1.7에서만 나빠졌다면, taxonomy가 불균형한 것 아닌가?

예상 reviewer comment:

> The taxonomy may overemphasize difficult scholarly dimensions such as novelty and citation audit.

대응 방향:

> The concentration of degradation in R1.4 and R1.7 is not a taxonomy flaw; it is theoretically informative. These dimensions require deep specialty engagement, external comparison, or citation verification, which are unlikely to be solved by prompt-level responsibility reminders alone.

핵심 방어:

- R1.6 writing polish 같은 표면적 차원은 prompt guidance로 개선될 수 있음.
- R1.4 novelty mapping, R1.7 citation audit은 단순 prompt guidance보다 외부 비교 corpus, retrieval, citation verification이 필요함.
- 따라서 dimension별 실패 양상은 taxonomy가 무의미하다는 증거가 아니라, taxonomy가 차이를 포착한다는 증거임.

---

### Attack 5. LLM judge가 평가했기 때문에 결과를 믿기 어렵지 않은가?

예상 reviewer comment:

> The settlement scores rely on LLM judges, which may be biased or inconsistent.

대응 방향:

> We do not rely on a single judge. The paper uses a cross-family judge panel and compares effects against within-family stochastic variance. The key claim is not an absolute score but a relative and structured pattern: cross-family projection mismatch exceeds stochastic variance, and injection-related losses concentrate in specific responsibility dimensions.

추가 방어 포인트:

- absolute score보다 **relative difference**가 중요함.
- within-family variance를 noise floor로 둔 점을 강조.
- 가능하면 Krippendorff's alpha / agreement / bootstrap CI 추가.
- judge family별 결과가 동일한 방향인지 robustness table 추가.

---

## 3. 논문 본문에서 보강해야 할 framing

### 3.1 Introduction 보강

기존 intro가 "projection을 잘하면 execution도 좋아질 것"처럼 읽히면 위험하다.  
다음 framing을 추가하는 것이 좋다.

추가 문장 후보:

> Responsibility projection is not assumed to be an execution policy. We treat it first as a measurable diagnostic object: a way to characterize how models infer the obligations implied by a delegation before any answer is produced.

한국어 의미:

> responsibility projection은 곧바로 실행 정책이라고 가정하지 않는다.  
> 먼저 delegation 안에 내포된 책임을 모델이 어떻게 해석하는지 측정하는 diagnostic object로 본다.

---

### 3.2 Contribution 보강

기존 contribution이 "projection injection improves performance"처럼 읽히면 안 된다.

안 좋은 기여 문장:

```text
We improve execution by injecting responsibility projections.
```

좋은 기여 문장:

```text
We show that responsibility projections are measurable, systematically model-dependent, and not safely reducible to direct execution instructions.
```

또는:

```text
We identify a failure mode in which explicit responsibility guidance can degrade execution, especially for deep specialty dimensions such as novelty mapping and citation audit.
```

---

### 3.3 Discussion 보강

Discussion에서 반드시 들어가야 할 메시지:

> The negative injection result is not a contradiction but a separation result.

즉:

```text
projection as measurement ≠ projection as instruction
```

문장 후보:

> The fact that projection injection does not consistently improve execution suggests a separation between responsibility recognition and responsibility fulfillment. Models may recognize that a task requires citation audit or novelty assessment without being able to fulfill that responsibility under the given prompt, context, or resource constraints.

한국어 의미:

> 모델은 어떤 책임이 필요한지 인식할 수 있지만, 그 책임을 실제로 수행할 능력이나 자원이 부족할 수 있다.

이게 매우 중요함.

---

## 4. 기존 논문의 가장 강한 defense 구조

논문을 다음 3단 구조로 방어하는 것이 좋다.

### Step 1. Responsibility recognition is measurable

자연어 delegation에는 실행 전 책임 해석 문제가 존재한다.

```text
delegation → projected responsibility vector
```

이 projection은 closed taxonomy 위에서 측정 가능하다.

---

### Step 2. Responsibility recognition is model-dependent

모델 family마다 projection이 다르고, 이 차이는 단순 stochastic variance보다 크다.

즉:

```text
cross-family mismatch > within-family stochastic variance
```

이것이 paper의 핵심 empirical finding이다.

---

### Step 3. Responsibility recognition does not automatically improve responsibility fulfillment

projection을 prompt에 직접 넣는다고 execution이 자동으로 좋아지지 않는다.

특히:

```text
R1.4 novelty mapping
R1.7 citation audit
```

같은 deep specialty dimension에서 손실이 집중된다.

따라서 결론:

> Models can recognize responsibility structure without reliably converting it into better execution.

이 문장이 논문을 지키는 핵심이다.

---

## 5. "왜 이게 중요한가?"에 대한 답

Reviewer가 다음처럼 물을 수 있다.

> If injection does not improve performance, why should we care?

답변:

> Because many real-world LLM agent systems implicitly assume that making instructions more explicit will make agents more responsible. Our results challenge this assumption. They show that responsibility must be measured separately from execution and that explicit responsibility guidance can introduce its own failure modes.

한국어:

> 실제 LLM agent 시스템은 보통 instruction을 더 명확히 하면 agent가 더 책임 있게 행동할 것이라고 가정한다.  
> 본 논문은 그 가정이 항상 맞지 않음을 보여준다.

이게 핵심 가치다.

---

## 6. 추가로 하면 좋은 최소 ablation

Review 전에 시간이 있다면, 아래 중 일부만 추가해도 defense가 강해진다.

### 6.1 Token-matched projection control

목적:

> projection injection의 성능 저하가 단순히 prompt 길이 증가 때문인지 확인.

조건:

```text
C0 direct
C1 projection injection
C2 length-matched irrelevant control
C3 length-matched generic checklist
```

해석:

- C1만 나쁘면 projection-specific distraction 가능성.
- C2/C3도 나쁘면 prompt length / attention dilution 가능성.
- 둘 다 논문에는 유리함. 왜냐하면 responsibility information is not free라는 주장이 강화됨.

---

### 6.2 Oracle projection vs model projection

목적:

> projection이 틀려서 망한 것인지, projection guidance 자체가 어려운 것인지 분리.

조건:

```text
C0 direct
C1 model-generated projection injection
C2 human/oracle projection injection
```

해석:

- C2는 좋아지고 C1만 나쁘면 projection quality 문제.
- C2도 나쁘면 injection mechanism 문제.
- 둘 다 중요한 finding.

---

### 6.3 Top-k projection injection

목적:

> full vector가 attention을 분산시키는지 확인.

조건:

```text
C0 direct
C1 full projection vector
C2 top-1 responsibility only
C3 top-2 responsibilities only
```

해석:

- full만 나쁘고 top-k가 나으면 over-specification / attention dilution.
- top-k도 나쁘면 responsibility guidance 자체가 execution mode를 방해할 가능성.

---

### 6.4 Hidden checklist condition

목적:

> surface compliance 문제 확인.

조건:

```text
C0 direct
C1 explicit responsibility labels in final answer
C2 hidden internal checklist, labels not allowed in final answer
```

해석:

- C1만 나쁘면 모델이 rubric wording을 따라가며 표면적 compliance를 한 것일 수 있음.
- C2가 좋으면 responsibility guidance를 output surface가 아니라 internal control로 써야 함.

---

### 6.5 Resource-mismatch probe

목적:

> R1.4/R1.7이 prompt instruction이 아니라 외부 자원이 필요한 dimension인지 확인.

조건:

```text
C0 direct
C1 projection injection
C2 projection + extra reasoning token
C3 projection + retrieval
C4 projection + comparator corpus
C5 projection + citation verification
```

해석:

- R1.4가 comparator corpus에서만 회복되면 novelty mapping은 prompt 문제가 아니라 comparison-resource 문제.
- R1.7이 citation verification에서만 회복되면 citation audit은 token 문제가 아니라 verification-resource 문제.

이 실험은 후속 논문으로 넘겨도 되지만, limitation에 넣으면 defense가 강해짐.

---

## 7. Review response용 Q&A 초안

### Q1. Why did projection injection hurt performance?

답변 초안:

> We view this as an important empirical finding rather than a failure of the projection framework. Projection injection tests whether recognizing responsibility structure can be directly converted into better execution through prompting. Our results suggest that this conversion is non-trivial. Explicit responsibility guidance may introduce attention dilution, token displacement, surface compliance, or resource mismatch, especially for dimensions requiring deep scholarly engagement.

---

### Q2. Does this mean responsibility projection is useless?

답변 초안:

> No. The projection remains useful as a diagnostic and measurement construct. It reveals how different model families infer the obligations implied by the same delegation and shows systematic mismatch beyond stochastic variance. What our results caution against is a naive use of projection as an executor instruction.

---

### Q3. Is the negative result caused by bad projection quality?

답변 초안:

> Projection quality may be one contributing factor, and we discuss this as a limitation. However, even this interpretation supports the need to separate responsibility recognition from responsibility fulfillment. A projected responsibility vector should not be assumed to be safe or beneficial when directly injected into an execution prompt.

---

### Q4. Why not simply remove the projection injection experiment?

답변 초안:

> The injection experiment is necessary because it tests a natural but flawed assumption: that making responsibility explicit should improve execution. The negative result is central to the paper because it shows that responsibility awareness is not equivalent to responsibility fulfillment.

---

### Q5. Are R1.4 and R1.7 failures just due to task difficulty?

답변 초안:

> Difficulty is likely part of the story, but the structured concentration of losses in novelty mapping and citation audit is meaningful. These dimensions differ from writing polish or structural reorganization because they often require external comparison, citation verification, or domain expertise. This supports the paper's broader conclusion that responsibility dimensions differ not only in difficulty but also in the kind of support required for fulfillment.

---

## 8. 논문에 추가하면 좋은 "separation result" 문단

아래 문단은 Discussion 또는 Conclusion에 넣기 좋다.

```text
Our findings suggest a separation between responsibility recognition and responsibility fulfillment. A model may correctly infer that a task calls for novelty assessment, citation audit, or evidence alignment, yet fail to perform those responsibilities when the inferred structure is simply injected into the execution prompt. This separation matters for LLM agent design: responsibility should not be treated as a prompt label that automatically improves behavior. Instead, responsibility projection should first be understood as a diagnostic signal whose downstream use requires additional mechanisms, resources, or verification.
```

한국어 의미:

```text
본 연구는 responsibility recognition과 responsibility fulfillment 사이의 분리를 보여준다. 모델은 어떤 task가 novelty assessment, citation audit, evidence alignment를 요구한다는 점을 인식할 수 있지만, 이 구조를 prompt에 직접 넣는다고 그 책임을 잘 수행하는 것은 아니다. 따라서 responsibility는 단순 prompt label이 아니라, 별도의 실행 메커니즘과 검증이 필요한 diagnostic signal로 다루어야 한다.
```

---

## 9. 논문에 추가하면 좋은 Limitation 문단

```text
This study does not identify a single causal mechanism behind the degradation observed under projection injection. Several mechanisms may contribute, including projection error, prompt-length effects, attention dilution, token displacement, surface-level compliance with responsibility labels, and resource mismatch for dimensions requiring external evidence or domain expertise. Our goal is therefore not to prescribe projection injection as a deployment strategy, but to show that responsibility projection is measurable and that naive conversion of projection into execution guidance can fail. Future work should isolate these mechanisms through token-matched controls, oracle projection conditions, compressed projection prompts, and resource-specific interventions.
```

---

## 10. 논문에 추가하면 좋은 Future Work 문단

```text
A natural next step is to investigate how projected responsibility should be used if not as a naive executor instruction. One possibility is to use projection as a diagnostic signal for deciding when to retrieve external evidence, request clarification, invoke citation verification, or route the task to a specialized reviewer. However, such uses require separate validation. Our results should therefore be read as motivating a broader design question: how can LLM agent systems convert responsibility recognition into responsibility fulfillment without inducing attention dilution or surface compliance?
```

---

## 11. Abstract 수정 방향

기존 abstract에 projection injection을 성능 개선처럼 암시하는 표현이 있다면 제거해야 한다.

### 피해야 할 표현

```text
We use responsibility projection to improve execution.
```

### 권장 표현

```text
We study whether responsibility structures implied by ambiguous delegations can be projected before execution, how such projections vary across model families, and whether making them explicit improves downstream work. Surprisingly, naive projection injection does not consistently improve execution and can degrade deep specialty dimensions, revealing a separation between responsibility recognition and responsibility fulfillment.
```

---

## 12. 제목 / 부제 보강 후보

기존 제목을 유지하되, subtitle이나 framing에 다음 표현을 활용할 수 있다.

### 후보 1

> Responsibility Projection in LLM Agents: Measuring the Gap Between Recognition and Fulfillment

### 후보 2

> When Responsibility Guidance Hurts: Projection, Execution, and Settlement in LLM Agents

### 후보 3

> Responsibility Recognition Is Not Responsibility Fulfillment

### 후보 4

> Measuring Responsibility Projection and Its Failure as Execution Guidance in LLM Agents

가장 방어력이 좋은 표현은:

> **Responsibility Recognition Is Not Responsibility Fulfillment**

이 문구는 reviewer가 projection injection 실패를 공격할 때 논문의 중심 주장으로 전환하기 좋다.

---

## 13. Reviewer 설득용 핵심 Figure 아이디어

### Figure A. Separation diagram

```text
Delegation
   ↓
Responsibility recognition
   ↓
Projected responsibility vector
   ↓
Naive injection
   ↓
Execution degradation in deep specialty dimensions
```

옆에 다음을 배치:

```text
Recognition ≠ Fulfillment
```

---

### Figure B. Dimension-specific degradation

x축:

```text
R1.1 R1.2 R1.3 R1.4 R1.5 R1.6 R1.7 RX.1 ...
```

y축:

```text
Δ settlement loss = L_projection_injection - L_direct
```

강조:

```text
R1.4, R1.7에서 손실 집중
```

---

### Figure C. Possible mechanism map

```text
Projection injection degradation
├── projection error
├── attention dilution
├── token displacement
├── surface compliance
└── resource mismatch
```

이 figure는 causal claim이 아니라 discussion map으로 쓰면 좋음.

---

## 14. 지금 당장 해야 할 manuscript 수정 checklist

> **주의**: 본 checklist는 v1.5 framing 작업 결정 시 활용. paper-6 v1.4 제출본은 현 시점에서 수정하지 않음.

### 반드시 수정

- [ ] Introduction에서 projection을 execution-improvement method처럼 보이게 하는 문장 제거
- [ ] Contribution을 "projection improves execution"이 아니라 "recognition–fulfillment separation"으로 수정
- [ ] Result section에서 negative result를 실패가 아니라 structured finding으로 서술
- [ ] Discussion에 separation result 문단 추가
- [ ] Limitation에 causal mechanism 미확정 명시
- [ ] Future work에 token-matched / oracle projection / resource-specific ablation 제안
- [ ] Abstract에 "surprisingly, naive injection can hurt"를 명시할지 검토

### 하면 좋은 수정

- [ ] R1.4/R1.7 손실 집중을 별도 figure/table로 강조
- [ ] within-family variance vs cross-family mismatch를 더 선명하게 보여주기
- [ ] judge robustness appendix 추가
- [ ] projection injection prompt 예시 appendix 추가
- [ ] reviewer가 "prompt engineering 문제"라고 공격할 경우를 대비한 문장 추가

---

## 15. 가장 중요한 논문 방어 논리 요약

최종 방어 논리는 다음 5문장으로 압축된다.

1. 이 논문은 responsibility projection을 execution policy로 제안하는 논문이 아니다.
2. 이 논문은 delegation에 내포된 responsibility structure가 실행 전에 측정 가능한지 보는 논문이다.
3. cross-family projection mismatch가 within-family stochastic variance보다 크다는 점이 핵심 empirical finding이다.
4. projection injection의 성능 저하는 실패가 아니라, responsibility recognition과 responsibility fulfillment가 분리되어 있음을 보여주는 결과다.
5. 따라서 projected responsibility는 naive prompt instruction이 아니라, 별도 검증과 메커니즘이 필요한 diagnostic signal로 보아야 한다.

---

## 16. 최종 결론

Review 전에 기존 논문은 다음 방향으로 defense를 고정하는 것이 좋다.

> **Responsibility Recognition Is Not Responsibility Fulfillment.**

이 문장이 가장 중요하다.

projection을 잘 측정할 수 있다는 것과, 그 projection을 prompt에 넣어 성능을 높일 수 있다는 것은 다른 문제다.  
기존 논문은 전자를 보여주고, 후자가 naive하게는 실패할 수 있음을 보여준다.

따라서 projection injection의 부정적 결과는 논문을 약화시키는 것이 아니라, 오히려 논문의 핵심 메시지를 강화한다.

```text
Projection is measurable.
Projection is model-dependent.
Projection injection can hurt.
Therefore, recognition and fulfillment must be separated.
```

이 frame으로 abstract, contribution, discussion, limitation, rebuttal을 모두 정렬해야 한다.
