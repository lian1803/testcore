#!/usr/bin/env python3
"""
고양이 플로팅 아바타 v2 — 움직이고 귀엽게
클릭: 표정변화  |  드래그: 이동  |  우클릭: 종료
"""

import tkinter as tk
import random
import time
import threading
import math

# ── 고양이 프레임 정의 ─────────────────────────────────────────
# (표정, 꼬리) 쌍으로 관리

BODY = {
    "idle":      [" (^･ω･^) ", " (^･ω･^) "],
    "blink":     [" (-･ω･-) ", " (-･ω･-) "],
    "happy":     [" (◕‿◕✿) ", " (◕‿◕✿) "],
    "love":      [" (♥ω♥✿) ", " (♥ω♥✿) "],
    "surprised": [" (°o°；)  ", " (°o°；)  "],
    "angry":     [" (ÒwÓ)   ", " (ÒwÓ)   "],
    "sleepy":    [" (－ω－) zzz", " (－ω－) zzz"],
    "thinking":  [" (・ω・?) ", " (・ω・?) "],
    "walk1":     [" (^･ω･^) ", " (^･ω･^) "],
    "walk2":     [" (^･ω･^) ", " (^･ω･^) "],
    "jump":      [" (^･ω･^) ", " (^･ω･^) "],
    "stretch":   [" (=･ω･=) ", " (=･ω･=) "],
}

# 꼬리 애니메이션 2프레임
TAIL = ["ﾉ", "ﾉ~"]

# 발 애니메이션
FEET = {
    "idle":   "  ⌒⌒  ",
    "walk1":  " ₍ᐢ ᐢ₎ ",
    "walk2":  " ₍ᐣ ᐣ₎ ",
    "jump":   "   ↑↑   ",
    "sleep":  "  zzz   ",
}

# 전체 프레임 빌더
def make_frame(mood, tail_idx, extra=""):
    top  = "  ∧＿∧  "
    body = BODY.get(mood, BODY["idle"])[0]
    tail = f" つ{TAIL[tail_idx % 2]}"
    feet = FEET.get(mood, FEET["idle"])
    return f"{top}\n{body}\n{tail}\n{feet}\n{extra}"

MESSAGES = {
    "idle":      ["", "냥~", "..."],
    "happy":     ["냥냥~!", "최고야!", "같이 놀자!"],
    "love":      ["냥 ♥", "좋아~", "♥♥♥"],
    "surprised": ["!?", "헉!", "뭐야뭐야?"],
    "sleepy":    ["zzz...", "졸려...", "5분만..."],
    "angry":     ["야옹!", "건들지마!", "흥!"],
    "thinking":  ["음...", "생각중...", "흠흠..."],
    "walk1":     ["어디가지~", "산책이다!", "냐~"],
    "stretch":   ["기지개~", "으으~", "스트레칭!"],
    "jump":      ["점프!", "냐앗!", "whoosh!"],
}

COLORS = {
    "idle":      "#FFD700",
    "blink":     "#FFD700",
    "happy":     "#FF69B4",
    "love":      "#FF1493",
    "surprised": "#FF8C00",
    "sleepy":    "#9370DB",
    "angry":     "#FF4500",
    "thinking":  "#00CED1",
    "walk1":     "#90EE90",
    "walk2":     "#90EE90",
    "jump":      "#00FF7F",
    "stretch":   "#87CEEB",
}


