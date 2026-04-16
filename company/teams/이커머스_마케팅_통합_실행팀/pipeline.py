import os
import anthropic
from dotenv import load_dotenv
from teams.이커머스_마케팅_통합_실행팀 import 진단사_지수
from teams.이커머스_마케팅_통합_실행팀 import 광고_최적화사_민준
from teams.이커머스_마케팅_통합_실행팀 import 콘텐츠_디렉터_예린
from teams.이커머스_마케팅_통합_실행팀 import crm_자동화사_승호
from teams.이커머스_마케팅_통합_실행팀 import 성과_리포터업셀러_다은
from teams.이커머스_마케팅_통합_실행팀 import 검증자_정우

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

    interview_prompt = "너는 이커머스 마케팅 통합 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 이커머스 마케팅 통합 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "이커머스 마케팅 통합 실행팀")

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
        fresh_knowledge = learn_before_run("이커머스_마케팅_통합_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 진단사 지수...")
    result_진단사_지수 = 진단사_지수.run(context, client)
    context["진단사_지수"] = result_진단사_지수
    save(output_dir, "진단사_지수_결과.md", result_진단사_지수)

    print("\n[2/6] 광고 최적화사 민준...")
    result_광고_최적화사_민준 = 광고_최적화사_민준.run(context, client)
    context["광고_최적화사_민준"] = result_광고_최적화사_민준
    save(output_dir, "광고_최적화사_민준_결과.md", result_광고_최적화사_민준)

    print("\n[3/6] 콘텐츠 디렉터 예린...")
    result_콘텐츠_디렉터_예린 = 콘텐츠_디렉터_예린.run(context, client)
    context["콘텐츠_디렉터_예린"] = result_콘텐츠_디렉터_예린
    save(output_dir, "콘텐츠_디렉터_예린_결과.md", result_콘텐츠_디렉터_예린)

    print("\n[4/6] CRM 자동화사 승호...")
    result_crm_자동화사_승호 = crm_자동화사_승호.run(context, client)
    context["crm_자동화사_승호"] = result_crm_자동화사_승호
    save(output_dir, "CRM_자동화사_승호_결과.md", result_crm_자동화사_승호)

    print("\n[5/6] 성과 리포터·업셀러 다은...")
    result_성과_리포터업셀러_다은 = 성과_리포터업셀러_다은.run(context, client)
    context["성과_리포터업셀러_다은"] = result_성과_리포터업셀러_다은
    save(output_dir, "성과_리포터·업셀러_다은_결과.md", result_성과_리포터업셀러_다은)

    print("\n[6/6] 검증자 정우...")
    result_검증자_정우 = 검증자_정우.run(context, client)
    context["검증자_정우"] = result_검증자_정우
    save(output_dir, "검증자_정우_결과.md", result_검증자_정우)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("이커머스_마케팅_통합_실행팀", f"{key}.md", val)
        collect_feedback("이커머스_마케팅_통합_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
