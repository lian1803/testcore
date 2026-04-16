import os
import anthropic
from dotenv import load_dotenv
from teams.완전자동_마케팅_SaaS_실행팀 import 도윤_saas_아키텍트
from teams.완전자동_마케팅_SaaS_실행팀 import 서연_구독_전환_설계자
from teams.완전자동_마케팅_SaaS_실행팀 import 지훈_콘텐츠_자동화_엔지니어
from teams.완전자동_마케팅_SaaS_실행팀 import 민아_pmf_검증_운영자
from teams.완전자동_마케팅_SaaS_실행팀 import 태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자
from teams.완전자동_마케팅_SaaS_실행팀 import 유진_팀_검증자

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

    interview_prompt = "너는 완전자동 마케팅 SaaS 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 완전자동 마케팅 SaaS 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "완전자동 마케팅 SaaS 실행팀")

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
        fresh_knowledge = learn_before_run("완전자동_마케팅_SaaS_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 도윤 (SaaS 아키텍트)...")
    result_도윤_saas_아키텍트 = 도윤_saas_아키텍트.run(context, client)
    context["도윤_saas_아키텍트"] = result_도윤_saas_아키텍트
    save(output_dir, "도윤_SaaS_아키텍트_결과.md", result_도윤_saas_아키텍트)

    print("\n[2/6] 서연 (구독 전환 설계자)...")
    result_서연_구독_전환_설계자 = 서연_구독_전환_설계자.run(context, client)
    context["서연_구독_전환_설계자"] = result_서연_구독_전환_설계자
    save(output_dir, "서연_구독_전환_설계자_결과.md", result_서연_구독_전환_설계자)

    print("\n[3/6] 지훈 (콘텐츠 자동화 엔지니어)...")
    result_지훈_콘텐츠_자동화_엔지니어 = 지훈_콘텐츠_자동화_엔지니어.run(context, client)
    context["지훈_콘텐츠_자동화_엔지니어"] = result_지훈_콘텐츠_자동화_엔지니어
    save(output_dir, "지훈_콘텐츠_자동화_엔지니어_결과.md", result_지훈_콘텐츠_자동화_엔지니어)

    print("\n[4/6] 민아 (PMF 검증 운영자)...")
    result_민아_pmf_검증_운영자 = 민아_pmf_검증_운영자.run(context, client)
    context["민아_pmf_검증_운영자"] = result_민아_pmf_검증_운영자
    save(output_dir, "민아_PMF_검증_운영자_결과.md", result_민아_pmf_검증_운영자)

    print("\n[5/6] 태민 (자동화 완성도 측정자 겸 글로벌 로드맵 설계자)...")
    result_태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자 = 태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자.run(context, client)
    context["태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자"] = result_태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자
    save(output_dir, "태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자_결과.md", result_태민_자동화_완성도_측정자_겸_글로벌_로드맵_설계자)

    print("\n[6/6] 유진 (팀 검증자)...")
    result_유진_팀_검증자 = 유진_팀_검증자.run(context, client)
    context["유진_팀_검증자"] = result_유진_팀_검증자
    save(output_dir, "유진_팀_검증자_결과.md", result_유진_팀_검증자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("완전자동_마케팅_SaaS_실행팀", f"{key}.md", val)
        collect_feedback("완전자동_마케팅_SaaS_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
