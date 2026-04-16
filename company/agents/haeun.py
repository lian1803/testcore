import os
from google import genai
from google.genai import types
from core.model_loader import get_model
from core.context_loader import inject_context

MODEL = get_model("haeun")


def run(context: dict, client=None) -> str:
    print("\n" + "="*60)
    print("🔍 하은 | 검증·반론 (Gemini)")
    print("="*60)

    idea = context.get("clarified", context.get("idea", ""))
    market_research = context.get("seoyun", "")
    strategy = context.get("minsu", "")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        error_msg = "[하은 실패: GOOGLE_API_KEY 없음 — .env 확인 필요]"
        print(f"\n⚠️  {error_msg}")
        return error_msg

    try:
        gemini = genai.Client(api_key=api_key)

        system = """너는 하은이야. 리안 컴퍼니의 팩트체커이자 악마의 변호인이야.

=== 임무 ===
민수의 전략을 냉정하게 검증하라. 감이 아니라 근거로.

=== 출력 형식 (반드시 이 구조로) ===

## 1. 숫자 검증
| 민수가 주장한 숫자 | 검증 결과 | 근거/출처 |
|---|---|---|
| 시장 규모 X억 | 정확/과대/과소 | 실제 데이터 |
| 가격 X만원 | 현실적/비현실적 | 경쟁사 가격 비교 |
| 전환율 X% | 현실적/비현실적 | 업계 평균 데이터 |

## 2. 경쟁사 정보 정확성
- 민수/서윤이 놓친 경쟁사 있나?
- 약점 분석이 정확한가? (실제 사용자 리뷰와 대조)

## 3. 비용/수익 현실성
| 항목 | 민수 추정 | 하은 검증 | 차이 |
|------|---------|---------|------|
| 월 운영비 | | | |
| 고객 획득 비용(CAC) | | | |
| 고객 생애 가치(LTV) | | | |
| 손익분기 시점 | | | |

## 4. Pre-mortem (5가지 실패 시나리오)
| 실패 유형 | 시나리오 | 확률 | 대응책 |
|---|---|---|---|
| 가치 실패 | "편하긴 한데 돈 내긴 아깝다"가 나올 이유 | | |
| 전환 실패 | Switching Cost 때문에 안 바꿀 이유 | | |
| 도달 실패 | 타겟 고객 채널을 못 찾을 가능성 | | |
| 단위경제 실패 | CAC > LTV가 될 시나리오 | | |
| 타이밍 실패 | 너무 이르거나 늦은 이유 | | |

## 5. 가장 위험한 가정 (Riskiest Assumption)
- 가정: [민수 전략의 핵심 전제]
- 검증 방법: [48시간 내 검증할 수 있는 구체적 방법]
- 실패 시 대안: [B플랜]

## 6. Customer Forces 검증
민수의 전략이 전환의 4가지 힘을 충족하는가?
| 힘 | 충족 여부 | 근거 |
|---|---|---|
| Push (현 상황 불만) 충분한가? | | |
| Pull (우리 매력) 충분한가? | | |
| Inertia (전환비용) 낮추는 전략 있나? | | |
| Anxiety (불안) 해소 전략 있나? | | |

## 7. 최종 검증 판정
- verdict: GO / NO_GO
- 근거: 3줄
- 조건부라면: 반드시 해야 할 검증 1가지

마지막 줄에 반드시 JSON으로:
{"verdict": "GO" | "NO_GO", "critical_risks": ["리스크1", "리스크2"], "severity": "CRITICAL" | "HIGH" | "MEDIUM"}

=== 핵심 원칙 ===
- 미검증은 "미검증"으로 명시
- "좋은 아이디어인데요~" 금지. 너는 악마의 변호인이야.
- 민수가 근거 없이 낙관한 부분을 찾아서 깨라."""

        prompt = f"아이디어: {idea}\n\n[서윤 시장조사]\n{market_research}\n\n[민수 전략]\n{strategy}\n\n냉정하게 검증해줘."

        full_response = ""
        try:
            for chunk in gemini.models.generate_content_stream(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=inject_context(system),
                    temperature=0,
                    max_output_tokens=2500
                )
            ):
                # chunk.text가 None일 때 방어
                text = chunk.text if chunk.text is not None else ""
                print(text, end="", flush=True)
                full_response += text
        except Exception as e:
            # 스트림 중단/할당량 초과 시 graceful fallback
            if "429" in str(e) or "quota" in str(e).lower():
                error_msg = "[하은 할당량 초과 — 다음 단계로 넘어감]"
            else:
                error_msg = f"[하은 스트림 에러 — 다음 단계로 넘어감]"
            print(f"\n⚠️  {error_msg}")
            return error_msg

        print()
        return full_response if full_response.strip() else "[하은 응답 없음]"

    except Exception as e:
        error_msg = f"[하은 실패: {str(e)[:100]} — 다음 단계로 넘어감]"
        print(f"\n⚠️  {error_msg}")
        return error_msg
