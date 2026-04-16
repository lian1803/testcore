"""
에이전트 성장 시스템

각 직원이 일할 때마다 경험을 쌓고, 피드백을 받고, 성과를 추적한다.
실제 회사 직원처럼 성장하는 AI 직원 구현.

구조:
  knowledge/agents/{이름}/
    experience.jsonl   — 업무 로그 (날짜, 업무, 결과, 품질)
    feedback.jsonl     — 리안 피드백 누적
    mistakes.md        — 실수 기록 (반복 방지)

  knowledge/performance/{이름}.json  — 성과 종합 (성공률, 평점, 전문분야)
"""

import json
import os
from datetime import datetime
from pathlib import Path

AGENTS_DIR = Path(__file__).parent / "agents"
PERF_DIR = Path(__file__).parent / "performance"

# 디렉토리 초기화
AGENTS_DIR.mkdir(exist_ok=True)
PERF_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
# 경험 기록 (업무 로그)
# ──────────────────────────────────────────────

def save_work_log(name: str, task: str, result_summary: str, success: bool = True, tags: list = None):
    """업무 완료 후 경험 기록."""
    agent_dir = AGENTS_DIR / name
    agent_dir.mkdir(exist_ok=True)

    log_path = agent_dir / "experience.jsonl"
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "task": task[:200],
        "result_summary": result_summary[:500],
        "success": success,
        "tags": tags or [],
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def save_feedback(name: str, task: str, feedback: str, score: int = None):
    """리안 피드백 저장 (1~5점)."""
    agent_dir = AGENTS_DIR / name
    agent_dir.mkdir(exist_ok=True)

    feedback_path = agent_dir / "feedback.jsonl"
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "task": task[:200],
        "feedback": feedback,
        "score": score,
    }
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 점수 낮으면 (1~2점) mistakes.md에도 기록 + 자기 개발 트리거
    if score and score <= 2:
        mistakes_path = agent_dir / "mistakes.md"
        with open(mistakes_path, "a", encoding="utf-8") as f:
            f.write(f"\n### {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**업무**: {task[:100]}\n")
            f.write(f"**피드백**: {feedback}\n")
            f.write(f"**교훈**: (다음 작업에 반영)\n")

        # 자기 개발 큐에 추가 (다음 실행 시 자동 학습)
        _queue_self_training(name, task, feedback)

    # 성과 업데이트
    _update_performance(name, score)


def _update_performance(name: str, score: int = None):
    """성과 지표 업데이트."""
    perf_path = PERF_DIR / f"{name}.json"

    # 기존 성과 로드
    if perf_path.exists():
        with open(perf_path, encoding="utf-8") as f:
            perf = json.load(f)
    else:
        perf = {
            "name": name,
            "total_tasks": 0,
            "feedback_count": 0,
            "feedback_total_score": 0,
            "feedback_avg": None,
            "specialties": [],
            "growth_log": [],
            "last_active": None,
        }

    perf["last_active"] = datetime.now().strftime("%Y-%m-%d")

    if score:
        perf["feedback_count"] += 1
        perf["feedback_total_score"] += score
        perf["feedback_avg"] = round(perf["feedback_total_score"] / perf["feedback_count"], 1)

    with open(perf_path, "w", encoding="utf-8") as f:
        json.dump(perf, f, ensure_ascii=False, indent=2)


