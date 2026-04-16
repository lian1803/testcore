import re
import anthropic
from core.model_loader import get_model
from core.context_loader import inject_context

MODEL = get_model("sieun")


def _safe(text: str) -> str:
    # surrogate pair 제거 + NUL 바이트 제거
    text = re.sub(r'[\ud800-\udfff]', '', text)
    text = text.replace('\0', '')
    return text

COMMERCIAL_KEYWORDS = ["상용화", "판매", "구독", "유료", "월정액", "수익", "고객", "사장님", "사업"]
PERSONAL_KEYWORDS = ["내가 쓸", "나만 쓸", "혼자 쓸", "개인용", "개인툴"]
SOFTWARE_KEYWORDS = ["앱", "서비스", "웹", "플랫폼", "개발", "소프트웨어", "툴", "시스템", "API", "자동화", "봇", "사이트", "프로그램", "기능", "배포"]
OFFLINE_KEYWORDS = ["오프라인", "영업", "방문", "대면", "전화", "소상공인", "마케팅 대행", "DM", "문자"]


def _detect_commercial(text: str) -> bool:
    """개인툴 키워드가 있으면 False, 상용화 키워드가 있으면 True, 둘 다 없으면 False."""
    for kw in PERSONAL_KEYWORDS:
        if kw in text:
            return False
    for kw in COMMERCIAL_KEYWORDS:
        if kw in text:
            return True
    return False


def _detect_software(text: str) -> bool:
    """소프트웨어 개발 프로젝트인지 감지. 오프라인 영업 키워드가 있으면 False."""
    for kw in OFFLINE_KEYWORDS:
        if kw in text:
            return False
    for kw in SOFTWARE_KEYWORDS:
        if kw in text:
            return True
    return False


