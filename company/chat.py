"""
단톡방 — 리안 + 직원들 실시간 대화

사용법:
  python chat.py                     # 전체 참여 (시은/민수/하은/서윤/태호/준혁)
  python chat.py 서윤 민수 하은       # 지정 직원만
  python chat.py --topic "카톡 영업 전략"  # 주제 설정 후 시작

대화 중 명령어:
  @서윤 질문           → 서윤에게 직접
  @전체 질문           → 모두 순서대로 응답
  /토론 주제           → 찬반 자동 토론 시작
  /나가 서윤           → 서윤 퇴장
  /들어와 서윤         → 서윤 재참여
  /요약               → 지금까지 대화 요약 (시은이 담당)
  /끝                 → 대화 종료 + 결론 저장
"""

import sys
import os
import io
import importlib
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

# ── 직원 정보 ─────────────────────────────────────────────────────────────────

AGENTS = {
    "시은": {
        "module": "agents.sieun",
        "ai": "Claude Sonnet",
        "role": "오케스트레이터 · 아이디어 명확화",
        "emoji": "🎯",
        "needs_client": True,
    },
    "민수": {
        "module": "agents.minsu",
        "ai": "GPT-4o",
        "role": "전략 · 수익모델",
        "emoji": "📊",
        "needs_client": False,
    },
    "하은": {
        "module": "agents.haeun",
        "ai": "Gemini",
        "role": "팩트체크 · 반론",
        "emoji": "🔍",
        "needs_client": False,
    },
    "서윤": {
        "module": "agents.seoyun",
        "ai": "Perplexity",
        "role": "실시간 시장조사",
        "emoji": "🌐",
        "needs_client": False,
    },
    "태호": {
        "module": "agents.taeho",
        "ai": "Claude Haiku",
        "role": "트렌드 스카우팅",
        "emoji": "📡",
        "needs_client": True,
    },
    "준혁": {
        "module": "agents.junhyeok",
        "ai": "Claude Opus",
        "role": "GO/NO-GO 판단",
        "emoji": "⚖️",
        "needs_client": True,
    },
}

NAME_ALIASES = {
    "시은아": "시은", "민수야": "민수", "하은아": "하은",
    "서윤아": "서윤", "태호야": "태호", "준혁아": "준혁",
    "전체": "__all__",
}


# ── 클라이언트 ────────────────────────────────────────────────────────────────

def get_anthropic_client():
    import anthropic
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── 대화 이력 포맷 ─────────────────────────────────────────────────────────────

def format_history(history: list, last_n: int = 20) -> str:
    """최근 N개 대화를 텍스트로 포맷."""
    recent = history[-last_n:]
    lines = []
    for msg in recent:
        speaker = msg["speaker"]
        content = msg["content"]
        lines.append(f"[{speaker}]: {content}")
    return "\n".join(lines)


# ── 에이전트 응답 ──────────────────────────────────────────────────────────────

def ask_agent(name: str, message: str, history: list, client) -> str:
    """에이전트 한 명한테 대화 이력 + 메시지 전달해서 응답 받기."""
    info = AGENTS[name]

    # 대화 이력 포함한 컨텍스트
    history_text = format_history(history)
    full_task = f"""지금 단톡방에서 대화 중이야.

=== 지금까지 대화 ===
{history_text}

=== 리안의 질문/발언 ===
{message}

너는 {name}({info['role']})이야.
이 대화에 자연스럽게 참여해. 다른 직원이 한 말에 동의/반박/보완도 해도 돼.
짧고 핵심만. 단톡방이니까 자연스럽게."""

    try:
        agent_module = importlib.import_module(info["module"])
        context = {
            "idea": full_task,
            "clarified": full_task,
            "task": full_task,
            "agent_memory": "",
        }
        result = agent_module.run(context, client=client if info["needs_client"] else None)
        return result if result else "(응답 없음)"
    except Exception as e:
        return f"(오류: {e})"


# ── 토론 모드 ─────────────────────────────────────────────────────────────────

