import os
import sys
import anthropic
from dotenv import load_dotenv
from teams.온라인영업팀 import 박탐정
from teams.온라인영업팀 import 이진단
from teams.온라인영업팀 import 김작가
from teams.온라인영업팀 import 최제안
from teams.온라인영업팀 import 정클로저
from teams.온라인영업팀 import 한총괄

# 파이프라인 캐시
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.cache import reset_pipeline_cache, get_pipeline_cache
    HAS_PIPELINE_CACHE = True
except ImportError:
    HAS_PIPELINE_CACHE = False

# 자동 레퍼런스 수집
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.pre_research import auto_research
    HAS_PRE_RESEARCH = True
except ImportError:
    HAS_PRE_RESEARCH = False

# 상태 추적
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

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
    """팀 시작 전 리안한테 디테일 인터뷰. 자동화 모드에서는 스킵."""
    # 자동화 모드 감지: sys.argv에 인자 있고 stdin이 tty가 아니면 스킵
    is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else True

    if not is_interactive:
        # subprocess/autopilot에서 호출 → 인터뷰 스킵, 기본값 반환
        return f"리안 답변:\n(자동화 모드 - 인터뷰 스킵)"

    print("\n" + "="*60)
    print("🎤 팀 인터뷰 | 리안한테 디테일 파악")
    print("="*60)

    interview_prompt = "너는 온라인영업팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    # ── 파이프라인 캐시 초기화 ──
    if HAS_PIPELINE_CACHE:
        reset_pipeline_cache()

    client = get_client()
    context = {"task": task}

    print(f"\n{'='*60}")
    print(f"🏢 온라인영업팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "온라인영업팀")

    # 자동 레퍼런스 수집 (팀 실행 전)
    if HAS_PRE_RESEARCH:
        try:
            research = auto_research(task, max_accounts=3, posts_per_account=3)
            if research:
                context["reference_research"] = research
                save(output_dir, "00_자동레퍼런스.md", research)
        except Exception as e:
            print(f"⚠️ 자동 레퍼런스 수집 실패: {e}")

    # import 분리 (Phase 5: self_critique 보장)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.pipeline_utils import enrich_context, self_critique_all
    try:
        context = enrich_context(context, team_slug="온라인영업팀")
    except Exception as e:
        print(f"⚠️ 미션/학습 로드 실패: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    print("\n[1/6] 박탐정...")
    if HAS_STATUS_TRACKER:
        update_status("박탐정", "온라인영업팀", "running", "잠재고객 분석 시작")
    try:
        result_박탐정 = 박탐정.run(context, client)
        context["박탐정"] = result_박탐정
        save(output_dir, "박탐정_결과.md", result_박탐정)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("박탐정")

    print("\n[2/6] 이진단...")
    if HAS_STATUS_TRACKER:
        update_status("이진단", "온라인영업팀", "running", "온라인 현황 진단서 작성 중")
    try:
        result_이진단 = 이진단.run(context, client)
        context["이진단"] = result_이진단
        save(output_dir, "이진단_결과.md", result_이진단)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("이진단")

    print("\n[3/6] 김작가...")
    if HAS_STATUS_TRACKER:
        update_status("김작가", "온라인영업팀", "running", "아웃리치 스크립트 작성 중")
    try:
        result_김작가 = 김작가.run(context, client)
        context["김작가"] = result_김작가
        save(output_dir, "김작가_결과.md", result_김작가)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("김작가")

    print("\n[4/6] 최제안...")
    if HAS_STATUS_TRACKER:
        update_status("최제안", "온라인영업팀", "running", "제안서/가격표 작성 중")
    try:
        result_최제안 = 최제안.run(context, client)
        context["최제안"] = result_최제안
        save(output_dir, "최제안_결과.md", result_최제안)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("최제안")

    print("\n[5/6] 정클로저...")
    if HAS_STATUS_TRACKER:
        update_status("정클로저", "온라인영업팀", "running", "미팅 대본/클로징 작성 중")
    try:
        result_정클로저 = 정클로저.run(context, client)
        context["정클로저"] = result_정클로저
        save(output_dir, "정클로저_결과.md", result_정클로저)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("정클로저")

    print("\n[6/6] 한총괄...")
    if HAS_STATUS_TRACKER:
        update_status("한총괄", "온라인영업팀", "running", "파이프라인 통합 중")
    try:
        result_한총괄 = 한총괄.run(context, client)
        context["한총괄"] = result_한총괄
        save(output_dir, "한총괄_결과.md", result_한총괄)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("한총괄")


    # 자가점검 + 자동 판단 (Phase 6)
    try:
        from core.pipeline_utils import auto_judge
        critique = self_critique_all(context, client, team_name="온라인영업팀")
        critique = auto_judge(critique, "온라인영업팀", client=client)
        context["critique"] = critique
        save(output_dir, "_자가점검_결과.md", critique.get("full_critique", ""))
    except Exception as e:
        print(f"\n⚠️ 자가점검 실패: {e}")

    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("온라인영업팀", f"{key}.md", val)
        collect_feedback("온라인영업팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"{'='*60}")

    # ── 파이프라인 캐시 통계 출력 ──
    if HAS_PIPELINE_CACHE:
        cache = get_pipeline_cache()
        cache.print_stats()

    return context
