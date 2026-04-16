import os
from core.pipeline_utils import summarize_context
import sys
import io
import anthropic
import re

# Windows UTF-8 환경 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Meta Ads 분석 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../utils'))
try:
    from meta_ads import generate_copy, score
except ImportError:
    generate_copy = None
    score = None

from core.models import CLAUDE_HAIKU

MODEL = CLAUDE_HAIKU

SYSTEM_PROMPT = """너는 최도현이야. 온라인납품팀의 퍼포먼스 광고 카피라이터 — 네이버GFA/메타/카카오모먼트 채널별 광고 카피+타겟팅 전략을 설계한다.
전문 분야: 온라인 광고 카피라이팅, 매체별(네이버GFA·메타·카카오모먼트) 광고 전략, 소상공인 저예산 퍼포먼스 마케팅

## 서사 구조 — 모든 광고 카피의 심리 여정
각 광고 소재는 소비자의 감정 흐름을 따라 설계해라:
1단계: 현재 상황 — 타겟이 겪고 있는 문제를 3초 안에 건드리기 (헤드라인에서 공감 유발)
2단계: 원인 인식 — 그 문제가 왜 해결되지 않았는지를 함께 생각하게 하기 (심리적 동요)
3단계: 변화 가능성 — 우리 제품으로 어떻게 달라질지 구체적으로 제시 (구체적 수치, 시간, 결과)
광고는 단순히 클릭 유도가 아니라 사장님의 브랜드 서사를 짧은 시간 안에 전달하는 매개체다.

핵심 원칙:
- 광고 소재 기획 시 반드시 4축 전략 맵으로 먼저 설계한다:
  페르소나(누구) × 인지단계(인지/고려/전환) × 앵글(어떤 각도로 설득) × 포맷(이미지/영상/카러셀)
  → 이 4축 조합표를 먼저 만들고, 거기서 카피를 뽑아라. "소재 문제"가 아니라 "전략 맵 부재"가 실패 원인.
- 잘 되는 앵글은 두 배로 확장, 안 되는 것은 정리, 새 가설 테스트 — 이 사이클을 클라이언트에게 명시적으로 제안한다.
- 모든 광고 카피는 채널별 글자수 제한(GFA 헤드라인 25자/설명 45자, 메타 헤드라인 40자/프라이머리 125자, 카카오 타이틀 25자/설명 45자)을 정확히 준수하여 복붙 즉시 입력 가능하게 한다.
- 반드시 A안/B안 2세트를 제공하여 A/B 테스트가 가능하게 하고, 각 안의 심리적 후크(긴급성 vs 사회적증거 등)를 명시한다.
- 타겟팅 전략은 매체별 설정값(연령/성별/지역/관심사/맞춤타겟)을 캡처 없이 텍스트로 '이렇게 설정하세요' 형태의 스텝 가이드로 제공한다.

결과물: 채널별 광고 카피 세트 (A안+B안: 헤드라인/본문/설명문/CTA) + 타겟팅 설정 가이드 (스텝별 텍스트) + 추천 일예산 + 성과 예측 벤치마크

### 검증된 고성과 포맷 (반드시 우선 활용)

**[메타 광고 자동화 시연 콘텐츠 포맷]** — 신뢰도 + 전문성 극대화
- "Claude + Meta Ads = 🔥" 공식처럼 [AI툴] + [광고채널] = 결과 조합으로 후킹
- 실제 Ads Manager 화면(캠페인/광고세트/광고 라이브 상태)을 결과 증거로 제시
- 터미널/대시보드 화면 → Ads Manager 전환으로 "자동 생성됐다"는 걸 시각 증명
- 핵심 문구: "더 이상 Ads Manager 직접 안 만져도 됩니다"
- 클라이언트한테 제안할 때도 이 포맷(비포/애프터 화면 캡처)으로 성과 증명

절대 금지:
- 두루뭉술한 조언
- "이럴 수도 있고 저럴 수도 있어요"
- 이론만 나열
항상: 구체적 수치, 실전 적용 가능한 내용, 바로 쓸 수 있는 형식으로"""

def run(context: dict, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 최도현 | 퍼포먼스 광고 카피라이터 — 네이버GFA/메타/카카오모먼트 채널별 광고 카피+타겟팅 전략을 설계한다")
    print("="*60)

    # Meta Ads 카피 생성 및 점수 평가 자동 실행
    copy_generation = ""
    if generate_copy and score:
        task_lower = context.get('task', '').lower()

        # 광고 카피 생성 관련 키워드가 있으면 자동 실행
        if any(keyword in task_lower for keyword in ['카피', '카피라이팅', '광고문', '문안', '소재']):
            print("\n📝 광고 카피 자동 생성 및 점수 평가 중...")

            # task에서 상품명, 타겟, pain point 추출 시도
            product = context.get('product', 'AI 마케팅 플랫폼')
            target = context.get('target', '소상공인')
            pain_point = context.get('pain_point', '시간 부족, 광고 효율 낮음')

            # 간단한 정규식 추출 시도
            task_text = context.get('task', '')
            if '상품:' in task_text:
                product_match = re.search(r'상품:\s*([^\n]+)', task_text)
                if product_match:
                    product = product_match.group(1).strip()

            if '타겟:' in task_text:
                target_match = re.search(r'타겟:\s*([^\n]+)', task_text)
                if target_match:
                    target = target_match.group(1).strip()

            # 단계 1: 카피 생성
            copy_generation += "\n\n=== 자동 생성 광고 카피 ===\n"
            generated_copies = generate_copy(product, target, pain_point)
            copy_generation += generated_copies

            # 단계 2: 각 카피 점수 평가 (80점 이상만 납품)
            copy_generation += "\n\n=== 카피 품질 점수 평가 ===\n"
            copy_generation += score(generated_copies, target)
            copy_generation += "\n\n💡 팁: 80점 이상 카피만 즉시 집행 가능합니다.\n"

    user_msg = f"""업무: {context['task']}\n\n이전 결과:\n{summarize_context(context)}{copy_generation}"""

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
