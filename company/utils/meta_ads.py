import os
import sys
import io
import json
import requests
from datetime import datetime, timedelta
from typing import Optional

# Windows UTF-8 환경 설정
try:
    if sys.stdout and hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except (ValueError, AttributeError):
    pass

import anthropic

# ============================================================================
# Meta Ads Spy & Gap Analysis Module
# ============================================================================

def spy(competitor_name: str, country: str = "KR") -> str:
    """
    Meta Ad Library API로 경쟁사 광고 전부 수집
    - 광고 소재, 후킹 문구, CTA, 집행 기간 분석

    Args:
        competitor_name: 경쟁사 이름
        country: 국가 코드 (기본값: "KR")

    Returns:
        경쟁사 광고 분석 결과 (한국어 텍스트)
    """
    meta_token = os.getenv("META_ACCESS_TOKEN", "").strip()

    if not meta_token:
        return """
[Meta Ads Spy 결과]

⚠️ Meta Access Token 필요합니다.

설정 방법:
1. Meta Business Suite 접속: https://business.facebook.com/
2. 설정 → 액세스 토큰 발급
3. .env 파일에 다음과 같이 추가:
   META_ACCESS_TOKEN=your_token_here

현재 상태: META_ACCESS_TOKEN이 .env에 설정되지 않았습니다.
"""

    try:
        # Meta Ad Library API 호출
        url = "https://graph.facebook.com/v21.0/ads_archive"
        params = {
            "access_token": meta_token,
            "search_terms": competitor_name,
            "ad_type": "ALL",
            "media_type": "ALL",
            "limit": 100,
            "fields": (
                "id,name,ad_snapshot_url,creation_time,first_snapshot_time,"
                "last_snapshot_time,spend_range,currency,media_type,images,video_hashes"
            )
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return f"""
[Meta Ads Spy 결과]

❌ API 호출 실패
상태 코드: {response.status_code}
응답: {response.text[:500]}

다시 시도하거나 토큰을 확인하세요.
"""

        data = response.json()
        ads = data.get("data", [])

        if not ads:
            return f"""
[Meta Ads Spy 결과]

"{competitor_name}" 광고 0개 발견

가능한 이유:
1. Meta Ads Library에서 비공개 광고 (정치/이슈 광고 아님)
2. 최근 30일 내 정지된 광고
3. 정확한 회사명 검색 필요 (예: "네이버" vs "NAVER")

조회된 광고: {len(ads)}개
"""

        # 광고 분석
        analysis = {
            "competitor": competitor_name,
            "total_ads": len(ads),
            "period": f"{datetime.now() - timedelta(days=30)} ~ {datetime.now()}",
            "ads": []
        }

        for ad in ads[:20]:  # 최대 20개만 분석
            ad_info = {
                "id": ad.get("id"),
                "name": ad.get("name", "제목 없음"),
                "created": ad.get("creation_time"),
                "last_seen": ad.get("last_snapshot_time"),
                "media_type": ad.get("media_type"),
                "spend_range": ad.get("spend_range", "정보 없음")
            }
            analysis["ads"].append(ad_info)

        # Claude로 분석 리포트 생성
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)

        prompt = f"""
다음 Meta Ads Library 데이터를 분석하고 경쟁사 광고 전략 리포트를 작성하세요.

데이터:
{analysis_json}

분석할 내용:
1. 경쟁사가 주로 사용하는 후킹 문구 패턴 (예: 긴급성, 혜택, 사회적 증거)
2. CTA (Call-to-Action) 전략 분석
3. 광고 소재 유형 및 빈도
4. 집행 기간 및 지속 시간 패턴
5. 광고 예산 규모 추정
6. 우리가 공략할 수 있는 틈새 (경쟁사가 안 건드린 각도)

출력 형식:
- 명확한 섹션 구분
- 수치와 구체적 사례 포함
- 실행 가능한 인사이트

작성하세요.
"""

        full_response = ""
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                full_response += text

        return f"""
[Meta Ads Spy 결과 — {competitor_name}]

총 광고 수: {len(ads)}개 (최근 30일)
분석 대상: {len(ads[:20])}개

=== 경쟁사 광고 전략 분석 ===

{full_response}
"""

    except requests.exceptions.RequestException as e:
        return f"""
[Meta Ads Spy 결과]

❌ 네트워크 오류: {str(e)}

확인 사항:
1. 인터넷 연결 확인
2. META_ACCESS_TOKEN 유효성 확인
3. 토큰 권한: ads:read, business_management 필요
"""
    except Exception as e:
        return f"""
[Meta Ads Spy 결과]

❌ 예상치 못한 오류: {str(e)}

다시 시도하세요.
"""


