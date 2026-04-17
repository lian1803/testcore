"""
영업 메시지 자동 생성기
진단 데이터 기반 1차~4차 영업 메시지 생성
원칙: 문제는 확실히 보여주되, 해결법은 절대 안 알려준다
"""
import math
import os
from typing import Dict, Any, List

from config.industry_weights import (
    get_avg_price,
    recommend_package,
    PACKAGES,
    detect_industry,
)


# ─────────────────────────────────────────────────────────────
# 내부 헬퍼
# ─────────────────────────────────────────────────────────────

def _get_total_search_volume(keywords: list) -> int:
    """키워드 목록에서 월 검색량 합산."""
    if not keywords:
        return 2000
    total = 0
    for kw in keywords:
        if isinstance(kw, dict):
            total += kw.get("search_volume", 0)
    return max(total, 2000)


def _eun_neun(word: str) -> str:
    """
    한국어 조사 '은/는' 선택.
    마지막 글자에 받침 있으면 '은', 없으면 '는'.
    """
    if not word:
        return "은"
    last = word[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        return "은" if (code - 0xAC00) % 28 != 0 else "는"
    return "은"


def _get_top_keyword_name(keywords: list) -> str:
    """가장 검색량 높은 키워드 이름 반환."""
    if not keywords:
        return "주요 키워드"
    best = None
    best_vol = -1
    for kw in keywords:
        if isinstance(kw, dict):
            vol = kw.get("search_volume", 0)
            name = kw.get("keyword", "")
            if name and vol > best_vol:
                best_vol = vol
                best = name
        elif isinstance(kw, str) and kw:
            if best is None:
                best = kw
    return best or "주요 키워드"


def _select_first_message_type(data: Dict[str, Any]) -> str:
    """
    1차 메시지 타입 자동 선택.
    A: 리뷰 격차형 (경쟁사 리뷰 >= 내 리뷰 × 3, 경쟁사 데이터 있을 때만)
    B: 순위형 (rank > 10)
    C: 방치형 (새소식 90일+ OR 사진 5장 미만)
    D: Hook형 (카카오톡 채널 없음 AND 인스타 없음 AND 점수 낮음)
    """
    my_review = data.get("review_count", 0)
    competitor_avg_review = data.get("competitor_avg_review", 0)
    rank = data.get("naver_place_rank", 0)
    news_days = data.get("news_last_days", 0)
    photo_count = data.get("photo_count", 0)
    total_score = data.get("total_score", 0)

    # 조건 A: 경쟁사 데이터 있고 리뷰 격차 3배 이상 (최우선 — 숫자 충격 최강)
    if competitor_avg_review > 0 and competitor_avg_review >= my_review * 3:
        return "A"
    # 조건 B: 순위 10위 밖 (실제 수집된 순위 기준)
    if rank > 10:
        return "B"
    # 조건 C: 실제 방치 증거 있을 때만 (bookmark=0은 수집 안 됨이라 제외)
    if news_days >= 90 or photo_count < 5:
        return "C"
    # 기본값: 경쟁사보다 내 리뷰가 적을 때만 A (내 리뷰 > 경쟁사면 충격 역효과)
    if competitor_avg_review > 0 and my_review <= competitor_avg_review:
        return "A"
    if rank > 0:
        return "B"
    # D형: 아무 강한 신호 없고 카카오/인스타도 없고 점수 낮으면 Hook형
    if not data.get("has_kakao", False) and not data.get("has_instagram", False) and total_score < 40:
        return "D"
    return "C"


def _build_missing_items_text(data: Dict[str, Any], max_count: int = 5) -> str:
    """비어있는 항목 텍스트 생성 (최대 5개)."""
    missing = []
    if not data.get("has_hours", False):
        missing.append("영업시간")
    if not data.get("has_menu", False):
        missing.append("메뉴")
    if not data.get("has_price", False):
        missing.append("가격정보")
    if not data.get("has_intro", False):
        missing.append("소개글")
    if not data.get("has_directions", False):
        missing.append("오시는길")
    if data.get("photo_count", 0) < 5:
        missing.append("충분한 사진")
    if data.get("review_count", 0) < 10:
        missing.append("고객리뷰")
    if not data.get("has_owner_reply", False):
        missing.append("사장님답글")

    return ", ".join(missing[:max_count])


# ─────────────────────────────────────────────────────────────
# 메인 생성 함수
# ─────────────────────────────────────────────────────────────

def _build_diagnosis_summary(data: Dict[str, Any]) -> str:
    """
    1차 메시지 하단에 붙는 진단 요약 — 핵심만, 짧게.
    문제만 보여준다. 해결법 없음.
    """
    total_score = data.get("total_score", 0)
    grade = data.get("grade", "D")
    my_photo = data.get("photo_count", 0)
    my_review = data.get("review_count", 0)
    competitor_avg_photo = data.get("competitor_avg_photo", 0)
    competitor_avg_review = data.get("competitor_avg_review", 0)
    estimated_lost = data.get("estimated_lost_customers", 0)
    missing_items = _build_missing_items_text(data, max_count=3)

    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}.get(grade, "🔴")

    lines = [
        "─────────────────",
        f"{grade_emoji} 진단 결과: {total_score:.0f}점 ({grade}등급)",
    ]

    if competitor_avg_photo > 0:
        lines.append(f"📸 사진: {my_photo}장 vs 경쟁사 {competitor_avg_photo}장")
    if competitor_avg_review > 0:
        lines.append(f"⭐ 리뷰: {my_review}개 vs 경쟁사 {competitor_avg_review}개")
    if missing_items:
        lines.append(f"❌ 비어있는 항목: {missing_items}")
    if estimated_lost > 0:
        lines.append(f"💸 월 추정 손실: {estimated_lost}명")

    lines.append("─────────────────")
    return "\n".join(lines)


