
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### LLM output evaluation frameworks — rubric design for business quality assessment (relevance, tone, conversion potential)
### **Rubric Design Framework for Business LLM Evaluation**
**Core rubric: 3-pillar scoring (1-10 scale per pillar, weighted average total). Pillars: Relevance (40%), Tone (30%), Conversion Potential (30%). Threshold: ≥8/10 passes; <6 auto-fail. Use LLM-as-judge (e.g., GPT-4o) with chain-of-thought prompts for 0.95+ inter-annotator agreement.**[1][3][5]

#### **1. Relevance (Query Match + Completeness) – 40% Weight**
- **Definition**: Output directly addresses user intent, covers key query elements without hallucination or drift (e.g., ≥90% semantic overlap via cosine similarity).[1][2][5]
- **Scoring Criteria** (LLM prompt template):
  | Score | Criteria | Example (Sales Query: "Best CRM for SMB?") |
  |-------|----------|------------------------------------------|
  | 10    | 100% on-topic, exhaustive coverage of top 3 options w/ pros/cons | "HubSpot (free tier, 4.5/5), Salesforce Essentials ($25/mo, scalable), Pipedrive ($14/mo, pipeline focus)"[7] |
  | 7-9   | Strong match, minor gaps (e.g., misses pricing) | Adds unrelated "enterprise tips" but core recs solid |
  | 4-6   | Partial match, drifts 30-50% | Recommends tools but ignores SMB scale |
  | 1-3   | Off-topic (>50% irrelevant) | Discusses "AI ethics" instead |
- **Metrics**: Contextual Relevancy (DeepEval: 0-1 score), Answer Relevancy, Faithfulness (no hallucination).[2][5]
- **Business ROI**: Boosts user retention 25% (e.g., e-comm chatbots).[4]

#### **2. Tone (Brand Alignment + Engagement) – 30% Weight**
- **Definition**: Matches brand voice (e.g., professional/friendly), persuasive without aggression; readability ≥Flesch 60+.[1][7]
- **Scoring Criteria** (LLM prompt: "Rate tone match to [brand guidelines] on coherence"):
  | Score | Criteria | Example (Brand: "Empathetic, concise") |
  |-------|----------|---------------------------------------|
  | 10    | Perfect alignment, engaging (e.g., active voice, questions) | "Struggling with leads? HubSpot's free tools fix that fast." |
  | 7-9   | Minor mismatches (e.g., slightly formal) | Good but wordy |
  | 4-6   | Neutral/mismatched (e.g., robotic) | "CRM software is available." |
  | 1-3   | Offensive/aloof | "Just use whatever." |
- **Metrics**: G-Eval Coherence (1-5 → scale to 10), Bias/Toxicity (<0.1).[2][5]
- **Business ROI**: Lifts NPS 15-20%; test via A/B on live traffic.[4]

#### **3. Conversion Potential (Actionability + Persuasiveness) – 30% Weight**
- **Definition**: Drives next step (e.g., CTA, clear value prop); predicts click/buy ≥20% uplift vs. baseline.[3][4]
- **Scoring Criteria** (Prompt: "Does this compel action? Score 1-10 w/ CoT"):
  | Score | Criteria | Example |
  |-------|----------|---------|
  | 10    | Strong CTA, urgency, proof (e.g., "Sign up free: [link], 30% users convert") | Includes testimonial + demo link |
  | 7-9   | Clear value, soft CTA | "Try HubSpot free trial" |
  | 4-6   | Informative but passive | Lists features, no nudge |
  | 1-3   | No path to action | Pure info dump |
- **Metrics**: Custom DAG (DeepEval: extract CTAs → binary yes/no → score).[5] LLM-judge conversion sim (Prometheus: reference high-converting outputs).[5]
- **Business ROI**: 10-40% conv. lift; validate w/ human thumbs-up (≥80% align auto-score).[3][4]

#### **Implementation Playbook (Production-Ready)**
1. **Dataset**: 500+ real logs (prompt/output/CTR labels); synth-aug w/ Evidently (80% coverage).[1][4]
2. **Auto-Eval Pipeline** (DeepEval/MLflow):
   ``

### Human evaluation protocol for AI agent outputs — how to minimize evaluator bias and maximize consistency
# 인간 평가 프로토콜: 편향 최소화 & 일관성 최대화

검색 결과에는 인간 평가자 편향 최소화에 대한 직접적인 내용이 제한적이지만, AI 에이전트 평가의 구조적 원칙에서 적용 가능한 실전 프레임워크를 추출할 수 있습니다.

## 핵심 전략

**1. LLM-as-a-Judge 도입으로 인간 평가 대체**

정성적 평가가 필요한 상황에서 **별도의 LLM에 프롬프트를 통해 에이전트 출력을 평가하도록 하는 방식**이 인간 피드백의 비용과 편향 문제를 동시에 해결합니다[1]. 이 접근법은 Arize AI의 벤치마크에서 **70~90% 정밀도와 70~85% F1 점수**
===

