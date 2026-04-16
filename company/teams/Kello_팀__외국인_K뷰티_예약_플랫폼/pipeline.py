import os
import anthropic
from dotenv import load_dotenv
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 지훈_샵_온보딩_영업_에이전트
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 소연_외국인_커뮤니티_아웃리치_에이전트
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 민재_수익_모델_검증_에이전트
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 하은_mvp_기획_에이전트
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 예린_마케팅_콘텐츠_에이전트
from teams.Kello_팀__외국인_K뷰티_예약_플랫폼 import 준호_검증_에이전트__validator

load_dotenv()

OUTPUT_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "team")


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def save(output_dir: str, filename: str, content: str):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 저장: {path}")


def team_interview(task: str, client: anthropic.Anthropic) -> str:
    """팀 시작 전 리안한테 디테일 인터뷰."""
    print("\n" + "="*60)
    print("🎤 팀 인터뷰 | 리안한테 디테일 파악")
    print("="*60)

    interview_prompt = "너는 Kello 팀 — 외국인 K-뷰티 예약 플랫폼의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

    resp = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=400,
        system=interview_prompt,
        messages=[{"role": "user", "content": f"업무: {task}"}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            resp += text

        # Phase 2: 인터뷰 자동화
        answer = ""

    return f"리안 답변:\n{answer}"


def run(task: str = ""):
    client = get_client()
    context = {"task": task}

    print(f"\n{'='*60}")
    print(f"🏢 Kello 팀 — 외국인 K-뷰티 예약 플랫폼 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "Kello 팀 — 외국인 K-뷰티 예약 플랫폼")

    # 미션 로드
    mission_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mission.md")
    try:
        with open(mission_path, encoding="utf-8") as f:
            context["mission"] = f.read()
        print(f"\n📋 미션 로드 완료")
    except FileNotFoundError:
        context["mission"] = ""

    # 학습 (Perplexity로 최신 자료 수집)
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from core.continuous_learning import learn_before_run
        fresh_knowledge = learn_before_run("Kello_팀__외국인_K뷰티_예약_플랫폼")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 지훈 (샵 온보딩 영업 에이전트)...")
    result_지훈_샵_온보딩_영업_에이전트 = 지훈_샵_온보딩_영업_에이전트.run(context, client)
    context["지훈_샵_온보딩_영업_에이전트"] = result_지훈_샵_온보딩_영업_에이전트
    save(output_dir, "지훈_샵_온보딩_영업_에이전트_결과.md", result_지훈_샵_온보딩_영업_에이전트)

    print("\n[2/6] 소연 (외국인 커뮤니티 아웃리치 에이전트)...")
    result_소연_외국인_커뮤니티_아웃리치_에이전트 = 소연_외국인_커뮤니티_아웃리치_에이전트.run(context, client)
    context["소연_외국인_커뮤니티_아웃리치_에이전트"] = result_소연_외국인_커뮤니티_아웃리치_에이전트
    save(output_dir, "소연_외국인_커뮤니티_아웃리치_에이전트_결과.md", result_소연_외국인_커뮤니티_아웃리치_에이전트)

    print("\n[3/6] 민재 (수익 모델 검증 에이전트)...")
    result_민재_수익_모델_검증_에이전트 = 민재_수익_모델_검증_에이전트.run(context, client)
    context["민재_수익_모델_검증_에이전트"] = result_민재_수익_모델_검증_에이전트
    save(output_dir, "민재_수익_모델_검증_에이전트_결과.md", result_민재_수익_모델_검증_에이전트)

    print("\n[4/6] 하은 (MVP 기획 에이전트)...")
    result_하은_mvp_기획_에이전트 = 하은_mvp_기획_에이전트.run(context, client)
    context["하은_mvp_기획_에이전트"] = result_하은_mvp_기획_에이전트
    save(output_dir, "하은_MVP_기획_에이전트_결과.md", result_하은_mvp_기획_에이전트)

    print("\n[5/6] 예린 (마케팅 콘텐츠 에이전트)...")
    result_예린_마케팅_콘텐츠_에이전트 = 예린_마케팅_콘텐츠_에이전트.run(context, client)
    context["예린_마케팅_콘텐츠_에이전트"] = result_예린_마케팅_콘텐츠_에이전트
    save(output_dir, "예린_마케팅_콘텐츠_에이전트_결과.md", result_예린_마케팅_콘텐츠_에이전트)

    print("\n[6/6] 준호 (검증 에이전트 — Validator)...")
    result_준호_검증_에이전트__validator = 준호_검증_에이전트__validator.run(context, client)
    context["준호_검증_에이전트__validator"] = result_준호_검증_에이전트__validator
    save(output_dir, "준호_검증_에이전트_—_Validator_결과.md", result_준호_검증_에이전트__validator)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("Kello_팀__외국인_K뷰티_예약_플랫폼", f"{key}.md", val)
        collect_feedback("Kello_팀__외국인_K뷰티_예약_플랫폼")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
