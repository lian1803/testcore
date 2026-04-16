import os
import anthropic
from dotenv import load_dotenv
from teams.마케팅_대시보드_SaaS_실행팀 import 지훈_제품_기획ux_설계자
from teams.마케팅_대시보드_SaaS_실행팀 import 승현_api_연동_개발자
from teams.마케팅_대시보드_SaaS_실행팀 import 다은_ai_인사이트_엔진_개발자
from teams.마케팅_대시보드_SaaS_실행팀 import 혜린_saas_마케팅그로스_매니저
from teams.마케팅_대시보드_SaaS_실행팀 import 소연_고객_성공리텐션_매니저
from teams.마케팅_대시보드_SaaS_실행팀 import 민재_검증자리스크_관리자

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

    interview_prompt = "너는 마케팅 대시보드 SaaS 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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

    print("\n\n리안: ", end="")
    try:
        answer = input().strip()
    except EOFError:
        answer = ""

    return f"리안 답변:\n{answer}"

def run(task: str = ""):
    client = get_client()
    context = {"task": task}

    print(f"\n{'='*60}")
    print(f"🏢 마케팅 대시보드 SaaS 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "마케팅 대시보드 SaaS 실행팀")

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
        fresh_knowledge = learn_before_run("마케팅_대시보드_SaaS_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 지훈 (제품 기획·UX 설계자)...")
    result_지훈_제품_기획ux_설계자 = 지훈_제품_기획ux_설계자.run(context, client)
    context["지훈_제품_기획ux_설계자"] = result_지훈_제품_기획ux_설계자
    save(output_dir, "지훈_제품_기획·UX_설계자_결과.md", result_지훈_제품_기획ux_설계자)

    print("\n[2/6] 승현 (API 연동 개발자)...")
    result_승현_api_연동_개발자 = 승현_api_연동_개발자.run(context, client)
    context["승현_api_연동_개발자"] = result_승현_api_연동_개발자
    save(output_dir, "승현_API_연동_개발자_결과.md", result_승현_api_연동_개발자)

    print("\n[3/6] 다은 (AI 인사이트 엔진 개발자)...")
    result_다은_ai_인사이트_엔진_개발자 = 다은_ai_인사이트_엔진_개발자.run(context, client)
    context["다은_ai_인사이트_엔진_개발자"] = result_다은_ai_인사이트_엔진_개발자
    save(output_dir, "다은_AI_인사이트_엔진_개발자_결과.md", result_다은_ai_인사이트_엔진_개발자)

    print("\n[4/6] 혜린 (SaaS 마케팅·그로스 매니저)...")
    result_혜린_saas_마케팅그로스_매니저 = 혜린_saas_마케팅그로스_매니저.run(context, client)
    context["혜린_saas_마케팅그로스_매니저"] = result_혜린_saas_마케팅그로스_매니저
    save(output_dir, "혜린_SaaS_마케팅·그로스_매니저_결과.md", result_혜린_saas_마케팅그로스_매니저)

    print("\n[5/6] 소연 (고객 성공·리텐션 매니저)...")
    result_소연_고객_성공리텐션_매니저 = 소연_고객_성공리텐션_매니저.run(context, client)
    context["소연_고객_성공리텐션_매니저"] = result_소연_고객_성공리텐션_매니저
    save(output_dir, "소연_고객_성공·리텐션_매니저_결과.md", result_소연_고객_성공리텐션_매니저)

    print("\n[6/6] 민재 (검증자·리스크 관리자)...")
    result_민재_검증자리스크_관리자 = 민재_검증자리스크_관리자.run(context, client)
    context["민재_검증자리스크_관리자"] = result_민재_검증자리스크_관리자
    save(output_dir, "민재_검증자·리스크_관리자_결과.md", result_민재_검증자리스크_관리자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("마케팅_대시보드_SaaS_실행팀", f"{key}.md", val)
        collect_feedback("마케팅_대시보드_SaaS_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