def generate_first_message(data: Dict[str, Any]) -> Dict[str, str]:
    """
    1차 메시지 생성 — 4가지 버전 (A/B/C/D).
    충격 오프닝 + 진단 요약 바로 포함. "보내드릴까요?" 없음.
    """
    msg_type = _select_first_message_type(data)
    business_name = data.get("business_name", "사장님")
    category = data.get("category", "")
    competitor_avg_review = data.get("competitor_avg_review", 0)
    my_review = data.get("review_count", 0)
    rank = data.get("naver_place_rank", 0)
    total_search = _get_total_search_volume(data.get("keywords", []))
    top_keyword = _get_top_keyword_name(data.get("keywords", []))
    estimated_lost = data.get("estimated_lost_customers", 0)
    news_days = data.get("news_last_days", 0)

    diag = _build_diagnosis_summary(data)

    if msg_type == "A":
        category_str = f"{category} " if category else ""
        opening = (
            f"{business_name} 사장님, 잠깐만요.\n\n"
            f"이 지역 {category_str}검색하면\n"
            f"사장님 리뷰 {my_review}개, 경쟁사 {competitor_avg_review}개예요.\n\n"
        )
        sms = f"{business_name} 리뷰 {my_review}개 vs 경쟁사 {competitor_avg_review}개. 월 {estimated_lost}명 손실 중."
        label = "리뷰 격차형"

    elif msg_type == "B":
        kw_display = top_keyword if top_keyword and top_keyword != "주요 키워드" else (f"{category} {top_keyword}".strip() if category else top_keyword)
        opening = (
            f"{business_name} 사장님, 네이버 '{kw_display}' 검색해보셨어요?\n\n"
            f"지금 {rank}위예요. 1~5위 밖이면 손님 눈에 사실상 없는 거예요.\n\n"
        )
        sms = f"{kw_display} 검색 {rank}위. 월 {total_search:,}명 중 {estimated_lost}명 경쟁사로."
        label = "순위형"

    elif msg_type == "C":
        photo_count = data.get('photo_count', 0)
        if news_days >= 90:
            key_issue = f"새소식이 {news_days}일째 멈춰있어요"
            sms = f"{business_name} 새소식 {news_days}일 미업데이트. 월 {estimated_lost}명 이탈 중."
        elif photo_count < 5:
            key_issue = f"사진이 {photo_count}장밖에 없어요"
            sms = f"{business_name} 사진 {photo_count}장. 월 {estimated_lost}명 경쟁사로."
        else:
            key_issue = f"기본 정보가 비어있어요"
            sms = f"{business_name} 플레이스 기본정보 미완성. 월 {estimated_lost}명 이탈 중."
        opening = (
            f"{business_name} 사장님, {key_issue}.\n\n"
            f"네이버 검색하는 손님들이 그냥 지나치고 있어요.\n\n"
        )
        label = "방치형"

    else:  # D
        category_str = f"{category} " if category else ""
        kw_str = category_str.strip() if category_str else "우리 업종"
        opening = (
            f"{business_name} 사장님, 네이버에서 '{kw_str}' 검색하면\n"
            f"지금 몇 위인지 아세요?\n\n"
            f"상위 업체들, 서비스가 더 좋아서가 아니에요.\n"
            f"플레이스 관리를 하고 있냐 없냐 차이예요.\n\n"
        )
        sms = f"{business_name} 플레이스 진단 완료. 월 {estimated_lost}명 이탈 중."
        label = "방치-Hook형"

    text = opening + diag

    return {
        "type": msg_type,
        "text": text,
        "sms_text": sms,
        "label": label,
    }