def run_debate(topic: str, participants: list, history: list, client, rounds: int = 2):
    """찬반 자동 토론. 민수(찬성)↔하은(반대), 또는 참가자 간 번갈아."""
    print(f"\n⚔️  토론 시작: '{topic}'")
    print(f"   참가자: {' vs '.join(participants[:2])}, {rounds}라운드")
    print("─" * 50)

    debate_history = history.copy()
    if len(participants) < 2:
        print("토론은 2명 이상 필요해.")
        return debate_history

    a, b = participants[0], participants[1]
    sides = {a: "찬성", b: "반대"}

    for r in range(1, rounds + 1):
        for name, side in sides.items():
            if name not in AGENTS:
                continue
            prompt = f"토론 주제: '{topic}'\n너의 입장: {side}\n상대 주장에 반박하거나 네 주장을 강화해. 3문장 이내."
            response = ask_agent(name, prompt, debate_history, client)
            emoji = AGENTS[name]["emoji"]
            print(f"\n{emoji} {name} ({side}, {r}라운드):")
            print(f"  {response}")
            debate_history.append({"speaker": name, "content": f"[토론/{side}] {response}"})

    # 시은이 결론 정리
    if "시은" in AGENTS:
        conclusion = ask_agent("시은", f"위 토론 '{topic}'의 핵심 합의점과 결론을 3줄로 정리해줘.", debate_history, client)
        print(f"\n🎯 시은 (토론 결론):")
        print(f"  {conclusion}")
        debate_history.append({"speaker": "시은", "content": f"[토론 결론] {conclusion}"})

    return debate_history


