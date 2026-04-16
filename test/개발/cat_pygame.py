#!/usr/bin/env python3
"""
고양이 데스크탑 펫 v3 — Pygame + Pillow
투명 창에 그림 고양이. 걷고 클릭하고 따라다님.
"""

import pygame
import ctypes
import math
import random
import threading
import time
from PIL import Image, ImageDraw, ImageFilter

# ── Win32 상수 ────────────────────────────────────
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST     = 0x00000008
LWA_COLORKEY      = 0x00000001
HWND_TOPMOST      = -1
SWP_NOMOVE        = 0x0002
SWP_NOSIZE        = 0x0001
TRANSPARENT_COLOR = (1, 1, 1)   # 이 색이 투명이 됨

# ── 설정 ──────────────────────────────────────────
WIN_W      = 160
WIN_H      = 180
CAT_W      = 120
CAT_H      = 140
FPS        = 30
WALK_SPEED = 3

# ── 색상 ──────────────────────────────────────────
C_BODY   = (245, 166, 35,  255)
C_BELLY  = (255, 221, 160, 255)
C_EAR_IN = (255, 140, 140, 255)
C_EYE    = (30,  20,  10,  255)
C_SHINE  = (255, 255, 255, 255)
C_NOSE   = (255, 105, 180, 255)
C_MOUTH  = (80,  40,  20,  255)
C_WHISK  = (200, 200, 200, 200)
C_STRIPE = (210, 140, 20,  120)

MEMOS = [
    "배고파요 냥~", "쉬어가세요 :3", "야근하지 마세요!",
    "커피 마셨어요?", "스트레칭 하세요!", "냥냥냥~",
    "오늘도 수고해요!", "물 마시는 거 잊지 마요",
    "저도 졸려요...", "집에 가고 싶다냥",
]


