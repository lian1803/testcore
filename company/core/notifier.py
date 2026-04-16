import os
import requests
import json
from typing import Optional

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL")

def send(title: str, body: str, color: int = 0x00FF00) -> bool:
    """Discord 웹훅으로 임베드 메시지 전송

    Args:
        title: 임베드 제목
        body: 임베드 본문 (마크다운 지원)
        color: 16진수 색상 (기본: 초록색)

    Returns:
        성공 여부
    """
    if "YOUR_WEBHOOK_URL" in DISCORD_WEBHOOK_URL:
        print(f"⚠️  DISCORD_WEBHOOK_URL 미설정 — 디스코드 알림 스킵: {title}")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": body,
                "color": color,
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 디스코드 알림 실패: {e}")
        return False


def wait_confirm(msg: str) -> bool:
    """디스코드로 메시지 전송 후 터미널에서 y/n 대기

    Args:
        msg: 전송할 메시지

    Returns:
        y 입력 시 True, n 입력 시 False
    """
    send("⏳ 리안 확인 필요", msg, color=0xFFD700)

    print(f"\n{msg}")
    print("리안 (y/n): ", end="")
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = "y"

    return answer in ("y", "yes", "ㅇㅇ", "진행", "")


def notify_pipeline_start(idea: str):
    """파이프라인 시작 알림"""
    send(
        "🚀 파이프라인 시작",
        f"**아이디어**: {idea}\n\n이사팀이 자동으로 실행됩니다.",
        color=0x3498DB
    )


def notify_agent_complete(agent_name: str, step: int, total: int):
    """에이전트 완료 알림"""
    send(
        f"✅ [{step}/{total}] {agent_name} 완료",
        f"`{agent_name}`이 정상 완료됐습니다.",
        color=0x2ECC71
    )


def notify_discussion_round(round_num: int, key_point: str):
    """토론 라운드 알림"""
    send(
        f"💬 토론 라운드 {round_num}",
        f"**쟁점**: {key_point}\n\n토론 중입니다...",
        color=0xE74C3C
    )


def notify_verdict(verdict: str, score: float, risks: Optional[str] = None):
    """최종 판단 알림"""
    color_map = {
        "GO": 0x27AE60,
        "CONDITIONAL_GO": 0xF39C12,
        "NO_GO": 0xE74C3C,
    }
    body = f"**판정**: {verdict}\n**점수**: {score}/10"
    if risks:
        body += f"\n\n**리스크**: {risks}"

    send(
        f"⚖️  최종 판단",
        body,
        color=color_map.get(verdict, 0x95A5A6)
    )


def notify_execution_start():
    """실행팀 시작 알림"""
    send(
        "🛠️  실행팀 시작",
        "PRD + 구현 지시서 작성이 시작됩니다.",
        color=0x3498DB
    )


def notify_completion(output_dir: str, project_name: str):
    """파이프라인 완료 알림"""
    send(
        "🎉 리안 컴퍼니 완료!",
        f"**프로젝트**: {project_name}\n**결과 경로**: `{output_dir}`\n\n다음 단계: `/work` 실행",
        color=0x9B59B6
    )


def notify_error(stage: str, error: str):
    """에러 알림"""
    send(
        f"⚠️  오류 발생 — {stage}",
        f"```\n{error}\n```",
        color=0xE74C3C
    )
