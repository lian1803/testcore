import os
import anthropic
from dotenv import load_dotenv
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 준혁_영업클로징_에이전트
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 서연_온보딩콘텐츠_생산_에이전트
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 민재_광고_운영_에이전트
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 지은_성과_보고고객_유지_에이전트
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 태준_ai_파이프라인_유지개선_에이전트
from teams.오프라인_자영업자_마케팅_대행_실행팀 import 현아_검증자_에이전트

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

    interview_prompt = "너는 오프라인 자영업자 마케팅 대행 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 오프라인 자영업자 마케팅 대행 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "오프라인 자영업자 마케팅 대행 실행팀")

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
        fresh_knowledge = learn_before_run("오프라인_자영업자_마케팅_대행_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 준혁 (영업·클로징 에이전트)...")
    result_준혁_영업클로징_에이전트 = 준혁_영업클로징_에이전트.run(context, client)
    context["준혁_영업클로징_에이전트"] = result_준혁_영업클로징_에이전트
    save(output_dir, "준혁_영업·클로징_에이전트_결과.md", result_준혁_영업클로징_에이전트)

    print("\n[2/6] 서연 (온보딩·콘텐츠 생산 에이전트)...")
    result_서연_온보딩콘텐츠_생산_에이전트 = 서연_온보딩콘텐츠_생산_에이전트.run(context, client)
    context["서연_온보딩콘텐츠_생산_에이전트"] = result_서연_온보딩콘텐츠_생산_에이전트
    save(output_dir, "서연_온보딩·콘텐츠_생산_에이전트_결과.md", result_서연_온보딩콘텐츠_생산_에이전트)

    print("\n[3/6] 민재 (광고 운영 에이전트)...")
    result_민재_광고_운영_에이전트 = 민재_광고_운영_에이전트.run(context, client)
    context["민재_광고_운영_에이전트"] = result_민재_광고_운영_에이전트
    save(output_dir, "민재_광고_운영_에이전트_결과.md", result_민재_광고_운영_에이전트)

    print("\n[4/6] 지은 (성과 보고·고객 유지 에이전트)...")
    result_지은_성과_보고고객_유지_에이전트 = 지은_성과_보고고객_유지_에이전트.run(context, client)
    context["지은_성과_보고고객_유지_에이전트"] = result_지은_성과_보고고객_유지_에이전트
    save(output_dir, "지은_성과_보고·고객_유지_에이전트_결과.md", result_지은_성과_보고고객_유지_에이전트)

    print("\n[5/6] 태준 (AI 파이프라인 유지·개선 에이전트)...")
    result_태준_ai_파이프라인_유지개선_에이전트 = 태준_ai_파이프라인_유지개선_에이전트.run(context, client)
    context["태준_ai_파이프라인_유지개선_에이전트"] = result_태준_ai_파이프라인_유지개선_에이전트
    save(output_dir, "태준_AI_파이프라인_유지·개선_에이전트_결과.md", result_태준_ai_파이프라인_유지개선_에이전트)

    print("\n[6/6] 현아 (검증자 에이전트)...")
    result_현아_검증자_에이전트 = 현아_검증자_에이전트.run(context, client)
    context["현아_검증자_에이전트"] = result_현아_검증자_에이전트
    save(output_dir, "현아_검증자_에이전트_결과.md", result_현아_검증자_에이전트)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("오프라인_자영업자_마케팅_대행_실행팀", f"{key}.md", val)
        collect_feedback("오프라인_자영업자_마케팅_대행_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
