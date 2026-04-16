"""
planner.py — 일일/주간 작업 계획기

자산 스캔 결과를 받아서 오늘 뭘 할지 우선순위 정렬.
두 가지 루트를 인식:
  - 루트1 (대행): 타겟→상품→가격→DM자동화→자체홍보→돌리고→수정→반복
  - 루트2 (플랫폼): 주제→타겟 명확화→자료수집→경쟁사→개발→홍보→반복
"""
import os
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET
from core.daily_log import get_recent, get_stats
from core.kpi import get_kpi_summary_for_planner

load_dotenv()

MODEL = CLAUDE_SONNET

# ── 루트 정의 ──

ROUTES = {
    "route1_agency": {
        "name": "마케팅 대행 (루트1)",
        "description": "타겟 잡기 → 상품 설정 → 가격 → DM/이메일 자동화 → 자체 홍보 → 반복",
        "phases": [
            {"id": "target", "name": "타겟 설정", "tasks": ["research"], "auto": True},
            {"id": "product", "name": "상품/가격 설정", "tasks": ["research"], "auto": False},
            {"id": "outreach", "name": "DM/이메일 자동화", "tasks": ["outreach"], "auto": True},
            {"id": "promote", "name": "자체 홍보", "tasks": ["content"], "auto": True},
            {"id": "iterate", "name": "돌리고 수정", "tasks": ["content", "outreach", "review"], "auto": True},
        ],
    },
    "route2_platform": {
        "name": "플랫폼/SaaS (루트2)",
        "description": "주제 → 타겟 명확화 → 자료 수집 → 경쟁사 → 개발 → 홍보 → 반복",
        "phases": [
            {"id": "clarify", "name": "주제/타겟 명확화", "tasks": ["research"], "auto": False},
            {"id": "research", "name": "니치/경쟁사 파악", "tasks": ["research"], "auto": True},
            {"id": "develop", "name": "개발팀 토스", "tasks": ["launch"], "auto": False},
            {"id": "promote", "name": "홍보", "tasks": ["content"], "auto": True},
            {"id": "iterate", "name": "돌리고 수정", "tasks": ["content", "outreach", "review"], "auto": True},
        ],
    },
}

# ── 하드코딩 규칙 ──

PLANNING_RULES = """
# 일일 계획 규칙

## 우선순위 판단 기준 (1이 가장 높음)
1. 돈과의 거리 — 매출에 가까운 것 우선
2. 기존 모멘텀 — 이미 진행 중인 것 우선
3. 비용 대비 효과 — API 비용 대비 기대 결과
4. 리안 피드백 반영

## 필수 태스크 (매일)
- launched 프로젝트: 콘텐츠 생성 (인스타 캡션 + 블로그 제목 + 영업 DM)
- 3일 이상 실행 안 한 active 팀: 우선순위 올림

## 정기 태스크
- 리서치: 주 2회 이상 (월, 목)
- 영업 DM: 매일 (launched 프로젝트만)
- 주간 리뷰: 매주 월요일

## 금지
- 하루 API 비용 $10 초과 금지
- 같은 태스크 하루 2회 이상 금지

## KPI 기반 우선순위
- 달성률 낮은 팀의 태스크를 우선순위 올림
- 이번 달 목표 달성한 팀은 유지 모드로
"""

PLANNER_PROMPT = f"""너는 리안 컴퍼니의 일일 작업 계획기야.
회사 자산 현황과 최근 실행 로그를 보고, 오늘 할 일을 정해.

{PLANNING_RULES}

## 루트 (돈 버는 경로)
회사는 두 가지 루트로 돈을 번다:
- 루트1 (대행): 타겟 → 상품 → 가격 → DM자동화 → 자체홍보 → 반복
- 루트2 (플랫폼): 주제 → 타겟 → 자료 → 경쟁사 → 개발 → 홍보 → 반복
둘 다 끝은 같다: 인스타 매일, 블로그 매일, 메타광고 테스트, 반복.

## 출력 형식 (반드시 JSON)
```json
[
  {{
    "id": "daily_YYYYMMDD_01",
    "type": "content|outreach|research|launch|team_run|review",
    "category": "daily_content|outreach_dm|blog_post|insta_caption|research|...",
    "target_project": "프로젝트명 또는 null",
    "target_team": "팀명 또는 null",
    "route": "route1_agency|route2_platform|both|none",
    "description": "무엇을 왜 하는지",
    "priority": 1,
    "needs_approval": false,
    "estimated_cost": "low"
  }}
]
```

반드시 JSON 배열만 출력해. 설명, 마크다운 코드블록, 주석 붙이지 마.
짧고 핵심만. 태스크 5개 이하."""


