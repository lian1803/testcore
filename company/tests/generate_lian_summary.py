#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""리안용 한 장 요약 생성기.

13개 기술 문서 → 프레임워크 용어 없는 1페이지 의사결정 문서로 재작성.
Claude Haiku로 전체 파이프라인 output을 읽고 "리안이 바로 이해할 수 있는 언어"로 재작성.

사용법:
    python -m tests.generate_lian_summary outputs/2026-04-13_xxx
    python -m tests.generate_lian_summary --all    # 모든 output
    python -m tests.generate_lian_summary --latest # 최신
"""
import os
import sys
import io
import json
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv()

import anthropic


SYSTEM_PROMPT = """너는 리안 컴퍼니의 "통역사"야.

기획팀이 만든 기술 문서(JTBD, Customer Forces Canvas, CAC/LTV, 5-Layer 역기획, Payback, Gross Margin 등 온갖 용어로 가득)를
**리안 사장님이 바로 이해할 수 있는 평범한 한국말**로 다시 써.

리안은 사업에 똑똑하지만 비개발자·비MBA야. 프레임워크 용어 금지.
각 섹션은 **짧고 구체적으로**. 한 섹션당 3~5줄 이내. 뜬구름 금지, 숫자·이름·경로 구체적으로.

=== 출력 형식 (정확히 이 순서, 17개 섹션 전부) ===

## 📋 1. 한 줄 설명
[한 문장. 친구한테 설명하듯. 예: "1인 카페 사장 인스타 글을 AI가 대신 써주는 월 3만원짜리 서비스"]

## 🧭 2. 사업 성격 분류
**유형**: [현금창출형 / 엑싯형 / 하이브리드 중 하나 선택]

- **현금창출형**이면: 매달 꾸준한 순이익 목표. 월 예상 순이익 + 손익분기 시점 명시.
- **엑싯형**이면: N년 후 매각/IPO. 예상 밸류에이션 + exit 시점 명시. (상세는 15번 섹션에서)
- **하이브리드**면: 둘 다 가능. 초기 현금창출 → 중장기 엑싯 경로 한 줄.

분류 근거 한 줄.

## 🎯 3. 누구한테 팔 건가
구체적 페르소나 1~2개. 직업/나이/월 매출/상황까지:
- [페르소나 1]: 직업 / 나이 / 상황
- [페르소나 2]: ...

## 💢 4. 진짜 고통 (3~5개)
구체적으로 3~5개. 각각 "지금 어떻게 버티는지 + 시간/돈 얼마나 드는지":
- **[고통 1]**: [구체적 상황] → 지금 [임시방편] 사용 → 월 [시간/돈] 씀
- **[고통 2]**: ...
- **[고통 3]**: ...

## 💰 5. 얼마에 팔까
| 플랜 | 가격 | 타겟 | 이유 |
|------|------|------|------|
| 기본 | | | |
| 프로 | | | |
| 엔터 | | | |

## 🏆 6. 왜 이길 수 있나
기존 경쟁사가 **못 하는 것** 3가지 (구체적으로):
1. [경쟁사 X는 Y 못 함] ← 우리는 Z로 해결
2. ...
3. ...

## 🔧 7. 회사 자산 활용도
**활용도 점수**: ?/10 (0=전혀 못 씀, 10=기존 자산이 핵심 무기)

기존 리안 컴퍼니 자산 중 어떤 걸 쓰나?
- [온라인팀 / naver-diagnosis / CRM / 디자인팀 / 마케팅팀 / 오프라인 영업 / ...]: 어떻게 쓸 건가 한 줄

활용도 3점 이하면: **왜 그래도 할 가치 있나?**

## 📅 8. 언제 뭐가 보일까
- **1개월**: [구체적 마일스톤]
- **3개월**: 고객 N명, 월 매출 M원
- **6개월**: [성장 단계 + 숫자]
- **1년**: [안정 단계 + 숫자]
- **3년**: [확장 또는 Exit 준비]

## 💵 9. 돈 계산
- **초기 필요 자본**: 약 ?원 (출시 전까지)
- **추가 투자 (6개월 내)**: 약 ?원
- **고객 1명 데려오는 데**: 약 ?원
- **고객 1명이 1년간 내는 돈**: 약 ?원
- **손익분기**: N개월 후
- **1년 목표**: 고객 N명, 월 매출 M원
- **3년 목표**: 고객 N명, 월 매출 M원

## ⏰ 10. 시간 투입 (리안 주당)
- **초기 (1~3개월)**: 주당 X시간
- **중기 (3~12개월)**: 주당 Y시간
- **장기 (1년+)**: 주당 Z시간 (자동화/위임 후)
- **개입 유형**: [핵심 의사결정만 / 실무 일부 / 실무 전면] 중 하나

## 🚪 11. 첫 고객 확보 경로 (구체적)
이론 금지. "페이스북 광고" / "SEO" / "바이럴" 같은 뜬구름 금지.
- **첫 5명**: [구체적 경로 — 리안 기존 지인 A/B, 특정 네이버 카페 C, 오픈채팅방 D 등]
- **다음 50명**: [구체적 확장 경로]
- **다음 500명**: [반복 가능 채널]

## ⚠️ 12. 가장 큰 리스크 3가지 + 망하면 잃는 것
- **리스크 1**: [뭐가 위험] → 대응: [구체적]
- **리스크 2**: ...
- **리스크 3**: ...

**망하면 잃는 것 (한 줄)**: 약 [돈 X원] + [시간 Y개월] + [기회비용 Z]

