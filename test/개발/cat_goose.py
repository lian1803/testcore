#!/usr/bin/env python3
"""
고양이 Goose — oneko + Desktop Goose 합체판
드래그: 이동  |  클릭: 상호작용  |  우클릭: 메뉴
"""

import tkinter as tk
import random
import time
import threading
import math

# ── 설정 ─────────────────────────────────────────
CAT_SIZE   = 70    # 고양이 기본 크기 (반지름)
WIN_SIZE   = 160   # 창 크기
WALK_SPEED = 4     # 걷기 속도 (픽셀/프레임)
FPS        = 30

MEMOS = [
    "배고파요 냥~", "쉬어가세요 :3", "야근하지 마세요!",
    "커피 마셨어요?", "스트레칭 하세요!", "냥냥냥~",
    "오늘도 수고해요!", "물 마시는 거 잊지 마요",
    "저도 졸려요...", "おやつ ください", "냥?",
    "집에 가고 싶다냥", "저 여기 있어요!",
]

STEAL_FILES = [
    "📄 중요파일.txt", "📊 보고서최종.xlsx",
    "🔑 비밀번호.txt", "💰 가계부.xlsx",
    "📝 TODO.md", "🎵 노래.mp3",
]

COLORS = {
    "body":   "#F5A623",
    "belly":  "#FFDDA0",
    "ear_in": "#FF9999",
    "eye":    "#1a1a1a",
    "pupil":  "#000000",
    "nose":   "#FF69B4",
    "mouth":  "#333333",
    "tail":   "#F5A623",
    "bg":     "#010101",   # 투명화할 색
    "border": "#5533ff",
}
TRANSPARENT = "#010101"   # 이 색이 완전 투명이 됨

MOODS = ["idle", "happy", "surprised", "angry", "sleepy", "love"]