# ── 메인 루프 ─────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="단톡방")
    parser.add_argument("members", nargs="*", help="참여 직원 이름 (없으면 전체)")
    parser.add_argument("--topic", "-t", default="", help="초기 주제")
    args = parser.parse_args()

    # 참여 직원 결정
    if args.members:
        active = []
        for m in args.members:
            canonical = NAME_ALIASES.get(m, m)
            if canonical in AGENTS:
                active.append(canonical)
            else:
                print(f"⚠️  '{m}' 없음, 스킵")
    else:
        active = list(AGENTS.keys())

    # Claude 클라이언트
    try:
        client = get_anthropic_client()
    except Exception:
        client = None

    # 헤더
    print("\n" + "=" * 60)
    print("💬  단톡방 — 리안컴퍼니")
    print("=" * 60)
    print("참여자:", "  ".join(f"{AGENTS[n]['emoji']}{n}" for n in active))
    print("\n명령어: @이름 질문 | /토론 주제 | /요약 | /나가 이름 | /끝")
    print("─" * 60)

    history = []
    topic = args.topic

    # 주제 있으면 시은이 먼저 오프닝
    if topic and "시은" in active:
        opening = ask_agent("시은", f"오늘 주제는 '{topic}'이야. 간단하게 오프닝 해줘.", history, client)
        print(f"\n🎯 시은: {opening}")
        history.append({"speaker": "시은", "content": opening})

    # 대화 루프
    while True:
        try:
            user_input = input("\n리안: ").strip()
        except (EOFError, KeyboardInterrupt):
            user_input = "/끝"

        if not user_input:
            continue

        history.append({"speaker": "리안", "content": user_input})

        # ── /명령어 처리 ──────────────────────────────────────────
        if user_input.startswith("/끝") or user_input.startswith("/종료"):
            # 시은이 전체 요약 후 저장
            if "시은" in active:
                summary = ask_agent("시은", "오늘 대화 전체를 핵심 3가지로 요약해줘. 결정된 것, 아직 열린 것, 다음 할 것.", history, client)
                print(f"\n🎯 시은 (마무리):\n{summary}")
                history.append({"speaker": "시은", "content": f"[마무리 요약] {summary}"})
            # 저장
            _save_session(history, topic)
            print("\n대화 저장 완료. 다음에 봐!")
            break

        elif user_input.startswith("/요약"):
            summarizer = "시은" if "시은" in active else active[0]
            summary = ask_agent(summarizer, "지금까지 대화 핵심을 3줄로 요약해줘.", history, client)
            print(f"\n🎯 {summarizer} (요약):\n{summary}")
            history.append({"speaker": summarizer, "content": f"[요약] {summary}"})

        elif user_input.startswith("/토론"):
            topic_part = user_input[3:].strip() or "현재 주제"
            debaters = [n for n in ["민수", "하은"] if n in active]
            if len(debaters) < 2:
                debaters = active[:2]
            history = run_debate(topic_part, debaters, history, client)

        elif user_input.startswith("/나가 "):
            name = user_input[4:].strip()
            canonical = NAME_ALIASES.get(name, name)
            if canonical in active:
                active.remove(canonical)
                print(f"👋 {canonical} 퇴장")
            else:
                print(f"'{name}' 현재 없어")

        elif user_input.startswith("/들어와 "):
            name = user_input[5:].strip()
            canonical = NAME_ALIASES.get(name, name)
            if canonical in AGENTS and canonical not in active:
                active.append(canonical)
                print(f"✅ {canonical} 입장")
            else:
                print(f"'{name}' 이미 있거나 없는 직원")

        # ── @멘션 처리 ────────────────────────────────────────────
        elif user_input.startswith("@"):
            parts = user_input.split(" ", 1)
            mention = parts[0][1:]  # @ 제거
            message = parts[1] if len(parts) > 1 else user_input

            canonical = NAME_ALIASES.get(mention, mention)

            if canonical == "__all__":
                # @전체 → 모두 순서대로 응답
                for name in active:
                    response = ask_agent(name, message, history, client)
                    emoji = AGENTS[name]["emoji"]
                    print(f"\n{emoji} {name}: {response}")
                    history.append({"speaker": name, "content": response})

            elif canonical in AGENTS:
                if canonical not in active:
                    active.append(canonical)
                    print(f"(📥 {canonical} 호출됨)")
                response = ask_agent(canonical, message, history, client)
                emoji = AGENTS[canonical]["emoji"]
                print(f"\n{emoji} {canonical}: {response}")
                history.append({"speaker": canonical, "content": response})
            else:
                print(f"'{mention}' 없는 직원")

        # ── 일반 메시지 → 자동 라우팅 ────────────────────────────
        else:
            # 시은이 먼저 누가 답해야 할지 판단
            responders = _auto_route(user_input, active, history, client)
            for name in responders:
                response = ask_agent(name, user_input, history, client)
                emoji = AGENTS[name]["emoji"]
                print(f"\n{emoji} {name}: {response}")
                history.append({"speaker": name, "content": response})


def _auto_route(message: str, active: list, history: list, client) -> list:
    """메시지 내용 보고 누가 답할지 자동 결정 (시은이 판단)."""
    keyword_map = {
        "시장": ["서윤"],
        "조사": ["서윤"],
        "트렌드": ["태호"],
        "전략": ["민수"],
        "수익": ["민수"],
        "팩트": ["하은"],
        "맞아": ["하은"],
        "GO": ["준혁"],
        "판단": ["준혁"],
        "요약": ["시은"],
        "정리": ["시은"],
    }

    # 키워드 매칭
    for kw, names in keyword_map.items():
        if kw in message:
            matched = [n for n in names if n in active]
            if matched:
                return matched

    # 짧은 질문 → 시은이 단독
    if len(message) < 20 and "시은" in active:
        return ["시은"]

    # 기본: active 중 앞 2명 (과부하 방지)
    return active[:2]


def _save_session(history: list, topic: str):
    """대화 이력 저장."""
    from datetime import datetime
    save_dir = ROOT / "knowledge" / "teams" / "단톡방"
    save_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = save_dir / f"{timestamp}_{topic[:20] if topic else '대화'}.md"

    lines = [f"# 단톡 세션 — {topic or '자유 대화'}", f"일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for msg in history:
        lines.append(f"**{msg['speaker']}**: {msg['content']}")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n💾 저장: {filename}")


if __name__ == "__main__":
    main()
