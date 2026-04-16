"""
pipeline_utils.py — 모든 팀 파이프라인 공통 유틸

이 파일의 함수들을 pipeline.py에서 호출하면:
1. 미션 + 학습자료가 에이전트한테 자동 전달
2. 결과물 자가점검 자동 실행
3. 에이전트 .py 파일은 수정할 필요 없음

사용법 (각 팀 pipeline.py에서):
    from core.pipeline_utils import enrich_context, self_critique_all

    # 에이전트 실행 전
    context = enrich_context(context, team_slug="온라인영업팀")

    # 에이전트 실행 후
    critique = self_critique_all(context, client)
"""
import os
import anthropic
from core.models import CLAUDE_SONNET

TEAMS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "teams")


def enrich_context(context: dict, team_slug: str) -> dict:
    """미션 + 학습자료를 context['task']에 합쳐서 에이전트가 자동으로 읽게 함.

    기존 에이전트 .py의 user_msg = f"업무: {context['task']}..." 이므로,
    task 문자열 자체에 미션과 학습자료를 넣으면 모든 에이전트가 읽음.
    """
    original_task = context.get("task", "")

    # 1. 미션 로드
    team_dir = _find_team_dir(team_slug)
    if team_dir:
        mission_path = os.path.join(team_dir, "mission.md")
        try:
            with open(mission_path, encoding="utf-8") as f:
                mission = f.read()
            context["mission"] = mission
            print(f"📋 미션 로드 완료")
        except FileNotFoundError:
            mission = ""
    else:
        mission = ""

    # 2. 학습 (Perplexity)
    fresh_knowledge = ""
    try:
        from core.continuous_learning import learn_before_run
        fresh_knowledge = learn_before_run(team_slug)
        if fresh_knowledge:
            context["fresh_knowledge"] = fresh_knowledge
    except Exception as e:
        print(f"⚠️ 학습 스킵: {e}")

    # 3. task에 합치기 (에이전트가 자동으로 읽음)
    enriched = original_task
    if mission:
        # 미션에서 핵심만 추출 (존재 이유 + 하는 일 + 절대 금지)
        enriched += f"\n\n=== 팀 미션 (반드시 따를 것) ===\n{mission[:1500]}\n==="
    if fresh_knowledge:
        enriched += f"\n\n=== 최신 학습 자료 (이걸 반영해서 결과물 내라) ===\n{fresh_knowledge[:3000]}\n==="

    context["task"] = enriched
    context["_original_task"] = original_task  # 원본 보존
    return context


def summarize_context(context: dict, max_chars: int = 1500) -> str:
    """context에서 직전 에이전트 결과만 추출해서 요약 반환.

    str(context)[:2000] 대신 사용. 불필요한 키(task, mission, meta 등)를 제외하고
    실제 에이전트 결과물만 전달해서 토큰 낭비를 줄인다.
    """
    skip_keys = {"task", "_original_task", "mission", "fresh_knowledge",
                 "interview", "reference_research", "critique"}
    parts = []
    total = 0
    # 역순으로 (최신 결과부터)
    for key in reversed(list(context.keys())):
        if key in skip_keys:
            continue
        val = context[key]
        if not isinstance(val, str) or not val.strip():
            continue
        entry = f"[{key}] {val[:500]}"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n".join(reversed(parts))


