"""
content_structurer.py — 콘텐츠 생성 전 구조화 선행 스텝

콘텐츠를 바로 생성하지 말고, 먼저 "어떻게 설득할 것인가"를 구조화.
이 구조가 후속 에이전트들의 context로 전달되어 일관성 있는 콘텐츠 생성 가능.

사용법:
    from core.content_structurer import structure_before_create

    # 콘텐츠 생성 전 구조 잡기
    structure = structure_before_create(
        task="마케팅팀이 뽑아줄 셀러 영업 카피",
        target_info={
            "industry": "음식점",
            "target": "음식점 사장",
            "challenge": "온라인 예약이 안 들어옴",
            "budget": "월 50만원"
        },
        client=anthropic_client
    )

    # 후속 에이전트에게 넘기기
    context["content_structure"] = structure
    result = follow_agent.run(context, client)
"""
import os
import json
import anthropic
from dotenv import load_dotenv
from core.models import CLAUDE_HAIKU

load_dotenv()


def structure_before_create(
    task: str,
    target_info: dict,
    client: anthropic.Anthropic = None,
    max_tokens: int = 1200
) -> dict:
    """
    콘텐츠 생성 전 구조를 먼저 설계.

    구조화 프롬프트는 다음을 포함:
    1. 타겟 Pain Point 분석
    2. 메시지 컴포넌트 분해 (훅/본문/CTA)
    3. 톤앤매너 정의
    4. 채널별 변환 포인트

    Args:
        task: 콘텐츠 생성 태스크 설명
        target_info: 타겟 정보 dict {industry, target, challenge, budget, ...}
        client: Anthropic 클라이언트 (없으면 신규 생성)
        max_tokens: 최대 토큰수 (기본 1200)

    Returns:
        {
            "pain_points": ["..."],
            "hook": "후킹 문장",
            "body_structure": ["포인트1", "포인트2", "포인트3"],
            "cta": "행동유도 문장",
            "tone": "톤앤매너 설명",
            "channels": {
                "insta": "인스타그램 변환 포인트",
                "blog": "블로그 변환 포인트",
                "kakao": "카카오톡 변환 포인트"
            },
            "success_metrics": ["방문율 XX%", "전환율 XX%"],
            "raw_response": "모델 전체 응답 (디버깅용)"
        }
    """
    if client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(".env에 ANTHROPIC_API_KEY 없음")
        client = anthropic.Anthropic(api_key=api_key)

    # 타겟 정보 포맷팅
    target_str = "\n".join(
        f"- {k}: {v}" for k, v in target_info.items() if v
    )

    system_prompt = """너는 콘텐츠 구조화 전문가야.
콘텐츠를 바로 생성하지 않고, 먼저 "어떻게 설득할 것인가"의 논리적 구조를 만드는 역할.

이 구조는:
1. 타겟의 pain point를 정확히 찌르는가?
2. 메시지가 훅 → 본문 → CTA로 일관되게 흘러가는가?
3. 각 채널(인스타/블로그/카톡)에 맞게 변환할 수 있는가?
를 충족해야 한다.

응답 형식은 반드시 JSON으로. 구조만 짜고 상세 콘텐츠는 작성하지 마."""

    user_prompt = f"""태스크: {task}

타겟 정보:
{target_str}

위 정보를 바탕으로 콘텐츠 구조를 JSON으로 짜줘.

응답 JSON 스키마:
{{
    "pain_points": ["고통점1", "고통점2", ...],
    "hook": "가장 먼저 눈을 끌 문장 한 줄",
    "body_structure": ["본문 포인트1", "본문 포인트2", "본문 포인트3"],
    "cta": "마지막 행동유도 (구체적)",
    "tone": "이 콘텐츠의 톤앤매너 설명",
    "channels": {{
        "insta": "인스타그램 특화 변환 포인트",
        "blog": "블로그 특화 변환 포인트",
        "kakao": "카카오톡 특화 변환 포인트"
    }},
    "success_metrics": ["성공 지표1", "성공 지표2"]
}}"""

    try:
        print(f"\n🔨 콘텐츠 구조화 중... ({CLAUDE_HAIKU})")

        response_text = ""
        with client.messages.stream(
            model=CLAUDE_HAIKU,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                response_text += text

        # JSON 파싱
        try:
            # JSON 블록 추출 (```json ... ``` 형식일 수도 있음)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                structure = json.loads(json_str)
            else:
                raise ValueError("JSON 블록을 찾을 수 없음")

            structure["raw_response"] = response_text

            print("✅ 구조화 완료")
            return structure

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 파싱 실패: {e}")
            # 폴백: 구조를 수동으로 구성
            return _fallback_structure(target_info, response_text)

    except Exception as e:
        print(f"❌ 구조화 실패: {e}")
        return _fallback_structure(target_info, "")


def _fallback_structure(target_info: dict, response_text: str) -> dict:
    """구조화 실패 시 기본 구조 반환. 콘텐츠 생성 계속 가능하도록."""
    return {
        "pain_points": [
            target_info.get("challenge", "비즈니스 과제"),
            "온라인 가시성 부족",
            "신규 고객 유입 어려움"
        ],
        "hook": "당신의 비즈니스가 온라인에서 보이지 않는 이유는?",
        "body_structure": [
            "타겟의 pain point 명확히",
            "우리 솔루션의 효과",
            "증명: 사례 또는 데이터"
        ],
        "cta": "먼저 무료 진단받아보세요",
        "tone": "전문적이면서도 친근함. 겁주지 않고 희망을 줌.",
        "channels": {
            "insta": "비주얼 중심. 숏폼 영상 또는 카루셀. 태그 활용.",
            "blog": "구체적 데이터. 제목 + 소제목 + 핵심 3포인트 + CTA.",
            "kakao": "짧고 명확함. 이미지 1장 + 텍스트 3줄. 버튼 명확."
        },
        "success_metrics": [
            "클릭율 (목표: 5%↑)",
            "전환율 (목표: 3%↑)",
            "상담 신청율 (목표: 10명/월)"
        ],
        "raw_response": response_text,
        "_fallback": True
    }


def merge_structure_to_context(context: dict, structure: dict) -> dict:
    """구조를 기존 context에 병합. 후속 에이전트가 쉽게 사용할 수 있게."""
    context["content_structure"] = structure
    context["pain_points"] = structure.get("pain_points", [])
    context["message_hook"] = structure.get("hook", "")
    context["message_body"] = structure.get("body_structure", [])
    context["message_cta"] = structure.get("cta", "")
    context["tone"] = structure.get("tone", "")
    context["channel_tips"] = structure.get("channels", {})

    return context