def record_task_start(name: str):
    """업무 시작 시 total_tasks 카운트."""
    perf_path = PERF_DIR / f"{name}.json"
    if perf_path.exists():
        with open(perf_path, encoding="utf-8") as f:
            perf = json.load(f)
    else:
        perf = {
            "name": name,
            "total_tasks": 0,
            "feedback_count": 0,
            "feedback_total_score": 0,
            "feedback_avg": None,
            "specialties": [],
            "growth_log": [],
            "last_active": None,
        }

    perf["total_tasks"] += 1
    perf["last_active"] = datetime.now().strftime("%Y-%m-%d")

    with open(perf_path, "w", encoding="utf-8") as f:
        json.dump(perf, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# 경험 로드 (다음 업무에 반영)
# ──────────────────────────────────────────────

def load_agent_memory(name: str, max_entries: int = 5) -> str:
    """에이전트 자신의 경험 기록을 불러와서 프롬프트에 주입할 텍스트로 반환."""
    agent_dir = AGENTS_DIR / name

    sections = []

    # 최근 업무 로그
    log_path = agent_dir / "experience.jsonl"
    if log_path.exists():
        entries = []
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        if entries:
            recent = entries[-max_entries:]
            log_text = "\n".join(
                f"- [{e['date']}] {e['task'][:80]}" for e in recent
            )
            sections.append(f"[최근 업무]\n{log_text}")

    # 피드백 (나쁜 피드백 우선 — 반복 방지)
    feedback_path = agent_dir / "feedback.jsonl"
    if feedback_path.exists():
        bad_feedback = []
        with open(feedback_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if entry.get("score") and entry["score"] <= 3:
                            bad_feedback.append(entry)
                    except json.JSONDecodeError:
                        pass
        if bad_feedback:
            recent_bad = bad_feedback[-3:]
            fb_text = "\n".join(
                f"- [{e['date']}] {e['feedback'][:100]}" for e in recent_bad
            )
            sections.append(f"[개선 필요 (이전 피드백)]\n{fb_text}")

    # 실수 기록
    mistakes_path = agent_dir / "mistakes.md"
    if mistakes_path.exists():
        with open(mistakes_path, encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            # 마지막 실수 3개만
            blocks = content.split("###")
            recent_mistakes = [b.strip() for b in blocks if b.strip()][-3:]
            if recent_mistakes:
                sections.append(f"[반복하면 안 되는 실수]\n" + "\n".join(f"### {m}" for m in recent_mistakes))

    if not sections:
        return ""

    return "\n\n".join(sections)


# ──────────────────────────────────────────────
# 성과 조회
# ──────────────────────────────────────────────

def get_performance(name: str) -> dict:
    """직원 성과 조회."""
    perf_path = PERF_DIR / f"{name}.json"
    if not perf_path.exists():
        return {"name": name, "total_tasks": 0, "feedback_avg": None}
    with open(perf_path, encoding="utf-8") as f:
        return json.load(f)


def get_all_performance() -> list:
    """전체 직원 성과 조회 (성과 순 정렬)."""
    results = []
    for path in PERF_DIR.glob("*.json"):
        with open(path, encoding="utf-8") as f:
            results.append(json.load(f))
    results.sort(key=lambda x: x.get("feedback_avg") or 0, reverse=True)
    return results


def print_performance_report():
    """성과 현황 출력."""
    all_perf = get_all_performance()
    if not all_perf:
        print("아직 업무 기록이 없어.")
        return

    print("\n" + "="*50)
    print("직원 성과 현황")
    print("="*50)
    for p in all_perf:
        avg = f"{p['feedback_avg']:.1f}/5" if p['feedback_avg'] else "평가 없음"
        # 자기 개발 대기 중인지 표시
        training_flag = ""
        training_queue = AGENTS_DIR / p['name'] / "training_queue.json"
        if training_queue.exists():
            training_flag = " [학습 대기중]"
        print(f"  {p['name']:8} | 업무 {p.get('total_tasks', 0):3}건 | 평점 {avg} | 최근 활동: {p.get('last_active', '-')}{training_flag}")
    print("="*50)


# ──────────────────────────────────────────────
# 자기 개발 시스템 (#5b)
# ──────────────────────────────────────────────

def _queue_self_training(name: str, task: str, feedback: str):
    """낮은 평점 피드백 시 자기 개발 큐에 추가."""
    agent_dir = AGENTS_DIR / name
    agent_dir.mkdir(exist_ok=True)

    queue_path = agent_dir / "training_queue.json"
    queue = []
    if queue_path.exists():
        with open(queue_path, encoding="utf-8") as f:
            queue = json.load(f)

    queue.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weak_area": task[:100],
        "reason": feedback[:200],
        "learned": False,
    })
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def run_self_training(name: str) -> str:
    """
    자기 개발 실행 — Perplexity로 부족한 분야 학습.
    낮은 평점 받은 업무 분야를 자동으로 리서치해서 training/ 폴더에 저장.

    반환: 학습 완료 메시지 or 학습할 것 없음
    """
    agent_dir = AGENTS_DIR / name
    queue_path = agent_dir / "training_queue.json"

    if not queue_path.exists():
        return f"{name}: 학습 큐가 비어있어. (낮은 평점 피드백이 없음)"

    with open(queue_path, encoding="utf-8") as f:
        queue = json.load(f)

    unlearned = [item for item in queue if not item.get("learned")]
    if not unlearned:
        return f"{name}: 모든 학습 항목 완료됨."

    # Perplexity로 학습
    import os
    from openai import OpenAI

    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    if not perplexity_key:
        return f"{name}: PERPLEXITY_API_KEY 없음. 학습 스킵."

    training_dir = agent_dir / "training"
    training_dir.mkdir(exist_ok=True)

    perplexity = OpenAI(
        api_key=perplexity_key,
        base_url="https://api.perplexity.ai",
        timeout=60.0,
    )

    results = []
    for item in unlearned:
        weak_area = item["weak_area"]
        reason = item["reason"]

        print(f"\n[{name}] 자기 개발: '{weak_area[:50]}' 분야 학습 중...")

        query = f"""
다음 업무 분야에서 전문가 수준의 핵심 지식을 알려줘:

업무: {weak_area}
부족했던 이유: {reason}

핵심 베스트 프랙티스, 주의할 점, 실제 예시 중심으로 정리해줘.
한국어로 답해줘.
"""
        try:
            response = perplexity.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {"role": "system", "content": "너는 세계 최고 수준의 전문가야. 핵심만 간결하게 가르쳐줘."},
                    {"role": "user", "content": query}
                ],
                max_tokens=1500,
            )
            learned_content = response.choices[0].message.content

            # 학습 내용 저장
            safe_name = weak_area[:30].replace("/", "_").replace(" ", "_")
            training_file = training_dir / f"{datetime.now().strftime('%Y%m%d')}_{safe_name}.md"
            with open(training_file, "w", encoding="utf-8") as f:
                f.write(f"# 자기 개발: {weak_area}\n\n")
                f.write(f"**학습 계기**: {reason}\n\n")
                f.write(f"**학습 일자**: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write("---\n\n")
                f.write(learned_content)

            item["learned"] = True
            item["learned_at"] = datetime.now().strftime("%Y-%m-%d")
            results.append(f"완료: {weak_area[:50]}")
            print(f"  -> 저장: {training_file.name}")

        except Exception as e:
            results.append(f"실패: {weak_area[:50]} ({e})")

    # 큐 업데이트
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    return f"{name} 자기 개발 완료:\n" + "\n".join(f"  - {r}" for r in results)


def load_training_knowledge(name: str) -> str:
    """자기 개발로 학습한 내용을 프롬프트에 주입할 텍스트로 반환."""
    training_dir = AGENTS_DIR / name / "training"
    if not training_dir.exists():
        return ""

    files = sorted(training_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return ""

    # 최근 3개 학습 내용만
    recent = files[:3]
    contents = []
    for f in recent:
        with open(f, encoding="utf-8") as fp:
            content = fp.read()
        # 첫 500자만 요약
        contents.append(content[:500])

    return "[자기 개발 학습 내용]\n" + "\n---\n".join(contents)
