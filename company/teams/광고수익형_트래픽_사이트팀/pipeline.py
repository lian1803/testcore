import os
import anthropic
from dotenv import load_dotenv
from teams.광고수익형_트래픽_사이트팀 import 정우_키워드_스나이퍼
from teams.광고수익형_트래픽_사이트팀 import 하윤_콘텐츠_아키텍트
from teams.광고수익형_트래픽_사이트팀 import 도현_도구_빌더
from teams.광고수익형_트래픽_사이트팀 import 서아_수익_최적화_전문가
from teams.광고수익형_트래픽_사이트팀 import 지호_데이터_애널리스트
from teams.광고수익형_트래픽_사이트팀 import 은서_검증자

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

    interview_prompt = "너는 광고수익형 트래픽 사이트팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 광고수익형 트래픽 사이트팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "광고수익형 트래픽 사이트팀")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 정우 (키워드 스나이퍼)...")
    result_정우_키워드_스나이퍼 = 정우_키워드_스나이퍼.run(context, client)
    context["정우_키워드_스나이퍼"] = result_정우_키워드_스나이퍼
    save(output_dir, "정우 (키워드 스나이퍼)_결과.md", result_정우_키워드_스나이퍼)

    print("\n[2/6] 하윤 (콘텐츠 아키텍트)...")
    result_하윤_콘텐츠_아키텍트 = 하윤_콘텐츠_아키텍트.run(context, client)
    context["하윤_콘텐츠_아키텍트"] = result_하윤_콘텐츠_아키텍트
    save(output_dir, "하윤 (콘텐츠 아키텍트)_결과.md", result_하윤_콘텐츠_아키텍트)

    print("\n[3/6] 도현 (도구 빌더)...")
    result_도현_도구_빌더 = 도현_도구_빌더.run(context, client)
    context["도현_도구_빌더"] = result_도현_도구_빌더
    save(output_dir, "도현 (도구 빌더)_결과.md", result_도현_도구_빌더)

    print("\n[4/6] 서아 (수익 최적화 전문가)...")
    result_서아_수익_최적화_전문가 = 서아_수익_최적화_전문가.run(context, client)
    context["서아_수익_최적화_전문가"] = result_서아_수익_최적화_전문가
    save(output_dir, "서아 (수익 최적화 전문가)_결과.md", result_서아_수익_최적화_전문가)

    print("\n[5/6] 지호 (데이터 애널리스트)...")
    result_지호_데이터_애널리스트 = 지호_데이터_애널리스트.run(context, client)
    context["지호_데이터_애널리스트"] = result_지호_데이터_애널리스트
    save(output_dir, "지호 (데이터 애널리스트)_결과.md", result_지호_데이터_애널리스트)

    print("\n[6/6] 은서 (검증자)...")
    result_은서_검증자 = 은서_검증자.run(context, client)
    context["은서_검증자"] = result_은서_검증자
    save(output_dir, "은서 (검증자)_결과.md", result_은서_검증자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("광고수익형_트래픽_사이트팀", f"{key}.md", val)
        collect_feedback("광고수익형_트래픽_사이트팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