def find_gaps(competitors: list[str]) -> str:
    """
    경쟁사 여러 개를 분석해서 그들이 안 건드린 틈새 발견

    Args:
        competitors: 경쟁사 이름 리스트

    Returns:
        틈새 전략 리포트 (한국어 텍스트)
    """
    if not competitors:
        return "경쟁사 리스트가 비어있습니다."

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 각 경쟁사별 spy 실행 (토큰 절약을 위해 간단히)
    competitors_list = ", ".join(competitors)

    prompt = f"""
아래 경쟁사들의 광고 전략을 분석하고, 그들이 놓친 틈새 기회를 찾으세요.

경쟁사: {competitors_list}

분석 관점:
1. 각 경쟁사가 타겟하는 고객층
2. 각 경쟁사의 주요 메시지/포지셔닝
3. 사용하는 채널 및 포맷
4. 가격대 및 프로모션 전략
5. 우리가 공략할 수 있는 틈새 (가격, 타겟, 메시지, 채널)

출력 형식:
## 경쟁사별 전략 요약
- [경쟁사1]: [핵심 포지셔닝]
- [경쟁사2]: [핵심 포지셔닝]
...

## 시장 공백 분석
1. [공백1] - 우리가 할 수 있는 방법
2. [공백2] - 우리가 할 수 있는 방법
...

## 우리의 차별화 전략
- [전략1]
- [전략2]
- [전략3]

구체적이고 실행 가능하게 작성하세요.
"""

    full_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return f"""
[경쟁사 틈새 분석]

분석 대상: {competitors_list}
분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 경쟁사 갭 분석 리포트 ===

{full_response}
"""


def generate_copy(product: str, target: str, pain_point: str) -> str:
    """
    Claude로 광고 카피 자동 생성 (후킹 3가지 버전)

    Args:
        product: 상품명
        target: 타겟 고객층
        pain_point: 고객 pain point

    Returns:
        광고 카피 3가지 버전 (한국어)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""
다음 정보를 바탕으로 Meta/네이버 광고용 고성과 카피 3가지 버전을 생성하세요.

상품: {product}
타겟: {target}
고객 pain point: {pain_point}

각 버전마다 다른 후킹 전략을 사용하세요:
1. 버전A: 긴급성/희소성 기반 ("오늘만!", "재고 소진")
2. 버전B: 혜택/수치 기반 ("70% 만족", "3일 만에 해결")
3. 버전C: 사회적 증거/신뢰 기반 ("1만명 선택", "#1 베스트셀러")

각 버전 구성:
- 헤드라인 (30자 이내, Meta 기준)
- 본문 (100자 이내)
- CTA (10자 이내)
- 심리학적 후킹 설명 (한 줄)

출력 형식:
## 버전A: [전략명]
- 헤드라인:
- 본문:
- CTA:
- 후킹:

## 버전B: [전략명]
...

## 버전C: [전략명]
...

## 추가 팁
- A/B 테스트 순서 추천
- 채널별 맞춤 수정안

구체적이고 즉시 사용 가능하게 작성하세요.
"""

    full_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return f"""
[광고 카피 자동 생성]

상품: {product}
타겟: {target}
Pain Point: {pain_point}

생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 3가지 버전 ===

{full_response}
"""


def audit(account_info: str) -> str:
    """
    광고 계정/광고 현황을 186가지 기준으로 감사 리포트

    Args:
        account_info: 계정 정보 (텍스트 형식)

    Returns:
        감사 리포트 (한국어)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""
다음 광고 계정 정보를 바탕으로 종합 감사 리포트를 작성하세요.

계정 정보:
{account_info}

감사 기준 (주요 항목):

## 1. 계정 설정 (20%)
- 비즈니스 정보 완성도
- 카테고리/업종 정확성
- 연락처/주소 정확성
- 프로필 사진/배경 품질

## 2. 캠페인 구조 (20%)
- 캠페인 명명 규칙
- 광고세트 목표 정의
- 예산 할당 전략
- 일정 설정 적절성

## 3. 타겟팅 (20%)
- 대상 고객층 정의
- 연령/성별/지역 적절성
- 관심사/행동 타겟팅
- 제외 대상 설정

## 4. 소재/크리에이티브 (20%)
- 이미지 품질 및 크기
- 영상 길이 및 형식
- 헤드라인/본문 글자수
- CTA 명확성
- 텍스트 오버레이 비율

## 5. 성과 추적 (20%)
- 픽셀 설치 여부
- 전환 이벤트 설정
- 속성(attribution) 설정
- 리포팅 대시보드 구성

## 출력 형식

### 종합 평가
- 현재 수준: [점수]/100
- 강점 3가지
- 약점 3가지
- 우선 개선 항목 TOP 5

### 항목별 상세 평가
각 항목마다:
- 현재 상태
- 발견된 문제
- 개선 방안 (구체적인 단계)
- 기대 효과

### 실행 로드맵
1주 / 2주 / 1개월 / 3개월 별 실행 계획

구체적인 수치와 예시를 포함하여 작성하세요.
"""

    full_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return f"""
[광고 계정 종합 감사 리포트]

감사 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 186가지 기준 종합 평가 ===

{full_response}
"""


