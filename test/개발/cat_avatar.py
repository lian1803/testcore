#!/usr/bin/env python3
"""
고양이 터미널 아바타 — Claude Code 관상용
스페이스/엔터: 상호작용  |  q: 종료
"""

import sys
import os
import time
import random
import threading
import msvcrt  # Windows 전용

# ANSI 코드
CLEAR = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# 색상
R = "\033[0m"          # 리셋
YELLOW = "\033[93m"    # 고양이 색
PINK = "\033[95m"      # 하이라이트
CYAN = "\033[96m"      # 테두리
GRAY = "\033[90m"      # 힌트
WHITE = "\033[97m"     # 텍스트
GREEN = "\033[92m"     # 상태

# 고양이 표정
CATS = {
    "idle": [
        "  /\\_/\\  ",
        " ( ^.^ ) ",
        "  > ~ <  ",
    ],
    "blink": [
        "  /\\_/\\  ",
        " ( -.- ) ",
        "  > ~ <  ",
    ],
    "happy": [
        "  /\\_/\\  ",
        " ( ◕‿◕) ",
        "  > ♪ <  ",
    ],
    "surprised": [
        "  /\\_/\\  ",
        " ( °o° ) ",
        "  > !! < ",
    ],
    "sleepy": [
        "  /\\_/\\  ",
        " ( zzZ ) ",
        "  > ～ <  ",
    ],
    "love": [
        "  /\\_/\\  ",
        " ( ♥.♥ ) ",
        "  > ~ <  ",
    ],
    "angry": [
        "  /\\_/\\  ",
        " ( ÒwÓ ) ",
        "  > ! <  ",
    ],
    "thinking": [
        "  /\\_/\\  ",
        " ( o.? ) ",
        "  > ... < ",
    ],
}

MESSAGES = {
    "idle":      ["...", "냐옹", ""],
    "happy":     ["냐옹~!", "같이 놀자!", "반가워!", "최고야!"],
    "surprised": ["!?", "헉!", "뭐야뭐야?", "갑자기!"],
    "sleepy":    ["...zzz", "졸려...", "5분만...", "으으..."],
    "love":      ["냥 ♥", "좋아~", "냐옹♥", "최고야!"],
    "angry":     ["야옹!", "건들지마!", "냥냥!", "흥!"],
    "thinking":  ["음...", "생각중...", "그게 뭐지?", "흠흠..."],
}

state = {
    "mood": "idle",
    "msg": "안녕! 나는 클로드 냥이야~",
    "running": True,
}


def draw():
    os.system("cls")
    cat = CATS[state["mood"]]
    msg = state["msg"]
    mood = state["mood"]

    border_top    = CYAN + "╭─────────────────╮" + R
    border_bot    = CYAN + "╰─────────────────╯" + R
    border_mid    = CYAN + "│" + R
    empty_line    = CYAN + "│                 │" + R

    print()
    print("  " + border_top)
    print("  " + border_mid + YELLOW + cat[0] + R + border_mid)
    print("  " + border_mid + YELLOW + cat[1] + R + border_mid)
    print("  " + border_mid + YELLOW + cat[2] + R + border_mid)
    print("  " + empty_line)
    # 메시지 라인 (최대 17자)
    msg_display = msg[:17].center(17)
    print("  " + border_mid + PINK + msg_display + R + border_mid)
    print("  " + border_bot)
    print()
    print("  " + GRAY + "[ 스페이스: 상호작용  |  q: 종료 ]" + R)
    print()


def set_mood(mood, msg=None):
    state["mood"] = mood
    if msg:
        state["msg"] = msg
    else:
        state["msg"] = random.choice(MESSAGES[mood])
    draw()


def idle_loop():
    """배경 루프 — 눈 깜빡임 + 랜덤 표정"""
    blink_counter = 0
    idle_counter = 0

    while state["running"]:
        time.sleep(0.5)
        blink_counter += 1
        idle_counter += 1

        # 6초마다 눈 깜빡임
        if blink_counter >= 12 and state["mood"] in ("idle",):
            state["mood"] = "blink"
            state["msg"] = "..."
            draw()
            time.sleep(0.15)
            state["mood"] = "idle"
            state["msg"] = random.choice(MESSAGES["idle"])
            draw()
            blink_counter = 0

        # 20초마다 랜덤 아이들 표정
        if idle_counter >= 40 and state["mood"] in ("idle", "blink"):
            mood = random.choice(["sleepy", "thinking", "idle"])
            set_mood(mood)
            time.sleep(2)
            set_mood("idle")
            idle_counter = 0


def interact():
    """스페이스/엔터 입력 → 랜덤 표정"""
    moods = ["happy", "surprised", "love", "angry", "thinking"]
    mood = random.choice(moods)
    set_mood(mood)
    time.sleep(2.5)
    set_mood("idle")


def main():
    # Windows ANSI 활성화
    os.system("color")

    print(HIDE_CURSOR, end="", flush=True)
    draw()

    # 배경 루프 시작
    t = threading.Thread(target=idle_loop, daemon=True)
    t.start()

    try:
        while state["running"]:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b" ", b"\r", b"\n"):
                    interact()
                elif key in (b"q", b"Q"):
                    state["running"] = False
            time.sleep(0.05)
    finally:
        print(SHOW_CURSOR, end="", flush=True)
        os.system("cls")
        print(YELLOW + "\n  냐옹~ 또 봐! ♥\n" + R)


if __name__ == "__main__":
    main()
