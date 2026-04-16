"""
API 비용 트래킹 시스템
- 모든 LLM 호출 기록
- 모델별 토큰 기반 비용 계산
- 일별/주별/월별 리포트
- JSONL 형식 저장 (append-only, 안전함)
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import defaultdict


# 모델별 가격 (1M tokens 기준, USD)
PRICING = {
    # Claude
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.8, "output": 4.0},
    "claude-haiku-3-5-20241022": {"input": 0.8, "output": 4.0},

    # GPT
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-2024-11-20": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-4": {"input": 30.0, "output": 60.0},

    # Gemini
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-pro": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gemini-pro": {"input": 0.5, "output": 1.5},

    # Perplexity
    "sonar-pro": {"input": 3.0, "output": 15.0},
    "sonar": {"input": 0.2, "output": 0.2},
    "sonar-reasoning-pro": {"input": 5.0, "output": 15.0},
}


class CostTracker:
    """API 비용 추적"""

    def __init__(self, log_file: str = "./logs/api_costs.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_call(
        self,
        agent: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: Optional[float] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        API 호출 기록

        Args:
            agent: 에이전트명 (minsu, sieun, etc.)
            model: 모델명
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수
            cost: 비용 (자동 계산하면 None)
            metadata: 추가 정보

        Returns:
            기록 성공 여부
        """
        if cost is None:
            cost = self.calculate_cost(model, input_tokens, output_tokens)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost, 6),
            "metadata": metadata or {}
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            print(f"⚠️  비용 로깅 실패: {e}")
            return False

    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """
        비용 계산 (1M tokens 기준)

        Args:
            model: 모델명
            input_tokens: 입력 토큰
            output_tokens: 출력 토큰

        Returns:
            비용 (USD)
        """
        if model not in PRICING:
            # 알 수 없는 모델은 기본값
            return 0.0

        pricing = PRICING[model]
        input_cost = input_tokens * pricing["input"] / 1_000_000
        output_cost = output_tokens * pricing["output"] / 1_000_000
        return input_cost + output_cost

    def get_summary(self, days: int = 30) -> dict:
        """
        기간별 비용 요약

        Args:
            days: 몇 일 이전부터 집계할지 (기본 30일)

        Returns:
            비용 요약 딕셔너리
        """
        if not self.log_file.exists():
            return {
                "total_cost": 0.0,
                "by_agent": {},
                "by_model": {},
                "by_date": {},
                "sample_count": 0
            }

        cutoff_date = datetime.now() - timedelta(days=days)
        costs_by_agent = defaultdict(float)
        costs_by_model = defaultdict(float)
        costs_by_date = defaultdict(float)
        total_cost = 0.0
        count = 0

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry["timestamp"])

                        if entry_date < cutoff_date:
                            continue

                        cost = entry.get("cost_usd", 0)
                        agent = entry.get("agent", "unknown")
                        model = entry.get("model", "unknown")
                        date = entry_date.date().isoformat()

                        costs_by_agent[agent] += cost
                        costs_by_model[model] += cost
                        costs_by_date[date] += cost
                        total_cost += cost
                        count += 1
                    except Exception:
                        pass
        except Exception as e:
            print(f"⚠️  비용 요약 조회 실패: {e}")

        # 날짜 정렬
        costs_by_date = dict(sorted(costs_by_date.items()))

        return {
            "total_cost": round(total_cost, 2),
            "by_agent": dict(sorted(costs_by_agent.items(), key=lambda x: x[1], reverse=True)),
            "by_model": dict(sorted(costs_by_model.items(), key=lambda x: x[1], reverse=True)),
            "by_date": costs_by_date,
            "sample_count": count,
            "days": days
        }

    def get_daily_report(self, date: Optional[str] = None) -> dict:
        """
        특정 날짜의 비용 리포트

        Args:
            date: YYYY-MM-DD (None이면 오늘)

        Returns:
            날짜별 상세 리포트
        """
        if date is None:
            date = datetime.now().date().isoformat()

        if not self.log_file.exists():
            return {"date": date, "total": 0.0, "entries": []}

        entries = []
        total = 0.0

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry["timestamp"]).date().isoformat()
                        if entry_date == date:
                            entries.append(entry)
                            total += entry.get("cost_usd", 0)
                    except Exception:
                        pass
        except Exception:
            pass

        return {
            "date": date,
            "total_cost": round(total, 2),
            "entry_count": len(entries),
            "entries": entries
        }

    def get_agent_report(self, agent: str, days: int = 30) -> dict:
        """
        특정 에이전트의 비용 리포트

        Args:
            agent: 에이전트명
            days: 몇 일 이전부터

        Returns:
            에이전트별 상세 리포트
        """
        if not self.log_file.exists():
            return {
                "agent": agent,
                "total_cost": 0.0,
                "calls": 0,
                "avg_cost_per_call": 0.0,
                "models": {}
            }

        cutoff_date = datetime.now() - timedelta(days=days)
        total_cost = 0.0
        calls = 0
        models = defaultdict(float)

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry["timestamp"])

                        if entry_date < cutoff_date:
                            continue
                        if entry.get("agent") != agent:
                            continue

                        cost = entry.get("cost_usd", 0)
                        model = entry.get("model", "unknown")

                        total_cost += cost
                        models[model] += cost
                        calls += 1
                    except Exception:
                        pass
        except Exception:
            pass

        return {
            "agent": agent,
            "total_cost": round(total_cost, 2),
            "calls": calls,
            "avg_cost_per_call": round(total_cost / calls, 6) if calls > 0 else 0.0,
            "models": dict(sorted(models.items(), key=lambda x: x[1], reverse=True)),
            "days": days
        }

    def print_summary(self, days: int = 30):
        """
        비용 요약 출력

        Args:
            days: 기간
        """
        summary = self.get_summary(days)

        print("\n" + "="*70)
        print(f"📊 API 비용 요약 (최근 {days}일)")
        print("="*70)
        print(f"💰 총 비용: ${summary['total_cost']:.2f}")
        print(f"📝 샘플 수: {summary['sample_count']}")

        if summary['by_agent']:
            print("\n📌 에이전트별 비용:")
            for agent, cost in summary['by_agent'].items():
                pct = (cost / summary['total_cost'] * 100) if summary['total_cost'] > 0 else 0
                print(f"   {agent:20s} ${cost:8.2f} ({pct:5.1f}%)")

        if summary['by_model']:
            print("\n🤖 모델별 비용:")
            for model, cost in summary['by_model'].items():
                pct = (cost / summary['total_cost'] * 100) if summary['total_cost'] > 0 else 0
                print(f"   {model:30s} ${cost:8.2f} ({pct:5.1f}%)")

        print("="*70 + "\n")

    def estimate_monthly_cost(self) -> Dict[str, float]:
        """
        월간 비용 추정 (최근 7일 데이터 기반)

        Returns:
            총 비용, 에이전트별 비용 등
        """
        summary = self.get_summary(days=7)
        if summary['sample_count'] == 0:
            return {"total": 0.0, "by_agent": {}}

        # 7일 → 30일로 외삽
        multiplier = 30 / 7
        total = summary['total_cost'] * multiplier
        by_agent = {
            agent: cost * multiplier
            for agent, cost in summary['by_agent'].items()
        }

        return {
            "total": round(total, 2),
            "by_agent": {k: round(v, 2) for k, v in by_agent.items()},
            "based_on_days": 7
        }


# 글로벌 트래커 인스턴스
_tracker = None

def get_tracker(log_file: str = "./logs/api_costs.jsonl") -> CostTracker:
    """글로벌 트래커 인스턴스 획득"""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker(log_file)
    return _tracker

def log_api_call(
    agent: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: Optional[float] = None,
    metadata: Optional[dict] = None
) -> bool:
    """편의 함수: get_tracker().log_call()"""
    return get_tracker().log_call(agent, model, input_tokens, output_tokens, cost, metadata)

def estimate_monthly() -> Dict:
    """편의 함수: get_tracker().estimate_monthly_cost()"""
    return get_tracker().estimate_monthly_cost()
