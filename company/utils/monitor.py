"""
Langfuse LLM 비용 모니터링 유틸.
키 없으면 no-op, 로컬 로그 폴백.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from functools import wraps


class LangfuseMonitor:
    """Langfuse 통합 비용 추적."""

    def __init__(self):
        self.enabled = bool(
            os.getenv("LANGFUSE_PUBLIC_KEY") and
            os.getenv("LANGFUSE_SECRET_KEY")
        )
        self.client = None
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "cost_log.jsonl"

        if self.enabled:
            try:
                from langfuse import Langfuse
                self.client = Langfuse(
                    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                )
            except Exception as e:
                print(f"⚠️  Langfuse 초기화 실패: {e}")
                self.enabled = False

    def track_llm_call(
        self,
        agent_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ) -> None:
        """LLM 호출 비용 기록."""
        timestamp = datetime.now().isoformat()

        # Langfuse 기록
        if self.enabled and self.client:
            try:
                self.client.observation(
                    name=f"{agent_name}:{model}",
                    type="llm",
                    input={"tokens": input_tokens},
                    output={"tokens": output_tokens},
                    metadata={"cost_usd": cost}
                )
            except Exception as e:
                print(f"⚠️  Langfuse 기록 실패: {e}")

        # 로컬 로그 (항상 기록)
        log_entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_summary(self) -> dict:
        """비용 통계 조회."""
        if not self.log_file.exists():
            return {"total_cost": 0, "total_tokens": 0, "calls": 0}

        total_cost = 0
        total_tokens = 0
        calls = 0

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_cost += entry.get("cost_usd", 0)
                    total_tokens += entry.get("total_tokens", 0)
                    calls += 1
                except:
                    pass

        return {
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "calls": calls,
            "log_file": str(self.log_file)
        }


# 싱글톤 인스턴스
_monitor = None


def get_monitor() -> LangfuseMonitor:
    """모니터 인스턴스 획득."""
    global _monitor
    if _monitor is None:
        _monitor = LangfuseMonitor()
    return _monitor


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """토큰 기반 예상 비용 계산 (USD)."""
    # 2024년 가격 기준
    pricing = {
        # Claude
        "claude-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        # OpenAI
        "gpt-4o": {"input": 0.0025, "output": 0.010},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        # Google
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        # Perplexity
        "pplx-7b-online": {"input": 0.00007, "output": 0.00028},
        "pplx-70b-online": {"input": 0.0007, "output": 0.0028},
    }

    # 정확한 모델명 또는 부분 일치 찾기
    rate = pricing.get(model)
    if not rate:
        # 부분 일치 (예: "claude-opus-latest" → "claude-opus")
        for key, value in pricing.items():
            if key in model or model in key:
                rate = value
                break

    if not rate:
        # 기본값: 대략 gpt-4o 정도
        rate = {"input": 0.0025, "output": 0.010}

    cost = (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1000
    return cost


def track_api_call(agent_name: str, model: str):
    """
    API 호출 비용 추적 데코레이터.
    response.usage.input_tokens와 response.usage.output_tokens를 자동으로 기록.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Anthropic 응답 객체인 경우
            if hasattr(result, "usage"):
                monitor = get_monitor()
                input_tokens = result.usage.input_tokens
                output_tokens = result.usage.output_tokens
                cost = estimate_cost(model, input_tokens, output_tokens)
                monitor.track_llm_call(agent_name, model, input_tokens, output_tokens, cost)

            return result

        return wrapper
    return decorator
