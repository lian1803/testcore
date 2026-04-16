"""
personalized_dm.py — 실제 가게 데이터 기반 개인화 DM 생성

크롤링한 실제 네이버 플레이스 데이터를 Claude에 넣어서
"이 가게만을 위한" 타겟팅된 영업 DM을 생성.

사용 예시:
    from core.naver_crawler import search_place
    from core.personalized_dm import generate_dm

    place_data = search_place("강남 스타벅스 역삼점")
    dm = generate_dm(place_data, service_package="주목")
    print(dm)
"""

import os
from typing import Dict, Optional
from anthropic import Anthropic

client = Anthropic()


def generate_dm(place_data: Dict, service_package: str = "주목") -> str:
    """
    실제 가게 데이터 기반으로 개인화된 영업 DM 생성.

    Args:
        place_data: naver_crawler.crawl_place() 또는 search_place()의 반환값
        service_package: 서비스 패키지명 ("주목", "집중", "성장" 등)

    Returns:
        생성된 DM 텍스트
    """

    if place_data.get('error'):
        return f"가게 데이터 수집 실패: {place_data['error']}"

    if not place_data.get('name'):
        return "가게명이 없어서 DM을 생성할 수 없습니다."

    # Claude에 보낼 컨텍스트 구성
    context = _build_context(place_data, service_package)

    prompt = f"""당신은 온라인 마케팅 회사의 영업 전문가입니다.
아래는 실제 가게의 네이버 플레이스 데이터입니다.
이 데이터를 기반으로 가게 사장님 입장에서 공감하고,
구체적인 문제점을 지적하면서도 해결책을 제시하는 영업 DM을 작성해주세요.

## 가게 데이터
{context}

## 요구사항
1. 톤: 친근하고 문제-해결 중심 (일반론 지양)
2. 길이: 문단 3-4개 (카톡 기준 3-4줄)
3. 구체성: 수치/사실 기반 (리뷰 수, 별점, 사진 업데이트일 등)
4. 주목점: 가게만의 약점을 지적한 후 우리 서비스로 어떻게 해결할지
5. CTA: 부드러운 접근 ("한 번 봐봐도 좋을 것 같아요", "5분이면 진단 가능해요" 등)

## 서비스 패키지: {service_package}
- 주목: 사진/콘텐츠 업로드 자동화 (월 20만원대)
- 집중: 리뷰 응답 + 콘텐츠 운영 (월 30만원대)
- 성장: 광고 + 최적화 전략 (월 50만원대)

이제 DM을 작성해주세요. 인사말부터 시작하세요.
"""

    try:
        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        dm_text = response.content[0].text
        return dm_text

    except Exception as e:
        return f"DM 생성 중 오류: {str(e)}"


def generate_dm_with_variations(
    place_data: Dict, service_package: str = "주목", num_variations: int = 3
) -> list[str]:
    """
    같은 가게에 대해 여러 변형의 DM을 생성.

    다양한 앵글로 테스트하고 가장 효과적인 버전을 선택할 때 사용.

    Args:
        place_data: 가게 데이터
        service_package: 서비스 패키지명
        num_variations: 생성할 변형 개수

    Returns:
        DM 텍스트 리스트
    """

    variations = []
    angles = [
        "약점 지적 강조 (리뷰 문제에 포커스)",
        "기회 강조 (경쟁사 벤치마크)",
        "쉬운 해결책 강조 (간단하고 비용 효율적)"
    ]

    for i, angle in enumerate(angles[:num_variations]):
        context = _build_context(place_data, service_package)

        prompt = f"""당신은 온라인 마케팅 회사의 영업 전문가입니다.

## 가게 데이터
{context}

## 접근 각도: {angle}

이 각도를 강조하면서 영업 DM을 작성해주세요.
(문단 3-4개, 구체적인 수치/사실 기반, 부드러운 CTA)
"""

        try:
            response = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            dm_text = response.content[0].text
            variations.append(dm_text)

        except Exception as e:
            variations.append(f"오류: {str(e)}")

    return variations