# ── 고양이 이미지 생성 ─────────────────────────────
def draw_cat(mood="idle", frame=0, direction=1, size=120):
    """Pillow로 고양이 그리기. direction: 1=오른쪽, -1=왼쪽"""
    w, h = size, int(size * 1.2)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = w // 2
    cy = h // 2 - 4

    # 몸통
    bw, bh = int(w * 0.44), int(h * 0.38)
    d.ellipse([cx-bw, cy+int(h*0.12), cx+bw, cy+int(h*0.12)+bh*2],
              fill=C_BODY)
    # 배
    d.ellipse([cx-int(bw*0.55), cy+int(h*0.18),
               cx+int(bw*0.55), cy+int(h*0.12)+int(bh*1.7)],
              fill=C_BELLY)

    # 줄무늬 (몸)
    for sy in range(cy+int(h*0.2), cy+int(h*0.4), 8):
        d.arc([cx-bw+4, sy, cx+bw-4, sy+6], 200, 340, fill=C_STRIPE, width=2)

    # 꼬리
    tail_swing = math.sin(frame * 0.3) * 18
    tx = cx + bw - 6
    ty = cy + int(h * 0.28)
    points = []
    for i in range(12):
        t = i / 11
        px = tx + int(math.sin(t * math.pi + tail_swing * 0.05) * 28 * t)
        py = ty + int(t * 34) + int(math.sin(t * math.pi) * 10)
        points.append((px * direction + cx * (1 - direction) * 2, py))
    if len(points) >= 2:
        for i in range(len(points)-1):
            d.line([points[i], points[i+1]], fill=C_BODY,
                   width=max(2, 7 - i // 2))

    # 귀
    ear_h = int(h * 0.22)
    # 왼쪽 귀
    d.polygon([(cx-int(w*0.32), cy-int(h*0.04)),
               (cx-int(w*0.18), cy-ear_h),
               (cx-int(w*0.02), cy-int(h*0.04))], fill=C_BODY)
    d.polygon([(cx-int(w*0.28), cy-int(h*0.03)),
               (cx-int(w*0.18), cy-int(ear_h*0.75)),
               (cx-int(w*0.07), cy-int(h*0.03))], fill=C_EAR_IN)
    # 오른쪽 귀
    d.polygon([(cx+int(w*0.02), cy-int(h*0.04)),
               (cx+int(w*0.18), cy-ear_h),
               (cx+int(w*0.32), cy-int(h*0.04))], fill=C_BODY)
    d.polygon([(cx+int(w*0.07), cy-int(h*0.03)),
               (cx+int(w*0.18), cy-int(ear_h*0.75)),
               (cx+int(w*0.28), cy-int(h*0.03))], fill=C_EAR_IN)

    # 머리
    hr = int(w * 0.38)
    d.ellipse([cx-hr, cy-int(h*0.3), cx+hr, cy+int(h*0.12)], fill=C_BODY)

    # 얼굴 줄무늬
    d.arc([cx-int(hr*0.5), cy-int(h*0.28), cx, cy-int(h*0.1)],
          240, 300, fill=C_STRIPE, width=2)
    d.arc([cx, cy-int(h*0.28), cx+int(hr*0.5), cy-int(h*0.1)],
          240, 300, fill=C_STRIPE, width=2)

    # ── 눈 ──────────────────────────────────
    ey = cy - int(h * 0.1)
    er = int(w * 0.08)
    elx = cx - int(w * 0.17)
    erx = cx + int(w * 0.17)

    if mood == "blink":
        d.line([(elx-er, ey), (elx+er, ey)], fill=C_EYE, width=3)
        d.line([(erx-er, ey), (erx+er, ey)], fill=C_EYE, width=3)
    elif mood == "happy":
        d.arc([elx-er, ey-er, elx+er, ey+er], 0, 180, fill=C_EYE, width=3)
        d.arc([erx-er, ey-er, erx+er, ey+er], 0, 180, fill=C_EYE, width=3)
    elif mood == "sleepy":
        d.arc([elx-er, ey-er, elx+er, ey], 180, 360, fill=C_EYE, width=3)
        d.arc([erx-er, ey-er, erx+er, ey], 180, 360, fill=C_EYE, width=3)
    elif mood == "surprised":
        d.ellipse([elx-er-2, ey-er-2, elx+er+2, ey+er+2], fill=C_EYE)
        d.ellipse([erx-er-2, ey-er-2, erx+er+2, ey+er+2], fill=C_EYE)
        d.ellipse([elx-3, ey-3, elx+3, ey+3], fill=C_SHINE)
        d.ellipse([erx-3, ey-3, erx+3, ey+3], fill=C_SHINE)
    elif mood == "love":
        for ex2 in [elx, erx]:
            d.text((ex2-6, ey-8), "♥", fill=(255, 20, 147, 255))
    elif mood == "angry":
        d.ellipse([elx-er, ey-er, elx+er, ey+er], fill=C_EYE)
        d.ellipse([erx-er, ey-er, erx+er, ey+er], fill=C_EYE)
        d.line([(elx-er-2, ey-er-3), (elx+er, ey-2)], fill=C_MOUTH, width=2)
        d.line([(erx-er, ey-2), (erx+er+2, ey-er-3)], fill=C_MOUTH, width=2)
    else:  # idle
        d.ellipse([elx-er, ey-er, elx+er, ey+er], fill=C_EYE)
        d.ellipse([erx-er, ey-er, erx+er, ey+er], fill=C_EYE)
        d.ellipse([elx-er//3, ey-er//3, elx+er//3, ey+er//3], fill=C_SHINE)
        d.ellipse([erx-er//3, ey-er//3, erx+er//3, ey+er//3], fill=C_SHINE)

    # 코
    ny = ey + int(h * 0.09)
    d.polygon([(cx, ny), (cx-5, ny+6), (cx+5, ny+6)], fill=C_NOSE)

    # 입
    if mood == "happy":
        d.arc([cx-10, ny+4, cx+10, ny+14], 0, 180, fill=C_MOUTH, width=2)
    elif mood == "surprised":
        d.ellipse([cx-5, ny+5, cx+5, ny+13], fill=C_MOUTH)
    else:
        d.arc([cx-7, ny+5, cx+7, ny+12], 20, 160, fill=C_MOUTH, width=2)

    # 수염
    wy = ny + 2
    for i, (wx1, wx2, wya) in enumerate([
        (cx-6, cx-35, wy-3), (cx-6, cx-34, wy+3),
        (cx+6, cx+35, wy-3), (cx+6, cx+34, wy+3),
    ]):
        d.line([(wx1, wy), (wx2, wya)], fill=C_WHISK, width=1)

    # 발 (걷기 애니메이션)
    fy = cy + int(h * 0.42)
    fw = int(w * 0.12)
    fh = int(h * 0.09)
    offset = int(math.sin(frame * 0.4) * 5) if mood in ("walk",) else 0
    d.ellipse([cx-int(w*0.25), fy+offset,    cx-int(w*0.05), fy+fh+offset],    fill=C_BODY)
    d.ellipse([cx+int(w*0.05), fy-offset,    cx+int(w*0.25), fy+fh-offset],    fill=C_BODY)

    # 방향 반전
    if direction == -1:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    return img


def pil_to_surface(pil_img):
    """PIL Image → Pygame Surface"""
    raw = pil_img.tobytes("raw", "RGBA")
    return pygame.image.fromstring(raw, pil_img.size, "RGBA")


# ── 메인 앱 ────────────────────────────────────────
class CatPet:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("냥이")

        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        self.sw, self.sh = sw, sh

        self.pos_x = sw - WIN_W - 30
        self.pos_y = sh - WIN_H - 60
        self.target_x = self.pos_x
        self.target_y = self.pos_y

        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{self.pos_x},{self.pos_y}'

        self.screen = pygame.display.set_mode(
            (WIN_W, WIN_H), pygame.NOFRAME
        )

        # Win32 투명 설정
        self.hwnd = pygame.display.get_wm_info()['window']
        self._setup_transparent()

        self.clock   = pygame.time.Clock()
        self.frame   = 0
        self.mood    = "idle"
        self.dir     = 1       # 1=오른쪽, -1=왼쪽
        self.following  = False
        self.running    = True
        self.msg        = "냥~ 안녕!"
        self.msg_timer  = 120  # 프레임

        # 드래그
        self.dragging   = False
        self.drag_off_x = 0
        self.drag_off_y = 0

        # 이미지 캐시
        self.img_cache = {}

        # 배경 이벤트 루프
        threading.Thread(target=self._event_loop, daemon=True).start()

        self._run()

    def _setup_transparent(self):
        style = ctypes.windll.user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            self.hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED
        )
        r, g, b = TRANSPARENT_COLOR
        ctypes.windll.user32.SetLayeredWindowAttributes(
            self.hwnd, r | (g << 8) | (b << 16), 0, LWA_COLORKEY
        )
        ctypes.windll.user32.SetWindowPos(
            self.hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )

    def _get_cat_img(self, mood, frame, direction):
        walk_f = (frame // 6) % 2 if mood == "walk" else 0
        key = (mood, walk_f, direction)
        if key not in self.img_cache:
            pil = draw_cat(mood, frame, direction, CAT_W)
            self.img_cache[key] = pil_to_surface(pil)
        return self.img_cache[key]

    def _set_pos(self, x, y):
        self.pos_x = max(0, min(x, self.sw - WIN_W))
        self.pos_y = max(0, min(y, self.sh - WIN_H))
        ctypes.windll.user32.SetWindowPos(
            self.hwnd, HWND_TOPMOST,
            self.pos_x, self.pos_y, WIN_W, WIN_H, 0
        )

    def _say(self, text, frames=120):
        self.msg = text
        self.msg_timer = frames

    def _set_mood(self, mood, msg=None):
        self.mood = mood
        if msg:
            self._say(msg)

    def _run(self):
        font_big  = pygame.font.SysFont("malguigothic", 14)
        font_hint = pygame.font.SysFont("malguigothic", 10)

        while self.running:
            self.clock.tick(FPS)
            self.frame += 1

            # ── 이벤트 ──────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging   = True
                        self.drag_off_x = event.pos[0]
                        self.drag_off_y = event.pos[1]
                        self._drag_moved = False
                    elif event.button == 3:
                        self._show_menu(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self._drag_moved = True
                        mx, my = ctypes.windll.user32.GetCursorPos.__class__.__mro__
                        p = ctypes.wintypes.POINT()
                        ctypes.windll.user32.GetCursorPos(ctypes.byref(p))
                        nx = p.x - self.drag_off_x
                        ny = p.y - self.drag_off_y
                        self._set_pos(nx, ny)
                        self.target_x = self.pos_x
                        self.target_y = self.pos_y

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.dragging and not getattr(self, '_drag_moved', True):
                            self._on_click()
                        self.dragging = False

            # ── 마우스 추적 ──────────────────────
            if self.following:
                p = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(p))
                self.target_x = p.x - WIN_W // 2
                self.target_y = p.y - WIN_H - 5

            # ── 이동 ─────────────────────────────
            dx = self.target_x - self.pos_x
            dy = self.target_y - self.pos_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > WALK_SPEED + 1:
                nx = self.pos_x + int(dx / dist * WALK_SPEED)
                ny = self.pos_y + int(dy / dist * WALK_SPEED)
                self._set_pos(nx, ny)
                if self.mood not in ("happy", "angry", "surprised", "love"):
                    self.mood = "walk"
                self.dir = 1 if dx > 0 else -1
            else:
                if self.mood == "walk":
                    self.mood = "idle"

            # ── 눈 깜빡임 ────────────────────────
            if self.frame % (FPS * 4) == 0 and self.mood == "idle":
                self.mood = "blink"
            if self.frame % (FPS * 4) == 5 and self.mood == "blink":
                self.mood = "idle"

            # ── 그리기 ───────────────────────────
            tr = TRANSPARENT_COLOR
            self.screen.fill(tr)

            cat_surf = self._get_cat_img(self.mood, self.frame, self.dir)
            ox = (WIN_W - CAT_W) // 2
            oy = 8
            self.screen.blit(cat_surf, (ox, oy))

            # 말풍선
            if self.msg_timer > 0:
                self.msg_timer -= 1
                alpha = min(255, self.msg_timer * 4)
                txt_surf = font_big.render(self.msg, True, (255, 255, 255))
                txt_surf.set_alpha(alpha)
                tx = WIN_W // 2 - txt_surf.get_width() // 2
                self.screen.blit(txt_surf, (tx, WIN_H - 28))

            pygame.display.flip()

        pygame.quit()

    def _on_click(self):
        moods = ["happy", "surprised", "love", "angry"]
        msgs  = ["냥냥~!", "헉!? 누구야!", "냥 ♥", "야옹! 건들지마!"]
        i = random.randrange(len(moods))
        self._set_mood(moods[i], msgs[i])
        def reset():
            time.sleep(2.5)
            if self.running:
                self.mood = "idle"
        threading.Thread(target=reset, daemon=True).start()

    def _show_menu(self, pos):
        """우클릭 메뉴 — tkinter로 팝업"""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="🐱 마우스 따라다니기 ON/OFF",
                         command=lambda: self._toggle_follow(root))
        menu.add_command(label="📝 메모 붙이기",
                         command=lambda: self._spawn_memo(root))
        menu.add_separator()
        menu.add_command(label="❌ 종료",
                         command=lambda: self._quit(root))
        p = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(p))
        try:
            menu.tk_popup(p.x, p.y)
        finally:
            root.destroy()

    def _toggle_follow(self, root=None):
        self.following = not self.following
        self._say("따라갈게요 냥~" if self.following else "이제 혼자 다닐게요")
        if root:
            root.destroy()

    def _spawn_memo(self, root=None):
        if root:
            root.destroy()
        import tkinter as tk
        memo_root = tk.Tk()
        memo_root.overrideredirect(True)
        memo_root.wm_attributes("-topmost", True)
        memo_root.wm_attributes("-alpha", 0.93)
        memo_root.config(bg="#FFFACD")
        x = random.randint(60, self.sw - 200)
        y = random.randint(60, self.sh - 150)
        memo_root.geometry(f"170x80+{x}+{y}")
        tk.Label(memo_root, text="📝 냥이 메모",
                 font=("Malgun Gothic", 8, "bold"),
                 bg="#FFE066", fg="#333").pack(fill="x", pady=2)
        tk.Label(memo_root, text=random.choice(MEMOS),
                 font=("Malgun Gothic", 9),
                 bg="#FFFACD", fg="#333", wraplength=150).pack(expand=True)
        tk.Label(memo_root, text="더블클릭으로 닫기",
                 font=("Malgun Gothic", 7),
                 bg="#FFFACD", fg="#aaa").pack()
        def sd(e): memo_root._dx, memo_root._dy = e.x_root-memo_root.winfo_x(), e.y_root-memo_root.winfo_y()
        def dr(e): memo_root.geometry(f"+{e.x_root-memo_root._dx}+{e.y_root-memo_root._dy}")
        memo_root.bind("<ButtonPress-1>", sd)
        memo_root.bind("<B1-Motion>", dr)
        memo_root.bind("<Double-Button-1>", lambda e: memo_root.destroy())
        memo_root.after(25000, memo_root.destroy)
        self._say("메모 붙였어요!")
        memo_root.mainloop()

    def _quit(self, root=None):
        if root:
            root.destroy()
        self.running = False

    def _event_loop(self):
        """배경 루프 — 랜덤 행동"""
        time.sleep(3)
        while self.running:
            time.sleep(random.randint(15, 25))
            if not self.running or self.following or self.mood not in ("idle", "blink", "walk"):
                continue
            action = random.choices(
                ["walk", "walk", "memo", "sit"],
                weights=[5, 5, 2, 3]
            )[0]
            if action == "walk":
                self.target_x = random.randint(20, self.sw - WIN_W - 20)
                self.target_y = random.randint(20, self.sh - WIN_H - 60)
                self._say("어디가볼까냥~")
            elif action == "memo":
                threading.Thread(target=self._spawn_memo, daemon=True).start()
            elif action == "sit":
                self._set_mood("sleepy", "잠깐 쉴게요 zzz")
                time.sleep(4)
                if self.running:
                    self.mood = "idle"


if __name__ == "__main__":
    # ctypes wintypes 임포트 보장
    import ctypes.wintypes
    CatPet()
