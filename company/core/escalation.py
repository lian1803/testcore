"""
escalation.py — 에스컬레이션 관리

리안한테 물어봐야 할 것과 스스로 판단할 것을 분리.
"""
import os
import json
from datetime import datetime
from core.notifier import send as discord_send

_ROOT = os.path.dirname(os.path.dirname(__file__))
PENDING_PATH = os.path.join(_ROOT, ".pending_questions.json")
ARCHIVE_PATH = os.path.join(_ROOT, ".pending_questions_archive.jsonl")
APPROVALS_PATH = os.path.join(_ROOT, ".autopilot_approvals.json")

# ── 에스컬레이션 기준 ──

ALWAYS_ESCALATE = [
    "new_project",       # 새 프로젝트 시작
    "stop_project",      # 프로젝트 중단/피벗
    "high_cost",         # 예산 $50 이상
    "new_service",       # 외부 서비스 신규 가입
    "org_change",        # 조직도 변경
    "first_publish",     # 고객 대면 콘텐츠 최초 발행
]

NEVER_ESCALATE = [
    "daily_content",     # 승인된 프로젝트의 일일 콘텐츠
    "research",          # 트렌드 리서치
    "team_routine",      # 기존 팀 정기 실행
    "knowledge_add",     # 지식 추가
    "log_write",         # 로그 기록
]

# 조건부: {타입: 자율 전환까지 필요한 승인 횟수}
CONDITIONAL = {
    "outreach_dm": 1,      # 영업 DM: 프로젝트별 1회 승인 후 자율
    "blog_post": 3,        # 블로그: 3건 승인 후 자율
    "insta_caption": 3,    # 인스타: 3건 승인 후 자율
    "ad_copy": 999,        # 광고: 항상 승인 필요 (비용 발생)
}


def _load_approvals() -> dict:
    """리안이 승인한 카테고리 목록."""
    if not os.path.exists(APPROVALS_PATH):
        return {}
    try:
        with open(APPROVALS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def mark_approved(category: str):
    """카테고리를 승인됨으로 기록."""
    approvals = _load_approvals()
    approvals[category] = {"approved_at": datetime.now().isoformat(), "count": approvals.get(category, {}).get("count", 0) + 1}
    try:
        with open(APPROVALS_PATH, "w", encoding="utf-8") as f:
            json.dump(approvals, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def should_escalate(task: dict, approval_count: int = 0) -> tuple[bool, str]:
    """에스컬레이션 여부 판단.

    Returns:
        (True/False, 사유)
    """
    task_type = task.get("type", "")
    category = task.get("category", "")

    # 이미 리안이 이 카테고리를 승인한 적 있으면 자율 실행
    approvals = _load_approvals()
    if category in approvals and category not in ALWAYS_ESCALATE:
        return False, f"이전 승인됨 ({approvals[category].get('approved_at', '?')[:10]})"

    # 무조건 에스컬레이션
    if category in ALWAYS_ESCALATE:
        return True, f"[필수 승인] {category}"

    # 절대 안 물어봄
    if category in NEVER_ESCALATE:
        return False, "자율 실행 가능"

    # 조건부
    if category in CONDITIONAL:
        threshold = CONDITIONAL[category]
        if approval_count >= threshold:
            return False, f"자율 전환됨 (승인 {approval_count}/{threshold}회)"
        return True, f"승인 필요 ({approval_count}/{threshold}회)"

    # 기본: needs_approval 플래그
    if task.get("needs_approval", False):
        return True, "태스크에 승인 플래그"

    return False, "기본 자율"


def escalate(question: str, category: str, options: list[str] = None):
    """질문을 .pending_questions.json에 저장 + Discord 알림."""
    # 기존 질문 로드
    pending = []
    if os.path.exists(PENDING_PATH):
        try:
            with open(PENDING_PATH, encoding="utf-8") as f:
                pending = json.load(f)
        except Exception:
            pending = []

    entry = {
        "id": f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "question": question,
        "category": category,
        "options": options or [],
        "answered": False,
        "answer": None,
        "created_at": datetime.now().isoformat(),
    }
    pending.append(entry)

    try:
        with open(PENDING_PATH, "w", encoding="utf-8") as f:
            json.dump(pending, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [escalation] 저장 실패: {e}")

    # Discord 알림
    options_text = ""
    if options:
        options_text = "\n선택지:\n" + "\n".join(f"  {i+1}. {o}" for i, o in enumerate(options))
    discord_send(
        "리안 확인 필요",
        f"**질문**: {question}{options_text}\n\n`.pending_questions.json`에서 답변해주세요.",
        color=0xFFD700,
    )
    print(f"  [escalation] 질문 등록: {question}")


def check_answers() -> list[dict]:
    """answered: true 항목 반환."""
    if not os.path.exists(PENDING_PATH):
        return []
    try:
        with open(PENDING_PATH, encoding="utf-8") as f:
            pending = json.load(f)
        return [q for q in pending if q.get("answered", False)]
    except Exception:
        return []


def get_unanswered() -> list[dict]:
    """미답변 질문 반환."""
    if not os.path.exists(PENDING_PATH):
        return []
    try:
        with open(PENDING_PATH, encoding="utf-8") as f:
            pending = json.load(f)
        return [q for q in pending if not q.get("answered", False)]
    except Exception:
        return []


def archive_answered():
    """답변된 항목을 아카이브로 이동."""
    if not os.path.exists(PENDING_PATH):
        return
    try:
        with open(PENDING_PATH, encoding="utf-8") as f:
            pending = json.load(f)

        answered = [q for q in pending if q.get("answered", False)]
        remaining = [q for q in pending if not q.get("answered", False)]

        # 아카이브에 추가
        if answered:
            with open(ARCHIVE_PATH, "a", encoding="utf-8") as f:
                for q in answered:
                    f.write(json.dumps(q, ensure_ascii=False) + "\n")

        # 남은 것만 유지
        with open(PENDING_PATH, "w", encoding="utf-8") as f:
            json.dump(remaining, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [escalation] 아카이브 실패: {e}")
