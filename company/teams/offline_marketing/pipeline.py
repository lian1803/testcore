import os
import sys
import json
import anthropic
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from teams.offline_marketing import researcher, strategist, copywriter, validator
from core.models import CLAUDE_OPUS

# 파이프라인 캐시
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.cache import reset_pipeline_cache, get_pipeline_cache
    HAS_PIPELINE_CACHE = True
except ImportError:
    HAS_PIPELINE_CACHE = False

# 상태 추적
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

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

# 팀 학습 지식 주입
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.knowledge_injector import inject_team_knowledge, get_team_knowledge
    HAS_KNOWLEDGE_INJECTOR = True
except ImportError:
    HAS_KNOWLEDGE_INJECTOR = False

load_dotenv()

TEAM_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "team", "[진행중] 오프라인 마케팅", "소상공인_영업툴")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(".env에 ANTHROPIC_API_KEY 없음")
    return anthropic.Anthropic(api_key=api_key)


def save(filename: str, content: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 저장: {path}")


def post_run_critique(output: dict, client: anthropic.Anthropic, max_iterations: int = 2) -> dict:
    """
    파이프라인 완료 후 아웃풋 자가점검 — 리안한테 보고 전에 팀이 스스로 잡아내기.

    체크리스트:
    1. 가격 심리 — 총액(6개월 합계)이 크게 노출되면 거절률 증가
    2. 해결책 노출 — "이렇게 하세요" 류 표현 있으면 신뢰도 하락
    3. 손실 가시화 — 월 손실금액이 투자금과 비교 안 되면 설득력 약함
    4. CTA 명확도 — 마지막에 연락처/버튼 없으면 액션율 0
    5. 개인화 — 업체명/지역이 없으면 스팸 분류 확률 증가
    """
    print("\n" + "="*60)
    print("🔍 자가점검 루프 | 아웃풋 품질 자동 점검")
    print("="*60)

    copy = output.get("copy", "")
    strategy = output.get("strategy", "")
    industry = output.get("industry", "서비스 미정")

    critique_result = {
        "passed": False,
        "iterations": 0,
        "issues": [],
        "improvements": [],
        "final_copy": copy,
        "final_strategy": strategy
    }

    current_copy = copy
    current_strategy = strategy

    for iteration in range(max_iterations):
        critique_result["iterations"] = iteration + 1

        critique_prompt = f"""너는 오프라인 마케팅팀의 자가점검 담당자야.

=== 검토 대상 ===
업종: {industry}

**스크립트/카피:**
{current_copy[:2000]}

**전략:**
{current_strategy[:1500]}

=== 자가점검 5가지 기준 ===
1. **가격 심리** — 총액(6개월 합계)이 크게 노출되면 거절률 증가
   - 점검: 월액 기준으로 표현됐는가? 6개월 합계가 노출되었는가?

2. **해결책 노출** — "이렇게 하세요" 류 표현 있으면 신뢰도 하락
   - 점검: 해결책을 제시하는가? 아니면 문제만 질문으로 유도하는가?

3. **손실 가시화** — 월 손실금액이 투자금(DM비, 시간)과 비교 안 되면 설득력 약함
   - 점검: 월 손실액이 구체적으로 표현되었는가?

4. **CTA 명확도** — 마지막에 연락처/카톡/전화 버튼 없으면 액션율 0
   - 점검: 명확한 행동유도(CTA)가 마지막에 있는가?

5. **개인화** — 업체명/지역이 없으면 스팸 분류 확률 증가
   - 점검: 템플릿 방식은 아닌가? 개인화 가능한 구조인가?

=== 반환 형식 (JSON) ===
{{
  "issues": [
    {{"criterion": "기준명", "status": "문제있음/정상", "detail": "구체적 지적"}},
    ...
  ],
  "has_issues": true/false,
  "improvement_suggestions": [
    "구체적 개선 방안 1",
    "구체적 개선 방안 2",
    "구체적 개선 방안 3"
  ]
}}

JSON만 반환."""

        try:
            response = client.messages.create(
                model=CLAUDE_OPUS,
                max_tokens=1000,
                messages=[{"role": "user", "content": critique_prompt}]
            )
            text = response.content[0].text.strip()

            # JSON 파싱
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()

            critique_data = json.loads(text)
        except Exception as e:
            print(f"\n⚠️  자가점검 분석 실패 (iteration {iteration+1}): {e}")
            critique_data = {"issues": [], "has_issues": False, "improvement_suggestions": []}

        # 이슈 기록
        issues = critique_data.get("issues", [])
        has_issues = critique_data.get("has_issues", False)

        if issues:
            critique_result["issues"].extend(issues)

        print(f"\n[자가점검 {iteration+1}/{max_iterations}]")
        if has_issues:
            print(f"⚠️  문제 발견: {len(issues)}개")
            for issue in issues:
                print(f"  - {issue.get('criterion', 'N/A')}: {issue.get('detail', 'N/A')}")
        else:
            print(f"✅ 체크 완료 — 이슈 없음")
            critique_result["passed"] = True
            break

        # 개선 제안이 있으면 다음 iteration을 위해 기록
        improvements = critique_data.get("improvement_suggestions", [])
        if improvements:
            critique_result["improvements"].extend(improvements)

            # 마지막 iteration이 아니면 카피 재작성 시도
            if iteration < max_iterations - 1:
                print(f"\n🔄 개선안 적용 — 스크립트 재작성 중...")

                revise_prompt = f"""너는 영업 카피라이터야.

다음 개선 제안에 따라 기존 스크립트를 수정해줘.

**개선 제안:**
{json.dumps(improvements[:3], ensure_ascii=False, indent=2)}

**기존 스크립트:**
{current_copy[:1500]}

**요구:**
- 개선 제안을 명확히 반영
- 기존 톤앤매너 유지
- 구체적이고 실행 가능한 내용
- 마크다운 포맷 유지

수정된 스크립트만 반환."""

                try:
                    revise_response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": revise_prompt}]
                    )
                    revised_copy = revise_response.content[0].text.strip()
                    current_copy = revised_copy
                    print(f"✓ 스크립트 수정 완료")
                except Exception as e:
                    print(f"⚠️  스크립트 수정 실패: {e}")
        else:
            print(f"✓ 더 이상의 개선 제안 없음")
            critique_result["passed"] = True
            break

    # 최종 아웃풋 저장
    critique_result["final_copy"] = current_copy
    critique_result["final_strategy"] = current_strategy

    print(f"\n{'='*60}")
    print(f"자가점검 결과: 총 {critique_result['iterations']}회 | ", end="")
    if critique_result["passed"]:
        print("✅ 통과")
    else:
        print(f"⚠️  미해결 이슈 {len(critique_result['issues'])}개 (리안 확인 필요)")
    print(f"{'='*60}")

    return critique_result


