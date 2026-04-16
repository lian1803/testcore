import os
import sys
import anthropic
from pathlib import Path
from dotenv import load_dotenv
from teams.온라인마케팅팀 import 서진혁
from teams.온라인마케팅팀 import 한소율
from teams.온라인마케팅팀 import 윤채원
from teams.온라인마케팅팀 import 박시우
from teams.온라인마케팅팀 import 이도현
from teams.온라인마케팅팀 import 강하린

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

# 콘텐츠 생성 전 구조화
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.content_structurer import structure_before_create, merge_structure_to_context
    HAS_STRUCTURER = True
except ImportError:
    HAS_STRUCTURER = False

# 상태 추적
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

# 팀 학습 지식 주입
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.knowledge_injector import inject_team_knowledge, get_team_knowledge
    HAS_KNOWLEDGE_INJECTOR = True
except ImportError:
    HAS_KNOWLEDGE_INJECTOR = False

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


def _load_marketing_skills() -> str:
    """설치된 마케팅 스킬들의 핵심 원칙을 컨텍스트로 로드."""
    _skills_base = Path.home() / ".agents" / "skills"
    skill_paths = [
        str(_skills_base / "marketing-psychology"),
        str(_skills_base / "marketing-ideas"),
        str(_skills_base / "product-marketing-context"),
    ]
    contexts = []
    for path in skill_paths:
        p = Path(path)
        if not p.exists():
            continue
        for md in p.glob("SKILL.md"):
            try:
                content = md.read_text(encoding="utf-8")
                # 첫 800자만 (핵심 원칙 부분)
                excerpt = content[:800]
                skill_name = p.name
                contexts.append(f"[{skill_name}]\n{excerpt}")
            except Exception as e:
                pass
    return "\n\n".join(contexts) if contexts else ""


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

    interview_prompt = "너는 온라인마케팅팀의 팀 리더야. 리안(CEO, 비개발자)한테 실제 업무를 파악해야 해. 구체적이고 실용적인 질문 3~5개를 한번에 물어봐. 짧고 친근하게."

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
    print(f"🏢 온라인마케팅팀 가동")
    print(f"업무: {task}")
    print(f"{'='*60}")

    output_dir = os.path.join(OUTPUT_BASE, "온라인마케팅팀")

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
        context = enrich_context(context, team_slug="온라인마케팅팀")
    except Exception as e:
        print(f"⚠️ 미션/학습 로드 실패: {e}")

    # 마케팅 컨텍스트 허브 로드
    hub_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                             "knowledge", "ops_templates", "marketing", "마케팅컨텍스트_허브.md")
    if os.path.exists(hub_path):
        try:
            with open(hub_path, "r", encoding="utf-8") as f:
                hub_content = f.read()
            if len(hub_content) > 500:
                context["marketing_hub"] = hub_content[:3000]
                print("  마케팅 컨텍스트 허브 로드 완료")
        except Exception as e:
            print(f"  마케팅 컨텍스트 허브 로드 실패: {e}")

    # 팀 인터뷰 (리안한테 디테일 파악)
    interview = team_interview(task, client)
    context["interview"] = interview
    save(output_dir, "00_팀인터뷰.md", interview)

    # 마케팅 스킬 컨텍스트 자동 로드
    marketing_skills_context = _load_marketing_skills()
    if marketing_skills_context:
        context["marketing_skills"] = marketing_skills_context
        print("  마케팅 스킬 컨텍스트 로드 완료")

    # 팀 학습 지식 주입
    if HAS_KNOWLEDGE_INJECTOR:
        try:
            team_knowledge = get_team_knowledge("온라인마케팅팀", max_tokens=2000)
            if team_knowledge:
                context["team_knowledge"] = team_knowledge
                print("  팀 학습 지식 로드 완료")
        except Exception as e:
            print(f"  팀 학습 지식 로드 실패 (무시됨): {e}")

    # === 순서: 리드 → 구조화 → 전략 → 콘텐츠 → 영업 → 운영 → 분석 ===

    print("\n[1/6] 서진혁 — 리드 발굴...")
    if HAS_STATUS_TRACKER:
        update_status("서진혁", "온라인마케팅팀", "running", "셀러 리드 발굴 중")
    try:
        result_서진혁 = 서진혁.run(context, client)
        context["서진혁"] = result_서진혁
        save(output_dir, "01_서진혁_리드카드.md", result_서진혁)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("서진혁")

    # 콘텐츠 생성 전 구조화 (리드별 메시징 전략 사전 설계)
    print("\n[1.5/6] 콘텐츠 구조화 — 메시징 전략 설계...")
    if HAS_STRUCTURER:
        try:
            structure = structure_before_create(
                task="셀러 영업 캠페인 메시징",
                target_info={
                    "target": "온라인 셀러 (쇼핑몰 운영자)",
                    "challenge": context.get("interview", "온라인 판매 확대"),
                    "leads_count": f"발굴 리드: {result_서진혁[:100]}"
                },
                client=client
            )
            context = merge_structure_to_context(context, structure)
            save(output_dir, "01_5_콘텐츠_구조.json", str(structure))
            print("✅ 메시징 구조화 완료")
        except Exception as e:
            print(f"⚠️  구조화 스킵: {e}")
    else:
        print("⚠️  구조화 모듈 미사용")

    print("\n[2/6] 윤채원 — 셀러별 전략 수립...")
    if HAS_STATUS_TRACKER:
        update_status("윤채원", "온라인마케팅팀", "running", "리드별 맞춤 전략 수립 중")
    try:
        result_윤채원 = 윤채원.run(context, client)
        context["윤채원"] = result_윤채원
        save(output_dir, "02_윤채원_전략.md", result_윤채원)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("윤채원")

    print("\n[3/6] 박시우 — 콘텐츠 제작...")
    if HAS_STATUS_TRACKER:
        update_status("박시우", "온라인마케팅팀", "running", "납품용 콘텐츠 제작 중")
    try:
        result_박시우 = 박시우.run(context, client)
        context["박시우"] = result_박시우
        save(output_dir, "03_박시우_콘텐츠.md", result_박시우)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("박시우")

    print("\n[4/6] 한소율 — 콜드메일/DM 작성...")
    if HAS_STATUS_TRACKER:
        update_status("한소율", "온라인마케팅팀", "running", "영업 메일·DM 작성 중")
    try:
        result_한소율 = 한소율.run(context, client)
        context["한소율"] = result_한소율
        save(output_dir, "04_한소율_영업자료.md", result_한소율)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("한소율")

    print("\n[5/6] 이도현 — 견적/계약/운영...")
    if HAS_STATUS_TRACKER:
        update_status("이도현", "온라인마케팅팀", "running", "견적서·계약서 작성 중")
    try:
        result_이도현 = 이도현.run(context, client)
        context["이도현"] = result_이도현
        save(output_dir, "05_이도현_운영관리.md", result_이도현)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("이도현")

    print("\n[6/6] 강하린 — 성과 추적 설계...")
    if HAS_STATUS_TRACKER:
        update_status("강하린", "온라인마케팅팀", "running", "KPI 추적 체계 설계 중")
    try:
        result_강하린 = 강하린.run(context, client)
        context["강하린"] = result_강하린
        save(output_dir, "06_강하린_성과분석.md", result_강하린)
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("강하린")


    # 자가점검 + 자동 판단 (Phase 6)
    try:
        from core.pipeline_utils import auto_judge
        critique = self_critique_all(context, client, team_name="온라인마케팅팀")
        critique = auto_judge(critique, "온라인마케팅팀", client=client)
        context["critique"] = critique
        save(output_dir, "_자가점검_결과.md", critique.get("full_critique", ""))
    except Exception as e:
        print(f"\n⚠️ 자가점검 실패: {e}")

    # 최종 요약 보고서 생성 (리안이 이것만 보면 됨)
    try:
        summary_prompt = """너는 온라인마케팅팀 총괄 보고관이야.
팀 6명의 결과물을 받아서 리안(CEO)이 바로 실행할 수 있는 액션 요약을 만들어.

형식:
## 이번 실행 요약
- 발굴된 A등급 리드 수, 총 리드 수

## 즉시 실행 리스트
리드별로:
1. [셀러명] — 무엇을 하라 (메일 보내기/DM 보내기)
   - 발송 채널: 이메일 or 인스타 DM
   - 발송 시간: 추천 요일/시간
   - 메일 제목 or DM 첫 줄 (미리보기)
   - 예상 견적: 베이직 XX만원 / 스탠다드 XX만원

## 전체 예상 매출
- 전체 전환 시 예상 월 매출
- 예상 마진

## 주의사항
- 리스크나 확인 필요한 사항

두루뭉술 금지. 셀러명, 금액, 날짜 전부 구체적으로."""

        summary_msg = f"""팀 결과물:

[서진혁 리드]
{context.get('서진혁', '')[:1500]}

[윤채원 전략]
{context.get('윤채원', '')[:1500]}

[한소율 영업]
{context.get('한소율', '')[:1500]}

[이도현 운영]
{context.get('이도현', '')[:1500]}

[강하린 분석]
{context.get('강하린', '')[:800]}"""

        print("\n📋 최종 요약 보고서 생성 중...")
        summary = ""
        with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            system=summary_prompt,
            messages=[{"role": "user", "content": summary_msg}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                summary += text
        save(output_dir, "00_리안_액션요약.md", summary)
        context["summary"] = summary
    except Exception as e:
        print(f"\n⚠️ 요약 보고서 생성 실패: {e}")

    # 결과물을 지식으로 저장 + 리안 피드백 수집
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import save_team_result, collect_feedback
        for key, val in context.items():
            if key not in ("task", "interview") and isinstance(val, str) and len(val) > 100:
                save_team_result("온라인마케팅팀", f"{key}.md", val)
        collect_feedback("온라인마케팅팀")
    except Exception as e:
        print(f"\n⚠️ 지식 저장/피드백 수집 실패: {e}")

    # 보고사항들.md에 결과 보고
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import write_report
        report_content = context.get("summary", "요약 생성 실패")
        write_report("온라인마케팅팀", "셀러 영업 파이프라인", report_content)
    except Exception as e:
        print(f"\n⚠️ 보고사항 작성 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 완료")
    print(f"저장 위치: {output_dir}")
    print(f"\n📌 리안이 볼 파일: {os.path.join(output_dir, '00_리안_액션요약.md')}")
    print(f"{'='*60}")

    # ── 파이프라인 캐시 통계 출력 ──
    if HAS_PIPELINE_CACHE:
        cache = get_pipeline_cache()
        cache.print_stats()

    return context
