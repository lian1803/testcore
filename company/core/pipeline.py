import os
import sys
import anthropic
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from agents import sieun, seoyun, minsu, haeun, junhyeok, taeho, jihun, designer
from core.handoff import PipelineHandoff
from core.discussion import DiscussionRoom
from core.ui import print_step, print_save_ok, print_section
from core.output import create_output_dir, save_file
from core.notifier import (
    notify_agent_complete,
    notify_discussion_round,
    notify_verdict,
    notify_execution_start,
    notify_completion,
    notify_error,
    wait_confirm,
)
from teams.education.pipeline import run as build_team
from core.report_generator import generate_board_report, save_report_to_보고사항
from core.self_improve import post_run_review

# 파이프라인 캐시
try:
    from core.cache import reset_pipeline_cache, get_pipeline_cache
    HAS_PIPELINE_CACHE = True
except ImportError:
    HAS_PIPELINE_CACHE = False

# 상태 추적
try:
    from utils.status_tracker import update_status, clear_status
    HAS_STATUS_TRACKER = True
except ImportError:
    HAS_STATUS_TRACKER = False

load_dotenv()


def get_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(".env 파일에 ANTHROPIC_API_KEY가 없어. .env.example 참고해서 만들어줘.")
    return anthropic.Anthropic(api_key=api_key)