def plan_daily(assets: dict) -> list[dict]:
    """오늘의 태스크 목록 생성."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 최근 7일 로그
    recent = get_recent(7)
    stats = get_stats(7)

    recent_summary = ""
    if recent:
        last_5 = recent[-5:]
        recent_summary = "\n".join(
            f"  - [{r['date']}] {r['type']}: {r.get('result_summary', '')[:100]} ({'O' if r['success'] else 'X'})"
            for r in last_5
        )

    # KPI 정보 추가
    try:
        kpi_summary = get_kpi_summary_for_planner()
    except Exception:
        kpi_summary = "(KPI 정보 로드 실패)"

    today = datetime.now().strftime("%Y-%m-%d (%A)")
    date_key = datetime.now().strftime("%Y%m%d")

    from core.asset_scanner import format_summary
    asset_text = format_summary(assets)

    user_msg = f"""오늘: {today}

{asset_text}

## 최근 실행 로그
{recent_summary if recent_summary else "(아직 실행 기록 없음)"}

## 통계 (7일)
- 총 실행: {stats['total']}회
- 성공률: {stats['success_rate']*100:.0f}%
- 타입별: {json.dumps(stats['by_type'], ensure_ascii=False)}
- 프로젝트별: {json.dumps(stats['by_project'], ensure_ascii=False)}

{kpi_summary}

오늘 뭐 할지 정해줘. task id에는 {date_key}을 넣어."""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=inject_context(PLANNER_PROMPT),
            messages=[{"role": "user", "content": user_msg}],
            temperature=0.3,
        )
        text = resp.content[0].text

        # JSON 추출
        import re
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            tasks = json.loads(json_match.group())
            # priority로 정렬
            tasks.sort(key=lambda t: t.get("priority", 99))
            return tasks
        else:
            print("  [planner] JSON 파싱 실패 — 기본 계획 사용")
            return _default_plan(assets, date_key)

    except Exception as e:
        print(f"  [planner] API 호출 실패: {e} — 기본 계획 사용")
        return _default_plan(assets, date_key)


def _default_plan(assets: dict, date_key: str) -> list[dict]:
    """API 실패 시 하드코딩 기본 계획."""
    tasks = []
    idx = 1

    # launched 프로젝트: 매일 콘텐츠
    for p in assets.get("projects", []):
        if p["status"] == "launched":
            tasks.append({
                "id": f"daily_{date_key}_{idx:02d}",
                "type": "content",
                "category": "daily_content",
                "target_project": p["name"],
                "target_team": None,
                "route": "both",
                "description": f"{p['name']} 일일 콘텐츠 생성",
                "priority": 1,
                "needs_approval": False,
                "estimated_cost": "low",
            })
            idx += 1

    # 팀 중 3일 이상 안 돌린 팀
    for t in assets.get("teams", []):
        if t["has_pipeline"]:
            tasks.append({
                "id": f"daily_{date_key}_{idx:02d}",
                "type": "team_run",
                "category": "team_routine",
                "target_project": None,
                "target_team": t["name"],
                "route": "route1_agency",
                "description": f"{t['name']} 정기 실행",
                "priority": 3,
                "needs_approval": False,
                "estimated_cost": "medium",
            })
            idx += 1

    # 리서치 (월, 목)
    weekday = datetime.now().weekday()
    if weekday in (0, 3):  # 월, 목
        tasks.append({
            "id": f"daily_{date_key}_{idx:02d}",
            "type": "research",
            "category": "research",
            "target_project": None,
            "target_team": None,
            "route": "both",
            "description": "트렌드 리서치 (정기)",
            "priority": 2,
            "needs_approval": False,
            "estimated_cost": "low",
        })

    return tasks


def plan_weekly(assets: dict) -> dict:
    """주간 계획. 이번 주 성과 → 다음 주 방향."""
    stats = get_stats(7)
    recent = get_recent(7)

    return {
        "stats": stats,
        "recent_count": len(recent),
        "recommendation": "주간 리뷰 실행 필요" if recent else "실행 기록 없음 — 첫 실행 필요",
    }
