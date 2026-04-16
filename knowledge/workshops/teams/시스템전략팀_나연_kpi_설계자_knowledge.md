
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### How to measure AI agent output quality improvement — quantitative metrics for before/after prompt injection experiments
# AI 에이전트 출력 품질 개선 측정: 프롬프트 인젝션 실험용 정량 지표

## 핵심 측정 프레임워크

**실험 설계 → 지표 정의 → 가설 수립 → 평가 실행 → 결과 비교** 순서로 진행합니다.[3]

구체적으로는 (1) 성공 기준을 명확한 임계값으로 설정하고 (2) 다차원 지표를 정의하며 (3) Before/After 성능 차이를 정량화합니다.[3]

## 실전 적용 가능한 지표 세트

| 지표 | 측정 방법 | 활용 시기 |
|------|---------|---------|
| **정확도 & 회수율** | 예상 출력과 실제 출력 비교 (결정적 평가) | 명확한 정답이 있을 때 |
| **의미적 유사성** | BERTScore 등으로 응답 텍스트 비교 | 자유형식 답변 평가 |
| **사실성** | 핵심 정보(IOC) 존재 여부, 분류 정확도 | 보안/업계 표준 준수 확인 |
| **완전성** | 필요한 모든 요소 포함 여부 | 누락된 정보 식별 |
| **일관성** | 반복 실행 시 출력 변동성 | 시스템 안정성 평가 |
| **지연시간** | 응답 속도 측정 | 성능 트레이드오프 확인 |

[3][4]

## Before/After 실험 구체적 프로세스

**1단계: 문제 식별**
- 프롬프트 인젝션으로 인한 구체적 실패 사례 수집
- 라우터, 스킬, 실행 분기별로 세분화[4]

**2단계: 가설 수립** (측정 가능해야 함)
- 예시: "공격 검색 도구 접근권 추가 → 보안 관련 쿼리 정확도 +5% 개선, 다른 영역 성능 저하 없음"[3]

**3단계: 평가 데이터셋 준비**
- 프롬프트 인젝션 시도 포함한 테스트 케이스 확보

**4단계: 정량적 평가 실행**
- 각 평가 항목에서 행 수준 출력(원래 쿼리, 에이전트 응답, 점수, 추론)로 상세 기록[2]
- 토큰 사용량까지 추적

**5단계: 결과 분석**
- 클러스터 분석으로 패턴 및 오류 식별[2]
- 성공 기준 충족까지 반복[2]

## LLM-as-Judge 평가 방식

정성적 평가가 필요할 때, LLM 자체를 평가자로 활용합니다.[1][5]

- **구조화된 프롬프트**로 일관된 평가 수행[1]
- 평가 점수 임계값 설정 (예: 8점 이상 = 품질 기준 달성)[1]
- 

### KPI design for internal AI automation systems: what metrics actually reflect business impact vs vanity metrics
### **Business Impact Metrics** (실제 ROI 반영, vanity 피함)
이 메트릭들은 비용 절감, 생산성 향상, 수익 기여를 직접 측정. Vanity(예: 요청 수, 대화량)는 무시하고 **비즈니스 결과** 중심.

| Metric | Definition & Calculation | Target Example | Business Case |
|--------|---------------------------|---------------|---------------|
| **Cost per Interaction** | 총 비용 / 총 상호작용 수 (인력+인프라 비용 포함) [4] | < $0.50 vs. human $5-10 | AI 챗봇이 고객 문의 70% 처리 시 연 $1M 절감 [4] |
| **ROI** | (이익 - 비용) / 비용 × 100 [4] | > 200% in 6개월 | 자동화로 cycle time 50% 단축 → 매출 15% ↑ [4] |
| **Call/Chat Containment Rate** | AI가 해결한 문의 비율 [1] | > 60% | 수동 문의 40% 감소, 스케일링 용이 [1] |
| **Average Handle Time (AHT)** | 문의 해결 평균 시간 (AI vs. human) [1] | AI: < 2분 (human: 5분) | 에이전트 생산성 2배 ↑ [1] |
| **Time Saved / Hit Rate** | 프로세스당 절감 시간; AI 정확 출력 비율 (편집 없음) [3] | Hit Rate > 85%; 시간 30-50% ↓ | 워크플로 100회 실행 시 85회 자동 완료 [3] |
| **Exception Rate** | 수동 개입 필요 비율 [4] | < 10% | 숨겨진 리워크 비용 드러냄, 운영 리스크 ↓ [4] |

**프레임워크: Tiered KPI Selection** [2]
- **Tier 1 (고위험: fraud/claims)**: Impact + Governance 필수 (ROI >150%, Risk <5%)
- **Tier 2 (중간)**: Impact + SLO (Uptime 99.9%)
- **Tier 3 (내부 생산성)**: Adoption + Cost (AHT ↓20%, Cost/Interaction ↓30%)
워크플로: 1) 비즈니스 목표 정의 → 2) Failure mode 식별 → 3) Leading(예측)/Lagging(결과) 선정 → 4) Target 설정 → 5) 모니터링 [2]

### **Vanity Metrics 피하기** (사용량 중심, 영향 미미)
- **요청/대화량, Visitor/Accounts**: 볼륨만 ↑, ROI 무관 [8] → 무시.
- **Accuracy/Coherence만**: 모델 품질이지 비즈니스 아님 [1][2]. Hit Rate로 대체.

### **Operational Excellence Metrics** (스케일링 필수, 비용 통제)
비즈니스 임팩트 뒷받침. **99%+ 신뢰성** 목표.

| Metric | Definition | Target | Impact |
|--------|------------|--------|--------|
| **Uptime** | 시스템 가용 시간 % [1] | 99.9% | 다운타임 1시간 = $10K 손실 |
| **Error Rate** | 오류 요청 비율 [1] | < 1% | 사용자 이탈 방지 |
| **Latency (Model/Retrieval)** | 응답 시간 (ms) [1] | < 500ms | UX 악화 시 adoption ↓50% |
| **Throughput (Req/Token)** | 초당 처리량 [1] | 1K req/sec | 피크 대응 |
| **GPU Utilization** | 하드웨어 사용률 % [1] | 70-80% | 비용 최적화, 오버프로비저닝 피함 |
| **% Automated Pipelines** | 자동화 워크플로 비율 [1] | > 80% | 수동 노력 최소화 |

**Scorecard 템플릿** (월간 리뷰) [2]:
- KPI명 | 정의 | Target | 최신값 | Owner | Action
- 예: ROI | (이익-비용)/비용 | 200% | 180% | AI Lead | 비용 10% ↓

### **Risk & Adoption Metrics** (지속성 확보)
- **% Models Monitored**: 성능 저하 감지 [1] → 100% 목표.
- **Adoptio

### A/B testing methodology for LLM prompt changes — sample size, evaluation rubrics, statistical significance in small teams
### **핵심 A/B 테스트 프레임워크 (LLM 프롬프트 변경용)**
**단계별 실행: 1) 목표/메트릭 정의 → 2) 데이터셋 구축 → 3) 변형 실행 → 4) 통계 검증 → 5) 배포.** 소규모 팀은 자동화 툴(Braintrust, Maxim AI)로 1인당 주 5-10회 테스트 가능[1][2].

#### **1. 샘플 사이즈 계산 (Small Team 최적화)**
- **최소 기준**: 100-500 쌍(각 변형당)으로 시작. 효과 크기(Effect Size) 10-20% 기준, Power 80%, α=0.05 
===