def generate_second_message(data: Dict[str, Any]) -> str:
    """
    2차 메시지 — 진단 결과 카톡 카드 형식.
    문제의 규모를 시각적으로 최대한 충격있게.
    """
    business_name = data.get("business_name", "업체")
    total_score = data.get("total_score", 0)
    grade = data.get("grade", "D")
    my_photo = data.get("photo_count", 0)
    my_review = data.get("review_count", 0)
    competitor_avg_photo = data.get("competitor_avg_photo", 0)
    competitor_avg_review = data.get("competitor_avg_review", 0)
    estimated_lost = data.get("estimated_lost_customers", 0)

    # 비어있는 항목 목록
    missing_items = _build_missing_items_text(data, max_count=5)

    # 등급 설명 + 시각적 강조
    grade_symbols = {"A": "✅", "B": "🟢", "C": "🟡", "D": "🔴"}
    grade_desc = {"A": "최상위", "B": "양호", "C": "주의", "D": "위험"}
    grade_label = grade_desc.get(grade, grade)
    grade_symbol = grade_symbols.get(grade, "")

    lines = [
        f"📊 {business_name} 네이버 플레이스 진단",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    # 등급을 크게 강조 (D등급이면 위험 표시)
    if grade == "D":
        lines.append(f"{grade_symbol} {grade}등급 — 위험")
    else:
        lines.append(f"{grade_symbol} {grade}등급 — {grade_label}")

    lines += [
        f"종합 점수: {total_score:.0f}점",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "🔍 현재 상황",
    ]

    # 경쟁사 비교를 격차로 강조
    if competitor_avg_photo > 0:
        gap = competitor_avg_photo - my_photo
        lines.append(f"사진: {my_photo}장 vs 경쟁사 {competitor_avg_photo}장 (-{gap}장)")
    else:
        lines.append(f"사진: {my_photo}장")

    if competitor_avg_review > 0:
        gap = competitor_avg_review - my_review
        lines.append(f"리뷰: {my_review}개 vs 경쟁사 {competitor_avg_review}개 (-{gap}개)")
    else:
        lines.append(f"리뷰: {my_review}개")

    lines += [
        "",
        "⛔ 지금 당장 손님을 놓치는 이유",
        missing_items,
        "",
    ]

    if estimated_lost > 0:
        lines.append("💸 매달 손실")
        lines.append(f"약 {estimated_lost}명이 경쟁사로 가고 있어요")
        lines.append("")

    lines.append("상세 분석 자료 보내드릴 거예요.")

    return "\n".join(lines)


def _get_weak_items(data: Dict[str, Any]) -> List[str]:
    """취약 항목 키 목록 반환."""
    weak = []
    if data.get("photo_score", 100) < 50:
        weak.append("photo")
    if data.get("review_score", 100) < 50:
        weak.append("review")
    if data.get("blog_score", 100) < 50:
        weak.append("blog")
    if data.get("info_score", 100) < 50:
        weak.append("info")
    if data.get("keyword_score", 100) < 50:
        weak.append("keyword")
    if data.get("convenience_score", 100) < 50:
        weak.append("convenience")
    if data.get("engagement_score", 100) < 50:
        weak.append("engagement")
    return weak


def _get_recommended_package(grade: str, weak_items: List[str]) -> str:
    """추천 패키지 반환."""
    return recommend_package(grade, weak_items)


def generate_third_message(data: Dict[str, Any]) -> str:
    """
    3차 메시지 — 패키지 소개 + 손익분기 계산.
    "이 부분만 하면 바뀐다" 메시지 금지.
    """
    category = data.get("category", "")
    avg_price = get_avg_price(category)
    estimated_lost = data.get("estimated_lost_customers", 0)
    grade = data.get("grade", "D")

    weak_items = _get_weak_items(data)
    recommended = _get_recommended_package(grade, weak_items)
    pkg = PACKAGES[recommended]
    plan_price = pkg["price"]
    daily_price = plan_price // 30

    # 손익분기 계산
    breakeven = math.ceil(plan_price / avg_price) if avg_price > 0 else 0

    lines = [
        "사장님, 저희 서비스 설명드릴게요 😊",
        "",
        "━━━━━━━━━━━━━━",
        f"{pkg['emoji']} 추천 플랜: {pkg['label']} (월 {plan_price:,}원 / 하루 약 {daily_price:,}원)",
        f"   {pkg['description']}",
        "━━━━━━━━━━━━━━",
        "",
    ]

    if estimated_lost > 0 and breakeven > 0:
        monthly_loss = estimated_lost * avg_price
        lines += [
            "💰 손익분기 계산",
            f"   월 {plan_price:,}원 ÷ 객단가 {avg_price:,}원",
            f"   = {breakeven}명만 더 오시면 본전이에요",
            "",
        ]
        if monthly_loss >= plan_price:
            lines += [
                f"지금 월 {estimated_lost}명 놓치고 계시니까",
                "첫 달부터 본전 돼요.",
                "",
            ]

    # 3차 메시지 마무리 강화 — 시간 경쟁 의식 + 결단 압박 + 체감 약속
    if estimated_lost > 0 and breakeven > 0:
        lines += [
            "━━━━━━━━━━━━━━━",
            "🚨 지금 경쟁사들이 쌓고 있는 리뷰·사진은",
            "나중에 따라잡기 어려워요.",
            "",
            f"{pkg['label']} 3개월 약정으로 시작할 수 있어요.",
            "2주 안에 플레이스 노출 변화 없으면 말씀해주세요.",
            "",
            "시작하시겠어요?",
        ]
    else:
        lines += [
            "━━━━━━━━━━━━━━━",
            f"{pkg['label']} 3개월 약정으로 시작할 수 있어요.",
            "2주 안에 플레이스 노출 변화 없으면 말씀해주세요.",
            "",
            "시작하시겠어요?",
        ]

    return "\n".join(lines)


def generate_fourth_messages(data: Dict[str, Any]) -> Dict[str, str]:
    """
    4차 메시지 — 4가지 상황별 대응.
    보류/무응답/비싸다/직접 하겠다.
    """
    category = data.get("category", "")
    avg_price = get_avg_price(category)
    estimated_lost = data.get("estimated_lost_customers", 0)
    grade = data.get("grade", "D")

    weak_items = _get_weak_items(data)
    recommended = _get_recommended_package(grade, weak_items)
    pkg = PACKAGES[recommended]
    plan_price = pkg["price"]

    loss_amount = estimated_lost * avg_price if estimated_lost > 0 else 0
    breakeven = math.ceil(plan_price / avg_price) if avg_price > 0 else 0

    business_name = data.get("business_name", "업체")

    # [보류용] — 독점 정책 기반 urgency (저희는 같은 지역 같은 업종 1곳만)
    holdback = (
        "사장님, 한 번 더 말씀드릴게요 😊\n\n"
        "저희는 같은 동네 같은 업종은 1곳만 받아요.\n"
        "먼저 시작하시는 분이 이 지역 독점이에요.\n\n"
        "경쟁 업체가 먼저 시작하면\n"
        "저희가 사장님을 도와드리기 어려워요.\n\n"
        "이번 달 시작하시는 건 어떠세요? 😊"
    )

    # [무응답용] — 독점 정책 + 시간 압박 강화
    no_response = (
        f"사장님, {business_name} 진단 결과 보내드렸는데\n"
        f"못 보셨을까봐요.\n\n"
        f"{grade}등급이에요.\n\n"
        "솔직히 말씀드리면,\n"
        "저희는 같은 동네 같은 업종 1곳만 받아요.\n"
        "이미 근처 경쟁 업체 몇 곳이 문의했어요.\n\n"
        "관심 있으시면 한 마디만 주세요."
    )

    # [비싸다고 할 때] — 손실금액이 패키지 가격보다 클 때만 비교 논리 사용
    if estimated_lost > 0 and loss_amount > plan_price:
        expensive = (
            "그 마음 충분히 이해돼요 😊\n\n"
            "근데 한 가지 생각해봐주세요.\n"
            f"{pkg['label']} 한 달 {plan_price:,}원인데\n"
            f"지금 매달 {estimated_lost}명이 경쟁사로 가고 있고\n"
            f"한 명당 {avg_price:,}원이면\n"
            f"월 {loss_amount:,}원 손실이에요.\n\n"
            "안 하는 게 더 비싼 거죠.\n\n"
            "플레이스 순위는 쌓이는 거라서 최소 3개월은 지켜봐야 결과가 나와요.\n"
            "3개월 끝나고 순위 변화 없으면 1달 무상 연장해드려요 😊"
        )
    else:
        expensive = (
            "그 마음 충분히 이해돼요 😊\n\n"
            "플레이스 순위는 쌓이는 거라서\n"
            "1개월로는 변화 보기가 어려워요.\n\n"
            "저희가 3개월 단위로 하는 것도\n"
            "그 안에 실제 순위 변화를 만들어드리려는 거예요.\n\n"
            "3개월 끝나고 순위 변화 없으면\n"
            "1달 무상 연장해드려요 😊"
        )

    # [직접 해보겠다고 할 때] — 시간 투자 강조
    weak_count = len(weak_items)
    # 약점 개수에 따라 예상 시간 조정 (항목당 3~5시간)
    hours_per_week = max(4, weak_count * 3)

    weak_labels = []
    for item in weak_items:
        label_map = {
            "photo": "사진 촬영/편집",
            "review": "리뷰 관리",
            "blog": "블로그 리뷰 유도",
            "info": "기본 정보 입력",
            "keyword": "키워드 등록",
            "convenience": "편의기능 설정",
            "engagement": "고객 소통",
        }
        weak_labels.append(label_map.get(item, item))

    weak_str = ", ".join(weak_labels[:3])  # 최대 3개만 표시

    diy = (
        "당연히 하실 수 있죠 😊\n\n"
        f"근데 아까 진단에서 항목이 {weak_count}개 나왔는데\n"
        f"({weak_str} 등)\n"
        "하나하나가 다 시간 걸리는 일들이에요.\n\n"
        f"사장님이 직접 하시려면\n"
        f"매주 최소 {hours_per_week}시간은 써야 해요.\n\n"
        "그 시간에 손님 보시는 게 훨씬 나잖아요?\n"
        "저희가 대신 해드릴게요."
    )

    # [전에 해봤는데 효과없었다고 할 때]
    experienced = (
        "어떤 방식이었는지 여쭤봐도 될까요?\n\n"
        "솔직히, 효과없는 방식들이 있어요.\n"
        "단순히 글자 올리거나 광고비 쓰는 거면\n"
        "저도 효과없다고 생각해요.\n\n"
        "저희가 하는 건 달라요.\n"
        "점수가 낮은 항목들을 하나씩 채워가는 거라서\n"
        "2주 안에 플레이스 점수 변화가 눈에 보여요.\n\n"
        "한 번 더 보실래요? 이번엔 다를 거예요."
    )

    return {
        "보류": holdback,
        "무응답": no_response,
        "비싸다": expensive,
        "직접": diy,
        "경험있음": experienced,
    }


def generate_fifth_message(data: Dict[str, Any]) -> str:
    """
    5차 메시지 — '네' 받은 후 결제/계약 안내.
    카톡에서 바로 결제 링크 전달.
    결제 링크는 환경변수(PAYMENT_LINK)에서 읽어옴.

    강화점:
    - 결제 CTA를 더 명확하고 직접적으로
    - 결제 망설임 방지를 위한 보증 멘트 추가 (환불/무상연장)
    - 심리적 안정감 제공 (전담 매니저, 즉시 시작)
    """
    grade = data.get("grade", "D")
    weak_items = _get_weak_items(data)
    recommended = _get_recommended_package(grade, weak_items)
    pkg = PACKAGES[recommended]
    plan_price = pkg["price"]
    business_name = data.get("business_name", "사장님")

    # 환경변수에서 결제 링크 읽기 (기본값: 네이버페이)
    payment_link = os.environ.get("PAYMENT_LINK", "https://pay.naver.com/")

    # 보증 멘트 추가 — 결제 망설임 방지
    warranty_msg = (
        "🛡️ 안심 보증\n"
        f"   • 3개월 시작 후 순위 변화 없으면 1개월 무상 연장\n"
        f"   • 전담 매니저가 주 1회 진행 상황 보고\n"
        f"   • 카톡/전화로 언제든 상담 가능\n"
    )

    return (
        f"그래요! 환영합니다 🎉\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"결제 정보\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{pkg['emoji']} {pkg['label']}: 월 {plan_price:,}원\n"
        f"   {pkg['description']}\n\n"
        f"{warranty_msg}\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"👉 아래 링크에서 지금 결제하세요\n"
        f"{payment_link}\n\n"
        f"✅ 결제 완료 후\n"
        f"   • 오늘 중으로 첫 상담 전화드릴게요\n"
        f"   • 내일부터 작업 시작합니다\n"
        f"   • {business_name} 네이버 플레이스 관리자 권한만 공유해주세요\n\n"
        f"감사합니다! 좋은 결과 만들어드릴게요 😊"
    )


def generate_sixth_message(data: Dict[str, Any]) -> str:
    """
    6차 메시지 — 결제 완료 후 온보딩 안내.
    """
    business_name = data.get("business_name", "사장님")

    return (
        f"결제 확인됐어요! 감사합니다 🎉\n\n"
        f"이번 주 안에 첫 작업 시작할게요.\n\n"
        f"📋 시작 전에 필요한 것\n"
        f"   • 네이버 플레이스 관리자 계정 공유\n"
        f"   • 가게 사진 있으시면 보내주세요\n"
        f"   • 메뉴/가격표 자료 있으면 첨부해주세요\n\n"
        f"궁금한 거 있으면 편하게 카톡 주세요 😊"
    )


def generate_all_messages(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    1~4차 메시지 전체 생성.
    Returns: {
        "first": {"type": "A", "text": "...", "sms_text": "...", "label": "..."},
        "second": "...",
        "third": "...",
        "fourth": {"보류": "...", "무응답": "...", "비싸다": "...", "직접": "..."},
        "recommended_package": "집중",
        "estimated_lost_customers": 45,
    }
    """
    try:
        grade = data.get("grade", "D")
        weak_items = _get_weak_items(data)
        recommended = _get_recommended_package(grade, weak_items)
        estimated_lost = data.get("estimated_lost_customers", 0)

        return {
            "first": generate_first_message(data),
            "second": generate_second_message(data),
            "third": generate_third_message(data),
            "fourth": generate_fourth_messages(data),
            "fifth": generate_fifth_message(data),
            "sixth": generate_sixth_message(data),
            "recommended_package": recommended,
            "estimated_lost_customers": estimated_lost,
        }
    except Exception as e:
        # 생성 실패 시 빈 구조 반환 (진단 자체가 실패하면 안 됨)
        return {
            "first": {
                "type": "A",
                "text": f"메시지 생성 오류: {str(e)}",
                "sms_text": "",
                "label": "오류",
            },
            "second": "",
            "third": "",
            "fourth": {"보류": "", "무응답": "", "비싸다": "", "직접": "", "경험있음": ""},
            "fifth": "",
            "sixth": "",
            "recommended_package": "집중",
            "estimated_lost_customers": 0,
        }
