import os
import anthropic
from dotenv import load_dotenv
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 서준_제품_전략가
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 지아_api_통합_엔지니어링_설계자
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 하은_ai_인사이트_설계자
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 민재_ux대시보드_설계자
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 소율_gtm그로스_전략가
from teams.인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀 import 태우_검증자

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

    interview_prompt = "너는 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "인하우스 마케터·프리랜서용 통합 마케팅 대시보드 SaaS 팀")

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
        fresh_knowledge = learn_before_run("인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 서준 (제품 전략가)...")
    result_서준_제품_전략가 = 서준_제품_전략가.run(context, client)
    context["서준_제품_전략가"] = result_서준_제품_전략가
    save(output_dir, "서준_제품_전략가_결과.md", result_서준_제품_전략가)

    print("\n[2/6] 지아 (API 통합 엔지니어링 설계자)...")
    result_지아_api_통합_엔지니어링_설계자 = 지아_api_통합_엔지니어링_설계자.run(context, client)
    context["지아_api_통합_엔지니어링_설계자"] = result_지아_api_통합_엔지니어링_설계자
    save(output_dir, "지아_API_통합_엔지니어링_설계자_결과.md", result_지아_api_통합_엔지니어링_설계자)

    print("\n[3/6] 하은 (AI 인사이트 설계자)...")
    result_하은_ai_인사이트_설계자 = 하은_ai_인사이트_설계자.run(context, client)
    context["하은_ai_인사이트_설계자"] = result_하은_ai_인사이트_설계자
    save(output_dir, "하은_AI_인사이트_설계자_결과.md", result_하은_ai_인사이트_설계자)

    print("\n[4/6] 민재 (UX/대시보드 설계자)...")
    result_민재_ux대시보드_설계자 = 민재_ux대시보드_설계자.run(context, client)
    context["민재_ux대시보드_설계자"] = result_민재_ux대시보드_설계자
    save(output_dir, "민재_UX_대시보드_설계자_결과.md", result_민재_ux대시보드_설계자)

    print("\n[5/6] 소율 (GTM·그로스 전략가)...")
    result_소율_gtm그로스_전략가 = 소율_gtm그로스_전략가.run(context, client)
    context["소율_gtm그로스_전략가"] = result_소율_gtm그로스_전략가
    save(output_dir, "소율_GTM·그로스_전략가_결과.md", result_소율_gtm그로스_전략가)

    print("\n[6/6] 태우 (검증자)...")
    result_태우_검증자 = 태우_검증자.run(context, client)
    context["태우_검증자"] = result_태우_검증자
    save(output_dir, "태우_검증자_결과.md", result_태우_검증자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀", f"{key}.md", val)
        collect_feedback("인하우스_마케터프리랜서용_통합_마케팅_대시보드_SaaS_팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