def generate_dm_interactive(place_data: Dict) -> str:
    """
    사용자와 대화하면서 DM을 점진적으로 개선.

    사용자가 피드백을 제공하면 그에 맞춰 DM을 수정.
    """

    if place_data.get('error'):
        return f"가게 데이터 수집 실패: {place_data['error']}"

    context = _build_context(place_data, "주목")

    system_prompt = f"""당신은 온라인 마케팅 회사의 영업 전문가입니다.
아래 가게의 실제 데이터를 기반으로 개인화된 영업 DM을 작성하고 개선합니다.

## 가게 데이터
{context}

사용자의 피드백에 따라 DM을 수정하세요.
- "더 강하게": 문제점 강조 → 긴급함 전달
- "더 부드럽게": 관계 구축 → 신뢰 형성
- "더 짧게": 핵심만
- "더 구체적으로": 수치/사실 추가
"""

    conversation_history = []

    # 초기 DM 생성
    print("초기 DM을 생성 중입니다...\n")

    conversation_history.append(
        {
            "role": "user",
            "content": f"이 가게를 위한 영업 DM을 만들어줘. (문단 3-4개, 구체적인 수치/사실 기반)",
        }
    )

    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=500,
        system=system_prompt,
        messages=conversation_history,
    )

    initial_dm = response.content[0].text
    conversation_history.append({"role": "assistant", "content": initial_dm})

    print("=== 초기 DM ===")
    print(initial_dm)
    print("\n" + "=" * 50 + "\n")

    # 대화 루프
    while True:
        user_input = input("피드백을 입력해주세요 (또는 'exit'로 종료): ").strip()

        if user_input.lower() in ['exit', 'quit', '끝', '나가']:
            break

        conversation_history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=500,
            system=system_prompt,
            messages=conversation_history,
        )

        updated_dm = response.content[0].text
        conversation_history.append({"role": "assistant", "content": updated_dm})

        print("\n=== 수정된 DM ===")
        print(updated_dm)
        print("\n" + "=" * 50 + "\n")

    # 최종 DM 반환
    final_response = conversation_history[-1]["content"]
    return final_response


def _build_context(place_data: Dict, service_package: str) -> str:
    """
    가게 데이터를 Claude 프롬프트용 텍스트로 변환.
    """

    lines = []

    lines.append(f"**가게명**: {place_data.get('name', 'N/A')}")
    lines.append(f"**업종**: {place_data.get('category', 'N/A')}")
    lines.append(f"**주소**: {place_data.get('address', 'N/A')}")
    lines.append("")

    # 평점 정보
    rating = place_data.get('rating')
    review_count = place_data.get('review_count', 0)
    if rating:
        lines.append(f"**평점**: {rating}점 (리뷰 {review_count}개)")
    else:
        lines.append(f"**리뷰**: {review_count}개")

    # 리뷰 통계
    visitor_reviews = place_data.get('visitor_review_count', 0)
    blog_reviews = place_data.get('blog_review_count', 0)
    if visitor_reviews or blog_reviews:
        lines.append(f"  - 방문자 리뷰: {visitor_reviews}개")
        lines.append(f"  - 블로그 리뷰: {blog_reviews}개")
    lines.append("")

    # 사진 정보
    photo_count = place_data.get('photo_count', 0)
    last_photo_date = place_data.get('last_photo_date')
    if photo_count:
        lines.append(f"**사진**: {photo_count}개")
        if last_photo_date:
            lines.append(f"  (최근 업데이트: {last_photo_date})")
    else:
        lines.append("**사진**: 거의 없음")
    lines.append("")

    # 영업시간/가격
    if place_data.get('hours'):
        lines.append(f"**영업시간**: {place_data['hours']}")
    if place_data.get('price_range'):
        lines.append(f"**가격대**: {place_data['price_range']}")
    lines.append("")

    # 약점 (마케팅 앵글 찾기)
    if place_data.get('weakness'):
        lines.append(f"**주요 불만점**: {', '.join(place_data['weakness'])}")
    lines.append("")

    # 키워드 (강점)
    if place_data.get('keywords'):
        lines.append(f"**강점 키워드**: {', '.join(place_data['keywords'])}")
    lines.append("")

    # 서비스 패키지 설명
    package_info = {
        "주목": "사진/콘텐츠 자동 업로드 (월 20만원대) → 사진 부족 문제 해결",
        "집중": "리뷰 응답 + 운영 (월 30만원대) → 리뷰 관리 + 콘텐츠",
        "성장": "광고 + 최적화 (월 50만원대) → 방문 고객 증가",
    }

    if service_package in package_info:
        lines.append(f"**추천 패키지**: {package_info[service_package]}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트 예시

    from naver_crawler import search_place

    print("=== 테스트: 개인화 DM 생성 ===\n")

    # 1. 가게 데이터 수집
    place_data = search_place("강남 스타벅스")

    if place_data and not place_data.get('error'):
        # 2. 기본 DM 생성
        print("1. 기본 DM:")
        print("-" * 50)
        dm = generate_dm(place_data, service_package="주목")
        print(dm)
        print("\n")

        # 3. 여러 변형 생성
        print("2. 변형 DM (3가지 앵글):")
        print("-" * 50)
        variations = generate_dm_with_variations(place_data, num_variations=3)
        for i, var in enumerate(variations, 1):
            print(f"\n[변형 {i}]")
            print(var)

        # 4. 대화형 개선 (선택사항)
        # print("\n3. 대화형 개선:")
        # print("-" * 50)
        # final_dm = generate_dm_interactive(place_data)
        # print("\n최종 DM:")
        # print(final_dm)

    else:
        print(f"가게 정보 수집 실패: {place_data}")