## 🔥 13. 가장 어려운 1가지 (Hard Part)
이 사업에서 **딱 하나 못 넘으면 다 무의미**한 핵심 난관.

[한 문장으로 명확히] — 이걸 넘기 위한 **첫 행동** 한 줄.

## 🚨 14. 피벗 신호 (언제 접을지)
- **3개월 시점**: [이 숫자 안 나오면 접어라. 예: "유료 전환 3명 미만"]
- **6개월 시점**: [이 숫자 안 나오면 접어라. 예: "월 매출 500만원 미만"]
- **사전 약속**: 이 신호 보면 감정 배제하고 접기. 매몰비용 무시.

## 🏁 15. 출구 전략 (Exit)
(2번 섹션 분류에 따라)

**현금창출형**이면: "해당없음. 매년 순이익 배당."

**엑싯형/하이브리드**면:
- 언제: 약 N년 후
- 어떻게: M&A / IPO / Secondary / 프라이빗
- 누구한테 팔 가능성: **구체적 인수자 후보 3개** (진짜 기업명으로)
- 예상 금액: 약 X억 ~ Y억원

## 🚀 16. 내일부터 뭐 할까
리안이 내일 당장 할 수 있는 **구체적 행동** 3~5개:
1. [구체적]
2. ...
3. ...

## 🧭 17. 준혁의 한 줄 판정
**판정**: [GO / 조건부 GO / NO-GO] ([점수]/10)

**한 줄 이유**: [왜 이 판정인지 한 문장]

---

=== 작성 원칙 ===
- **용어 금지**: JTBD, Customer Forces, Canvas, CAC, LTV, Payback, Gross Margin, Churn, ARPU, PMF, TAM/SAM/SOM, 5-Layer, Push/Pull/Inertia/Anxiety, MVP, MRR, NPS — 전부 평범한 말로 풀기
- **모든 숫자 명시**: 추정이어도 "약 X" 형식으로. "적당히", "충분히", "많이" 같은 모호한 말 금지
- **구체적 이름 사용**: 경쟁사명, 인수자 후보 기업명, 네이버 카페 이름, 리안의 기존 자산명 등 구체적으로
- **의사결정 가능성**: 리안이 읽고 "내일 이거부터 하자" 또는 "이건 접자"가 나와야 함
- 각 섹션 짧게 (3~5줄). 전체를 1-2 스크롤에 다 보일 정도로
- 중요한 건 빠뜨리지 마. 리안이 이 한 장으로 의사결정할 수 있어야 함"""


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def extract_idea_title(folder: Path) -> str:
    name = folder.name
    match = re.match(r'\d{4}-\d{2}-\d{2}_\d{6}_(.*)', name)
    if match:
        return match.group(1).rstrip('_').replace('_', ' ')
    return name


def generate_summary(folder: Path, client: anthropic.Anthropic) -> Path:
    idea_title = extract_idea_title(folder)

    minsu = read_file(folder / "02_전략_민수.md")
    haeun = read_file(folder / "03_검증_하은.md")
    seoyun = read_file(folder / "01_시장조사_서윤.md")
    jihun = read_file(folder / "05_PRD_지훈.md")

    junhyeok_path = folder / "04_최종판단_준혁.json"
    junhyeok_text = ""
    verdict = "UNKNOWN"
    score = 0.0
    if junhyeok_path.exists():
        try:
            data = json.loads(junhyeok_path.read_text(encoding="utf-8"))
            junhyeok_text = data.get("text", "")
            verdict = data.get("verdict", "UNKNOWN")
            score = float(data.get("score", 0))
        except Exception:
            pass

    content = f"""아이디어: {idea_title}

[준혁 최종 판정]
verdict: {verdict}
score: {score}
{junhyeok_text[:3000]}

[민수 전략 — 가장 중요]
{minsu}

[서윤 시장조사 — Pain Point + 경쟁사]
{seoyun[:6000]}

[하은 검증·반론]
{haeun[:3000]}

[지훈 PRD — 제품 기획]
{jihun[:3000]}

위 내용을 기반으로 리안 사장님용 한 장 요약을 작성해. 프레임워크 용어 전부 빼고."""

    print(f"\n📝 {idea_title[:40]}... 요약 생성 중")

    full_response = ""
    try:
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
            temperature=0.4,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
    except Exception as e:
        print(f"  ❌ Claude 호출 실패: {e}")
        return None

    output_path = folder / "00_리안_한장요약.md"
    output_path.write_text(full_response, encoding="utf-8")
    return output_path


def main():
    outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
    if not outputs_dir.exists():
        print(f"❌ outputs 폴더 없음: {outputs_dir}")
        sys.exit(1)

    all_dirs = sorted(
        [d for d in outputs_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        targets = all_dirs
    elif len(sys.argv) > 1 and sys.argv[1] == "--latest":
        targets = [all_dirs[0]] if all_dirs else []
    elif len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if not p.is_absolute():
            p = outputs_dir / p.name
        targets = [p]
    else:
        targets = [all_dirs[0]] if all_dirs else []

    if not targets:
        print("❌ 타겟 없음")
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 없음")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    generated = []
    for folder in targets:
        try:
            out = generate_summary(folder, client)
            if out:
                generated.append(out)
                print(f"  ✅ → {out.name}")
        except Exception as e:
            print(f"  ❌ {folder.name}: {e}")

    print(f"\n총 {len(generated)}개 리안 요약 생성 완료")


if __name__ == "__main__":
    main()