def score(ad_copy: str, target: str) -> str:
    """
    광고 카피 집행 전 0~100점 점수 + 개선 포인트

    Args:
        ad_copy: 광고 카피 텍스트
        target: 타겟 고객층

    Returns:
        점수 + 개선안 (한국어)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""
다음 광고 카피를 평가하고 점수를 매기세요.

광고 카피:
{ad_copy}

타겟: {target}

평가 기준 (각 10점):

1. 후킹 (3초 이내 주목도)
   - 문제/욕구를 명확히 제시했는가?
   - 감정적 반응을 유발하는가?

2. 명확성 (메시지가 명확한가?)
   - 고객이 한 문장으로 이해하는가?
   - 애매한 표현은 없는가?

3. 혜택 제시 (구체적인 이점이 있는가?)
   - 수치/구체성이 있는가?
   - "왜 우리를 선택해야 하는가?" 명확한가?

4. 신뢰도 (신뢰감이 있는가?)
   - 근거/사례가 있는가?
   - 과장이나 거짓이 없는가?

5. CTA (행동 유도가 명확한가?)
   - "지금 구매" / "상담 예약" 등 명확한가?
   - 클릭 유도 문구가 강력한가?

6. 채널 최적화 (매체별 최적화가 되어 있는가?)
   - 글자수 제한 준수 (Meta 40자, 네이버 25자 등)
   - 모바일 최적화 되어 있는가?

7. 타겟 적합도 (타겟 고객에게 어필하는가?)
   - {target} 입장에서 관심 유발하는가?
   - 언어/톤이 적절한가?

8. 차별화 (경쟁사 대비 뭐가 다른가?)
   - 고유한 가치 제안이 있는가?
   - "왜 다른 상품이 아니라 이것인가?" 설득하는가?

9. 긴급성 (지금 해야 한다고 느끼게 하는가?)
   - 시간 제약이 있는가?
   - 한정성/희소성이 있는가?

10. 사용 용이성 (실제로 쓸 수 있는가?)
    - 즉시 복붙 가능한가?
    - 문법/오타는 없는가?

## 출력 형식

### 종합 점수
[점수]/100

### 항목별 점수
1. 후킹: [점수]/10 - [한 줄 평가]
2. 명확성: [점수]/10 - [한 줄 평가]
... (각각)

### 강점 (잘한 점)
- [강점1]
- [강점2]

### 약점 (개선할 점)
- [약점1]
- [약점2]

### 개선안 (구체적인 수정 제안)
```
기존: {ad_copy}
개선: [수정된 카피]
이유: [개선 이유]
```

### 추가 팁
- A/B 테스트 시 어떤 변수와 조합할 것인가?
- 채널별 수정 버전 필요 여부

집행 판단:
- 80점 이상: ✅ 즉시 집행 가능
- 70-79점: ⚠️ 한 두 곳 수정 후 집행
- 70점 미만: ❌ 대폭 리라이팅 필요

구체적이고 실행 가능하게 작성하세요.
"""

    full_response = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return f"""
[광고 카피 점수 평가]

평가 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
타겟: {target}

=== 0-100점 점수 + 개선 포인트 ===

{full_response}
"""


# ============================================================================
# CLI 테스트 함수
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Meta Ads Analysis Module - 테스트 실행")
    print("="*70)

    # 테스트 1: spy
    print("\n[테스트 1] 경쟁사 광고 분석 (spy)")
    print("-" * 70)
    result = spy("네이버")
    print(result[:500] + "...\n")

    # 테스트 2: find_gaps
    print("\n[테스트 2] 경쟁사 틈새 분석 (find_gaps)")
    print("-" * 70)
    result = find_gaps(["네이버", "구글", "카카오"])
    print(result[:500] + "...\n")

    # 테스트 3: generate_copy
    print("\n[테스트 3] 광고 카피 생성 (generate_copy)")
    print("-" * 70)
    result = generate_copy(
        product="AI 마케팅 자동화 플랫폼",
        target="소상공인 사업가",
        pain_point="시간 부족, 광고 효율 낮음"
    )
    print(result[:500] + "...\n")

    # 테스트 4: audit
    print("\n[테스트 4] 광고 계정 감사 (audit)")
    print("-" * 70)
    result = audit("""
    계정명: 한국 음식점
    캠페인: 3개 (브랜드/성과/동적)
    광고: 25개
    월 예산: 500만원
    현황: 3개월 집행, ROAS 2.5배
    문제점: 타겟팅 너무 넓음, 소재 1개만 사용 중
    """)
    print(result[:500] + "...\n")

    # 테스트 5: score
    print("\n[테스트 5] 광고 카피 점수 평가 (score)")
    print("-" * 70)
    result = score(
        ad_copy="지금 50% 할인! 피부 트러블 3일 만에 해결. 지금 구매하기",
        target="20대 여성, 피부 고민 있음"
    )
    print(result[:500] + "...\n")

    print("\n" + "="*70)
    print("✅ 모든 테스트 함수 실행 완료")
    print("="*70)
