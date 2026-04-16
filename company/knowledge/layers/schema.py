"""
계층형 지식구조 스키마 정의

각 layer는 특정 에이전트 역할에 필요한 정보만 담는다.
- raw: 수집 원본 데이터 (크롤링, 상담 내용)
- entities: 클라이언트 기본정보 (상호명, 업종, 위치, 매출규모 등)
- analyses: 진단 분석 결과 (문제점, 점수, 개선방향)
- concepts: 포지셔닝 + 전략 (타겟 포지셔닝, 마케팅 메시지, 가격 제안)
"""


class RawLayer:
    """원본 데이터 레이어 — 수집된 데이터 그대로"""

    fields = {
        "client_id": "고유 클라이언트 ID",
        "naver_place_url": "네이버 플레이스 URL",
        "naver_place_data": "네이버 플레이스 크롤링 원본 (JSON)",
        "photos": "업체 사진 URL 리스트",
        "reviews": "고객 리뷰 원본 (JSON)",
        "consultation_notes": "상담 기록 원본 텍스트",
        "collected_at": "수집 날짜",
    }


class EntitiesLayer:
    """개체 정보 레이어 — 구조화된 기본정보"""

    fields = {
        "client_id": "고유 ID",
        "business_name": "업체명",
        "industry": "업종 (예: 미용, 카페, 식당)",
        "location": "지역 (시/구)",
        "address": "상세 주소",
        "phone": "전화번호",
        "naver_rank": "네이버 검색 순위 (현재)",
        "review_count": "리뷰 개수",
        "review_score": "평점",
        "operating_years": "영업 연수",
        "estimated_monthly_sales": "추정 월매출",
        "staff_count": "직원 수",
    }


class AnalysesLayer:
    """분석 레이어 — 진단 결과 + 문제점 + 점수"""

    fields = {
        "client_id": "고유 ID",
        "diagnosis_score": "종합 진단 점수 (0~100)",
        "search_visibility_score": "검색 가시성 점수",
        "review_score": "리뷰 점수",
        "content_quality_score": "콘텐츠 품질 점수",
        "main_problems": [
            {
                "problem": "구체적 문제",
                "impact": "미칠 영향 (손실액 추정)",
                "severity": "심각도 (high/medium/low)",
            }
        ],
        "improvement_opportunities": [
            "개선 기회 1",
            "개선 기회 2",
        ],
        "monthly_estimated_loss": "월 추정 손실액 (단위: 원)",
        "analysis_date": "분석 날짜",
    }


class ConceptsLayer:
    """컨셉/전략 레이어 — 포지셔닝 + 메시지 + 제안"""

    fields = {
        "client_id": "고유 ID",
        "target_positioning": "목표 포지셔닝 (예: 강남역 가까운 프리미엄 미용실)",
        "key_messaging": "핵심 메시지 (최대 1줄)",
        "value_proposition": "가치 제안 (고객이 얻는 것)",
        "ideal_customer_profile": "이상적 고객 프로필",
        "pricing_strategy": "가격 전략",
        "marketing_channels": ["추천 마케팅 채널"],
        "3month_plan": "3개월 마케팅 계획 (bullet points)",
        "6month_expected_result": "6개월 기대 효과",
        "recommended_package": "추천 패키지 (주목/집중/시선)",
    }


# 에이전트별 필요 레이어 매핑
AGENT_LAYER_MAP = {
    # PDF 진단서 생성
    "pdf_generator": ["entities", "analyses", "concepts"],

    # DM/영업메시지 작성
    "dm_writer": ["entities", "concepts"],
    "copywriter": ["entities", "analyses", "concepts"],

    # 전략 수립 (이사팀)
    "strategist": ["entities", "analyses"],
    "strategy_designer": ["analyses", "concepts"],

    # 영업 제안
    "proposer": ["entities", "analyses", "concepts"],
    "closer": ["entities", "concepts"],

    # 검증
    "validator": ["analyses", "concepts"],

    # 전체 데이터 (관리자)
    "admin": ["raw", "entities", "analyses", "concepts"],

    # 기본값
    "default": ["entities", "concepts"],
}


def get_layers_for_role(role: str) -> list[str]:
    """에이전트 역할에 맞는 layer 리스트 반환.

    Args:
        role: 에이전트 역할 (예: "pdf_generator", "dm_writer")

    Returns:
        필요한 layer 이름 리스트 (예: ["entities", "analyses"])
    """
    return AGENT_LAYER_MAP.get(role, AGENT_LAYER_MAP["default"])


def validate_layer(layer_name: str) -> bool:
    """유효한 layer 이름인지 검증."""
    valid_layers = ["raw", "entities", "analyses", "concepts"]
    return layer_name in valid_layers