class CatAvatar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.93)
        self.root.config(bg="#0d0d1a")

        self.mood = "idle"
        self.tail_idx = 0
        self.running = True
        self._drag_x = 0
        self._drag_y = 0
        self._moved = False

        # 초기 위치
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.win_w = 170
        self.win_h = 160
        self.pos_x = sw - self.win_w - 20
        self.pos_y = sh - self.win_h - 60
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.pos_x}+{self.pos_y}")

        self._build_ui()
        self._bind_events()

        # 배경 루프 시작
        threading.Thread(target=self._main_loop, daemon=True).start()

        self.root.mainloop()

    # ── UI 빌드 ────────────────────────────────────────────────
    def _build_ui(self):
        self.frame = tk.Frame(
            self.root, bg="#0d0d1a",
            highlightbackground="#5533ff",
            highlightthickness=2,
        )
        self.frame.pack(fill="both", expand=True, padx=3, pady=3)

        self.cat_label = tk.Label(
            self.frame,
            text=make_frame("idle", 0),
            font=("Consolas", 11, "bold"),
            fg=COLORS["idle"],
            bg="#0d0d1a",
            justify="center",
            pady=2,
        )
        self.cat_label.pack(fill="both", expand=True)

        self.msg_label = tk.Label(
            self.frame,
            text="안녕~ 나는 냥이야 ♥",
            font=("Malgun Gothic", 8),
            fg="#aaaaff",
            bg="#0d0d1a",
        )
        self.msg_label.pack()

        hint = tk.Label(
            self.frame,
            text="클릭•드래그•우클릭:종료",
            font=("Malgun Gothic", 7),
            fg="#333355",
            bg="#0d0d1a",
        )
        hint.pack(pady=(0, 3))

    # ── 이벤트 ─────────────────────────────────────────────────
    def _bind_events(self):
        for w in (self.root, self.frame, self.cat_label, self.msg_label):
            w.bind("<ButtonPress-1>",   self._on_press)
            w.bind("<B1-Motion>",       self._on_drag)
            w.bind("<ButtonRelease-1>", self._on_release)
            w.bind("<Button-3>",        self._quit)

    def _on_press(self, e):
        self._drag_x = e.x_root - self.root.winfo_x()
        self._drag_y = e.y_root - self.root.winfo_y()
        self._moved = False

    def _on_drag(self, e):
        self._moved = True
        self.pos_x = e.x_root - self._drag_x
        self.pos_y = e.y_root - self._drag_y
        self.root.geometry(f"+{self.pos_x}+{self.pos_y}")

    def _on_release(self, e):
        if not self._moved:
            self._interact()

    def _quit(self, e=None):
        self.running = False
        self.root.destroy()

    # ── 표정 변경 ──────────────────────────────────────────────
    def _set_mood(self, mood, msg=None):
        self.mood = mood
        if msg is None:
            msg = random.choice(MESSAGES.get(mood, [""]))
        color = COLORS.get(mood, "#FFD700")
        frame = make_frame(mood, self.tail_idx)
        self.cat_label.config(text=frame, fg=color)
        self.msg_label.config(text=msg)

    def _interact(self):
        moods = ["happy", "surprised", "love", "angry", "thinking", "stretch", "jump"]
        mood = random.choice(moods)
        self.root.after(0, lambda: self._set_mood(mood))
        # jump면 실제로 튀어오르기
        if mood == "jump":
            threading.Thread(target=self._do_jump, daemon=True).start()
        self.root.after(2500, lambda: self._set_mood("idle"))

    # ── 점프 모션 ──────────────────────────────────────────────
    def _do_jump(self):
        orig_y = self.pos_y
        for i in range(12):
            if not self.running:
                return
            dy = int(-math.sin(i / 11 * math.pi) * 40)
            self.root.after(0, lambda y=orig_y + dy: self.root.geometry(f"+{self.pos_x}+{y}"))
            time.sleep(0.04)
        self.pos_y = orig_y
        self.root.after(0, lambda: self.root.geometry(f"+{self.pos_x}+{self.pos_y}"))

    # ── 걷기 모션 ──────────────────────────────────────────────
    def _do_walk(self, target_x, target_y):
        steps = 40
        start_x, start_y = self.pos_x, self.pos_y
        dx = (target_x - start_x) / steps
        dy = (target_y - start_y) / steps

        for i in range(steps):
            if not self.running or self.mood not in ("walk1", "walk2"):
                break
            walk = "walk1" if i % 2 == 0 else "walk2"
            self.mood = walk
            nx = int(start_x + dx * i)
            ny = int(start_y + dy * i)
            self.pos_x, self.pos_y = nx, ny
            self.root.after(0, lambda x=nx, y=ny: self.root.geometry(f"+{x}+{y}"))
            self.root.after(0, lambda m=walk: self._set_mood(m, random.choice(MESSAGES["walk1"])))
            time.sleep(0.045)

        self.pos_x, self.pos_y = target_x, target_y
        self.root.after(0, lambda: self.root.geometry(f"+{target_x}+{target_y}"))

    # ── 메인 배경 루프 ─────────────────────────────────────────
    def _main_loop(self):
        blink_tick = 0
        event_tick = 0

        while self.running:
            time.sleep(0.4)
            blink_tick += 1
            event_tick += 1

            # 꼬리 흔들기 (항상)
            self.tail_idx += 1
            if self.mood in ("idle", "blink", "thinking", "sleepy"):
                frame = make_frame(self.mood, self.tail_idx)
                self.root.after(0, lambda f=frame: self.cat_label.config(text=f))

            # 4초마다 눈 깜빡임
            if blink_tick >= 10 and self.mood == "idle":
                self.root.after(0, lambda: self._set_mood("blink", "..."))
                time.sleep(0.18)
                self.root.after(0, lambda: self._set_mood("idle", ""))
                blink_tick = 0

            # 12초마다 랜덤 이벤트
            if event_tick >= 30:
                event_tick = 0
                event = random.choice(["walk", "walk", "stretch", "sleepy", "idle"])

                if event == "walk":
                    sw = self.root.winfo_screenwidth()
                    sh = self.root.winfo_screenheight()
                    tx = random.randint(20, sw - self.win_w - 20)
                    ty = random.randint(20, sh - self.win_h - 60)
                    self.root.after(0, lambda: self._set_mood("walk1", "어디가지~"))
                    self._do_walk(tx, ty)
                    self.root.after(0, lambda: self._set_mood("idle"))

                elif event == "stretch":
                    self.root.after(0, lambda: self._set_mood("stretch", "기지개~"))
                    time.sleep(2)
                    self.root.after(0, lambda: self._set_mood("idle"))

                elif event == "sleepy":
                    self.root.after(0, lambda: self._set_mood("sleepy", "zzz..."))
                    time.sleep(3)
                    self.root.after(0, lambda: self._set_mood("idle"))


if __name__ == "__main__":
    CatAvatar()