def _read_current_state() -> dict:
    """현재 팀 산출물 + 피드백 전부 읽어서 상태 파악."""
    state = {}
    files = {
        "스크립트": "영업_스크립트_v2.md",
        "전략": "영업_전략_재설계.md",
        "검증": "영업_사업검증.md",
        "실전가이드": "영업_실전가이드_최종.md",
        "퍼널": "영업_퍼널_설계.md",
        "플레이북": "영업_플레이북.md",
    }
    for key, fname in files.items():
        path = os.path.join(OUTPUT_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            state[key] = {"exists": True, "preview": content[:500], "size": len(content)}
        except Exception:
            state[key] = {"exists": False}

    # 피드백 파일 확인
    feedback_path = os.path.join(OUTPUT_DIR, "_feedback.json")
    try:
        with open(feedback_path, encoding="utf-8") as f:
            state["feedback"] = json.load(f)
    except Exception:
        state["feedback"] = {}

    return state


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


def _self_assess(client, state: dict, mission: str) -> dict:
    """팀이 스스로 현재 상태 진단 → 이번 실행에서 뭘 집중할지 결정."""
    existing = [k for k, v in state.items() if isinstance(v, dict) and v.get("exists")]
    missing = [k for k, v in state.items() if isinstance(v, dict) and not v.get("exists") and k != "feedback"]
    feedback_text = str(state.get("feedback", {}))

    prompt = f"""너는 오프라인 마케팅팀 팀장이야.

=== 팀 미션 ===
{mission}

=== 현재 산출물 상태 ===
있는 것: {existing}
없는 것: {missing}

=== 최근 피드백 ===
{feedback_text if feedback_text != '{}' else '피드백 없음 (첫 실행 또는 아직 없음)'}

=== 지시 ===
지금 우리 팀이 가장 임팩트 있는 결과를 내려면 이번에 뭘 집중해야 하는지 판단해라.

반환 형식 (JSON만):
{{
  "assessment": "현재 상태 한 줄 요약",
  "priority": "이번 실행 최우선 과제 (research/strategy/copy/validation/full 중 하나)",
  "reason": "왜 이게 우선인지",
  "focus": "이번 실행에서 특히 집중할 포인트 (구체적으로)"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    # JSON 파싱
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()
    try:
        return json.loads(text)
    except Exception:
        return {"assessment": "판단 실패", "priority": "full", "reason": "자동 판단 불가", "focus": "전체 실행"}


def run(industry: str = "소상공인 네이버 플레이스 마케팅 대행"):
    # ── 파이프라인 캐시 초기화 ──
    if HAS_PIPELINE_CACHE:
        reset_pipeline_cache()

    client = get_client()
    context = {"industry": industry}

    # BUG-006: 변수 미바인딩 방지를 위해 사전 초기화
    research = ""
    strategy = ""
    copy = ""
    validation = ""

    print(f"\n{'='*60}")
    print(f"🏢 오프라인 마케팅 팀 자율 가동")
    print(f"{'='*60}")

    # ── 0-1. 자동 레퍼런스 수집 ──────────────────────────────
    if HAS_PRE_RESEARCH:
        try:
            research_data = auto_research(industry, max_accounts=3, posts_per_account=3)
            if research_data:
                context["reference_research"] = research_data
                print("  자동 레퍼런스 수집 완료")
        except Exception as e:
            print(f"  자동 레퍼런스 수집 실패: {e}")

    # ── 0-2. 미션 + 학습 자동 로드 ──────────────────────────────
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from core.pipeline_utils import enrich_context, self_critique_all
        context = enrich_context(context, team_slug="offline_marketing")
    except Exception as e:
        print(f"⚠️ 미션/학습 로드 실패: {e}")

    mission_path = os.path.join(TEAM_DIR, "mission.md")
    try:
        with open(mission_path, encoding="utf-8") as f:
            mission = f.read()
    except Exception:
        mission = "소상공인 대상 카톡/문자 비대면 영업으로 월 5건 계약 달성"

    # ── 마케팅 스킬 컨텍스트 자동 로드 ──────────────────────────────
    marketing_skills_context = _load_marketing_skills()
    if marketing_skills_context:
        context["marketing_skills"] = marketing_skills_context
        print("  마케팅 스킬 컨텍스트 로드 완료")

    # ── 팀 학습 지식 주입 ──────────────────────────────
    if HAS_KNOWLEDGE_INJECTOR:
        try:
            team_knowledge = get_team_knowledge("offline_marketing", max_tokens=2000)
            if team_knowledge:
                context["team_knowledge"] = team_knowledge
                print("  팀 학습 지식 로드 완료")
        except Exception as e:
            print(f"  팀 학습 지식 로드 실패 (무시됨): {e}")

    # ── 1. 현재 상태 파악 ─────────────────────────────────────
    print("\n[자가진단] 현재 팀 산출물 상태 파악 중...")
    state = _read_current_state()

    # 기존 자료 컨텍스트로 로드
    for key, info in state.items():
        if isinstance(info, dict) and info.get("exists"):
            context[f"current_{key}"] = info.get("preview", "")
    context["current_materials"] = context.get("current_스크립트", "")

    # ── 2. 자율 판단 — 이번에 뭘 집중할지 ────────────────────
    print("[자가진단] 이번 실행 우선순위 판단 중...")
    assessment = _self_assess(client, state, mission)
    priority = assessment.get("priority", "full")
    focus = assessment.get("focus", "")
    context["focus"] = focus
    context["assessment"] = assessment.get("assessment", "")

    print(f"\n📋 팀 자가진단 결과:")
    print(f"   현재 상태: {assessment.get('assessment', '')}")
    print(f"   이번 집중: {priority} — {assessment.get('reason', '')}")
    print(f"   포커스: {focus}")

    # ── 3. 우선순위에 따른 선택적 실행 ───────────────────────
    # BUG-FIX: 첫 실행 시 strategy/copy가 비어있으므로 validation을 선택하기 전에 먼저 생성해야 함
    # 부분 실행도 "full"과 동일하게 전체 흐름 실행 (strategy/copy 없이는 validation 불가)

    if priority in ("research", "strategy", "copy", "validation", "full") or priority not in ("research", "strategy", "copy", "validation", "full"):
        # 모든 경우 전체 실행 (부분 실행은 폐기)
        print("\n[1] 영업 전문가 자료 수집...")
        if HAS_STATUS_TRACKER:
            update_status("researcher", "offline_marketing", "running", "영업 자료 수집 중")
        try:
            research = researcher.run(context)
            context["research"] = research
            save("_research_영업전문가자료.md", research)
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("researcher")

        print("\n[2] 영업 전략 설계...")
        if HAS_STATUS_TRACKER:
            update_status("strategist", "offline_marketing", "running", "전략 수립 중")
        try:
            strategy = strategist.run(context, client)
            context["strategy"] = strategy
            save("영업_전략_재설계.md", strategy)
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("strategist")

        # 콘텐츠 생성 전 구조화 (스크립트 생성 전 메시징 구조 확정)
        print("\n[2.5] 스크립트 메시징 구조화...")
        if HAS_STRUCTURER:
            try:
                structure = structure_before_create(
                    task="소상공인 대상 영업 스크립트",
                    target_info={
                        "industry": industry,
                        "challenge": context.get("assessment", "업체 온라인 매출 부진"),
                        "strategy_preview": strategy[:300] if strategy else ""
                    },
                    client=client
                )
                context = merge_structure_to_context(context, structure)
                save("_구조_메시징설계.json", str(structure))
                print("✅ 메시징 구조화 완료")
            except Exception as e:
                print(f"⚠️  구조화 스킵: {e}")
        else:
            print("⚠️  구조화 모듈 미사용")

        print("\n[3] 스크립트 + PPT 카피 생성...")
        if HAS_STATUS_TRACKER:
            update_status("copywriter", "offline_marketing", "running", "스크립트 작성 중")
        try:
            copy = copywriter.run(context, client)
            context["copy"] = copy
            save("영업_스크립트_v2.md", copy)
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("copywriter")

        print("\n[4] 현장 관점 검증...")
        if HAS_STATUS_TRACKER:
            update_status("validator", "offline_marketing", "running", "검증 중")
        try:
            validation = validator.run(context, client)
            context["validation"] = validation
            save("영업_사업검증.md", validation)
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("validator")

    # ── 4.5 검증자 피드백 → 스크립트 재작성 ───────────────────────────
    if validation and copy:
        print("\n[4.5] 검증자 피드백 반영 — 스크립트 재작성...")
        if HAS_STATUS_TRACKER:
            update_status("copywriter", "offline_marketing", "running", "검증 피드백 반영 재작성 중")
        try:
            revise_prompt = f"""너는 영업 카피라이터야. 검증자가 현장 관점에서 지적한 문제들을 반영해서 스크립트를 수정해.

=== 검증자 피드백 (Opus 현장 전문가) ===
{validation[:4000]}

=== 현재 스크립트 ===
{copy[:6000]}

=== 수정 규칙 ===
1. 검증자가 🔴로 표시한 항목은 반드시 수정
2. 검증자가 제시한 대체 스크립트가 있으면 그걸 사용
3. 기존 마크다운 포맷 유지
4. 거절 대응 스크립트, 7일 캘린더가 없으면 추가
5. 모든 메시지 끝에 CTA(카톡링크/전화번호) 포함

수정된 전체 스크립트를 반환해."""

            revise_response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                messages=[{"role": "user", "content": revise_prompt}],
                system="검증자의 피드백을 정확히 반영해서 수정해. 회사명 첫줄 금지, 거짓 사회적 증거 금지, 가짜 희소성 금지, CTA 필수."
            )
            revised_copy = revise_response.content[0].text.strip()
            if len(revised_copy) > len(copy) * 0.5:  # 너무 짧으면 실패로 간주
                copy = revised_copy
                context["copy"] = copy
                save("영업_스크립트_v3_검증반영.md", copy)
                print("✅ 검증 피드백 반영 완료 → 영업_스크립트_v3_검증반영.md")
            else:
                print("⚠️ 재작성 결과가 너무 짧음 — 기존 스크립트 유지")
        except Exception as e:
            print(f"⚠️ 검증 피드백 반영 실패: {e}")
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("copywriter")

    # ── 5. 아웃풋 자가점검 (리안 보고 전 마지막 QA) ───────────────────
    print("\n[5] 최종 품질 검사 | 자가점검 루프...")
    try:
        critique_output = {
            "copy": copy,
            "strategy": strategy,
            "industry": industry,
            "context": context
        }
        critique_result = post_run_critique(critique_output, client, max_iterations=2)

        # 수정된 스크립트 저장 (이슈가 있더라도 개선된 버전 저장)
        if critique_result["final_copy"] != copy:
            save("영업_스크립트_v2_자가수정.md", critique_result["final_copy"])
            copy = critique_result["final_copy"]
            context["copy"] = copy

        # 자가점검 보고서 저장
        critique_report = {
            "passed": critique_result["passed"],
            "iterations": critique_result["iterations"],
            "issues_found": len(critique_result["issues"]),
            "improvements_applied": len(critique_result["improvements"]),
            "unresolved_issues": [i for i in critique_result["issues"] if i.get("status") == "문제있음"]
        }
        with open(os.path.join(OUTPUT_DIR, "_critique_report.json"), "w", encoding="utf-8") as f:
            json.dump(critique_report, f, ensure_ascii=False, indent=2)

        context["critique_result"] = critique_result

    except Exception as e:
        print(f"⚠️  자가점검 루프 에러 (파이프라인 계속 진행): {e}")
        context["critique_result"] = {"passed": False, "error": str(e)}

    # 자가점검
    try:
        critique = self_critique_all(context, client, team_name="offline_marketing")
        context["critique"] = critique
        save("_자가점검_결과.md", critique.get("full_critique", ""))
    except Exception as e:
        print(f"\n⚠️ 자가점검 실패: {e}")

    # 보고사항들.md 업데이트
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import write_report, save_team_result, collect_feedback

        # 결과물 지식으로 저장
        save_team_result("offline_marketing", "_research_영업전문가자료.md", research,
                         tags=["영업", "SPIN", "Challenger", "클로징", "소상공인"])
        save_team_result("offline_marketing", "영업_전략_재설계.md", strategy,
                         tags=["영업", "전략", "퍼널", "소상공인"])
        save_team_result("offline_marketing", "영업_스크립트_v2.md", copy,
                         tags=["영업", "DM", "스크립트", "카피"])

        # 보고
        critique_summary = ""
        if context.get("critique_result"):
            cr = context["critique_result"]
            if cr.get("passed"):
                critique_summary = (
                    f"\n\n**✅ 자가점검 통과** (총 {cr.get('iterations', 0)}회 검토)\n"
                    f"- 발견 이슈: {len(cr.get('issues', []))}개\n"
                    f"- 적용 개선안: {len(cr.get('improvements', []))}개"
                )
            else:
                unresolved = len([i for i in cr.get('issues', []) if i.get('status') == '문제있음'])
                critique_summary = (
                    f"\n\n**⚠️  자가점검 진행 중** (총 {cr.get('iterations', 0)}회 검토)\n"
                    f"- 미해결 이슈: {unresolved}개\n"
                    f"- 상세: `_critique_report.json` 참조"
                )

        report_content = (
            f"**{industry}** 영업 자료 완성.\n\n"
            f"- 재원: 영업 전문가 자료 수집 완료\n"
            f"- 승현: 영업 전략 재설계 완료 (운영 7개 항목 포함)\n"
            f"- 예진: DM 스크립트 + PPT 카피 완성\n"
            f"- 검증자: 현장 관점 사업 검증 완료"
            f"{critique_summary}\n\n"
            f"저장 위치: `{OUTPUT_DIR}`\n\n"
            f"리안, **영업_사업검증.md 먼저 봐줘.** "
            f"영업 시작 전에 고쳐야 할 것들 정리되어 있어."
        )
        write_report("재원/승현/예진/검증자", "오프라인 마케팅팀", report_content)

        # 피드백 수집
        collect_feedback("offline_marketing")
    except Exception as e:
        print(f"\n보고/저장 실패: {e}")

    print(f"\n{'='*60}")
    print("✅ 오프라인 마케팅 팀 완료")
    print(f"저장 위치: {OUTPUT_DIR}")
    print(f"{'='*60}")

    # ── 파이프라인 캐시 통계 출력 ──
    if HAS_PIPELINE_CACHE:
        cache = get_pipeline_cache()
        cache.print_stats()

    return context


# ── 자율 루프: 결과 수집 + 자동 개선 ────────────────────────────────────

def ingest_results(raw_text: str):
    """
    리안이 results.txt에 자유 형식으로 적은 결과를 파싱해서 status.json 업데이트.
    예: "미용실 거절, 이유: 비싸다"
        "포에트리헤어 계약 성사, 주목패키지"
        "3건 DM 발송, 1건 답장"
    """
    client = get_client()
    status_path = os.path.join(TEAM_DIR, "status.json")

    # 현재 status 로드
    if os.path.exists(status_path):
        with open(status_path, encoding="utf-8") as f:
            status = json.load(f)
    else:
        status = {
            "team": "offline_marketing",
            "last_updated": datetime.now().isoformat(),
            "kpi": {"계약전환율": None, "답장률": None, "클로징사이클_일": None, "월계약건수": 0},
            "current_version": "v1",
            "data_count": 0,
            "results_log": [],
            "last_improvement_reason": "초기 세팅",
            "next_action": "데이터 수집 대기"
        }

    # Claude Sonnet으로 자유 형식 파싱
    parse_prompt = f"""너는 영업팀 데이터 수집자야.

리안이 영업 결과를 자유 형식으로 적은 텍스트를 구조화된 JSON으로 변환해줘.

=== 입력 텍스트 ===
{raw_text}

=== 추출할 정보 ===
각 문장/라인에서:
- result_type: "계약" | "거절" | "DM발송" | "답장" | "기타"
- value: 숫자 (예: 거절이면 거절건수, DM발송이면 발송건수)
- reason: 거절 이유 (있으면), 기타 정보

=== 반환 형식 (JSON 배열) ===
[
  {{"result_type": "계약", "value": 1, "reason": "주목패키지 패턴"}},
  {{"result_type": "거절", "value": 1, "reason": "비싸다"}},
  {{"result_type": "DM발송", "value": 3, "reason": ""}},
  {{"result_type": "답장", "value": 1, "reason": ""}}
]

JSON 배열만 반환. 설명 없음."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": parse_prompt}]
    )
    text = response.content[0].text.strip()

    # JSON 파싱
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()

    try:
        parsed_results = json.loads(text)
    except Exception as e:
        print(f"파싱 실패: {e}")
        parsed_results = []

    # ── status.json에 누적 ──
    for item in parsed_results:
        result_type = item.get("result_type", "기타")
        value = item.get("value", 1)
        reason = item.get("reason", "")

        status["results_log"].append({
            "timestamp": datetime.now().isoformat(),
            "type": result_type,
            "value": value,
            "reason": reason
        })

        # KPI 업데이트
        if result_type == "계약":
            current = status["kpi"].get("월계약건수") or 0
            status["kpi"]["월계약건수"] = current + value
        elif result_type == "DM발송":
            # DM 발송 추적용 (별도 처리)
            pass
        elif result_type == "답장":
            # 답장률 계산 (별도 처리)
            pass

    status["data_count"] = len(status["results_log"])
    status["last_updated"] = datetime.now().isoformat()

    # status.json 저장
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    print(f"\n📊 결과 수집 완료: {status['data_count']}건")
    print(f"월 계약: {status['kpi']['월계약건수']}건")

    # ── 5건 이상이면 자동 improve() 실행 ──
    if status["data_count"] >= 5 and status["data_count"] % 5 == 0:
        print(f"\n🚀 데이터 {status['data_count']}건 도달. 자동 개선 시작...")
        improve()

    return status


