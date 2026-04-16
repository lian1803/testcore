"""
디스코드 봇 패턴 매칭 테스트

사용법:
  python test_discord_bot.py
"""

import discord_bot
import sys
import json
from pathlib import Path

# Windows UTF-8 인코딩
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def test_patterns():
    """패턴 매칭 테스트"""
    test_cases = [
        # (입력, 기대 명령 타입, 설명)
        ("이사팀 AI 이력서 생성 서비스", "script", "이사팀 명령"),
        ("AI 이력서 자동 생성 해볼까", "script", "해볼까 패턴"),
        ("영업 우리 SaaS 제품 피칭 자료", "script", "영업팀 명령"),
        ("납품 블로그 SEO 콘텐츠", "script", "납품팀 명령"),
        ("마케팅 인스타그램 광고 전략", "script", "마케팅팀 명령"),
        ("오프라인 서울 강남 카페 방문", "script", "오프라인 명령"),
        ("데일리", "script", "데일리 명령"),
        ("daily", "script", "영어 데일리"),
        ("상태", "status", "상태 조회"),
        ("status", "status", "영어 상태"),
        ("보고", "report", "보고서 조회"),
        ("report", "report", "영어 보고서"),
        ("아무거나", None, "인식 안 하는 텍스트"),
        ("", None, "빈 텍스트"),
    ]

    print("=" * 70)
    print("디스코드 봇 패턴 매칭 테스트")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for text, expected_type, description in test_cases:
        result = discord_bot.match_command(text)
        result_type = result["type"] if result else None

        if result_type == expected_type:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"{status} | {description:20} | '{text}'")
        if result:
            print(f"       └─ 타입: {result['type']:10} | 설명: {result['desc']}")
        print()

    print("=" * 70)
    print(f"결과: {passed} 성공, {failed} 실패 / {len(test_cases)} 테스트")
    print("=" * 70)

    return failed == 0


def test_file_operations():
    """파일 작업 테스트"""
    print()
    print("=" * 70)
    print("파일 작업 테스트")
    print("=" * 70)
    print()

    LIAN_COMPANY = Path(__file__).parent

    # 상태 파일 테스트
    status_file = LIAN_COMPANY / ".agent_status.json"
    print(f"상태 파일: {status_file}")
    print(f"  존재: {status_file.exists()}")
    if status_file.exists():
        with open(status_file, "r") as f:
            status = json.load(f)
            print(f"  현재 태스크: {status.get('current_task', '없음')}")
    print()

    # 보고서 파일 테스트
    report_file = LIAN_COMPANY / "보고사항들.md"
    print(f"보고서: {report_file}")
    print(f"  존재: {report_file.exists()}")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = len(content.split("\n"))
            print(f"  줄 수: {lines}")
            print(f"  크기: {len(content)} 바이트")
    print()

    print("=" * 70)


def test_env():
    """환경변수 테스트"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    print()
    print("=" * 70)
    print("환경변수 검사")
    print("=" * 70)
    print()

    vars_to_check = [
        ("DISCORD_BOT_TOKEN", "봇 토큰"),
        ("DISCORD_LIAN_USER_ID", "리안 유저 ID"),
        ("DISCORD_CHANNEL_ID", "채널 ID"),
        ("ANTHROPIC_API_KEY", "Anthropic API"),
        ("OPENAI_API_KEY", "OpenAI API"),
    ]

    for var_name, description in vars_to_check:
        value = os.getenv(var_name, "")
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            status = "✅ 설정됨"
        else:
            masked = "(미설정)"
            status = "⚠️ 미설정"

        print(f"{status} | {description:20} | {masked}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    all_pass = test_patterns()
    test_file_operations()
    test_env()

    if all_pass:
        print()
        print("✅ 모든 테스트 통과!")
        print()
        print("다음 단계:")
        print("1. DISCORD_BOT_TOKEN을 .env에 설정")
        print("2. DISCORD_LIAN_USER_ID를 .env에 설정 (보안)")
        print("3. python discord_bot.py로 봇 실행")
        sys.exit(0)
    else:
        print()
        print("❌ 일부 테스트 실패. 위를 확인하세요.")
        sys.exit(1)