SYSTEM_PROMPT = """너는 시은이야. 리안 컴퍼니의 오케스트레이터이자 리안의 가장 가까운 AI 동료야.

리안은 온·오프라인 마케팅 회사를 운영하는 CEO야. 개발자는 아니야.
아이디어는 엄청 많은데 혼자서 기획·개발·마케팅을 다 할 시간이 없어.

네 역할:
1. 리안이 던진 아이디어를 받아서 루트를 감지한다
2. 루트에 맞는 명확화 질문을 해 (최대 2번)
3. 말투는 친근하게. 짧고 핵심만. 리안이 피곤하지 않게.

## 루트 감지 (아이디어 받으면 즉시 판단)

### 루트1 — 마케팅 대행 사업
키워드: 셀러, 소상공인, 블로그 대행, 인스타 대행, 마케팅, 콘텐츠 납품
→ 명확화 질문:
  1. 타겟이 누구야? (쿠팡 셀러? 스마트스토어? 어떤 업종?)
  2. 우리 상품은 뭐야? (블로그만? 인스타+블로그? 풀패키지?)
  → 답 나오면: 타겟/상품/가격/아웃리치채널/자체마케팅계획 5가지로 정리해서 이사팀 넘김

### 루트2 — SaaS / 플랫폼 / 개발
키워드: 앱, 서비스, 플랫폼, 자동화 툴, SaaS, 웹사이트, 시스템
→ 명확화 질문:
  1. 타겟이 누구야? (소상공인이랑 마케터를 이어주는 플랫폼? 우리 서비스 홍보 사이트? SaaS?)
  2. 핵심 기능이 딱 하나라면 뭐야?
  → 답 나오면: 타겟/핵심기능/경쟁사/수익모델 4가지로 정리해서 이사팀 넘김

### 루트3 — 오프라인 / 대면 영업
키워드: 직접 방문, 대면, 소상공인 영업, 카톡
→ 오프라인 마케팅팀 파이프라인으로 연결

명확화가 끝나면 이렇게 마무리해:
"알겠어. [루트N] 기반으로 이사팀한테 넘길게. [진행해] 입력하면 시작해."

## ── 린스타트업_적용원칙 ──
아이디어 명확화와 팀 설계를 위해 리안과 함께할 때, 나는 먼저 그가 솔루션 자체에 빠지기보다 '문제'에 사랑에 빠지도록 유도해야 한다. 솔루션은 얼마든지 바뀔 수 있지만, 고객의 '진짜 문제'는 영원하다. 이를 위해 리안에게 고객이 진짜 아파하는 Top 3 문제가 무엇인지, 그리고 현재 그 문제를 어떻게 해결하고 있는지(기존 대안)를 구체적으로 물어보도록 가이드할 것이다. 이때 "이런 서비스가 있다면 쓰시겠어요?"와 같은 미래 지향적인 질문 대신, "지난주에 이 문제가 생겼을 때 어떻게 하셨어요?"처럼 과거의 실제 '행동'을 묻는 질문을 통해 고객의 의견이 아닌 약속을 받아낼 수 있도록 한다. 고객이 자신의 현재 현실을 '소유'하게 함으로써, 해결책이 메워야 할 '간극'을 명확히 하는 것이 중요하다.

리안과의 인터뷰를 통해 다음과 같은 4가지 핵심 가설을 파악해야 한다. 첫째, **고객 가설**은 "누구의 문제를 풀 것인가?"를 명확히 하는 것이다. '모든 사람'이 아닌 '매일 점심 메뉴 고르는 데 10분 이상 쓰는 1인 가구 직장인'처럼 구체적인 얼리어답터를 특정하도록 한다. 둘째, **문제 가설**은 "고객이 정말 아파하는 Top 3 문제는 무엇이며, 지금은 어떻게 해결하고 있는가?"이다. 기존 대안이 없다면 문제가 없거나 아직 발견하지 못한 것일 수 있다. 셋째, **솔루션 가설**은 "우리의 최소한의 해결책(Top 3 기능)이 고객의 문제를 효과적으로 해결하며, 왜 기존 대안과 다른 고유한 가치를 제공하는가?"이다. 넷째, **비즈니스 가설**은 "이 솔루션이 고객에게 도달하고 지속 가능한 형태로 수익을 창출할 수 있는가?"를 포함하며, 초기에는 채널, 수익 모델, 비용 구조 등에 대한 가설을 세운다.

BML(Build-Measure-Learn) 루프 관점에서 MVP(최소 기능 제품) 범위를 좁히도록 리안을 유도하기 위해서는, '만들기(Build)'부터 시작하는 일반적인 함정을 피하고 '배우기(Learn)'에서 시작하여 '측정하기(Measure)'를 거쳐 '만들기(Build)'로 이어지는 역순의 사고방식을 강조해야 한다. "우리가 무엇을 배워야 하는가? -> 그것을 측정하기 위해 무엇이 필요한가? -> 그 측정을 위해 무엇을 만들어야 하는가?"의 흐름이다. MVP는 '배우고 싶은 것을 발견하기 위한 최소한의 작업'임을 인지시키고, 완성된 제품을 만드는 것이 아니라 가장 위험한 가설을 검증하는 도구임을 강조한다. 특히 'Demo-Sell-Build' 순서를 통해 고객이 구매 의사를 밝힌 후에 제품을 만들도록 유도한다. 데모는 실제 작동하는 제품이 아니라 피그마 목업, 스크린샷, 심지어 말로 설명하는 것만으로도 충분하며, 그 목적은 고객을 감동시키는 것이 아닌 '구매를 유발하는 것'임을 명확히 한다. 처음에는 10명 정도의 소수 고객에게 '컨시어지 MVP'처럼 직접 서비스를 제공하며 가치를 검증한 후 점차 확장하는 '10X 롤아웃 전략'을 제안한다.

GO/NO-GO 결정을 위한 '검증된 학습' 기준을 체크할 때는 '말이나 느낌'이 아닌 '행동의 변화'만이 진짜 학습의 증거임을 명확히 한다. "좋아요 100개"보다 "결제 1건"이 더 중요한 진짜 검증임을 강조하고, 단순한 총 가입자 수 같은 '허영 지표'가 아닌 '유료 전환율'이나 '7일 후 재방문율' 같은 '실행 지표'에 집중해야 한다. 솔루션 인터뷰의 유일한 성공 기준은 "고객이 돈을 내겠다고 했는가"이다. 만약 반복된 실험에도 불구하고 핵심 지표가 움직이지 않거나 유료 전환이 0에 가깝다면 과감한 피봇을 고려해야 한다. 반대로 소수라도 제품에 열광하는 고객이 존재하고 핵심 지표가 조금씩 개선된다면, 아직 검증되지 않은 가설이 남아있을 가능성을 열어두고 인내하며 학습을 이어나가야 한다.
"""

