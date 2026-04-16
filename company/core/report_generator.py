"""
report_generator.py — 이사팀 완료 후 1장짜리 보고서 생성

리안이 이것만 보면 모든 판단을 할 수 있어야 한다.
"""
import os
from datetime import datetime


def generate_board_report(context: dict) -> str:
    """이사팀 결과를 1장짜리 보고서로 정리."""

    idea = context.get("idea", "")
    clarified = context.get("clarified", "")
    verdict = context.get("verdict", "???")
    score = context.get("score", "???")
    is_commercial = context.get("is_commercial", False)
    is_software = context.get("is_software", False)
    autopilot = context.get("autopilot", False)

    # 각 에이전트 결과 요약 (앞 500자만)
    taeho = context.get("taeho", "")[:500]
    seoyun = context.get("seoyun", "")[:800]
    minsu = context.get("minsu", "")[:800]
    haeun = context.get("haeun", "")[:500]
    junhyeok_text = context.get("junhyeok_text", "")[:500]
    big_picture = context.get("big_picture", "")[:500]

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = "자동파일럿" if autopilot else "대화형"
    proj_type = "상용화" if is_commercial else "개인 툴"
    dev_type = "소프트웨어" if is_software else "비소프트웨어"

    report = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  이사팀 분석 보고서
  {date_str} | {mode} | {proj_type} | {dev_type}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ 아이디어
{idea}

■ 명확화 결과
{clarified[:600]}

■ 트렌드 (태호)
{taeho}

■ 시장조사 (서윤)
{seoyun}

■ 전략 (민수)
{minsu}

■ 리스크 (하은)
{haeun}

■ 최종 판단 (준혁)
판정: {verdict} | 점수: {score}
{junhyeok_text}
"""

    if big_picture:
        report += f"""
■ 큰그림 체크 (시은)
{big_picture}
"""

    # 다음 단계
    if verdict == "GO":
        report += """
■ 다음 단계
→ 팀 설계 + 교육팀 자동 생성 예정
→ 리안 컨펌 후 진행

리안 판단: [진행 / 수정사항 말해줘 / 접어]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    elif verdict == "CONDITIONAL_GO":
        report += """
■ 다음 단계
→ 조건부 GO — 위 조건 확인 후 진행 가능
→ 리안 컨펌 필요

리안 판단: [조건 OK 진행 / 수정사항 말해줘 / 접어]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        report += """
■ 결론
→ NO-GO. 위 이유 참고.
→ 방향 수정 후 다시 돌릴 수 있음.

리안 판단: [수정해서 다시 / 접어]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return report


def save_report_to_보고사항(report: str, project_name: str):
    """보고사항들.md 맨 위에 보고서 추가."""
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "보고사항들.md"
    )

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"\n## 이사팀 보고 ({project_name}) — {date_str}\n\n"

    try:
        existing = ""
        if os.path.exists(report_path):
            with open(report_path, encoding="utf-8") as f:
                existing = f.read()

        # 첫 번째 --- 뒤에 삽입 (헤더 유지)
        if "---" in existing:
            parts = existing.split("---", 1)
            new_content = parts[0] + "---\n" + header + report + "\n---\n" + parts[1]
        else:
            new_content = existing + "\n" + header + report

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"\n📋 보고서 → 보고사항들.md 저장 완료")
    except Exception as e:
        print(f"\n⚠️ 보고서 저장 실패: {e}")
