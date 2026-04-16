import os
import json
from datetime import datetime, timedelta
import anthropic
from . import notify
from core.models import CLAUDE_HAIKU

MIJEONG_MODEL = CLAUDE_HAIKU
MIJEONG_SYSTEM_PROMPT = """너는 미정이야. 리안 컴퍼니의 일일 보고담당이야.

매일 아침 8시에 지난 24시간의 주요 지표를 수집해서 일일 보고서를 작성해.

보고 항목:
1. 신규 가입자 수 (어제 vs 지난주 평균)
2. 매출 현황 (어제 vs 월 목표 대비)
3. 에러율 (Critical/High/Medium)
4. 마케팅 진행율 (진행중인 캠페인 상태)
5. 특이사항 (알림할 건 뭔가?)

형식:
```
📊 일일 보고 — 2026-03-30

✅ 신규 가입: 5명 (지난주 평균: 3명)
💰 매출: $1,200 (월 목표: $50,000 중 2.4%)
⚠️  에러율: 0.2% (정상)
🎯 마케팅: 3개 캠페인 진행 중
🔔 특이: 없음
```

간단하고 명확하게. 숫자는 실제 환경에서 DB 쿼리로 가져올 거야."""


def generate_daily_report() -> str:
    """Claude Haiku로 일일 보고서 생성"""
    client = anthropic.Anthropic()

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 실제 환경: DB에서 메트릭스 쿼리
    # 지금은 더미 데이터
    metrics = {
        "date": today,
        "new_signups": 5,
        "weekly_avg_signups": 3,
        "revenue_yesterday": 1200,
        "monthly_target": 50000,
        "error_rate": 0.2,
        "critical_errors": 0,
        "high_errors": 1,
        "running_campaigns": 3,
        "notes": "없음",
    }

    prompt = f"""날짜: {today}
지난날 ({yesterday}) 메트릭스:
- 신규 가입: {metrics['new_signups']}명 (지난주 평균: {metrics['weekly_avg_signups']}명)
- 매출: ${metrics['revenue_yesterday']} (월 목표: ${metrics['monthly_target']})
- 에러율: {metrics['error_rate']}% (Critical: {metrics['critical_errors']}, High: {metrics['high_errors']})
- 진행중 캠페인: {metrics['running_campaigns']}개
- 특이사항: {metrics['notes']}

위 데이터를 바탕으로 일일 보고서를 작성해줘."""

    try:
        message = client.messages.create(
            model=MIJEONG_MODEL,
            max_tokens=500,
            system=MIJEONG_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        report = message.content[0].text
        return report

    except Exception as e:
        print(f"❌ 일일 보고서 생성 실패: {e}")
        return f"❌ 보고서 생성 오류: {e}"


def run_daily_report():
    """일일 보고 실행"""
    print("📊 일일 보고 생성 중...")
    report = generate_daily_report()
    print(report)

    # 디스코드 전송
    notify.notify_daily_report(report)


if __name__ == "__main__":
    run_daily_report()
