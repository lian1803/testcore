import os
from core.pipeline_utils import summarize_context
import sys
import io
import anthropic

# Windows UTF-8 환경 설정 (runner에서 이미 처리됐으면 스킵)
if not os.environ.get("_LIANCP_UTF8_DONE"):
    try:
        if sys.stdout and hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except (ValueError, AttributeError):
        pass

# Meta Ads 분석 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../utils'))
try:
    from meta_ads import audit
except ImportError:
    audit = None

MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """너는 이진단이야. 온라인영업팀의 업체별 온라인 현황 무료 진단서 자동 생성 전문가.
전문 분야: 네이버플레이스·인스타그램·블로그·광고 4대 채널 점수화 진단, 경쟁업체 비교 분석, 예상 개선효과 수치화

핵심 원칙:
- 진단서는 반드시 4대 채널(네이버플레이스/인스타그램/블로그/광고) 각각 100점 만점 점수와 총점 400점 체계로 구성한다. 감이 아니라 체크항목별 배점으로 누구나 동일하게 채점 가능해야 한다
- 경쟁업체 비교는 반드시 포함한다. 해당 업체의 동일 업종·동일 지역 상위 3개 업체와 비교하여 격차를 시각적으로 보여준다
- 예상 개선효과는 구체적 수치로 제시한다. '네이버플레이스 최적화 시 월 방문자 약 30-50% 증가 예상' 등 업종별 평균 데이터 기반 추정치를 반드시 포함한다

결과물: 업체별 온라인 현황 진단서(PDF 레이아웃 텍스트): 표지(업체명+진단일자) → 총점 요약(4채널 레이더차트 텍스트 설명) → 채널별 상세 점수(항목별 배점표) → 경쟁업체 비교표 → 핵심 문제점 TOP3 → 개선 시 예상 효과(수치) → '다음 단계: 무료 30분 상담 예약' CTA

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 이진단 | 업체별 온라인 현황 무료 진단서 자동 생성 전문가")
    print("="*60)

    # Meta Ads 감사 자동 실행 (광고 계정 정보가 있으면)
    audit_analysis = ""
    if audit:
        task_lower = context.get('task', '').lower()

        # 광고 관련 키워드가 있으면 audit 실행
        if any(keyword in task_lower for keyword in ['광고', '계정', '감사', 'ads', '메타']):
            print("\n🔍 광고 계정 종합 감사 중...")

            # context에서 계정 정보 추출
            account_info = str(context)[:1000]  # 첫 1000자까지 계정 정보로 간주

            audit_analysis = f"\n\n=== 광고 계정 종합 감사 결과 ===\n"
            audit_analysis += audit(account_info)

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}{audit_analysis}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": user_msg}],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response
