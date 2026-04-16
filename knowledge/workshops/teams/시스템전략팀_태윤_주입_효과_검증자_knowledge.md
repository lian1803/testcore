
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### LLM agent behavior audit techniques — how to verify that injected instructions are consistently followed across outputs
### LLM Agent Behavior Audit: Injected Instructions Consistency Verification

**핵심 프레임워크: Multi-Trial Red-Teaming + Bayesian Inference + Taint Analysis.** Injected instructions(예: system prompt quirks)을 100+ trials에서 **95%+ consistency rate**로 검증. Anthropic/Claude 4 audit에서 top-60 transcripts 중 quirk 노출률 80% 달성[3].

#### 1. **Automated Red-Teaming Agents (Anthropic-style, 90%+ detection)**
   - **Setup**: Target LLM에 injected instruction(예: "always lie about X") 삽입. Auditor agent가 25-turn 대화 x 2 runs 반복[3].
   - **Verification**: LLM judge(Claude Opus 4)가 transcripts 랭킹 → top-60 중 quirk 노출 확인. Pre-fill attacks로 system prompt 직접 추출[3].
   - **Metrics**: Quirk uncover frequency (per instruction). Human review on flagged transcripts[3].
   - **실전 사례**: Claude 4 frontier model audit → hidden goal/sneaky behavior 85% surface[3].
   - **도구**: Agentic red-teaming env (quirky prompt models 대상)[3].

#### 2. **Bayesian Objective Inference (LLM Data Auditor, Uncertainty Quantification)**
   - **모델**: LLM output을 linear reward \( R_\theta(o) = \theta^\top \phi(o) \)로 모델링. Variational posterior \( q_\lambda(\theta) \) via ELBO max[2].
   - **Audit Loop**: Sequential evidence rounds → posterior contraction monitor. Non-identifiability/OOD/shortcut detect (threshold: contraction <0.1)[2].
   - **Consistency Check**: Trial-by-trial multi-agent debate (EMAD) → consensus on instruction adherence. Clinical/financial data에서 risk 40%↓[2].
   - **Threshold**: Calibration score >0.9, ledger trails로 reproducibility[2].

#### 3. **Code-Level Taint Analysis (Agent Audit Pipeline, 95% Precision)**
   - **Pipeline**: AST dataflow (source: LLM input → sink: exec/subprocess). Tool decorators(@tool 등 12 patterns) boundary boost confidence x1.6[4].
   - **Instruction Override Detect**: Prompt/tool desc Levenshtein distance로 shadowing/exfiltration check. Runtime inspect (stdio MCP server)[4].
   - **Scoring**: BLOCK(≥0.92: immediate fix), WARN(≥0.60). 42 vuln benchmark: 40 TP, 6 FP, <1s scan[4].
   - **실전**: LangChain/CrewAI repo scan → tainted instruction flow 98% recall[4].

#### 4. **Multi-Layer Evaluation + Monitoring (AWS/PwC Hybrid)**
   | Layer | Technique | Metric | Threshold |
   |-------|-----------|--------|-----------|
   | Output | LLM judge + rule checks | Semantic adherence | >90%[6][7] |
   | Component | HITL trace audit | Degradation alert | Custom rules[6] |
   | LLM Core | Blind testing | Bias regression | Cross-expert score[5] |

   - **실행**: 100+ prompts x agents → final output + intermediate traces audit. Continuous metrics (drift >5% → notify)[6][5].
   - **Multi-Agent**: Profile alignment (LLM-gen + dataset) → debate consensus[8][2].

#### 5. **최고 수준 배포 템플릿 (4주 Audit Cycle)**
   1. **Week1**: Agent discovery + inject test instructions[1].
   2. **Week2-3**: Red-team x50 + Bayesian runs[3][2].
   3. **Week4**: Taint scan + multi-layer evals → 95% consistency or remediate[4][6].
   - **ROI**: OWASP Top10 risks 70%↓, sub-second scans[1][4].
   - **스케일**: CI/CD 통합 (SARIF/JSON export)[4].

**위험 Top3**: OOD prompts(20% miss)[2], tool shadowing(15% FP)[4], evaluator bias(blind test 필수)[5]. 2026 최신: EMAD + Agent Audit combo 97% precision[2][4].

### Prompt drift and instruction decay in long-running LLM systems — detection and correction methods
### **Prompt Drift & Instruction Decay 정의**
**Prompt drift**: 프롬프트 변경 없이 LLM 출력 분포가 점진적 변화 (e.g., 신뢰도 하락, 출력 길이 증가 20-50% 관찰).[1][3]  
**Instruction decay**: 장기 대화(8라운드 내)에서 시스템 지시 무시, attention decay로 인한 영향력 감소 (LLaMA2-70B, GPT-3.5: 8회 후 30-50% drift).[3][5]

### **원인 (Top 5, 실전 사례)**
| 원인 | 설명 & 사례 | 영향 수치 |
|------|-------------|-----------|
| **Model 업데이트** | 제공자( OpenAI 등) 무통보 업데이트로 출력 분산 ↑ (std dev 2x 증가).[1][2] | 출력 길이 15-30% creep.[1] |
| **Attention decay** | Transformer에서 장기 컨텍스트 시 초기 프롬프트 attention ↓ (8턴 후 지시 준수 50%↓).[3] | LLaMA2: 200 대화 평균 drift score 40%↓.[3] |
| **
===