def improve():
    """
    data_count >= 5일 때 자동 호출.
    약한 KPI 구간 분석 → 개선안 생성 → 파이프라인 재실행.
    """
    client = get_client()
    status_path = os.path.join(TEAM_DIR, "status.json")
    results_dir = os.path.join(TEAM_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    # status.json 읽기
    if not os.path.exists(status_path):
        print("status.json이 없습니다. ingest_results()를 먼저 실행하세요.")
        return

    with open(status_path, encoding="utf-8") as f:
        status = json.load(f)

    results_log = status.get("results_log", [])
    if not results_log:
        print("분석할 데이터가 없습니다.")
        return

    print(f"\n{'='*60}")
    print(f"🔍 데이터 분석 및 개선 시작 (총 {len(results_log)}건)")
    print(f"{'='*60}")

    # ── 약한 KPI 구간 식별 ──
    contracts = [r for r in results_log if r["type"] == "계약"]
    rejections = [r for r in results_log if r["type"] == "거절"]
    rejection_reasons = {}
    for r in rejections:
        reason = r.get("reason", "미기입")
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

    # ── 분석 프롬프트 생성 ──
    analysis_prompt = f"""너는 영업 전략 컨설턴트야.

=== 현재 데이터 ===
- 총 접촉: {len(results_log)}건
- 계약 성사: {len(contracts)}건
- 거절: {len(rejections)}건
- 계약 전환율: {(len(contracts) / len(results_log) * 100 if results_log else 0):.1f}%

=== 거절 사유 분석 ===
{json.dumps(rejection_reasons, ensure_ascii=False, indent=2)}

=== 과제 ===
데이터를 보면 가장 약한 부분이 뭔지 식별하고, 그 부분을 강화할 구체적인 개선안을 제시해줘.
예를 들어:
- 거절이 비싼 이유로 많으면 → 가격 정당화 스크립트 강화
- 답장이 없으면 → 첫 DM 오픈율 높이는 제목/내용
- 클로징이 늦으면 → 빠른 약속 취급 메시지 추가

=== 반환 형식 (JSON) ===
{{
  "weak_point": "가장 약한 KPI 이름 (예: 거절사유 비싼 것)",
  "impact": "이 부분이 전환율에 미치는 영향 (%)",
  "improvement_focus": "개선할 팀원 (researcher/strategist/copywriter/validator 중 하나)",
  "specific_actions": [
    "구체적 개선 액션 1",
    "구체적 개선 액션 2",
    "구체적 개선 액션 3"
  ],
  "expected_impact": "개선 후 예상 전환율 증대 (%)"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": analysis_prompt}]
    )
    text = response.content[0].text.strip()

    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()

    try:
        analysis = json.loads(text)
    except Exception as e:
        print(f"분석 실패: {e}")
        analysis = {"weak_point": "전체", "improvement_focus": "full", "specific_actions": []}

    print(f"\n📌 약한 포인트: {analysis.get('weak_point', '전체')}")
    print(f"📌 개선 필요 영역: {analysis.get('improvement_focus', 'full')}")
    print(f"📌 기대 효과: {analysis.get('expected_impact', '-')}%")

    # ── 체크포인트: 리안 확인이 필요한 상황이면 멈추고 질문 ──
    clarify = _check_clarification_needed(analysis, status, results_log)
    if clarify:
        _ask_lian(clarify, analysis, status)
        print(f"\n⏸️  리안 확인 필요 → 보고사항들.md에 질문 올림. 답변 후 improve() 재실행.")
        return

    # ── 개선 포커스 결정 ──
    improvement_focus = analysis.get("improvement_focus", "full")
    focus_text = f"데이터 기반 개선: {analysis.get('weak_point')}. 조치: {', '.join(analysis.get('specific_actions', [])[:2])}"

    # ── 파이프라인 재실행 (선택된 영역만) ──
    print(f"\n🔄 파이프라인 재실행 중 ({improvement_focus})...")

    # 버전 업그레이드
    old_version = status.get("current_version", "v1")
    version_num = int(old_version[1:]) + 1
    new_version = f"v{version_num}"

    context = {
        "industry": "소상공인 네이버 플레이스 마케팅 대행",
        "focus": focus_text,
        "improvement_actions": analysis.get("specific_actions", [])
    }

    # 선택적 재실행
    if improvement_focus in ("researcher", "full"):
        print("\n[1] 영업 전문가 자료 재수집...")
        research = researcher.run(context)
        save(f"_research_{new_version}.md", research)

    if improvement_focus in ("strategist", "full"):
        print("\n[2] 영업 전략 재설계...")
        strategy = strategist.run(context, client)
        save(f"영업_전략_{new_version}.md", strategy)

    if improvement_focus in ("copywriter", "full"):
        print("\n[3] 스크립트 재작성...")
        copy = copywriter.run(context, client)
        save(f"영업_스크립트_{new_version}.md", copy)

    if improvement_focus in ("validator", "full"):
        print("\n[4] 현장 검증...")
        validation = validator.run(context, client)
        save(f"영업_사업검증_{new_version}.md", validation)

    # ── 결과 저장 (results/ 폴더에 날짜별) ──
    improvement_result = {
        "timestamp": datetime.now().isoformat(),
        "version": new_version,
        "data_count_at_improvement": status["data_count"],
        "weak_point": analysis.get("weak_point"),
        "improvement_focus": improvement_focus,
        "actions_taken": analysis.get("specific_actions", []),
        "expected_impact": analysis.get("expected_impact")
    }

    result_filename = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_path = os.path.join(results_dir, result_filename)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(improvement_result, f, ensure_ascii=False, indent=2)

    # ── status.json 업데이트 ──
    status["current_version"] = new_version
    status["last_improvement_reason"] = analysis.get("weak_point")
    status["last_updated"] = datetime.now().isoformat()

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    # ── 보고 ──
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from knowledge.manager import write_report

        actions_text = "".join([f"- {action}\n" for action in analysis.get("specific_actions", [])])
        report_content = (
            f"**데이터 기반 자동 개선** — {new_version}\n\n"
            f"- 수집 데이터: {status['data_count']}건\n"
            f"- 약한 포인트: {analysis.get('weak_point', 'N/A')}\n"
            f"- 개선 영역: {improvement_focus}\n"
            f"- 예상 효과: {analysis.get('expected_impact', 'N/A')}%\n\n"
            f"조치 내용:\n"
            f"{actions_text}\n"
            f"저장 위치: `{results_dir}`"
        )
        write_report("오프라인 마케팅팀", "자율 개선", report_content)
    except Exception as e:
        print(f"보고 실패: {e}")

    print(f"\n{'='*60}")
    print(f"✅ 개선 완료 ({new_version})")
    print(f"{'='*60}")


# ── 체크포인트 함수들 ──────────────────────────────────────────────────────────

def _check_clarification_needed(analysis: dict, status: dict, results_log: list) -> str | None:
    """
    리안 확인이 필요한 상황 감지.
    확인 필요하면 이유 문자열 반환, 없으면 None.
    """
    weak_point = analysis.get("weak_point", "")
    actions = analysis.get("specific_actions", [])
    focus = analysis.get("improvement_focus", "")
    expected = analysis.get("expected_impact", "0")

    # 1. 가격/패키지 변경 감지
    price_keywords = ["가격", "패키지", "요금", "29만", "49만", "89만", "단가", "할인"]
    if any(kw in weak_point or any(kw in a for a in actions) for kw in price_keywords):
        return "가격/패키지 변경이 필요한 것 같아요"

    # 2. 타겟 업종/지역 변경 감지
    target_keywords = ["업종 변경", "지역 변경", "타겟 변경", "다른 업종", "새로운 타겟"]
    if any(kw in weak_point or any(kw in a for a in actions) for kw in target_keywords):
        return "타겟 업종 또는 지역을 바꾸는 방향 같아요"

    # 3. 전면 방향 전환 감지 (focus=full + 데이터 적음)
    data_count = status.get("data_count", 0)
    if focus == "full" and data_count < 10:
        return f"데이터가 {data_count}건밖에 없는데 전면 개선을 하려고 해요. 방향이 맞는지 확인 필요해요"

    # 4. 기대 효과 비현실적 (50% 이상)
    try:
        impact_num = float(str(expected).replace("%", "").strip())
        if impact_num >= 50:
            return f"기대 효과가 {expected}%로 너무 높게 잡혔어요. 방향이 맞는지 확인 필요해요"
    except Exception:
        pass

    # 5. 계약이 아예 0건인데 데이터가 10건 이상
    contracts = [r for r in results_log if r["type"] == "계약"]
    if data_count >= 10 and len(contracts) == 0:
        return f"데이터 {data_count}건인데 계약이 0건이에요. 영업 방향 자체를 점검해야 할 수 있어요"

    return None


def _ask_lian(reason: str, analysis: dict, status: dict):
    """
    .pending_questions.json에 저장.
    Claude Code가 대화 시작 시 이 파일 확인 → 리안에게 바로 질문.
    """
    questions_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "company", ".pending_questions.json"
    )

    # 기존 질문 로드
    pending = []
    if os.path.exists(questions_path):
        try:
            with open(questions_path, encoding="utf-8") as f:
                pending = json.load(f)
        except Exception:
            pending = []

    # 새 질문 추가
    pending.append({
        "timestamp": datetime.now().isoformat(),
        "team": "오프라인 마케팅팀",
        "reason": reason,
        "weak_point": analysis.get("weak_point", ""),
        "improvement_focus": analysis.get("improvement_focus", ""),
        "planned_actions": analysis.get("specific_actions", []),
        "data_count": status.get("data_count", 0),
        "answered": False
    })

    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    print(f"\n❓ 질문 저장됨 → company/.pending_questions.json")
    print(f"   Claude Code 열면 자동으로 물어볼 거야.")
