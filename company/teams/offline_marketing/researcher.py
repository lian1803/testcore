import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.models import SONAR_PRO

MODEL = SONAR_PRO

# 영업 전문가 자료 수집 쿼리 목록
# 네이버 플레이스 마케팅 대행 카톡 영업 특화
SALES_QUERIES = [
    # ── 타겟 심리 & Pain ──
    "한국 소상공인 미용실 식당 카페 학원 네이버 플레이스 관리 안 하는 이유 Pain Point 실제 인터뷰",
    "소상공인 사장님 마케팅 대행사 거절 이유 Top 5 비싸다 직접한다 효과없다 신뢰문제 실제 사례",
    "경기 북부 양주 포천 의정부 소상공인 디지털 마케팅 인식 수준 실태 조사",
    "네이버 플레이스 순위 낮은 소상공인 매출 손실 실증 데이터 연구",

    # ── 설득 & 클로징 심리학 ──
    "손실 회피 편향 Loss Aversion 영업 활용법 소상공인 대상 구체 사례",
    "앵커링 효과 가격 제시 순서 전략 월구독 서비스 29만 49만 89만 제시법",
    "사회적 증거 Social Proof 소상공인 영업 적용 경쟁사 비교 수치 신뢰 구축",
    "Foot in the Door 기법 소액 첫계약 업셀 전략 월구독 서비스 실전",

    # ── 카카오톡 DM 클로징 ──
    "카카오톡 문자 콜드 DM 소상공인 영업 오픈율 답장률 높이는 첫 문장 한국 2025",
    "비대면 카카오톡 문자만으로 계약 클로징 성공 사례 월구독 서비스",
    "영업 DM 시퀀스 설계 1차~4차 메시지 타이밍 간격 전환율 최적화",
    "카카오페이 청구서 토스 링크 비대면 결제 소상공인 계약 전환율",

    # ── 거절 처리 ──
    "비싸다 거절 처리 손익분기 ROI 설득 소상공인 마케팅 대행 실전 스크립트",
    "직접 하겠다 거절 처리 시간비용 기회비용 설득 자영업자 대상",
    "나중에 생각해볼게요 보류 거절 처리 urgency 만들기 지역 독점 전략",
    "무응답 잠수 고객 재연락 타이밍 방법 B2SMB 영업 실전",

    # ── 네이버 플레이스 마케팅 전문 지식 ──
    "네이버 플레이스 순위 결정 알고리즘 2024 2025 리뷰 사진 정보완성도 가중치",
    "네이버 플레이스 최적화 마케팅 대행 서비스 실제 성과 사례 순위 상승 리뷰 증가",
    "소상공인 네이버 플레이스 경쟁사 분석 방법 차별화 전략 지역 마케팅",
    "네이버 플레이스 마케팅 대행 시장 규모 경쟁사 가격 비교 2025",
]


def _query_single(perplexity: OpenAI, query: str) -> str:
    try:
        resp = perplexity.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "영업/마케팅 전문 리서처야. 실전에서 바로 쓸 수 있는 구체적 인사이트만 뽑아. 이론 설명 최소화, 실전 사례와 수치 위주로."
                },
                {
                    "role": "user",
                    "content": f"다음 주제를 조사해서 핵심만 뽑아줘:\n\n{query}"
                }
            ],
            max_tokens=800,
        )
        return f"### {query}\n\n{resp.choices[0].message.content}\n"
    except Exception as e:
        return f"### {query}\n\n조사 실패: {e}\n"


def run(context: dict, client=None) -> str:
    print("\n" + "="*60)
    print("🔍 리서처 | 영업 전문가 자료 수집 (Perplexity x12)")
    print("="*60)

    industry = context.get("industry", context.get("idea", "소상공인 네이버 플레이스 대행"))

    perplexity = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai",
        timeout=120.0,
    )

    # 업종별 추가 쿼리
    industry_queries = [
        f"{industry} 영업 성공 사례 전환율 높은 멘트 실전",
        f"{industry} 타겟 고객 Pain Point 구매 거절 이유 분석",
    ]
    all_queries = SALES_QUERIES + industry_queries

    print(f"총 {len(all_queries)}개 쿼리 병렬 수집 중...")

    results = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_query = {
            executor.submit(_query_single, perplexity, q): q
            for q in all_queries
        }
        for i, future in enumerate(as_completed(future_to_query), 1):
            q = future_to_query[future]
            result = future.result()
            results[q] = result
            print(f"  [{i}/{len(all_queries)}] 완료: {q[:40]}...")

    full_report = f"# 영업 전문가 자료 수집 보고서\n\n대상 업종: {industry}\n\n"
    for q in all_queries:
        full_report += results.get(q, "") + "\n"

    print("\n✅ 자료 수집 완료")
    return full_report
