"""
cost_tracker.py — 에이전트 호출 비용/품질 자체 tracker

PostHog 대신 가벼운 내부 기록.
나중에 PostHog 붙이려면 _emit()만 교체.

사용법:
    from tools.cost_tracker import track

    with track(agent="be", task="API 설계", model="sonnet"):
        result = run_something()
    # 자동으로 실행 시간 + 토큰 추정 + 성공 여부 기록

    # 또는 직접:
    from tools.cost_tracker import log_call
    log_call(agent="yejin", model="haiku", input_tokens=1200, output_tokens=400, success=True)
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

LOG_PATH = Path(__file__).parent.parent / "knowledge" / "agent_costs.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Anthropic 가격 (2026-04 기준, 1M 토큰당 USD)
PRICES = {
    "opus": (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku": (0.80, 4.0),
    "gpt-4o": (2.50, 10.0),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-pro": (1.25, 10.0),
    "perplexity-sonar": (1.0, 1.0),
}


def _price(model: str, inp: int, out: int) -> float:
    key = next((k for k in PRICES if k in model.lower()), None)
    if not key:
        return 0.0
    pi, po = PRICES[key]
    return (inp * pi + out * po) / 1_000_000


def _emit(record: dict):
    """실제 저장. 추후 PostHog로 교체 가능."""
    record["ts"] = datetime.now().isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_call(
    agent: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    success: bool = True,
    elapsed_sec: float = 0,
    task: str = "",
    meta: dict | None = None,
):
    """에이전트 호출 1건 기록."""
    cost = _price(model, input_tokens, output_tokens)
    _emit({
        "agent": agent,
        "model": model,
        "task": task[:200],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "success": success,
        "elapsed_sec": round(elapsed_sec, 2),
        "meta": meta or {},
    })


@contextmanager
def track(agent: str, task: str, model: str = "sonnet"):
    """컨텍스트 매니저 — with 블록 실행 시간 + 성공 여부 자동 기록."""
    start = time.time()
    success = True
    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        log_call(
            agent=agent,
            model=model,
            task=task,
            success=success,
            elapsed_sec=time.time() - start,
        )


def summary(days: int = 7) -> dict:
    """최근 N일 요약. 비용/호출수/실패율."""
    if not LOG_PATH.exists():
        return {"total_calls": 0, "total_cost_usd": 0}
    cutoff = time.time() - days * 86400
    totals = {"calls": 0, "cost": 0.0, "fails": 0, "by_agent": {}, "by_model": {}}
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                ts = datetime.fromisoformat(r["ts"]).timestamp()
                if ts < cutoff:
                    continue
                totals["calls"] += 1
                totals["cost"] += r.get("cost_usd", 0)
                if not r.get("success", True):
                    totals["fails"] += 1
                a = r.get("agent", "?")
                totals["by_agent"][a] = totals["by_agent"].get(a, 0) + r.get("cost_usd", 0)
                m = r.get("model", "?")
                totals["by_model"][m] = totals["by_model"].get(m, 0) + r.get("cost_usd", 0)
            except Exception:
                continue
    totals["cost"] = round(totals["cost"], 4)
    totals["fail_rate"] = round(totals["fails"] / max(totals["calls"], 1), 3)
    return totals


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    s = summary(days)
    print(json.dumps(s, ensure_ascii=False, indent=2))
