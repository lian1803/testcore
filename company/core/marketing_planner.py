"""
marketing_planner.py — 마케팅 전략 자동 수립 + 팀 활성화 결정

product_analyzer 결과를 받아서:
1. 채널별 구체적 실행 계획 수립
2. 온라인마케팅팀 / 온라인납품팀 활성화 결정
3. marketing_config.json에 저장
4. ops_loop에 등록할 설정 생성

사용법:
    from core.marketing_planner import plan_marketing
    plan = plan_marketing(analysis_result, "프로젝트명", client)
"""
import os
import json
import re
import subprocess
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET

load_dotenv()

MODEL = CLAUDE_SONNET
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "marketing_config.json")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")


def _load_config() -> dict:
    """marketing_config.json 로드 (없으면 빈 딕셔너리)."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}}


def _save_config(config: dict):
    """marketing_config.json 저장."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


BRIEF_PLANNER_PROMPT = """너는 마케팅 전략 총괄이야.
사이트가 아직 없어. 기획서(아이디어, 타겟, 전략)만 보고 마케팅 채널과 전략을 먼저 잡아야 해.
개발하는 동안 마케팅팀이 병렬로 콘텐츠를 미리 준비할 수 있도록.

JSON으로 출력해. 다른 텍스트 없이 JSON만:

{
  "target_persona": "타겟 페르소나 (구체적으로)",
  "key_message": "핵심 메시지 한 줄",
  "channels": [
    {
      "name": "채널명",
      "priority": 1,
      "reason": "이 타겟이 이 채널에 있는 이유",
      "format": "콘텐츠 포맷",
      "frequency": "주기",
      "tone": "톤앤매너",
      "hashtags_base": ["#해시태그"],
      "keywords": ["SEO키워드"],
      "team": "온라인마케팅팀 또는 온라인납품팀",
      "prelaunch_content": "개발 기간 중 미리 만들어둘 콘텐츠 (티징/교육/신뢰구축)"
    }
  ],
  "teams_to_activate": ["팀명"],
  "team_tasks": {
    "온라인마케팅팀": "개발 기간 중 할 것: 티징 콘텐츠 N개 준비, 팔로워 모으기 등",
    "온라인납품팀": "개발 기간 중 할 것: SEO 블로그 N개 미리 작성 등"
  },
  "prelaunch_plan": [
    {"week": "개발 1주차", "action": "할 것", "output": "산출물"}
  ],
  "launch_day_plan": "배포 당일 마케팅 액션 (이미 준비된 것들 동시 런칭)",
  "kpi": {"week1": "출시 1주차 KPI", "month1": "1개월 KPI"},
  "summary": "전략 요약 3문장"
}

타겟에 맞는 채널을 현실적으로 최대 3개만. 선택과 집중."""


PLANNER_PROMPT = """너는 마케팅 전략 총괄이야.
분석 결과를 보고 구체적인 실행 계획을 JSON으로 출력해. 다른 텍스트 없이 JSON만:

{
  "channels": [
    {
      "name": "채널명",
      "priority": 1,
      "format": "콘텐츠 포맷",
      "frequency": "매일/격일/주3회",
      "tone": "톤앤매너",
      "hashtags_base": ["#해시태그1", "#해시태그2"],
      "keywords": ["SEO키워드1", "SEO키워드2"],
      "team": "온라인마케팅팀 또는 온라인납품팀",
      "first_content_idea": "첫 번째 콘텐츠 아이디어"
    }
  ],
  "teams_to_activate": ["온라인마케팅팀"],
  "team_tasks": {
    "온라인마케팅팀": "팀에게 줄 구체적 태스크 설명",
    "온라인납품팀": "팀에게 줄 구체적 태스크 설명"
  },
  "week1_plan": [
    {"day": "Day 1", "channel": "채널명", "action": "할 것", "output": "산출물"}
  ],
  "budget_estimate": "예상 마케팅 예산 (월)",
  "kpi": {
    "week1": "1주차 KPI",
    "month1": "1개월 KPI"
  },
  "summary": "마케팅 전략 요약 (3문장)"
}

팀 결정 기준:
- 인스타/유튜브/SNS → 온라인마케팅팀
- 블로그/SEO/상세페이지 → 온라인납품팀
- 둘 다 필요하면 둘 다 포함"""


