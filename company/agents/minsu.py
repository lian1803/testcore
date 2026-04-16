import os
from openai import OpenAI
from core.models import GPT4O
from core.context_loader import inject_context
from core.model_loader import get_model

# 모델 설정: config에서 "budget_strategy" 역할의 모델 로드
# 기본값 GPT-4o (하위호환)
MODEL = get_model("minsu")


def run(context: dict, client=None) -> str:
    print("\n" + "="*60)
    print(f"📈 민수 | 전략 수립 ({MODEL})")
    print("="*60)

    idea = context.get("clarified", context.get("idea", ""))
    market_research = context.get("seoyun", "")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        error_msg = "[민수 실패: OPENAI_API_KEY 없음 — .env 확인 필요]"
        print(f"\n⚠️  {error_msg}")
        return error_msg

    try:
        openai_client = OpenAI(api_key=api_key, timeout=240.0)

        system = """너는 민수야. 리안 컴퍼니의 비즈니스 전략가.

⚠️ **역할 재정의 (2026-04-13 변경)**
너는 이제 **방향성 결정자**만 맡아. 깊은 전략 설계는 다음 단계 '설계자' 에이전트가 처리해.
너의 임무: 서윤의 Pain Point에서 **어느 아이템을 공략할지 1순위만 뽑는 것**.
OKR/필터링/STP/VPC/BM/가격 티어/유닛이코노믹스/단계별실행/출구전략 등 **깊은 섹션은 전부 쓰지 마**. 설계자가 전담한다.

=== 임무 (이 3가지만) ===
1. 서윤의 50개 Pain Point 중 돈 되는 것 필터링 (간략)
2. TOP 3~5 클러스터 선정 + 가중치 스코어링
3. **1순위 선택** + 선택 근거 3줄 (Pain # 역추적)

=== 출력 형식 (정확히 이 3개 섹션만) ===

## 1. Pain Point 필터링 (요약)

서윤 50개 Pain Point 중:
- Level 4~5 통과: N개 (Level 1~3 제외)
- Workaround 관찰: N개 (is_workaround_observed=true)
- 블루오션 플래그 (Level 4~5 + competitor_url=none): N개 + 목록 나열

**필터링 결과**: 최종 N개 통과 (상세 필터링 과정은 설계자가 처리하므로 여기선 요약만)

## 2. TOP 3~5 클러스터 + 가중치 스코어링

### 클러스터링
통과한 Pain Point를 JTBD 유사성 기준으로 3~5개 아이템으로 묶기:

| 아이템 | 관련 Pain # | 핵심 JTBD (한 줄) |
|--------|-------------|------------------|
| A. | #1, #3, #7 | |
| B. | | |
| C. | | |

### 가중치 스코어링

| 기준 (가중치) | A | B | C |
|--------------|---|---|---|
| Workaround 비용 (20%) | | | |
| Payer 명확성 (15%) | | | |
| Pre-sell 가능성 (15%) | | | |
| 경쟁 빈틈 (25%) | | | |
| Build 난이도 (15%) | | | |
| 우리 자산 활용도 (10%) | | | |
| **종합 점수** | | | |

**각 점수 옆에 산출 근거 1줄 필수** (빈 칸 금지).

## 3. 1순위 선택 + 킬러 오퍼

**1순위 선택**: [아이템명]

**선택 근거 3줄** (Pain # 역추적):
1. [서윤 Pain #N의 evidence_quote 인용 + 왜 이게 1순위인가]
2. [경쟁 빈틈 근거 (서윤 Phase 2 Layer 5 인용)]
3. [우리 리안 컴퍼니 자산 활용 포인트 — naver-diagnosis, 온라인팀 등 구체적 연결]

**킬러 오퍼 (한 문장 공식)**:
공식: [극도로 좁은 타겟] + [측정 가능한 결과] + [구체적 방법론] + [가격]

좋은 예: "객단가 10만원 이상 눈썹 반영구 손님만 타겟, 월 10명 신규 예약 보장하는 인스타 퍼널 세팅 (89만원)"
나쁜 예: "뷰티샵 마케팅 해드립니다 (89만원)"

---

=== 절대 금지 ===
- **섹션 4 이후 쓰지 마**. STP, VPC, Problem Statement, Lean Canvas, 수익 모델, 가격 티어 상세, 유닛이코노믹스, 출구 전략, 단계별 실행 계획, TAM/SAM/SOM 전부 설계자가 처리함. 여기 쓰면 중복 낭비.
- "이론 금지" — 바로 실행 가능한 판단만
- "좋아요 100개"보다 "결제 1건" — 허영 지표 금지
- Pain #번호 없이 근거 인용 금지. 모든 주장은 서윤 Pain # 역추적 가능해야 함
- 인사말 금지. 바로 `## 1. Pain Point 필터링`부터
"""

        content = f"아이디어: {idea}\n\n[서윤의 시장조사]\n{market_research}\n\n전략을 수립해줘."

        full_response = ""
        attempt = 0
        max_retries = 1

        while attempt <= max_retries:
            try:
                stream = openai_client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": inject_context(system)},
                        {"role": "user", "content": content}
                    ],
                    stream=True,
                    temperature=0.7,
                    max_tokens=3000,  # 슬림화 이후 섹션 3개만 출력 (2026-04-13)
                    timeout=180
                )
                for chunk in stream:
                    # chunk.choices[0] IndexError 방어
                    if not chunk.choices:
                        continue
                    text = chunk.choices[0].delta.content or ""
                    print(text, end="", flush=True)
                    full_response += text
                break  # 성공하면 루프 탈출
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    raise
                # 429나 네트워크 에러면 1회 재시도
                if "429" in str(e) or "timeout" in str(e).lower():
                    print(f"\n⚠️  API 한도/타임아웃 — {attempt}회 재시도...")
                else:
                    raise

        print()
        return full_response if full_response.strip() else "[민수 응답 없음]"

    except Exception as e:
        error_msg = f"[민수 실패: {str(e)[:100]} — 다음 단계로 넘어감]"
        print(f"\n⚠️  {error_msg}")
        return error_msg
