"""
디스코드 봇 — 리안이 디코에서 지시하면 시스템 자동 실행

사용법:
  python discord_bot.py

.env 필요:
  DISCORD_BOT_TOKEN=봇토큰
  DISCORD_LIAN_USER_ID=리안 유저ID (보안)
  DISCORD_CHANNEL_ID=채널ID (선택)
"""

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import discord
import subprocess
import asyncio
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

LIAN_COMPANY = Path(__file__).parent
PYTHON = str(LIAN_COMPANY / "venv/Scripts/python.exe")

# 환경변수
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_LIAN_USER_ID = os.getenv("DISCORD_LIAN_USER_ID", "")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")

# 디스코드 인텐트
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def load_agent_status():
    """현재 실행 중인 에이전트 상태 조회"""
    status_file = LIAN_COMPANY / ".agent_status.json"
    if status_file.exists():
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None


def read_reports(limit=3):
    """보고사항들.md 최신 보고 읽기"""
    report_file = LIAN_COMPANY / "보고사항들.md"
    if not report_file.exists():
        return "보고사항이 없습니다."

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 최신 N개 섹션 추출 (## 로 시작하는 라인)
        lines = content.split("\n")
        sections = []
        current = []

        for line in lines:
            if line.startswith("##"):
                if current:
                    sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            sections.append("\n".join(current))

        # 최신 3개만
        latest = sections[-limit:]
        result = "\n".join(latest)

        # 2000자 제한
        if len(result) > 1900:
            result = result[:1900] + "...\n\n(더 보기: 보고사항들.md 참조)"

        return result
    except Exception as e:
        return f"보고서 읽기 실패: {str(e)}"


def match_command(text: str) -> dict | None:
    """메시지 패턴 매칭 및 명령 반환"""
    text = text.strip()

    # 상태 조회
    if text.lower() in ["상태", "status"]:
        status = load_agent_status()
        if status:
            desc = f"현재 실행 중: {status.get('current_task', '대기 중')}"
        else:
            desc = "대기 중"
        return {
            "type": "status",
            "desc": desc,
        }

    # 보고서 확인
    if text.lower() in ["보고", "report", "보고서"]:
        return {
            "type": "report",
            "desc": "최신 보고사항 조회",
        }

    # 데일리 루프
    if text.lower() in ["데일리", "daily", "일일"]:
        return {
            "type": "script",
            "desc": "일일 자동 루프 실행",
            "args": ["main.py", "daily"],
            "script": "daily_auto.py",
        }

    # 이사팀 (맨 뒤에 "해볼까" 또는 "이사팀 {아이디어}")
    match = re.search(r"이사팀\s+(.+)$|(.+?)\s*해볼까$", text)
    if match:
        idea = match.group(1) or match.group(2)
        idea = idea.strip()
        return {
            "type": "script",
            "desc": f"이사팀 소집: {idea}",
            "args": ["main.py", idea],
            "script": "main.py",
        }

    # 영업팀
    match = re.search(r"영업\s+(.+)$", text)
    if match:
        task = match.group(1).strip()
        return {
            "type": "script",
            "desc": f"온라인영업팀: {task}",
            "args": ["run_온라인영업팀.py", task],
            "script": "run_온라인영업팀.py",
        }

    # 납품팀
    match = re.search(r"납품\s+(.+)$", text)
    if match:
        task = match.group(1).strip()
        return {
            "type": "script",
            "desc": f"온라인납품팀: {task}",
            "args": ["run_온라인납품팀.py", task],
            "script": "run_온라인납품팀.py",
        }

    # 마케팅팀
    match = re.search(r"마케팅\s+(.+)$", text)
    if match:
        task = match.group(1).strip()
        return {
            "type": "script",
            "desc": f"온라인마케팅팀: {task}",
            "args": ["run_온라인마케팅팀.py", task],
            "script": "run_온라인마케팅팀.py",
        }

    # 오프라인
    match = re.search(r"오프라인\s+(.+)$", text)
    if match:
        task = match.group(1).strip()
        return {
            "type": "script",
            "desc": f"오프라인마케팅: {task}",
            "args": ["offline_sales.py", task],
            "script": "offline_sales.py",
        }

    return None


async def run_script(args: list) -> str:
    """비동기로 스크립트 실행 및 결과 반환"""
    try:
        proc = await asyncio.create_subprocess_exec(
            PYTHON,
            *args,
            cwd=str(LIAN_COMPANY),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # 타임아웃 60초 (각 팀마다 다름)
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=300  # 5분
            )
        except asyncio.TimeoutError:
            proc.kill()
            return "실행 중... (완료 후 보고사항들.md 확인해)\n⏱️ (타임아웃 5분)"

        output = stdout.decode("utf-8", errors="replace").strip()
        error = stderr.decode("utf-8", errors="replace").strip()

        # 성공
        if proc.returncode == 0:
            result = output[-1000:] if len(output) > 1000 else output  # 최대 1000자
            if not result:
                result = "✅ 실행 완료"
            return f"✅ {result}\n\n→ 보고사항들.md 확인해"
        else:
            error_msg = error[-500:] if len(error) > 500 else error
            return f"❌ 실행 실패\n\n{error_msg}"

    except Exception as e:
        return f"❌ 에러: {str(e)}"


@client.event
async def on_ready():
    print(f"[OK] 봇 로그인: {client.user}", flush=True)


@client.event
async def on_message(message):
    """메시지 수신 및 처리"""
    print(f"[DEBUG] 메시지 수신: '{message.content}' from {message.author} (id:{message.author.id})", flush=True)

    # 봇 자신 메시지 무시
    if message.author == client.user:
        return

    # 지정된 채널만 처리 (채널ID 설정되어 있으면)
    if DISCORD_CHANNEL_ID and str(message.channel.id) != DISCORD_CHANNEL_ID:
        return

    # 리안만 허용 (ID 설정되어 있으면)
    if DISCORD_LIAN_USER_ID and str(message.author.id) != DISCORD_LIAN_USER_ID:
        return

    text = message.content.strip()

    # 빈 메시지 무시
    if not text:
        return

    # 명령 매칭
    cmd = match_command(text)

    if not cmd:
        return  # 인식 못 한 명령은 무시

    # 상태 조회
    if cmd["type"] == "status":
        await message.reply(f"**{cmd['desc']}**")
        return

    # 보고서 조회
    if cmd["type"] == "report":
        reports = read_reports(3)
        await message.reply(f"**최신 보고사항:**\n\n{reports}")
        return

    # 스크립트 실행
    if cmd["type"] == "script":
        # 실행 시작 알림
        embed = discord.Embed(
            title="🚀 실행 시작",
            description=cmd["desc"],
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="스크립트", value=f"`{cmd['args'][0]}`", inline=False)
        start_msg = await message.reply(embed=embed)

        # 백그라운드에서 실행
        result = await run_script(cmd["args"])

        # 결과 알림
        if result.startswith("✅"):
            color = discord.Color.green()
        else:
            color = discord.Color.red()

        result_embed = discord.Embed(
            title="✅ 실행 완료" if result.startswith("✅") else "❌ 실행 실패",
            description=result,
            color=color,
            timestamp=datetime.now(),
        )

        await start_msg.reply(embed=result_embed)


def main():
    if not DISCORD_BOT_TOKEN:
        print("❌ 에러: DISCORD_BOT_TOKEN이 .env에 설정되지 않았습니다.")
        print("   Discord Developer Portal에서 봇 토큰을 얻고 .env에 추가하세요.")
        return

    print("🤖 디스코드 봇 시작...")
    print(f"   리안 ID: {DISCORD_LIAN_USER_ID or '(미설정 — 모든 사용자 허용)'}")
    print(f"   채널 ID: {DISCORD_CHANNEL_ID or '(미설정 — 모든 채널)'}")
    print()

    try:
        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ 봇 실행 실패: {e}")


if __name__ == "__main__":
    main()