def plan_from_brief(context: dict, project_name: str, client: anthropic.Anthropic) -> dict:
    """사이트 없이 기획서 기반으로 마케팅 전략 수립 (개발 시작 전 단계).

    context: launch_prep 또는 이사팀 결과 (idea, target, strategy 등)
    """
    print(f"\n{'='*60}")
    print(f"📣 마케팅 전략 수립 (기획서 기반): {project_name}")
    print("="*60)

    idea = context.get("clarified", context.get("idea", project_name))
    strategy = context.get("minsu", context.get("strategy", ""))[:600]
    market = context.get("seoyun", context.get("market", ""))[:600]
    launch_plan = context.get("launch_plan", "")[:800]

    user_msg = f"""프로젝트명: {project_name}

== 아이디어 ==
{idea}

== 시장/타겟 조사 ==
{market}

== 전략 ==
{strategy}

== 런칭 준비 (채널/가격/타겟 기획) ==
{launch_plan}

사이트가 아직 없어. 기획서만 보고 마케팅 전략을 먼저 잡아줘.
개발 기간 중 마케팅팀이 병렬로 준비할 수 있도록."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=inject_context(BRIEF_PLANNER_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    try:
        clean = re.sub(r'```json', '', full_response, flags=re.IGNORECASE)
        clean = re.sub(r'```', '', clean)
        json_match = re.search(r'\{[\s\S]*\}', clean, re.DOTALL)
        plan = json.loads(json_match.group(0)) if json_match else {}
    except json.JSONDecodeError:
        plan = {"summary": full_response, "channels": [], "teams_to_activate": [], "prelaunch_plan": []}

    plan["project_name"] = project_name
    plan["created"] = datetime.now().strftime("%Y-%m-%d")
    plan["stage"] = "prelaunch"  # 배포 후 product_analyzer로 보완 예정

    _register_to_config(project_name, plan, context)

    print(f"\n  ✅ 마케팅 전략 수립 완료")
    print(f"  채널: {[c['name'] for c in plan.get('channels', [])]}")
    print(f"  개발 기간 중 활성화할 팀: {plan.get('teams_to_activate', [])}")

    return plan


def plan_marketing(analysis: dict, project_name: str, client: anthropic.Anthropic) -> dict:
    """분석 결과 기반으로 마케팅 실행 계획 수립."""
    print(f"\n{'='*60}")
    print(f"📣 마케팅 전략 수립: {project_name}")
    print("="*60)

    channels_text = json.dumps(analysis.get("recommended_channels", []), ensure_ascii=False, indent=2)

    user_msg = f"""프로젝트명: {project_name}
URL: {analysis.get('url', '')}

== 사이트 분석 결과 ==
타겟: {analysis.get('target_persona', '')}
핵심 메시지: {analysis.get('key_message', '')}
포지셔닝: {analysis.get('positioning', '')}
차별점: {analysis.get('differentiator', '')}

== 추천 채널 (분석 기반) ==
{channels_text}

== 분석 요약 ==
{analysis.get('summary', '')}

위 분석을 기반으로 구체적인 마케팅 실행 계획 JSON을 작성해."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        system=inject_context(PLANNER_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    # JSON 파싱 (```json 코드블록 제거 후 시도)
    try:
        clean = re.sub(r'```json', '', full_response, flags=re.IGNORECASE)
        clean = re.sub(r'```', '', clean)
        json_match = re.search(r'\{[\s\S]*\}', clean, re.DOTALL)
        plan = json.loads(json_match.group(0)) if json_match else {}
    except json.JSONDecodeError:
        plan = {"summary": full_response, "channels": [], "teams_to_activate": [], "week1_plan": []}

    # 채널명 정규화 (인스타그램 → 인스타, 블로그(티스토리+네이버) → 블로그)
    channel_name_map = {
        "인스타그램": "인스타", "instagram": "인스타",
        "블로그(티스토리": "블로그", "블로그 (티스토리": "블로그", "네이버블로그": "블로그",
        "유튜브": "유튜브", "youtube": "유튜브",
        "메타광고": "메타광고", "meta": "메타광고",
        "네이버카페": "네이버카페", "카카오": "카카오",
    }
    for ch in plan.get("channels", []):
        raw = ch.get("name", "")
        for k, v in channel_name_map.items():
            if k in raw:
                ch["name"] = v
                break

    plan["project_name"] = project_name
    plan["created"] = datetime.now().strftime("%Y-%m-%d")
    plan["url"] = analysis.get("url", "")

    # marketing_config.json에 저장
    _register_to_config(project_name, plan, analysis)

    # 결과 출력
    print(f"\n  ✅ 전략 수립 완료")
    print(f"  채널: {[c['name'] for c in plan.get('channels', [])]}")
    print(f"  활성화할 팀: {plan.get('teams_to_activate', [])}")

    return plan