def run_pipeline(sieun_result: dict, autopilot: bool = False) -> None:
    # ── 파이프라인 캐시 초기화 ──
    if HAS_PIPELINE_CACHE:
        reset_pipeline_cache()
        print("\n💾 파이프라인 캐시 초기화")

    client = get_client()
    context = dict(sieun_result)

    # 프로젝트명 추출 (아이디어 앞 20자)
    raw_idea = context.get("idea", "프로젝트")
    project_name = raw_idea[:20].strip()
    output_dir = create_output_dir(project_name)

    print(f"\n\n{'='*60}")
    print(f"📁 산출물 저장 경로: {output_dir}")
    print(f"{'='*60}\n")

    # ── 이사팀 ──────────────────────────────────────────────────

    # 태호 + 서윤: 병렬 실행 (둘 다 아이디어만 필요, 서로 독립)
    print(f"\n[1-2/9] 트렌드 + 시장조사 (병렬)...")

    def _run_taeho():
        if HAS_STATUS_TRACKER:
            update_status("태호", "이사팀", "running", "트렌드 스카우팅 중")
        try:
            result = taeho.run(context, client)
            if HAS_STATUS_TRACKER:
                clear_status("태호")
            return result
        except Exception as e:
            if HAS_STATUS_TRACKER:
                clear_status("태호")
            print(f"\n⚠️  태호 에러 (건너뜀): {e}")
            return f"트렌드 스카우팅 실패: {e}"

    def _run_seoyun():
        if HAS_STATUS_TRACKER:
            update_status("서윤", "이사팀", "running", "시장조사 중")
        try:
            result = seoyun.run(context, client)
            if HAS_STATUS_TRACKER:
                clear_status("서윤")
            return result
        except Exception as e:
            if HAS_STATUS_TRACKER:
                clear_status("서윤")
            print(f"\n⚠️  서윤 에러 (건너뜀): {e}")
            return f"시장조사 실패: {e}"

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_taeho = pool.submit(_run_taeho)
        fut_seoyun = pool.submit(_run_seoyun)
        try:
            # 각 에이전트에 180초(3분) 타임아웃 설정
            taeho_result = fut_taeho.result(timeout=180)
        except Exception as e:
            print(f"\n⚠️  태호 타임아웃 또는 에러: {e}")
            taeho_result = "[태호 타임아웃 — 건너뜀]"

        try:
            # 서윤 2-pass (Pass 1 + Pass 2)라 타임아웃 충분히 확보
            seoyun_result = fut_seoyun.result(timeout=540)
        except Exception as e:
            print(f"\n⚠️  서윤 타임아웃 또는 에러: {e}")
            seoyun_result = "[서윤 타임아웃 — 건너뜀]"

    # 에러 결과 필터링 (다음 에이전트 context에 유효한 데이터만 주입)
    def _is_error_result(result: str) -> bool:
        """에러/빈 결과 판정."""
        if not result or not result.strip():
            return True
        return result.strip().startswith("[")

    taeho_clean = "" if _is_error_result(taeho_result) else taeho_result
    seoyun_clean = "" if _is_error_result(seoyun_result) else seoyun_result

    context["taeho"] = taeho_result
    save_file(output_dir, "08_트렌드_태호.md", taeho_result)
    print_save_ok("08_트렌드_태호.md")
    notify_agent_complete("태호 | 트렌드 스카우팅", 1, 9)

    context["seoyun"] = seoyun_result
    save_file(output_dir, "01_시장조사_서윤.md", seoyun_result)
    print_save_ok("01_시장조사_서윤.md")
    notify_agent_complete("서윤 | 시장조사", 2, 9)

    # 민수: 전략 (clean 데이터 사용)
    context_for_minsu = dict(context)
    if seoyun_clean:
        context_for_minsu["seoyun"] = seoyun_clean
    print(f"\n[3/9] 전략 수립...")
    if HAS_STATUS_TRACKER:
        update_status("민수", "이사팀", "running", "전략 수립 중")
    try:
        minsu_result = minsu.run(context_for_minsu, client)
    except Exception as e:
        print(f"\n⚠️  민수 에러 (건너뜀): {e}")
        minsu_result = f"전략 수립 실패: {e}"
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("민수")
    context["minsu"] = minsu_result
    save_file(output_dir, "02_전략_민수.md", minsu_result)
    print_save_ok("02_전략_민수.md")
    notify_agent_complete("민수 | 전략 수립", 3, 9)

    # 하은: 검증 (clean 데이터 사용)
    context_for_haeun = dict(context)
    minsu_clean = "" if _is_error_result(minsu_result) else minsu_result
    context_for_haeun["minsu"] = minsu_clean
    context_for_haeun["seoyun"] = seoyun_clean
    print(f"\n[4/9] 검증/반론...")
    if HAS_STATUS_TRACKER:
        update_status("하은", "이사팀", "running", "검증/반론 중")
    try:
        haeun_result = haeun.run(context_for_haeun, client)
    except Exception as e:
        print(f"\n⚠️  하은 에러 (건너뜀): {e}")
        haeun_result = f"검증 실패: {e}"
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("하은")
    context["haeun"] = haeun_result
    save_file(output_dir, "03_검증_하은.md", haeun_result)
    print_save_ok("03_검증_하은.md")
    notify_agent_complete("하은 | 검증/반론", 4, 9)

    # 토론 루프: 민수↔하은 (최대 2라운드)
    print(f"\n[4.5/9] 토론 루프...")
    if HAS_STATUS_TRACKER:
        update_status("토론", "이사팀", "running", "민수↔하은 토론 중")
    try:
        discussion = DiscussionRoom()
        context = discussion.run(context, client)
    except Exception as e:
        print(f"\n⚠️  토론 루프 에러 (건너뜀): {e}")
        context["discussion_transcript"] = []
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("토론")
    save_file(output_dir, "03b_토론_결과.md", "\n\n".join([
        f"## 라운드 {t['round']}\n{t['analysis']}\n\n[민수 수정]\n{t['minsu_revised']}\n\n[하은 최종]\n{t['haeun_final']}"
        for t in context.get("discussion_transcript", [])
    ]) or "토론 없음")
    print_save_ok("03b_토론_결과.md")

    # 준혁: 최종 판단 (V4 이후 full context 전달 — Quality Gate가 실제 내용을 검증해야 함)
    context_for_junhyeok = dict(context)
    context_for_junhyeok["taeho"] = context.get("taeho", "")[:1500]
    context_for_junhyeok["seoyun"] = context.get("seoyun", "")
    context_for_junhyeok["minsu"] = context.get("minsu", "")
    context_for_junhyeok["haeun"] = context.get("haeun", "")
    transcripts = context.get("discussion_transcript", [])
    if transcripts:
        last = transcripts[-1]
        context_for_junhyeok["discussion_transcript"] = [{
            "round": last.get("round", 1),
            "analysis": last.get("analysis", "")[:300],
            "minsu_revised": last.get("minsu_revised", "")[:500],
            "haeun_final": last.get("haeun_final", "")[:500],
        }]

    print(f"\n[5/9] 최종 판단...")
    if HAS_STATUS_TRACKER:
        update_status("준혁", "이사팀", "running", "최종 판단 중")
    try:
        junhyeok_result = junhyeok.run(context_for_junhyeok, client)
    except Exception as e:
        print(f"\n⚠️  준혁 에러: {e}")
        junhyeok_result = {"text": f"판단 실패: {e}", "verdict": "CONDITIONAL_GO", "score": 50}
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("준혁")
    context["junhyeok_text"] = junhyeok_result["text"]
    context["verdict"] = junhyeok_result["verdict"]
    context["score"] = junhyeok_result["score"]

    import json
    save_file(output_dir, "04_최종판단_준혁.json", json.dumps({
        "verdict": junhyeok_result["verdict"],
        "score": junhyeok_result["score"],
        "text": junhyeok_result["text"]
    }, ensure_ascii=False, indent=2))
    print_save_ok("04_최종판단_준혁.json")
    notify_agent_complete("준혁 | 최종 판단", 5, 9)
    notify_verdict(junhyeok_result["verdict"], junhyeok_result["score"])

    # ── 시은: 최종 재검토 (델타봇 패턴) ────────────────────────────
    print(f"\n[5.2/9] 최종 재검토 (시은 델타봇)...")
    if HAS_STATUS_TRACKER:
        update_status("시은", "이사팀", "running", "최종 재검토 중")
    try:
        context = sieun.review(context, client)
        save_file(output_dir, "04c_최종재검토_시은.md", context.get("sieun_review", ""))
        print_save_ok("04c_최종재검토_시은.md")
    except Exception as e:
        print(f"\n⚠️  시은 재검토 에러 (건너뜀): {e}")
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("시은")

    # ── 보고서 생성 + 저장 ────────────────────────────────────────
    report = generate_board_report(context)
    save_file(output_dir, "00_이사팀_보고서.md", report)
    print_save_ok("00_이사팀_보고서.md")

    # 보고사항들.md에도 저장
    save_report_to_보고사항(report, project_name)

    # GO 판단이 아니면 종료 (FORCE_GO 환경변수로 강제 통과 가능)
    if junhyeok_result["verdict"] == "NO_GO" and not os.getenv("FORCE_GO"):
        print(f"\n\n❌ 준혁 판단: NO-GO (점수: {junhyeok_result['score']})")
        print("실행팀 진행 안 함. 보고서는 보고사항들.md에 저장됨.")
        print(f"\n📁 결과 저장: {output_dir}")
        return

    # ── 리안 컨펌 ───────────────────────────────────────────────

    verdict_label = {
        "GO": f"GO ({junhyeok_result['score']}점)",
        "CONDITIONAL_GO": f"조건부 GO ({junhyeok_result['score']}점) — 조건 확인 필요",
    }.get(junhyeok_result["verdict"], "GO")

    print(f"\n\n{'='*60}")
    print(f"  이사팀 완료. 준혁 판단: {verdict_label}")
    print(f"  결과 확인: {output_dir}")
    print(f"  📋 보고서: 보고사항들.md 확인")
    print(f"{'='*60}")

    # GO / CONDITIONAL_GO 모두 자동 진행 (조건은 보고사항들.md에 기록됨)
    if junhyeok_result["verdict"] == "CONDITIONAL_GO":
        print(f"\n조건부 GO — 자동 진행 (조건은 보고사항들.md 참고)")
    else:
        print(f"\nGO — 자동 진행")

    notify_execution_start()

    # ── 시은: 큰그림 체크 (GO 확정 직후) ────────────────────────────
    print(f"\n[5.5/9] 큰그림 체크 (시은)...")
    try:
        big_picture = sieun.big_picture_check(context, client)
        context["big_picture"] = big_picture
        save_file(output_dir, "04b_큰그림체크_시은.md", big_picture)
        print_save_ok("04b_큰그림체크_시은.md")
    except Exception as e:
        print(f"\n⚠️  큰그림 체크 에러 (건너뜀): {e}")
        context["big_picture"] = ""

    # ── 설계자: 심층 비즈니스 설계 (2-call 순차) ─────────────────
    # 민수(slim)가 1순위만 뽑으면 설계자가 OKR/필터/STP/VPC/BM 전체를 깊게 설계.
    # 서윤 원본 + 민수 1순위 + 하은 반론을 truncation 없이 전달.
    print(f"\n[5.8/9] 심층 설계 (설계자 2-call)...")
    if HAS_STATUS_TRACKER:
        update_status("설계자", "이사팀", "running", "전략 브리프 + BM 설계 중")
    try:
        designer_result = designer.run(context, client)
        strategy_brief = designer_result.get("strategy_brief", "")
        business_model = designer_result.get("business_model", "")

        # 저장
        save_file(output_dir, "02b_전략브리프_설계자.md", strategy_brief)
        print_save_ok("02b_전략브리프_설계자.md")
        save_file(output_dir, "02c_비즈니스모델_설계자.md", business_model)
        print_save_ok("02c_비즈니스모델_설계자.md")

        # context 업데이트 — 지훈이 볼 수 있게
        context["strategy_brief"] = strategy_brief
        context["business_model"] = business_model
        # 지훈은 기본적으로 context["minsu"]를 전략으로 읽음.
        # 민수(slim) + 설계자(deep) 합쳐서 넘기면 지훈 코드 변경 없이 풍부한 context 활용 가능.
        context["minsu"] = (
            context.get("minsu", "")
            + "\n\n---\n\n# [설계자 1회차] 전략 브리프\n\n"
            + strategy_brief
            + "\n\n---\n\n# [설계자 2회차] 비즈니스 모델\n\n"
            + business_model
        )
    except Exception as e:
        print(f"\n⚠️  설계자 에러 (건너뜀): {e}")
        context["strategy_brief"] = ""
        context["business_model"] = ""
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("설계자")

    # ── 지훈: PRD 작성 ────────────────────────────────────────────

    print(f"\n[6/9] PRD 작성 (지훈)...")
    if HAS_STATUS_TRACKER:
        update_status("지훈", "이사팀", "running", "PRD 작성 중")
    try:
        prd_result = jihun.run(context, client)
        context["prd"] = prd_result
    except Exception as e:
        print(f"\n⚠️  지훈 에러: {e}")
        prd_result = f"PRD 작성 실패: {e}"
        context["prd"] = prd_result
    finally:
        if HAS_STATUS_TRACKER:
            clear_status("지훈")
    save_file(output_dir, "05_PRD_지훈.md", prd_result)
    print_save_ok("05_PRD_지훈.md")
    notify_agent_complete("지훈 | PRD 작성", 6, 9)

    # ── launch_prep: 런칭 준비 (마케팅 채널 + 상품 정의 + 첫 주 플랜) ──
    print(f"\n[6.8/9] 런칭 준비 (마케팅 방향 수립)...")
    try:
        from core.launch_prep import run_launch_prep
        launch_result = run_launch_prep(context, client)
        save_file(output_dir, "07_런칭준비.md", launch_result)
        print_save_ok("07_런칭준비.md")
    except Exception as e:
        print(f"\n⚠️  런칭 준비 에러 (건너뜀): {e}")

    # ── PipelineHandoff: 소프트웨어 프로젝트면 브리핑 문서 생성 ──────

    is_software = context.get("is_software", False)
    handoff_path = None
    if is_software:
        print(f"\n[6.5/9] UltraProduct 브리핑 문서 생성...")
        if HAS_STATUS_TRACKER:
            update_status("시은", "이사팀", "running", "UltraProduct 브리핑 생성 중")
        try:
            handoff = PipelineHandoff(context, output_dir)
            handoff_path = handoff.generate()
            print(f"✅ 브리핑 문서 생성: {handoff_path}")
            print(f"\n{'='*60}")
            print(f"  🚀 소프트웨어 프로젝트 — UltraProduct 준비 완료!")
            print(f"{'='*60}")
            print(f"  다음 단계:")
            print(f"  1. 아래 폴더로 이동:")
            print(f"     cd \"{handoff_path}\"")
            print(f"  2. Claude Code 실행:")
            print(f"     claude")
            print(f"  3. /work 입력 → Wave 3부터 자동 실행")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"\n⚠️  핸드오프 에러: {e}")
        finally:
            if HAS_STATUS_TRACKER:
                clear_status("시은")

    # ── 리안 인터뷰 + 팀 설계 + 교육팀 ────────────────────────────

    print(f"\n\n{'='*60}")
    print(f"  팀 설계 시작")
    print(f"{'='*60}")

    # 시은: 리안 워크플로우 인터뷰 (자동파일럿이면 추론, 대화형이면 직접 질문)
    print(f"\n[6/8] 리안 인터뷰 ({'자동 추론' if autopilot else '실제 워크플로우 파악'})...")
    try:
        if autopilot:
            interview = sieun.autopilot_interview(context, client)
        else:
            interview = sieun.interview_for_team(context, client, interactive=True)
        context["interview"] = interview
    except Exception as e:
        print(f"\n⚠️  인터뷰 에러: {e}")
        context["interview"] = ""
    save_file(output_dir, "05_리안인터뷰_시은.md", context.get("interview", ""))
    print_save_ok("05_리안인터뷰_시은.md")

    # 시은: 팀 구성 설계
    print(f"\n[7/8] 팀 구성 설계...")
    try:
        team_name, team_purpose = sieun.design_team(context, client)
    except Exception as e:
        print(f"\n⚠️  시은 팀 설계 에러: {e}")
        team_name = project_name + "_팀"
        team_purpose = context.get("clarified", "")
    save_file(output_dir, "06_팀설계_시은.md", f"# 팀 설계\n\n팀 이름: {team_name}\n\n팀 업무:\n{team_purpose}")
    print_save_ok("06_팀설계_시은.md")
    notify_agent_complete("시은 | 팀 구성 설계", 7, 8)

    # 리안 확인 + 수정
    print(f"\n\n{'='*60}")
    print(f"  📋 시은이 설계한 팀:")
    print(f"  팀 이름: {team_name}")
    print(f"  팀 업무:")
    for line in team_purpose.split("\n")[:8]:
        if line.strip():
            print(f"    {line.strip()}")
    print(f"{'='*60}")
    # 팀 설계 자동 승인 (결과는 보고사항들.md에 저장됨)
    team_feedback = ""
    print(f"\n팀 설계 자동 승인")

    # 이사팀 분석 결과를 팀 업무에 포함
    board_summary = f"""{team_purpose}

=== 이사팀 분석 결과 (팀 교육 시 참고) ===
트렌드: {context.get('taeho', '')[:300]}
시장조사: {context.get('seoyun', '')[:500]}
전략: {context.get('minsu', '')[:500]}
검증: {context.get('haeun', '')[:300]}
Go/No-Go: {context.get('verdict', '')} ({context.get('score', '')}점)"""

    # 교육팀: 자동으로 팀 생성
    print(f"\n[7/7] 교육팀 → 팀 생성 + 교육...")
    try:
        team_dir = build_team(team_name, board_summary)
        print(f"\n✅ {team_name} 생성 완료: {team_dir}")
        notify_agent_complete(f"교육팀 | {team_name} 생성", 7, 7)
    except Exception as e:
        print(f"\n⚠️  교육팀 에러: {e}")
        team_dir = None

    # 이사팀 결과 저장
    save_file(output_dir, "06_이사팀_컨텍스트.md", board_summary)
    print_save_ok("06_이사팀_컨텍스트.md")

    # ── 완료 ──────────────────────────────────────────────────

    print(f"\n\n{'='*60}")
    print(f"  리안 컴퍼니 완료!")
    print(f"{'='*60}")
    print(f"\n  산출물: {output_dir}")
    if team_dir:
        print(f"  생성된 팀: {team_dir}")

    # 비용 통계 출력
    try:
        from utils.monitor import get_monitor
        monitor = get_monitor()
        summary = monitor.get_summary()
        if summary["calls"] > 0:
            print(f"\n  💰 LLM 비용 통계:")
            print(f"     호출 수: {summary['calls']}")
            print(f"     총 토큰: {summary['total_tokens']:,}")
            print(f"     예상 비용: ${summary['total_cost']:.4f}")
            print(f"     로그: {summary['log_file']}")
    except Exception as e:
        pass  # 모니터 에러 무시

    # 디스코드 완료 알림
    notify_completion(output_dir, project_name)

    # ── 시스템 자기 점검 ─────────────────────────────────────────
    try:
        post_run_review("이사팀 파이프라인", context)
    except Exception as e:
        print(f"\n⚠️ 자기 점검 에러 (무시): {e}")

    # ── V4 Framework Validator (Level 1 구조 검증) ──────────────
    try:
        from tests.v4_validator import validate as _v4_validate
        _v4_validate(output_dir)
    except Exception as e:
        print(f"\n⚠️ V4 validator 에러 (무시): {e}")

    # ── 사업기획서 HTML 자동 생성 ────────────────────────────────
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from generate_brief import generate_report
        html_path = generate_report(Path(output_dir), client)
        print(f"\n📄 사업기획서 HTML 생성: {html_path}")
    except Exception as e:
        print(f"\n⚠️ HTML 생성 에러 (무시): {e}")

    # ── 파이프라인 캐시 통계 출력 ─────────────────────────────────
    if HAS_PIPELINE_CACHE:
        cache = get_pipeline_cache()
        cache.print_stats()
