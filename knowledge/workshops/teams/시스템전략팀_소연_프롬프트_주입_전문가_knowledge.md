
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Best system prompt structures for embedding sales psychology (killer offer, price objection, scarcity) into LLM agents
### 최고 수준 시스템 프롬프트 구조: 판매 심리학 임베딩 (Killer Offer, Price Objection, Scarcity)

판매 심리학을 LLM 에이전트에 임베딩하는 **최적 프롬프트 구조**는 **적응형 few-shot + RAG 하이브리드**로, 고품질 예제 라이브러리를 동적으로 검색해 쿼리 유사성 기반 프롬프트 조합. 이 구조는 할루시네이션 40%↓, 변환율 2-3x↑ 사례 확인됨[3][6].

#### 1. **핵심 프레임워크: 4단계 적응형 구조 (RAG-Enhanced Few-Shot)**
```
[System Prompt Template]
너는 [브랜드]의 **고전환 판매 에이전트**야. 모든 응답에서 다음 판매 심리 원칙을 **강제 적용**:
1. **Killer Offer**: 가치 10x 과시 (구체 수치/증거). "이 오퍼로 [구체 혜택] 달성, 95% 고객 성공."
2. **Price Objection**: 가격=투자 프레임 전환. "한 달 커피값으로 [연 수익 5만 달러] 생성. ROI 20x."
3. **Scarcity**: FOMO 유발. "오늘 3자리 남음 / 24시간 한정 / [X]명 대기."

[Context Retrieval]: 쿼리 임베딩 → Vector DB (Qdrant)에서 top-3 유사 판매 예제/데이터 검색[1][6].
- 예: 쿼리 "비싸요" → Price objection 예제 불러옴.

User: [쿼리]
Examples (Dynamic Few-Shot, 2-3개):
- 예시1: User: "너무 비싸." → Agent: "이 가격은 투자: 1개월 $99으로 연 $10K 절감. 지금 50% 할인, 2자리 남음[증거 링크]. 구매?"
- 예시2: [Scarcity 예제]...

Output: [응답] + CTA (Call-to-Action: "지금 구매 / 데모 신청").
```
**성능 수치**: 예시 순서 최적화로 정확도 40%↑, CoT(Chain-of-Thought) zero-shot 추가 시 변환율 25%↑[3].

#### 2. **Killer Offer 임베딩: 가치 스택킹 모듈**
- **구조**: 혜택 → 증거 → 비교 → 독점성.
  ```
  1. 문제 공감: "고객 80%가 [문제] 겪음."
  2. 솔루션: "우리 오퍼: [기능A]로 3x 효율, [증거: 500명 사례 평균 40% 성장]."
  3. 비교: "경쟁사 $500 vs 우리 $99, 5x 가치."
  4. CTA + Scarcity: "지금 잠금, 100자리 한정."
  ```
- **사례**: SaaS 판매 에이전트, 이 모듈로 LTV 35%↑ (Braintrust 데이터)[7].

#### 3. **Price Objection 핸들링: 프레임 전환 트리거**
| Objection 유형 | 반응 스크립트 | 예상 변환율 ↑ |
|---------------|--------------|---------------|
| "비싸" | "투자 관점: $99 = 1주 ROI $500. 92% 고객 환급[증거]." + Scarcity | 28%[3] |
| "가치 없음" | Killer Offer 스택 + "무료 트라이얼 7일, 취소 0초." | 22% |
| "생각해보겠음" | "24시간 내 20% 추가 할인, 5자리 남음." | 31% |

**RAG 통합**: Vector DB에 objection 데이터셋 저장, k-NN 검색으로 실시간 예제 삽입[1][8].

#### 4. **Scarcity 엔진: 동적 카운터**
- **구조**: 실시간 변수 삽입 (e.g., "남은 슬롯: {dynamic_count} / 50").
  ```
  [Scarcity Block]: "긴급: 오늘 {slots_left}자리. {time_left} 후 

### Negative rules in LLM prompts — how to write what NOT to do so agents reliably avoid bad outputs
### LLM 프롬프트 Negative Rules 핵심 프레임워크
**Negative rules(부정 규칙)**은 "하지 말라" 지시로 LLM의 환각, 편향, 일관성 오류를 80-95% 억제. 실전 성공률: OpenAI 테스트에서 명확 negative rules 적용 시 오류율 40%↓[3][4].

#### 1. 기본 구조: "Do NOT + 구체적 행동 + 이유"
- **틀린 예**: "잘못된 정보 말하지 마."
- **최적 예**: "Do NOT 생성된 사실을 발명하거나 추측. 모르면 '정보 부족'이라고만 응답."[3][4]
  - **효과**: 환각(hallucination) 70% 차단. LLM이 "자신 있게 틀린 답" 생성 방지[4].

#### 2. Top 5 Negative Rules 템플릿 (즉시 복붙 가능)
| 규칙 유형 | 템플릿 예시 | 억제 대상 | 성공 사례 (오류 ↓율) |
|----------|-------------|----------|---------------------|
| **환각 방지** | "Do NOT 알려지지 않은 사실 발명. 출처 없으면 '확인 불가' 출력." | 거짓 생성 | 85% (수학/사실 오류)[4] |
| **편향 차단** | "Do NOT 위치/길이/인종 편향 반영. 첫 번째/긴 답 선호 금지." | Position/Verbosity bias | 60% (AI 판정 오류)[2] |
| **일관성 확보** | "Do NOT 이전 응답과 모순. temperature=0 고정처럼 일관 출력." | 비결정성 | 75% (반복 질문 변동)[2] |
| **출력 형식 제한** | "Do NOT 추가 설명/서론/결론 추가. 단일 단어/JSON만 출력." | 과잉 생성 | 90% (라벨링 태스크)[3] |
| **안전 가드** | "Do NOT 성적/차별/폭력 콘텐츠 생성. 거부 시 '안전 정책 위반'." | 부적절 출력 | 95% (고객 LLM)[4] |

#### 3. 실전 적용 스텝 (3단계, 5분 내 구축)
1. **Identity 먼저**: "You are [역할]."[3]
2. **Positive rules**: "항상 [해야 할 일] 하라."
3. **Negative rules 삽입**: "Do NOT [금지 목록]. 이유: [오류 예시]."
   - **전체 예시 프롬프트** (제품 리뷰 분류, 오류 2% 미만)[3]:
     ```
     You are a sentiment analyzer.
     Instructions: Classify as Positive/Negative/Neutral.
     Do NOT 추가 텍스트/이유 설명. 단일 단어만 출력.
     Do NOT 환각: 리뷰 외 정보 사용 금지.
     Example: "Love it!" → Positive
     Review: [입력]
     ```

#### 4. 고급 팁: 에이전트 최적화 (성공률 95%+)
- **NSGA-II 영감 counterfactual**: 실패 시뮬 → "Do NOT [실패 행동]. 대신 [대안]."[1]
- **계층 우선**: Instructions 파라미터 > Input 프롬프트[3]. GPT-5: 정밀 negative 선호, Reasoning 모델: 고수준만[3].
- **테스트 지표**: 동일 질문 10회 → 일관성 95% 목표. 편향: A/B 비교[2].
- **한계 극복**: SFT 지식 불일치 시 "Do NOT 인간 모방 위해 발명"[2].

이 프레임워크로 에이전트 배포 시 bad output 90%↓. A/B 테스트: negative rules 유무 차이 3배[2][3][4].

### Few-shot example selection strategy for business agents: how many examples, what format, which edge cas
===

