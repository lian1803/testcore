import os
import anthropic
from dotenv import load_dotenv
from teams.LLM비용서킷브레이커팀 import 준혁_sdk_아키텍트
from teams.LLM비용서킷브레이커팀 import 서연_백엔드__데이터_엔지니어
from teams.LLM비용서킷브레이커팀 import 민재_프론트엔드__대시보드_엔지니어
from teams.LLM비용서킷브레이커팀 import 지은_그로스__커뮤니티_마케터
from teams.LLM비용서킷브레이커팀 import 태양_수익화__프라이싱_전략가
from teams.LLM비용서킷브레이커팀 import 하늘_검증자__리스크__제약_관리자

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

    interview_prompt = "너는 LLM-비용-서킷브레이커팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 LLM-비용-서킷브레이커팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "LLM-비용-서킷브레이커팀")

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
        fresh_knowledge = learn_before_run("LLM비용서킷브레이커팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 준혁 (SDK 아키텍트)...")
    result_준혁_sdk_아키텍트 = 준혁_sdk_아키텍트.run(context, client)
    context["준혁_sdk_아키텍트"] = result_준혁_sdk_아키텍트
    save(output_dir, "준혁_SDK_아키텍트_결과.md", result_준혁_sdk_아키텍트)

    print("\n[2/6] 서연 (백엔드 & 데이터 엔지니어)...")
    result_서연_백엔드__데이터_엔지니어 = 서연_백엔드__데이터_엔지니어.run(context, client)
    context["서연_백엔드__데이터_엔지니어"] = result_서연_백엔드__데이터_엔지니어
    save(output_dir, "서연_백엔드_&_데이터_엔지니어_결과.md", result_서연_백엔드__데이터_엔지니어)

    print("\n[3/6] 민재 (프론트엔드 & 대시보드 엔지니어)...")
    result_민재_프론트엔드__대시보드_엔지니어 = 민재_프론트엔드__대시보드_엔지니어.run(context, client)
    context["민재_프론트엔드__대시보드_엔지니어"] = result_민재_프론트엔드__대시보드_엔지니어
    save(output_dir, "민재_프론트엔드_&_대시보드_엔지니어_결과.md", result_민재_프론트엔드__대시보드_엔지니어)

    print("\n[4/6] 지은 (그로스 & 커뮤니티 마케터)...")
    result_지은_그로스__커뮤니티_마케터 = 지은_그로스__커뮤니티_마케터.run(context, client)
    context["지은_그로스__커뮤니티_마케터"] = result_지은_그로스__커뮤니티_마케터
    save(output_dir, "지은_그로스_&_커뮤니티_마케터_결과.md", result_지은_그로스__커뮤니티_마케터)

    print("\n[5/6] 태양 (수익화 & 프라이싱 전략가)...")
    result_태양_수익화__프라이싱_전략가 = 태양_수익화__프라이싱_전략가.run(context, client)
    context["태양_수익화__프라이싱_전략가"] = result_태양_수익화__프라이싱_전략가
    save(output_dir, "태양_수익화_&_프라이싱_전략가_결과.md", result_태양_수익화__프라이싱_전략가)

    print("\n[6/6] 하늘 (검증자 — 리스크 & 제약 관리자)...")
    result_하늘_검증자__리스크__제약_관리자 = 하늘_검증자__리스크__제약_관리자.run(context, client)
    context["하늘_검증자__리스크__제약_관리자"] = result_하늘_검증자__리스크__제약_관리자
    save(output_dir, "하늘_검증자_—_리스크_&_제약_관리자_결과.md", result_하늘_검증자__리스크__제약_관리자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("LLM비용서킷브레이커팀", f"{key}.md", val)
        collect_feedback("LLM비용서킷브레이커팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
