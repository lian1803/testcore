import os
import anthropic
from dotenv import load_dotenv
from teams.인테리어_SaaS_실행팀 import 준혁_제품_아키텍트
from teams.인테리어_SaaS_실행팀 import 다은_렌더링ux_설계자
from teams.인테리어_SaaS_실행팀 import 재원_데이터법률_모듈_빌더
from teams.인테리어_SaaS_실행팀 import 소연_b2b_영업온보딩_설계자
from teams.인테리어_SaaS_실행팀 import 민준_수익_검증성과_관리자
from teams.인테리어_SaaS_실행팀 import 하영_검증자리스크_관리자

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

    interview_prompt = "너는 인테리어 SaaS 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 인테리어 SaaS 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "인테리어 SaaS 실행팀")

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
        fresh_knowledge = learn_before_run("인테리어_SaaS_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 준혁 (제품 아키텍트)...")
    result_준혁_제품_아키텍트 = 준혁_제품_아키텍트.run(context, client)
    context["준혁_제품_아키텍트"] = result_준혁_제품_아키텍트
    save(output_dir, "준혁_제품_아키텍트_결과.md", result_준혁_제품_아키텍트)

    print("\n[2/6] 다은 (렌더링·UX 설계자)...")
    result_다은_렌더링ux_설계자 = 다은_렌더링ux_설계자.run(context, client)
    context["다은_렌더링ux_설계자"] = result_다은_렌더링ux_설계자
    save(output_dir, "다은_렌더링·UX_설계자_결과.md", result_다은_렌더링ux_설계자)

    print("\n[3/6] 재원 (데이터·법률 모듈 빌더)...")
    result_재원_데이터법률_모듈_빌더 = 재원_데이터법률_모듈_빌더.run(context, client)
    context["재원_데이터법률_모듈_빌더"] = result_재원_데이터법률_모듈_빌더
    save(output_dir, "재원_데이터·법률_모듈_빌더_결과.md", result_재원_데이터법률_모듈_빌더)

    print("\n[4/6] 소연 (B2B 영업·온보딩 설계자)...")
    result_소연_b2b_영업온보딩_설계자 = 소연_b2b_영업온보딩_설계자.run(context, client)
    context["소연_b2b_영업온보딩_설계자"] = result_소연_b2b_영업온보딩_설계자
    save(output_dir, "소연_B2B_영업·온보딩_설계자_결과.md", result_소연_b2b_영업온보딩_설계자)

    print("\n[5/6] 민준 (수익 검증·성과 관리자)...")
    result_민준_수익_검증성과_관리자 = 민준_수익_검증성과_관리자.run(context, client)
    context["민준_수익_검증성과_관리자"] = result_민준_수익_검증성과_관리자
    save(output_dir, "민준_수익_검증·성과_관리자_결과.md", result_민준_수익_검증성과_관리자)

    print("\n[6/6] 하영 (검증자·리스크 관리자)...")
    result_하영_검증자리스크_관리자 = 하영_검증자리스크_관리자.run(context, client)
    context["하영_검증자리스크_관리자"] = result_하영_검증자리스크_관리자
    save(output_dir, "하영_검증자·리스크_관리자_결과.md", result_하영_검증자리스크_관리자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("인테리어_SaaS_실행팀", f"{key}.md", val)
        collect_feedback("인테리어_SaaS_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