def _register_to_config(project_name: str, plan: dict, analysis: dict):
    """marketing_config.json에 프로젝트 마케팅 설정 등록."""
    config = _load_config()
    config["projects"][project_name] = {
        "url": plan.get("url", ""),
        "target_persona": analysis.get("target_persona", ""),
        "key_message": analysis.get("key_message", ""),
        "channels": plan.get("channels", []),
        "teams_to_activate": plan.get("teams_to_activate", []),
        "team_tasks": plan.get("team_tasks", {}),
        "week1_plan": plan.get("week1_plan", []),
        "kpi": plan.get("kpi", {}),
        "budget_estimate": plan.get("budget_estimate", ""),
        "created": plan.get("created", ""),
        "status": "pending_confirm",  # 리안 컨펌 전
    }
    _save_config(config)
    print(f"  📝 marketing_config.json 저장 완료")


def activate_teams(project_name: str, plan: dict):
    """리안 컨펌 후 팀 자동 활성화."""
    teams = plan.get("teams_to_activate", [])
    team_tasks = plan.get("team_tasks", {})

    if not teams:
        print("  ⚠️  활성화할 팀 없음")
        return

    company_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))

    for team in teams:
        task = team_tasks.get(team, f"{project_name} 마케팅 콘텐츠 제작")
        print(f"\n  🚀 {team} 활성화: {task[:50]}...")
        try:
            runner_map = {
                "온라인마케팅팀": "run_온라인마케팅팀.py",
                "온라인납품팀": "run_온라인납품팀.py",
                "온라인영업팀": "run_온라인영업팀.py",
            }
            runner = runner_map.get(team)
            if runner:
                runner_path = os.path.join(company_dir, runner)
                if os.path.exists(runner_path):
                    subprocess.Popen(
                        ["./venv/Scripts/python.exe", runner, task],
                        cwd=company_dir,
                    )
                    print(f"    ✅ {team} 실행 시작")
                else:
                    print(f"    ⚠️  {runner} 없음")
            else:
                print(f"    ⚠️  {team} 러너 없음")
        except Exception as e:
            print(f"    ❌ {team} 실행 실패: {e}")

    # config에 status 업데이트
    config = _load_config()
    if project_name in config.get("projects", {}):
        config["projects"][project_name]["status"] = "active"
        config["projects"][project_name]["activated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        _save_config(config)

    # ops_loop에 자동 등록 (daily_auto.py가 있으면)
    _register_to_ops(project_name)


def _register_to_ops(project_name: str):
    """ops_loop 매일 루프에 프로젝트 자동 등록."""
    daily_auto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "daily_auto.py")
    if not os.path.exists(daily_auto_path):
        return

    try:
        with open(daily_auto_path, encoding="utf-8") as f:
            content = f.read()

        # PROJECTS 리스트에 추가 (중복 체크)
        if project_name not in content:
            new_content = content.replace(
                "PROJECTS = [",
                f'PROJECTS = [\n    "{project_name}",  # 자동 등록 {datetime.now().strftime("%Y-%m-%d")}',
                1,
            )
            if new_content != content:
                with open(daily_auto_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  📅 daily_auto.py에 '{project_name}' 자동 등록")
    except Exception as e:
        print(f"  ⚠️  ops_loop 등록 실패: {e}")


def print_confirmation_prompt(project_name: str, plan: dict) -> str:
    """리안에게 보여줄 마케팅 전략 컨펌 메시지 생성."""
    channels = plan.get("channels", [])
    teams = plan.get("teams_to_activate", [])
    budget = plan.get("budget_estimate", "미정")
    summary = plan.get("summary", "")
    kpi = plan.get("kpi", {})

    lines = [
        "",
        "=" * 60,
        f"  📣 {project_name} — 마케팅 전략 컨펌",
        "=" * 60,
        "",
        f"  전략 요약: {summary}",
        "",
        "  채널:",
    ]
    for ch in channels:
        lines.append(f"    [{ch.get('priority', '?')}순위] {ch['name']} — {ch.get('format', '')} ({ch.get('frequency', '')})")

    lines += [
        "",
        f"  활성화할 팀: {', '.join(teams)}",
        f"  예상 예산: {budget}",
        "",
        f"  1개월 KPI: {kpi.get('month1', '미정')}",
        "",
        "  [진행해] → 팀 자동 활성화 + 매일 루프 등록",
        "  [수정해 + 내용] → 전략 수정",
        "=" * 60,
    ]
    return "\n".join(lines)