DIRECTION_PROMPT = """너는 시은이야. 리안과 나눈 대화를 바탕으로 내가 이해한 방향을 딱 4줄로 요약해줘.

형식 (반드시 이 형식 그대로):
✅ 내가 이해한 방향

- 타겟: (한 줄)
- 핵심 기능: (한 줄, 제일 중요한 것 하나만)
- 수익 모델: (한 줄)
- 제외할 것: (한 줄, MVP에 안 들어가는 것)

이 방향 맞아? [맞아 / 아니 (수정 내용)]
"""


def clarify(idea: str, client: anthropic.Anthropic) -> str:
    print("\n" + "="*60)
    print("🤖 시은 | 오케스트레이터")
    print("="*60)

    messages = [{"role": "user", "content": f"아이디어: {idea}"}]
    full_response = ""

    with client.messages.stream(
        model=MODEL,
        max_tokens=600,
        system=inject_context(SYSTEM_PROMPT),
        messages=messages,
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response.encode("utf-8", errors="replace").decode("utf-8")


def ask_clarification(idea: str, prev_answer: str, question: str, client: anthropic.Anthropic) -> str:

    print("\n" + "="*60)
    print("🤖 시은 | 오케스트레이터")
    print("="*60)

    messages = [
        {"role": "user", "content": f"아이디어: {idea}"},
        {"role": "assistant", "content": question},
        {"role": "user", "content": prev_answer},
    ]
    full_response = ""

    with client.messages.stream(
        model=MODEL,
        max_tokens=600,
        system=inject_context(SYSTEM_PROMPT),
        messages=messages,
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()
    return _safe(full_response)


def confirm_direction(idea: str, conversation: list, client: anthropic.Anthropic) -> str:
    """대화 내용 기반으로 방향 요약 생성 후 리안 컨펌."""
    print("\n" + "="*60)
    print("🤖 시은 | 방향 확인")
    print("="*60)

    safe_conv = [{"role": m["role"], "content": _safe(m["content"])} for m in conversation]
    messages = safe_conv + [{"role": "user", "content": "지금까지 대화 바탕으로 방향 요약해줘."}]
    summary = ""

    with client.messages.stream(
        model=MODEL,
        max_tokens=300,
        system=inject_context(DIRECTION_PROMPT),
        messages=messages,
        temperature=0,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            summary += text

    print("\n\n리안: ", end="")
    try:
        answer = input().strip()
    except EOFError:
        answer = ""

    return _safe(summary), answer


def run(idea: str, client: anthropic.Anthropic, interactive: bool = True) -> dict:
    """
    시은과 대화하며 아이디어 명확화 + 방향 컨펌.
    interactive=False이면 input() 없이 자동 진행.
    returns: {"idea": str, "clarified": str, "is_commercial": bool}
    """
    response = clarify(idea, client)
    conversation = [
        {"role": "user", "content": f"아이디어: {idea}"},
        {"role": "assistant", "content": response},
    ]

    if interactive:
        # 진행해 포함된 경우 바로 방향 확인으로
        if not ("[진행해]" in response or "진행해" in response.lower()):
            # 첫 번째 명확화 질문
            print("\n리안: ", end="")
            try:
                answer1 = input().strip()
            except EOFError:
                answer1 = ""
            if not answer1:
                answer1 = "그냥 진행해줘"

            conversation.append({"role": "user", "content": answer1})
            response2 = ask_clarification(idea, answer1, response, client)
            conversation.append({"role": "assistant", "content": response2})

            if not ("[진행해]" in response2 or "진행해" in response2.lower()):
                # 두 번째 명확화 질문
                print("\n리안: ", end="")
                try:
                    answer2 = input().strip()
                except EOFError:
                    answer2 = ""
                if not answer2:
                    answer2 = "그냥 진행해줘"
                conversation.append({"role": "user", "content": answer2})

        # 방향 확인 루프 (최대 3번)
        for _ in range(3):
            summary, confirm = confirm_direction(idea, conversation, client)

            if not confirm or confirm.lower() in ("맞아", "ㅇㅇ", "ok", "good", "진행해", ""):
                break

            conversation.append({"role": "user", "content": f"수정: {confirm}"})
            response_fix = ask_clarification(idea, confirm, summary, client)
            conversation.append({"role": "assistant", "content": response_fix})

    clarified = "\n".join([
        m["content"] for m in conversation if m["role"] == "user"
    ])
    is_commercial = _detect_commercial(clarified)
    is_software = _detect_software(clarified)

    return {"idea": idea, "clarified": clarified, "is_commercial": is_commercial, "is_software": is_software}


BIG_PICTURE_PROMPT = """너는 시은이야. 이사팀이 방금 GO 판정을 냈어.

근데 너는 오케스트레이터야. 이 프로젝트 하나만 보면 안 돼.
리안이 운영하는 전체 회사 맥락에서 "이 프로젝트를 시작하면 뭐가 더 필요한지" 생각해야 해.

분석할 것:
1. 이 사업이 성공하려면 어떤 인프라가 필요한가? (홈페이지, SNS, 블로그, 포트폴리오 등)
2. 현재 진행중인 다른 프로젝트들과 어떻게 연결되는가? (시너지, 공유 자원 등)
3. 지금 당장 없으면 손해인 것들은 뭔가?
4. 리안이 미처 생각 못 했을 것들은?

출력 형식:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
시은의 큰그림 체크
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[프로젝트명]을 시작하면 이것도 필요해:

🔴 지금 당장 필요 (없으면 손해):
- [항목]: [왜 필요한지 한 줄]

🟡 곧 필요 (초기 3개월 내):
- [항목]: [왜 필요한지 한 줄]

🔗 다른 프로젝트와 연결:
- [연결 고리 설명]

💡 리안이 놓쳤을 것:
- [뜻밖의 제안]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
짧고 핵심만. 리안이 "아 맞다!" 할 것들만."""


def big_picture_check(context: dict, client) -> str:
    """GO 결정 후 연결 고리 + 빠진 것 자동 제안."""
    print("\n" + "="*60)
    print("🌐 시은 | 큰그림 체크")
    print("="*60)

    # PROJECTS.md 읽기 시도 (있으면 참고)
    import os
    projects_context = ""
    projects_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "PROJECTS.md")
    try:
        with open(projects_path, encoding="utf-8") as f:
            projects_context = f.read()[:1500]
    except Exception:
        pass

    idea = context.get("clarified", context.get("idea", ""))
    verdict = context.get("verdict", "GO")
    score = context.get("score", "")

    user_msg = f"""방금 GO 판정 난 프로젝트:
{idea}

판정: {verdict} ({score}점)

현재 진행중인 다른 프로젝트들:
{projects_context if projects_context else "(PROJECTS.md 없음)"}

이 프로젝트 시작하면 뭐가 더 필요한지 큰그림으로 봐줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=600,
        system=inject_context(BIG_PICTURE_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()
    return _safe(full_response)


TEAM_INTERVIEW_PROMPT = """너는 시은이야. 이사팀 분석이 끝났고, 이제 실행할 팀을 설계해야 해.
그 전에 리안한테 실제 워크플로우를 파악해야 해.

리안은 비개발자 CEO야. 짧고 친근하게 물어봐.

물어봐야 할 것:
- 이 일을 지금 실제로 어떻게 하고 있는지 (어떤 프로그램, 어떤 사이트)
- 뭐가 수동이고 뭐가 자동인지
- 제일 시간 많이 걸리는 / 귀찮은 부분
- 혹시 특수한 도구나 프로그램이 있는지

3~4개 질문을 한 번에 물어봐. 리안이 한 번에 답할 수 있게.
마지막에 "이거 답해주면 팀 설계 바로 들어갈게!" 넣어."""


def interview_for_team(context: dict, client: anthropic.Anthropic, interactive: bool = True) -> str:
    """팀 설계 전 리안 워크플로우 파악 인터뷰. interactive=False면 input() 없음."""
    print("\n" + "="*60)
    print("🤖 시은 | 팀 설계 전 인터뷰")
    print("="*60)

    idea = context.get("clarified", context.get("idea", ""))
    board_summary = f"""프로젝트: {idea}
트렌드: {context.get('taeho', '')[:200]}
시장: {context.get('seoyun', '')[:200]}
전략: {context.get('minsu', '')[:200]}"""

    # 시은이 질문
    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=inject_context(TEAM_INTERVIEW_PROMPT),
        messages=[{"role": "user", "content": f"이사팀 분석 결과:\n{board_summary}"}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    # 리안 답변 받기 (자동파일럿이면 input() 안 함)
    answer = ""
    if interactive:
        print("\n\n리안: ", end="")
        try:
            answer = input().strip()
        except EOFError:
            answer = ""
    if not answer:
        answer = "그냥 알아서 해줘"

    # 추가 질문 필요하면 1번 더
    follow_up = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=300,
        system=inject_context("너는 시은이야. 리안 답변을 듣고 추가로 궁금한 게 있으면 1~2개만 짧게 물어봐. 충분하면 '알겠어, 팀 설계 들어갈게!'라고 해."),
        messages=[
            {"role": "user", "content": f"질문: {full_response}\n\n리안 답변: {answer}"}
        ],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            follow_up += text

    # 추가 질문이 있으면 답변 한 번 더 (자동파일럿이면 input() 안 함)
    extra_answer = ""
    if interactive and "?" in follow_up and "팀 설계 들어갈게" not in follow_up:
        print("\n\n리안: ", end="")
        try:
            extra_answer = input().strip()
        except EOFError:
            extra_answer = ""

    interview_result = f"리안 워크플로우:\n{answer}"
    if extra_answer:
        interview_result += f"\n추가 정보:\n{extra_answer}"

    print()
    return interview_result


TEAM_DESIGN_PROMPT = """너는 시은이야. 이사팀 분석이 끝났어.
이제 이 프로젝트를 실행할 전문 팀을 설계해야 해.

이사팀 결과(시장조사, 전략, 검증, Go/No-Go)를 바탕으로:
1. 이 프로젝트에 필요한 팀 이름
2. 이 팀이 해야 할 구체적 업무 (교육팀이 이걸 보고 에이전트를 구성함)

반드시 다음 형식으로만 출력해:

[팀 이름]
(한 줄, 프로젝트 성격을 반영한 이름)

[팀 업무]
(5줄 이내, 이 팀이 해야 할 구체적 업무. 교육팀이 이걸 읽고 에이전트를 뽑아서 교육시킴.
기획, 개발, 마케팅, 영업 등 이 프로젝트에 실제로 필요한 것만 포함.)"""


def design_team(context: dict, client: anthropic.Anthropic) -> tuple[str, str]:
    """이사팀 결과를 바탕으로 전문 팀 구성 설계."""
    print("\n" + "="*60)
    print("🤖 시은 | 팀 구성 설계")
    print("="*60)

    interview = context.get("interview", "")
    feedback = context.get("team_feedback", "")
    summary = f"""프로젝트: {context.get('idea', '')}
명확화: {context.get('clarified', '')[:500]}
리안 워크플로우 (인터뷰): {interview[:500]}
트렌드: {context.get('taeho', '')[:300]}
시장조사: {context.get('seoyun', '')[:500]}
전략: {context.get('minsu', '')[:500]}
검증: {context.get('haeun', '')[:300]}
Go/No-Go: {context.get('verdict', '')} (점수: {context.get('score', '')})
판단 근거: {context.get('junhyeok_text', '')[:300]}"""
    if feedback:
        summary += f"\n\n⚠️ 리안 피드백 (반드시 반영): {feedback}"

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=500,
        system=inject_context(TEAM_DESIGN_PROMPT),
        messages=[{"role": "user", "content": summary}],
        temperature=0,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()

    # 팀 이름과 업무 파싱
    lines = full_response.strip().split("\n")
    team_name = ""
    team_purpose = ""
    parsing_purpose = False

    for line in lines:
        line = line.strip()
        if "[팀 이름]" in line:
            continue
        elif "[팀 업무]" in line:
            parsing_purpose = True
            continue
        elif not parsing_purpose and not team_name and line:
            team_name = line
        elif parsing_purpose and line:
            team_purpose += line + "\n"

    if not team_name:
        team_name = context.get("idea", "프로젝트")[:20] + "_팀"
    if not team_purpose:
        team_purpose = context.get("clarified", "")

    print(f"\n\n📋 팀 이름: {team_name}")
    print(f"📋 팀 업무: {team_purpose.strip()[:100]}...")

    return team_name.strip(), team_purpose.strip()


# ── 자동파일럿 모드 ──────────────────────────────────────────────

AUTOPILOT_CLARIFY_PROMPT = """너는 시은이야. 리안 컴퍼니의 오케스트레이터야.

리안이 아이디어를 던졌어. 리안한테 질문하지 마. 네가 알아서 명확화해.
회사 컨텍스트를 보면 리안이 어떤 사람이고, 회사가 뭐하는지, 뭘 가지고 있는지 다 나와있어.

네가 할 것:
1. 아이디어가 대행 사업인지 SaaS인지 판단
2. 타겟이 누군지 추론 (회사 컨텍스트 기반)
3. 핵심 기능/서비스가 뭔지 정리
4. 수익 모델 추론
5. 우리 자산 중 활용할 수 있는 것
6. **STEP 0 변수 추출** (서윤이 시장조사에서 검색 범위 좁힐 때 사용)

출력 형식:
## 시은의 자동 명확화
- 유형: [대행 사업 / SaaS / 자동화 툴 / 기타]
- 타겟: [구체적으로]
- 핵심: [한 줄]
- 수익 모델: [추론]
- 우리 자산 활용: [naver-diagnosis, 온라인팀 등]
- 상용화 여부: [상용화 / 개인 툴]

### STEP 0 변수 (서윤 Phase 1 검색용)
- **DOMAIN**: [한 단어 — 예: "인테리어 견적 자동화", "토지 사업성 분석", "마케팅 대시보드"]
- **SUB_DOMAINS**: [세부 카테고리 3~5개 — 예: ["견적서 자동화", "자재 추천", "공기 산출"]]
- **REGION**: [한국 / 미국 / 글로벌 — 주 타겟 지역]
- **TARGET_SEGMENT**: [B2B / B2C / SMB / B2B2C 중 선택 + 구체적 페르소나]
- **DOMAIN_COMMUNITIES**: [해당 도메인 커뮤니티 3~5개 — 네이버 카페/Reddit/Discord 등]
- **OKR 추정**:
  - Objective: [한 문장 — 북극성 지표]
  - KR1: [측정 가능한 목표]
  - KR2: [측정 가능한 목표]
  - KR3: [측정 가능한 목표]

확신이 없는 부분은 "추정:" 표기. 절대 리안한테 질문하지 마."""


def autopilot_run(idea: str, client: anthropic.Anthropic) -> dict:
    """자동파일럿 모드 — input() 없이 회사DNA 기반으로 자동 명확화."""
    print("\n" + "="*60)
    print("🤖 시은 | 자동파일럿 명확화")
    print("="*60)

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1500,
        system=inject_context(AUTOPILOT_CLARIFY_PROMPT),
        messages=[{"role": "user", "content": f"아이디어: {idea}"}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()

    clarified = f"아이디어: {idea}\n\n{full_response}"
    is_commercial = _detect_commercial(clarified)
    is_software = _detect_software(clarified)

    return {
        "idea": idea,
        "clarified": clarified,
        "is_commercial": is_commercial,
        "is_software": is_software,
        "autopilot": True,
    }


def autopilot_interview(context: dict, client: anthropic.Anthropic) -> str:
    """자동파일럿 인터뷰 — 리안한테 안 물어보고 회사DNA로 추론."""
    print("\n" + "="*60)
    print("🤖 시은 | 자동파일럿 워크플로우 추론")
    print("="*60)

    system = """너는 시은이야. 팀 설계를 위해 리안의 워크플로우를 파악해야 하는데,
리안한테 직접 물어보지 않고 회사 컨텍스트에서 추론해.

회사 컨텍스트를 보면 리안이 뭘 하고 있고, 어떤 자산이 있고, 어떤 채널을 쓰는지 나와있어.
이걸 기반으로 이 프로젝트의 실제 워크플로우를 추론해서 정리해줘.

출력: "추론된 리안 워크플로우:" + 구체적 내용 5줄 이내"""

    idea = context.get("clarified", context.get("idea", ""))
    board_summary = f"""프로젝트: {idea}
트렌드: {context.get('taeho', '')[:200]}
시장: {context.get('seoyun', '')[:200]}
전략: {context.get('minsu', '')[:200]}"""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=inject_context(system),
        messages=[{"role": "user", "content": f"이사팀 분석 결과:\n{board_summary}"}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()
    return _safe(full_response)


# ── 시은 재검토 (델타봇 패턴) ──────────────────────────────────────

REVIEW_PROMPT = """너는 시은이야. 이사팀 분석이 모두 끝났어.

근데 여기서 멈추면 안 돼. 한 발 물러서서 전체를 다시 봐야 해.

네가 할 것:
1. 내가 처음에 명확화한 방향이 현재 상황과 일치하는지 체크
2. 민수(전략), 하은(검증), 토론 결과에서 새로운 인사이트가 나왔는지 확인
3. 초기 명확화와 최종 분석이 맞지 않으면 "여기가 안 맞아" 지적
4. 없으면 "일관성 있어" 승인
5. 최종 context 제안 (다음 단계로 넘어갈 때 이걸 기준으로)

체크할 것:
- 타겟 고객이 처음과 같은지
- 핵심 기능이 처음과 같은지, 아니면 더 정제됐는지
- 수익 모델이 현실적인지
- 경쟁사/시장 조건이 이전 가정과 일치하는지
- 놓친 risk가 있는지

출력 형식:
## 시은의 최종 재검토

✅ 방향 일관성: [일관 / 부분 수정 필요 / 전면 수정]

📊 초기 vs 최종 비교:
| 항목 | 초기 명확화 | 최종 분석 | 일치 여부 |
|------|----------|---------|---------|

🔴 불일치 항목 (있으면만):
- [항목]: [초기] → [최종] (수정 사유)

💡 새로운 인사이트:
- [토론/검증에서 나온 새로운 것]

⚠️ 추가 risk:
- [새로 발견된 risk]

🚀 최종 승인:
[일관 / 부분 수정 / 전면 재검토 필요]"""


def review(context: dict, client: anthropic.Anthropic) -> dict:
    """모든 에이전트 결과 종합 검토 — 놓친 사항 + 일관성 체크."""
    print("\n" + "="*60)
    print("🔍 시은 | 최종 재검토 (델타봇 패턴)")
    print("="*60)

    # context에서 핵심 정보 추출
    idea = context.get("idea", "")
    clarified = context.get("clarified", "")
    minsu = context.get("minsu", "")
    haeun = context.get("haeun", "")
    discussion = context.get("discussion_transcript", [])
    junhyeok_text = context.get("junhyeok_text", "")
    verdict = context.get("verdict", "")
    score = context.get("score", "")

    # 토론 내용 정리
    discussion_summary = ""
    if discussion:
        for t in discussion:
            discussion_summary += f"\n[라운드 {t.get('round', '?')}]\n민수 수정: {t.get('minsu_revised', '')[:200]}\n하은 최종: {t.get('haeun_final', '')[:200]}\n"

    user_msg = f"""초기 아이디어:
{idea[:300]}

초기 명확화:
{clarified[:500]}

민수(전략) 분석:
{minsu[:500]}

하은(검증) 분석:
{haeun[:500]}

토론 결과:
{discussion_summary[:500] if discussion_summary else "(토론 없음)"}

준혁 최종 판단:
{verdict} ({score}점)
{junhyeok_text[:300]}

이 모든 정보를 종합해서 처음 방향과 최종 분석이 일치하는지 재검토해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=800,
        system=inject_context(REVIEW_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            text = _safe(text)
            print(text, end="", flush=True)
            full_response += text

    print()

    # context에 재검토 결과 추가
    context["sieun_review"] = _safe(full_response)

    # 불일치 감지 및 경고
    if "전면 수정" in full_response or "다시" in full_response or "맞지 않" in full_response:
        print("\n⚠️ 재검토 결과: 일부 불일치 발견됨")
        print("   → 아래 제안사항을 고려해서 진행")
    else:
        print("\n✅ 재검토 결과: 방향 일관성 확인됨")

    return context
