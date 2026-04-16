import os
import anthropic
from dotenv import load_dotenv
from teams.이커머스_셀러_통합_마케팅_실행팀 import 지훈_영업온보딩_전문가
from teams.이커머스_셀러_통합_마케팅_실행팀 import 수빈_퍼포먼스_광고_운영가
from teams.이커머스_셀러_통합_마케팅_실행팀 import 예린_콘텐츠_기획제작_디렉터
from teams.이커머스_셀러_통합_마케팅_실행팀 import 민준_crm_자동화_설계가
from teams.이커머스_셀러_통합_마케팅_실행팀 import 하은_성과_보고업셀_전략가
from teams.이커머스_셀러_통합_마케팅_실행팀 import 도현_검증자품질_관리자

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

    interview_prompt = "너는 이커머스 셀러 통합 마케팅 실행팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 이커머스 셀러 통합 마케팅 실행팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "이커머스 셀러 통합 마케팅 실행팀")

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
        fresh_knowledge = learn_before_run("이커머스_셀러_통합_마케팅_실행팀")
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"\n⚠️ 학습 스킵: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 지훈 (영업·온보딩 전문가)...")
    result_지훈_영업온보딩_전문가 = 지훈_영업온보딩_전문가.run(context, client)
    context["지훈_영업온보딩_전문가"] = result_지훈_영업온보딩_전문가
    save(output_dir, "지훈_영업·온보딩_전문가_결과.md", result_지훈_영업온보딩_전문가)

    print("\n[2/6] 수빈 (퍼포먼스 광고 운영가)...")
    result_수빈_퍼포먼스_광고_운영가 = 수빈_퍼포먼스_광고_운영가.run(context, client)
    context["수빈_퍼포먼스_광고_운영가"] = result_수빈_퍼포먼스_광고_운영가
    save(output_dir, "수빈_퍼포먼스_광고_운영가_결과.md", result_수빈_퍼포먼스_광고_운영가)

    print("\n[3/6] 예린 (콘텐츠 기획·제작 디렉터)...")
    result_예린_콘텐츠_기획제작_디렉터 = 예린_콘텐츠_기획제작_디렉터.run(context, client)
    context["예린_콘텐츠_기획제작_디렉터"] = result_예린_콘텐츠_기획제작_디렉터
    save(output_dir, "예린_콘텐츠_기획·제작_디렉터_결과.md", result_예린_콘텐츠_기획제작_디렉터)

    print("\n[4/6] 민준 (CRM 자동화 설계가)...")
    result_민준_crm_자동화_설계가 = 민준_crm_자동화_설계가.run(context, client)
    context["민준_crm_자동화_설계가"] = result_민준_crm_자동화_설계가
    save(output_dir, "민준_CRM_자동화_설계가_결과.md", result_민준_crm_자동화_설계가)

    print("\n[5/6] 하은 (성과 보고·업셀 전략가)...")
    result_하은_성과_보고업셀_전략가 = 하은_성과_보고업셀_전략가.run(context, client)
    context["하은_성과_보고업셀_전략가"] = result_하은_성과_보고업셀_전략가
    save(output_dir, "하은_성과_보고·업셀_전략가_결과.md", result_하은_성과_보고업셀_전략가)

    print("\n[6/6] 도현 (검증자·품질 관리자)...")
    result_도현_검증자품질_관리자 = 도현_검증자품질_관리자.run(context, client)
    context["도현_검증자품질_관리자"] = result_도현_검증자품질_관리자
    save(output_dir, "도현_검증자·품질_관리자_결과.md", result_도현_검증자품질_관리자)


    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("이커머스_셀러_통합_마케팅_실행팀", f"{key}.md", val)
        collect_feedback("이커머스_셀러_통합_마케팅_실행팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")
    return context