class CatGoose:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)  # 배경 완전 투명
        self.root.config(bg=TRANSPARENT)

        # 상태
        self.mood       = "idle"
        self.tail_angle = 0
        self.blink      = False
        self.running    = True
        self.following  = False   # 마우스 추적 모드

        # 위치
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.pos_x = sw - WIN_SIZE - 30
        self.pos_y = sh - WIN_SIZE - 60
        self.target_x = self.pos_x
        self.target_y = self.pos_y
        self.screen_w  = sw
        self.screen_h  = sh

        self.root.geometry(f"{WIN_SIZE}x{WIN_SIZE+30}+{self.pos_x}+{self.pos_y}")

        self._build_ui()
        self._bind_events()

        threading.Thread(target=self._game_loop, daemon=True).start()
        threading.Thread(target=self._event_loop, daemon=True).start()

        self.root.mainloop()

    # ── UI ───────────────────────────────────────
    def _build_ui(self):
        # 테두리/프레임 없이 캔버스 바로
        self.canvas = tk.Canvas(self.root,
                                width=WIN_SIZE, height=WIN_SIZE,
                                bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()

        # 말풍선 라벨 (투명 배경)
        self.msg_label = tk.Label(self.root,
                                  text="",
                                  font=("Malgun Gothic", 8, "bold"),
                                  fg="#ffffff", bg=TRANSPARENT)
        self.msg_label.pack(pady=0)

        self._draw_cat()

    # ── 고양이 그리기 ─────────────────────────────
    def _draw_cat(self):
        self.canvas.delete("all")
        cx, cy = WIN_SIZE // 2, WIN_SIZE // 2 - 2
        m = self.mood

        # ── 꼬리 (뒤에 그려야 몸 아래로) ──
        self.tail_angle += 0.15
        tx = cx + 26
        ty = cy + 18
        tx2 = tx + int(math.sin(self.tail_angle) * 22)
        ty2 = ty + 18
        tx3 = tx2 + int(math.sin(self.tail_angle + 1) * 10)
        ty3 = ty2 + 10
        self.canvas.create_line(tx, ty, tx2, ty2, tx3, ty3,
                                fill=COLORS["tail"], width=5,
                                smooth=True, capstyle="round")

        # ── 몸 ──
        self.canvas.create_oval(cx-22, cy+10, cx+22, cy+36,
                                fill=COLORS["body"], outline="")
        # 배
        self.canvas.create_oval(cx-13, cy+13, cx+13, cy+33,
                                fill=COLORS["belly"], outline="")

        # ── 귀 ──
        # 왼쪽 귀
        self.canvas.create_polygon(
            cx-22, cy-12,   cx-14, cy-28,   cx-4, cy-12,
            fill=COLORS["body"], outline=""
        )
        self.canvas.create_polygon(
            cx-19, cy-13,   cx-14, cy-23,   cx-8, cy-13,
            fill=COLORS["ear_in"], outline=""
        )
        # 오른쪽 귀
        self.canvas.create_polygon(
            cx+4, cy-12,    cx+14, cy-28,   cx+22, cy-12,
            fill=COLORS["body"], outline=""
        )
        self.canvas.create_polygon(
            cx+8, cy-13,    cx+14, cy-23,   cx+19, cy-13,
            fill=COLORS["ear_in"], outline=""
        )

        # ── 머리 ──
        self.canvas.create_oval(cx-24, cy-24, cx+24, cy+14,
                                fill=COLORS["body"], outline="")

        # ── 눈 ──
        if self.blink:
            # 눈 감기
            self.canvas.create_line(cx-13, cy-6, cx-6, cy-6,
                                    fill=COLORS["eye"], width=2, capstyle="round")
            self.canvas.create_line(cx+6, cy-6, cx+13, cy-6,
                                    fill=COLORS["eye"], width=2, capstyle="round")
        elif m == "sleepy":
            self.canvas.create_arc(cx-14, cy-10, cx-6, cy-2,
                                   start=0, extent=180, fill=COLORS["eye"], outline="")
            self.canvas.create_arc(cx+6, cy-10, cx+14, cy-2,
                                   start=0, extent=180, fill=COLORS["eye"], outline="")
        elif m == "happy":
            self.canvas.create_arc(cx-14, cy-12, cx-5, cy-4,
                                   start=0, extent=180, fill=COLORS["eye"], outline="")
            self.canvas.create_arc(cx+5, cy-12, cx+14, cy-4,
                                   start=0, extent=180, fill=COLORS["eye"], outline="")
        elif m == "surprised":
            self.canvas.create_oval(cx-14, cy-11, cx-6, cy-3,
                                    fill=COLORS["eye"], outline="")
            self.canvas.create_oval(cx+6, cy-11, cx+14, cy-3,
                                    fill=COLORS["eye"], outline="")
            # 동공
            self.canvas.create_oval(cx-12, cy-9, cx-8, cy-5,
                                    fill="white", outline="")
            self.canvas.create_oval(cx+8, cy-9, cx+12, cy-5,
                                    fill="white", outline="")
        elif m == "angry":
            self.canvas.create_oval(cx-13, cy-10, cx-5, cy-2,
                                    fill=COLORS["eye"], outline="")
            self.canvas.create_oval(cx+5, cy-10, cx+13, cy-2,
                                    fill=COLORS["eye"], outline="")
            # 눈썹
            self.canvas.create_line(cx-15, cy-14, cx-4, cy-11,
                                    fill="#333", width=2)
            self.canvas.create_line(cx+4, cy-11, cx+15, cy-14,
                                    fill="#333", width=2)
        elif m == "love":
            # 하트 눈
            for ox in (-10, 9):
                x0 = cx + ox
                self.canvas.create_text(x0, cy-6,
                                        text="♥", fill="#FF1493",
                                        font=("Arial", 8, "bold"))
        else:  # idle
            self.canvas.create_oval(cx-13, cy-10, cx-5, cy-2,
                                    fill=COLORS["eye"], outline="")
            self.canvas.create_oval(cx+5, cy-10, cx+13, cy-2,
                                    fill=COLORS["eye"], outline="")
            # 반짝임
            self.canvas.create_oval(cx-11, cy-9, cx-9, cy-7,
                                    fill="white", outline="")
            self.canvas.create_oval(cx+8, cy-9, cx+10, cy-7,
                                    fill="white", outline="")

        # ── 코 ──
        self.canvas.create_polygon(
            cx, cy+1,   cx-3, cy+5,   cx+3, cy+5,
            fill=COLORS["nose"], outline=""
        )

        # ── 입 ──
        if m == "happy":
            self.canvas.create_arc(cx-6, cy+4, cx+6, cy+11,
                                   start=200, extent=140,
                                   outline=COLORS["mouth"], width=2, style="arc")
        elif m == "surprised":
            self.canvas.create_oval(cx-4, cy+5, cx+4, cy+11,
                                    fill=COLORS["mouth"], outline="")
        elif m == "angry":
            self.canvas.create_arc(cx-6, cy+6, cx+6, cy+13,
                                   start=20, extent=140,
                                   outline=COLORS["mouth"], width=2, style="arc")
        else:
            self.canvas.create_arc(cx-5, cy+4, cx+5, cy+10,
                                   start=200, extent=140,
                                   outline=COLORS["mouth"], width=1, style="arc")

        # ── 수염 ──
        wlen = 18
        self.canvas.create_line(cx-4, cy+3, cx-4-wlen, cy+1,
                                fill="#ccc", width=1)
        self.canvas.create_line(cx-4, cy+5, cx-4-wlen, cy+7,
                                fill="#ccc", width=1)
        self.canvas.create_line(cx+4, cy+3, cx+4+wlen, cy+1,
                                fill="#ccc", width=1)
        self.canvas.create_line(cx+4, cy+5, cx+4+wlen, cy+7,
                                fill="#ccc", width=1)

    # ── 이벤트 ───────────────────────────────────
    def _bind_events(self):
        self._dx = 0
        self._dy = 0
        self._moved = False
        for w in (self.root, self.canvas, self.msg_label):
            w.bind("<ButtonPress-1>",   self._press)
            w.bind("<B1-Motion>",       self._drag)
            w.bind("<ButtonRelease-1>", self._release)
            w.bind("<Button-3>",        self._right_click)

    def _press(self, e):
        self._dx = e.x_root - self.root.winfo_x()
        self._dy = e.y_root - self.root.winfo_y()
        self._moved = False

    def _drag(self, e):
        self._moved = True
        self.pos_x = e.x_root - self._dx
        self.pos_y = e.y_root - self._dy
        self.target_x = self.pos_x
        self.target_y = self.pos_y
        self.root.geometry(f"+{self.pos_x}+{self.pos_y}")

    def _release(self, e):
        if not self._moved:
            self._on_click()

    def _on_click(self):
        mood = random.choice(["happy", "surprised", "love", "angry", "sleepy"])
        self._set_mood(mood)
        self.root.after(2500, lambda: self._set_mood("idle"))

    def _right_click(self, e):
        menu = tk.Menu(self.root, tearoff=0, bg="#1a1a2e", fg="white",
                       activebackground="#5533ff")
        menu.add_command(label="🐱 따라다니기 ON/OFF",
                         command=self._toggle_follow)
        menu.add_command(label="📝 메모 붙이기",
                         command=self._spawn_memo)
        menu.add_command(label="📄 파일 훔치기",
                         command=lambda: threading.Thread(
                             target=self._steal_file, daemon=True).start())
        menu.add_separator()
        menu.add_command(label="❌ 종료", command=self._quit)
        menu.tk_popup(e.x_root, e.y_root)

    def _toggle_follow(self):
        self.following = not self.following
        msg = "마우스 따라갈게요 냥~" if self.following else "이제 혼자 다닐게요"
        self.msg_label.config(text=msg)

    def _quit(self):
        self.running = False
        self.root.destroy()

    # ── 상태 변경 ─────────────────────────────────
    def _set_mood(self, mood, msg=None):
        self.mood = mood
        if msg:
            self.root.after(0, lambda: self.msg_label.config(text=msg))

    # ── 메모 붙이기 ───────────────────────────────
    def _spawn_memo(self):
        memo = tk.Toplevel()
        memo.overrideredirect(True)
        memo.wm_attributes("-topmost", True)
        memo.wm_attributes("-alpha", 0.92)
        memo.config(bg="#FFFACD")

        x = random.randint(50, self.screen_w - 200)
        y = random.randint(50, self.screen_h - 150)
        memo.geometry(f"160x80+{x}+{y}")

        text = random.choice(MEMOS)
        tk.Label(memo, text="📝 냥이 메모",
                 font=("Malgun Gothic", 8, "bold"),
                 bg="#FFE066", fg="#333").pack(fill="x", pady=2)
        tk.Label(memo, text=text,
                 font=("Malgun Gothic", 9),
                 bg="#FFFACD", fg="#333",
                 wraplength=140).pack(expand=True)

        # 드래그 가능
        def start(e): memo._dx, memo._dy = e.x_root - memo.winfo_x(), e.y_root - memo.winfo_y()
        def drag(e): memo.geometry(f"+{e.x_root - memo._dx}+{e.y_root - memo._dy}")
        def close(e): memo.destroy()
        memo.bind("<ButtonPress-1>", start)
        memo.bind("<B1-Motion>", drag)
        memo.bind("<Double-Button-1>", close)

        tk.Label(memo, text="더블클릭으로 닫기",
                 font=("Malgun Gothic", 7),
                 bg="#FFFACD", fg="#aaa").pack()

        # 30초 후 자동 닫기
        memo.after(30000, lambda: memo.destroy() if memo.winfo_exists() else None)

    # ── 파일 훔치기 ───────────────────────────────
    def _steal_file(self):
        fname = random.choice(STEAL_FILES)

        # 화면 어딘가에 파일 아이콘 등장
        fx = random.randint(100, self.screen_w - 200)
        fy = random.randint(100, self.screen_h - 200)

        file_win = tk.Toplevel()
        file_win.overrideredirect(True)
        file_win.wm_attributes("-topmost", True)
        file_win.wm_attributes("-alpha", 0.9)
        file_win.geometry(f"140x36+{fx}+{fy}")
        file_win.config(bg="#2a2a3e")
        tk.Label(file_win, text=fname,
                 font=("Malgun Gothic", 9),
                 fg="white", bg="#2a2a3e").pack(expand=True)

        self.root.after(0, lambda: self.msg_label.config(text="앗! 저 저거 가질래요!"))

        # 고양이가 파일로 걷기
        self.target_x = fx - WIN_SIZE // 2
        self.target_y = fy - WIN_SIZE // 2
        time.sleep(2)

        # 파일 집어들고 원위치
        file_win.destroy()
        self.root.after(0, lambda: self.msg_label.config(text=f"냐하하! {fname} 냠냠!"))
        time.sleep(1)

        # 랜덤 위치로 도망
        self.target_x = random.randint(50, self.screen_w - WIN_SIZE - 50)
        self.target_y = random.randint(50, self.screen_h - WIN_SIZE - 100)
        time.sleep(2)
        self.root.after(0, lambda: self.msg_label.config(text="냥~"))

    # ── 게임 루프 (이동 + 그리기) ─────────────────
    def _game_loop(self):
        while self.running:
            # 마우스 추적 모드
            if self.following:
                try:
                    mx = self.root.winfo_pointerx()
                    my = self.root.winfo_pointery()
                    self.target_x = mx - WIN_SIZE // 2
                    self.target_y = my - WIN_SIZE - 10
                except Exception:
                    pass

            # 목표 지점으로 이동
            dx = self.target_x - self.pos_x
            dy = self.target_y - self.pos_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > WALK_SPEED:
                self.pos_x += int(dx / dist * WALK_SPEED)
                self.pos_y += int(dy / dist * WALK_SPEED)
                self.root.after(0, lambda x=self.pos_x, y=self.pos_y:
                                self.root.geometry(f"+{x}+{y}"))

            # 그리기
            self.root.after(0, self._draw_cat)

            time.sleep(1 / FPS)

    # ── 이벤트 루프 (눈 깜빡임 + 랜덤 행동) ────────
    def _event_loop(self):
        blink_t = 0
        event_t = 0

        while self.running:
            time.sleep(0.4)
            blink_t += 1
            event_t += 1

            # 5초마다 눈 깜빡임
            if blink_t >= 12 and self.mood == "idle":
                self.blink = True
                time.sleep(0.15)
                self.blink = False
                blink_t = 0

            # 20초마다 랜덤 이벤트
            if event_t >= 50:
                event_t = 0
                if self.following:
                    continue

                action = random.choices(
                    ["walk", "memo", "steal", "sit", "walk"],
                    weights=[4, 2, 1, 3, 4]
                )[0]

                if action == "walk":
                    self.target_x = random.randint(20, self.screen_w - WIN_SIZE - 20)
                    self.target_y = random.randint(20, self.screen_h - WIN_SIZE - 80)
                    self.root.after(0, lambda: self.msg_label.config(text="어디가볼까냥~"))

                elif action == "memo":
                    self._spawn_memo()
                    self.root.after(0, lambda: self.msg_label.config(text="메모 붙였어요!"))

                elif action == "steal":
                    threading.Thread(target=self._steal_file, daemon=True).start()

                elif action == "sit":
                    self._set_mood("sleepy", "잠깐 쉴게요 zzz")
                    time.sleep(4)
                    self._set_mood("idle", "냥~")


if __name__ == "__main__":
    CatGoose()
