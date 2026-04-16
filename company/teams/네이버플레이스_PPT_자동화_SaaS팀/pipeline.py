import os
import anthropic
from dotenv import load_dotenv
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 서진_saas_아키텍트
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 하은_프론트엔드ux_설계자
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 준혁_결제인증_시스템_전문가
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 민지_ppt_품질_최적화_전문가
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 태영_초기_고객_확보그로스_전문가
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 수빈_데이터수익_최적화_전문가
from teams.네이버플레이스_PPT_자동화_SaaS팀 import 정우_검증자qa_총괄

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

    interview_prompt = "너는 네이버플레이스 PPT 자동화 SaaS팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 네이버플레이스 PPT 자동화 SaaS팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "네이버플레이스 PPT 자동화 SaaS팀")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/7] 서진 (SaaS 아키텍트)...")
    result_서진_saas_아키텍트 = 서진_saas_아키텍트.run(context, client)
    context["서진_saas_아키텍트"] = result_서진_saas_아키텍트
    save(output_dir, "서진_결과.md", result_서진_saas_아키텍트)

    print("\n[2/7] 하은 (프론트엔드/UX 설계자)...")
    result_하은_프론트엔드ux_설계자 = 하은_프론트엔드ux_설계자.run(context, client)
    context["하은_프론트엔드ux_설계자"] = result_하은_프론트엔드ux_설계자
    save(output_dir, "하은_결과.md", result_하은_프론트엔드ux_설계자)

    print("\n[3/7] 준혁 (결제/인증 시스템 전문가)...")
    result_준혁_결제인증_시스템_전문가 = 준혁_결제인증_시스템_전문가.run(context, client)
    context["준혁_결제인증_시스템_전문가"] = result_준혁_결제인증_시스템_전문가
    save(output_dir, "준혁_결과.md", result_준혁_결제인증_시스템_전문가)

    print("\n[4/7] 민지 (PPT 품질 최적화 전문가)...")
    result_민지_ppt_품질_최적화_전문가 = 민지_ppt_품질_최적화_전문가.run(context, client)
    context["민지_ppt_품질_최적화_전문가"] = result_민지_ppt_품질_최적화_전문가
    save(output_dir, "민지_결과.md", result_민지_ppt_품질_최적화_전문가)

    print("\n[5/7] 태영 (초기 고객 확보/그로스 전문가)...")
    result_태영_초기_고객_확보그로스_전문가 = 태영_초기_고객_확보그로스_전문가.run(context, client)
    context["태영_초기_고객_확보그로스_전문가"] = result_태영_초기_고객_확보그로스_전문가
    save(output_dir, "태영_결과.md", result_태영_초기_고객_확보그로스_전문가)

    print("\n[6/7] 수빈 (데이터/수익 최적화 전문가)...")
    result_수빈_데이터수익_최적화_전문가 = 수빈_데이터수익_최적화_전문가.run(context, client)
    context["수빈_데이터수익_최적화_전문가"] = result_수빈_데이터수익_최적화_전문가
    save(output_dir, "수빈_결과.md", result_수빈_데이터수익_최적화_전문가)

    print("\n[7/7] 정우 (검증자/QA 총괄)...")
    result_정우_검증자qa_총괄 = 정우_검증자qa_총괄.run(context, client)
    context["정우_검증자qa_총괄"] = result_정우_검증자qa_총괄
    save(output_dir, "정우_결과.md", result_정우_검증자qa_총괄)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("네이버플레이스_PPT_자동화_SaaS팀", f"{key}.md", val)
        collect_feedback("네이버플레이스_PPT_자동화_SaaS팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
