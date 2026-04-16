import os
import anthropic
from dotenv import load_dotenv
from teams.토지SaaS_사업화_실행팀 import 준호_제품_기획관
from teams.토지SaaS_사업화_실행팀 import 다인_ai_엔진_개발관
from teams.토지SaaS_사업화_실행팀 import 세연_데이터_수집정합성_관리관
from teams.토지SaaS_사업화_실행팀 import 재원_b2b_영업온보딩_관
from teams.토지SaaS_사업화_실행팀 import 하율_수익_모델_검증관
from teams.토지SaaS_사업화_실행팀 import 민준_팀_검증관validator

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

    interview_prompt = "너는 토지SaaS 사업화 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 토지SaaS 사업화 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "토지SaaS 사업화 실행팀")

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
        fresh_knowledge = learn_before_run("토지SaaS_사업화_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 준호 (제품 기획관)...")
    result_준호_제품_기획관 = 준호_제품_기획관.run(context, client)
    context["준호_제품_기획관"] = result_준호_제품_기획관
    save(output_dir, "준호_제품_기획관_결과.md", result_준호_제품_기획관)

    print("\n[2/6] 다인 (AI 엔진 개발관)...")
    result_다인_ai_엔진_개발관 = 다인_ai_엔진_개발관.run(context, client)
    context["다인_ai_엔진_개발관"] = result_다인_ai_엔진_개발관
    save(output_dir, "다인_AI_엔진_개발관_결과.md", result_다인_ai_엔진_개발관)

    print("\n[3/6] 세연 (데이터 수집·정합성 관리관)...")
    result_세연_데이터_수집정합성_관리관 = 세연_데이터_수집정합성_관리관.run(context, client)
    context["세연_데이터_수집정합성_관리관"] = result_세연_데이터_수집정합성_관리관
    save(output_dir, "세연_데이터_수집·정합성_관리관_결과.md", result_세연_데이터_수집정합성_관리관)

    print("\n[4/6] 재원 (B2B 영업·온보딩 관)...")
    result_재원_b2b_영업온보딩_관 = 재원_b2b_영업온보딩_관.run(context, client)
    context["재원_b2b_영업온보딩_관"] = result_재원_b2b_영업온보딩_관
    save(output_dir, "재원_B2B_영업·온보딩_관_결과.md", result_재원_b2b_영업온보딩_관)

    print("\n[5/6] 하율 (수익 모델 검증관)...")
    result_하율_수익_모델_검증관 = 하율_수익_모델_검증관.run(context, client)
    context["하율_수익_모델_검증관"] = result_하율_수익_모델_검증관
    save(output_dir, "하율_수익_모델_검증관_결과.md", result_하율_수익_모델_검증관)

    print("\n[6/6] 민준 (팀 검증관·Validator)...")
    result_민준_팀_검증관validator = 민준_팀_검증관validator.run(context, client)
    context["민준_팀_검증관validator"] = result_민준_팀_검증관validator
    save(output_dir, "민준_팀_검증관·Validator_결과.md", result_민준_팀_검증관validator)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("토지SaaS_사업화_실행팀", f"{key}.md", val)
        collect_feedback("토지SaaS_사업화_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
