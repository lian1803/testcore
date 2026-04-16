
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### LLM API cost guardrail implementation — token budget enforcement, hard stop vs soft warning patterns in Python
### LLM API Cost Guardrail 핵심 구현 (Python)

**토큰 예산 강제 + Hard Stop vs Soft Warning 패턴.** LLM API 비용 폭증 방지: 요청 전 토큰/예산 체크 → Hard Stop(즉시 차단, 비용 0) 우선 → Soft Warning(알림 후 진행, 사용자 경험 유지).[1][2]

#### 1. 토큰 예산 추적 프레임워크 (실전 코드)
Redis + Python으로 **per-user 토큰 버킷** 구현. 1M 토큰/일 예산 예시 (OpenAI GPT-4o: $5/M input, $15/M output 기준).[1]

```python
import redis
import tiktoken  # OpenAI 토큰 카운터
from openai import OpenAI
from typing import Dict

r = redis.Redis(host='localhost', port=6379, db=0)
ENC = tiktoken.get_encoding("cl100k_base")  # GPT-4o 엔코더

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    return len(ENC.encode(text))

def get_user_budget(user_id: str) -> Dict:
    key = f"budget:{user_id}"
    daily_limit = 1_000_000  # 1M 토큰/일
    used = int(r.get(key) or 0)
    return {"limit": daily_limit, "used": used, "remaining": daily_limit - used}

def check_token_budget(user_id: str, prompt: str, max_output: int = 4096) -> tuple[bool, str]:
    input_tokens = count_tokens(prompt)
    total_est = input_tokens + max_output  # 보수적 추정
    budget = get_user_budget(user_id)
    
    if budget["remaining"] < total_est:
        pct_used = (budget["used"] / budget["limit"]) * 100
        return False, f"예산 초과: {pct_used:.1f}% 사용 ({budget['used']:,}/{budget['limit']:,} 토큰)"
    return True, "OK"
```

**사용 예시 (Pre-call Guard):**
```python
def call_llm_safely(user_id: str, prompt: str):
    ok, msg = check_token_budget(user_id, prompt)
    if not ok:
        return {"error": "HARD STOP: 토큰 예산 초과", "detail": msg}  # 비용 0 차단[1][2]
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096
    )
    
    output_tokens = len(ENC.encode(response.choices[0].message.content))
    r.incrby(f"budget:{user_id}", input + output_tokens)  # 사용량 누적
    r.expire(f"budget:{user_id}", 86400)  # 24h 리셋
    return response
```
**효과:** 1 요청당 0.1초 지연, 비용 폭증 100% 차단. MarginDash 스타일 예산 알림 추가 가능.[1]

#### 2. Hard Stop vs Soft Warning 패턴 비교
| 패턴 | 트리거 | 동작 | Python 구현 | 비용 절감 | UX 영향 |
|------|--------|------|-------------|----------|---------|
| **Hard Stop** | total_est > remaining | 즉시 Reject (HTTP 429) | `if not ok: return {"error": msg}` | 100% (요청 안 보냄) | 낮음 (예상 오류) |
| **Soft Warning** | used > 80% limit | Log + Email + 진행 | `if budget["used"] > 0.8 * budget["limit"]:`<br>`send_alert(user_id)`<br>`return call_llm(...)` | 20-50% (과사용 억제) | 높음 (연속 사용 OK) |[1][2]

**하이브리드 추천:** 예산 90% 초과 시 Hard Stop, 70-90% Soft Warning + 이메일 (`smtplib`).[1] 토큰 기반 Rate Limit: Redis `INCR/EXPIRE`로 초당 10K 토큰 제한.[2]

#### 3. 고급 최적화 (Top 3 사례)
- **Guar

### Per-user LLM usage tracking architecture: database schema, real-time monitoring, alerting thresholds
### Database Schema (PostgreSQL 기반 LiteLLM 예시)
LiteLLM + PostgreSQL로 사용자별 토큰/비용 추적. 핵심 테이블[2][4]:

| 테이블 | 주요 컬럼 | 용도 |
|--------|-----------|------|
| **litellm_logs** | id (PK), user_id, model, prompt_tokens, completion_tokens, total_cost (USD), start_time, end_time, metadata (JSON: team/project tag) | 요청별 상세 로그. `user_id`로 사용자 attribution. |
| **customer_usage** | customer_id (PK), spend_total, token_usage (prompt+completion), api_key_id, date_range | 고객별 집계. /user/daily/activity API로 daily spend/prompt_tokens 조회[2][4]. |
| **budgets** | user_id, daily_limit (e.g. $50), monthly_limit, current_spend, exceeded (bool) | 예산 초과 체크용. |

**쿼리 예시** (top 5 고비용 사용자):
```sql
SELECT user_id, SUM(total_cost) as spend, SUM(prompt_tokens) as tokens
FROM litellm_logs 
WHERE start_time > NOW() - INTERVAL '30 days'
GROUP BY user_id ORDER BY spend DESC LIMIT 5;
```
**인덱스**: `user_id`, `start_time`에 composite index로 실시간 쿼리 최적화 (10M rows/sec)[2].

### Real-time Monitoring (Proxy + OpenTelemetry)
1. **LLM Proxy 도입** (LiteLLM/TrueFoundry): 모든 API 요청 중앙화. 요청 시 `user_id`, `feature_name`, `team_id` 태그 자동 attach[1][2][6
===