def self_critique_all(context: dict, client: anthropic.Anthropic, team_name: str = "") -> dict:
    """모든 팀 공통 자가점검. 결과물을 Sonnet으로 점검 → 이슈 있으면 수정.

    Args:
        context: 파이프라인 결과가 담긴 context dict
        client: Anthropic client
        team_name: 팀 이름 (보고용)

    Returns:
        {"passed": bool, "score": int, "issues": list, "improved": str}
    """
    # 결과물 수집 — head(2000자) + tail(1000자) 구조로 완성도 판단
    EXCLUDED = {"task", "_original_task", "interview", "mission", "fresh_knowledge",
                "reference_research", "fresh_knowledge", "critique", "summary"}

    results_combined = []
    for key, val in context.items():
        if key not in EXCLUDED and isinstance(val, str) and len(val) > 100:
            head = val[:2000]
            # tail: 마지막 1000자 (내용이 완성됐는지 판단용)
            tail = val[-1000:] if len(val) > 2500 else ""
            tail_section = f"\n...[중략]...\n[마지막 1000자]\n{tail}" if tail else ""
            results_combined.append(f"[{key} — 총 {len(val)}자]\n{head}{tail_section}")

    if not results_combined:
        return {"passed": True, "score": 10, "issues": [], "improved": ""}

    all_results = "\n\n---\n\n".join(results_combined)
    mission = context.get("mission", "")

    critique_prompt = f"""너는 QA 검수관이야. 팀 결과물을 점검하고 점수를 매겨.

=== 팀 미션 ===
{mission[:1000]}

=== 점검 기준 (각 10점 만점) ===
1. **실행 가능성**: 리안이 이걸 받고 바로 실행할 수 있는가? 복붙 가능한가? [GIF URL], [아이콘N] 같은 플레이스홀더 있으면 감점. 이도현/강하린 결과물 없으면 감점.
2. **설득력**: 고객(타겟)이 이걸 보고 "이거다" 할 것 같은가? 출처 없는 수치("검색량 240% 증가", "19배 증가") 있으면 감점. 실제 수집 데이터(팔로워 1,195명, 리뷰 0개)에 기반한 근거 있으면 가점.
3. **구체성**: 수치, 날짜, 이름, 구체적 행동이 명시돼 있는가? 견적서(3패키지 전부, 원가 근거)·계약서·대시보드 템플릿·A/B테스트 계획이 있는지 확인.
4. **차별화**: 다른 대행사도 할 수 있는 뻔한 내용인가, 우리만의 관점이 있는가? '체험단+SEO+광고' 루틴에서 벗어난 독창적 전략 있는지 확인.

=== 평가 맥락 ===
이건 파이프라인 **첫 실행(데모)**이므로:
- 리드 수량 KPI(50개/주) 미달은 감점 대상 아님 — 크롤러가 물리적으로 3개만 분석 가능
- 대신 제출된 리드의 **분석 깊이와 활용성**으로 평가
- 에이전트 시스템 프롬프트에 포함된 [1][2][3] 각주는 학습자료 인용이지 출처 위조 아님 — 에이전트 결과물에 [1][2] 나와도 이것만으로 감점하지 마
- 금액/원가는 이도현이 유일한 소스. 다른 에이전트가 금액 안 써도 감점 아님

=== 결과물 (에이전트별 처음 2000자 + 마지막 1000자, 총 글자수 표시) ===
중요: "[마지막 1000자]" 섹션이 있으면 그 에이전트는 완성된 것으로 판단. 잘림 여부는 마지막 부분의 문장이 완성됐는지로 판단.
{all_results[:24000]}

=== 출력 ===
각 기준 점수 + 총점(40점 만점) + 이슈 목록.
이슈가 있으면 "이렇게 고쳐라"까지 구체적으로.
점수와 이슈를 이 형식으로 마지막에 반드시 출력:
SCORE: XX/40
ISSUES: [이슈1] | [이슈2] | ...
"""

    print(f"\n{'='*60}")
    print(f"🔍 자가점검 | {team_name}")
    print("="*60)

    full_response = ""
    try:
        with client.messages.stream(
            model=CLAUDE_SONNET,
            max_tokens=7000,
            messages=[{"role": "user", "content": critique_prompt}],
            system="너는 냉정한 QA 검수관이야. 점수 후하게 주지 마. 리안이 직접 했을 때보다 못하면 0점이야.",
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text
        print()
    except Exception as e:
        print(f"\n⚠️ 자가점검 실패: {e}")
        return {"passed": False, "score": 0, "issues": [str(e)], "improved": ""}

    # 점수 파싱
    score = 0
    import re
    score_match = re.search(r'SCORE:\s*(\d+)/40', full_response)
    if score_match:
        score = int(score_match.group(1))
    else:
        # 폴백 1: "소계: X/10" 패턴 (가장 정확)
        subtotals_10 = re.findall(r'소계:\s*(\d+)/10', full_response)
        if subtotals_10:
            score = min(40, sum(int(s) for s in subtotals_10[:4]))
        else:
            # 폴백 2: "소계: XX/40" 패턴
            subtotals = re.findall(r'소계:\s*(\d+)/40', full_response)
            if subtotals:
                score = sum(int(s) for s in subtotals) // max(len(subtotals), 1)
            else:
                # 폴백 3: 첫 4개 X/10 점수만 합산 (중복 방지)
                per10 = re.findall(r'\b(\d+)/10\b', full_response)
                if per10:
                    score = min(40, sum(int(s) for s in per10[:4]))

    issues = []
    issues_match = re.search(r'ISSUES:\s*(.+)', full_response)
    if issues_match:
        issues = [i.strip() for i in issues_match.group(1).split('|') if i.strip()]
    # ISSUES 없으면 문제 키워드 줄에서 추출
    if not issues:
        problem_lines = [l.strip() for l in full_response.split('\n')
                        if l.strip().startswith(('❌', '⚠️', '- 문제', '- 이슈'))
                        and len(l.strip()) > 5]
        issues = problem_lines[:5]

    passed = score >= 28  # 70% 이상이면 통과

    result = {
        "passed": passed,
        "score": score,
        "issues": issues,
        "full_critique": full_response,
    }

    if passed:
        print(f"\n✅ 자가점검 통과 ({score}/40)")
    else:
        print(f"\n❌ 자가점검 미통과 ({score}/40) — 이슈 {len(issues)}개")
        # 미통과 시 mission.md에 피드백 자동 기록
        if team_name:
            _write_critique_to_mission(team_name, score, issues, full_response)

    return result


def auto_judge(critique: dict, team_name: str, rerun_fn=None, client=None) -> dict:
    """Phase 6: 점수 기반 자동 판단.

    - 28/40 (7/10) 이상 → 자동 통과
    - 미만 → rerun_fn 있으면 1회 재실행 → 여전히 미달이면 디스코드 알림
    """
    score = critique.get("score", 0)

    if score >= 28:
        print(f"\n✅ {team_name} 자동 통과 ({score}/40)")
        return critique

    print(f"\n⚠️ {team_name} 미달 ({score}/40) — 재실행 시도")

    # 재실행 1회
    if rerun_fn and client:
        try:
            new_context = rerun_fn()
            retry_critique = self_critique_all(new_context, client, team_name=team_name)
            retry_score = retry_critique.get("score", 0)

            if retry_score >= 28:
                print(f"\n✅ {team_name} 재실행 통과 ({retry_score}/40)")
                return retry_critique
            else:
                print(f"\n❌ {team_name} 재실행 후에도 미달 ({retry_score}/40)")
                critique = retry_critique
        except Exception as e:
            print(f"\n⚠️ 재실행 실패: {e}")

    # 여전히 미달 → 디스코드 알림
    try:
        from core.notifier import send
        issues = critique.get("issues", [])
        issues_text = "\n".join(f"• {i}" for i in issues[:3])
        send(
            f"⚠️ {team_name} 품질 미달 ({score}/40)",
            f"재실행 후에도 기준 미달.\n\n{issues_text}\n\n리안 확인 필요.",
            color=0xE74C3C
        )
    except Exception:
        pass

    return critique


def _write_critique_to_mission(team_name: str, score: int, issues: list, full_critique: str):
    """자가점검 미통과 시 mission.md에 개선 필요 항목 자동 기록.
    다음 실행 때 에이전트들이 enrich_context()로 이 내용을 읽게 됨.
    """
    import re
    from datetime import datetime

    team_dir = _find_team_dir(team_name)
    if not team_dir:
        return

    mission_path = os.path.join(team_dir, "mission.md")
    if not os.path.exists(mission_path):
        return

    date_str = datetime.now().strftime("%Y-%m-%d")

    # 이슈 요약 추출 (없으면 full_critique에서 핵심 줄 뽑기)
    if issues:
        issue_text = "\n".join(f"- {i}" for i in issues[:5])
    else:
        # 점수 관련 줄 파싱 시도
        lines = [l.strip() for l in full_critique.split("\n") if l.strip() and any(
            kw in l for kw in ["미달", "부족", "없음", "오류", "틀림", "미완성", "문제"]
        )]
        issue_text = "\n".join(f"- {l}" for l in lines[:5]) if lines else "- 상세 이슈는 _자가점검_결과.md 참고"

    feedback_block = f"""

## 자가점검 피드백 ({date_str}) — {score}/40점
> 이전 실행에서 발견된 문제. 이번 실행에서 반드시 개선할 것.

{issue_text}

"""

    try:
        with open(mission_path, encoding="utf-8") as f:
            content = f.read()

        # 기존 피드백 블록 제거 후 새 것으로 교체
        content = re.sub(
            r"\n## 자가점검 피드백 \([\d-]+\).*?(?=\n## |\Z)",
            "",
            content,
            flags=re.DOTALL
        )
        content = content.rstrip() + feedback_block

        with open(mission_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📝 mission.md 피드백 업데이트 완료 ({score}/40 → 다음 실행에 반영)")
    except Exception as e:
        print(f"⚠️ mission.md 피드백 업데이트 실패: {e}")


def _find_team_dir(team_slug: str) -> str | None:
    """팀 디렉토리 찾기."""
    exact = os.path.join(TEAMS_DIR, team_slug)
    if os.path.isdir(exact):
        return exact
    for d in os.listdir(TEAMS_DIR):
        if team_slug.lower() in d.lower():
            path = os.path.join(TEAMS_DIR, d)
            if os.path.isdir(path):
                return path
    return None
