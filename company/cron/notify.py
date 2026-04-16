import os
import requests
from datetime import datetime
from typing import Optional

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


def send_embed(title: str, body: str, color: int = 0x00FF00) -> bool:
    """디스코드 임베드 메시지 전송"""
    if not DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL" in DISCORD_WEBHOOK_URL:
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": body,
                "color": color,
                "footer": {"text": f"🤖 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 디스코드 알림 실패: {e}")
        return False


def send_simple(message: str) -> bool:
    """간단한 텍스트 메시지 전송"""
    if not DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL" in DISCORD_WEBHOOK_URL:
        return False

    payload = {"content": message}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 디스코드 알림 실패: {e}")
        return False


def notify_health_check(project_url: str, status: str, response_time: float):
    """헬스체크 결과 알림"""
    color = 0x27AE60 if status == "OK" else 0xE74C3C
    emoji = "✅" if status == "OK" else "⚠️"

    send_embed(
        f"{emoji} 헬스체크 — {status}",
        f"**프로젝트**: {project_url}\n**응답시간**: {response_time:.2f}초",
        color=color
    )


def notify_daily_report(report_content: str):
    """일일 보고 알림"""
    send_embed(
        "📊 일일 보고",
        report_content,
        color=0x3498DB
    )


def notify_error_detected(error_type: str, details: str):
    """이상감지 알림"""
    send_embed(
        f"🚨 이상감지 — {error_type}",
        f"```\n{details[:500]}\n```",
        color=0xE74C3C
    )


def notify_fix_applied(fix_description: str, pr_url: Optional[str] = None):
    """자동 수정 적용 알림"""
    body = f"✨ 자동 수정이 적용됐습니다.\n\n{fix_description}"
    if pr_url:
        body += f"\n\n📌 PR: {pr_url}"

    send_embed(
        "🔧 자동 수정 완료",
        body,
        color=0x2ECC71
    )
