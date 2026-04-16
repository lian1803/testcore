import tkinter as tk
import urllib.request
import os

# 피카츄 애니 GIF 다운로드
GIF_PATH = os.path.join(os.environ['TEMP'], 'pikachu.gif')
if not os.path.exists(GIF_PATH):
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/25.gif",
        GIF_PATH
    )

root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes('-topmost', True)
root.wm_attributes('-transparentcolor', 'white')
root.config(bg='white')

sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
root.geometry(f'+{sw-220}+{sh-220}')

# GIF 프레임 로드 (2배 확대)
frames = []
try:
    i = 0
    while True:
        f = tk.PhotoImage(file=GIF_PATH, format=f'gif -index {i}')
        frames.append(f.zoom(3, 3))
        i += 1
except tk.TclError:
    pass

label = tk.Label(root, image=frames[0], bg='white', cursor='hand2')
label.pack()

# 애니메이션
def animate(i=0):
    label.config(image=frames[i])
    root.after(80, animate, (i+1) % len(frames))

# 드래그
def press(e):
    root._x, root._y, root._moved = e.x, e.y, False

def drag(e):
    root._moved = True
    root.geometry(f'+{e.x_root - root._x}+{e.y_root - root._y}')

label.bind('<ButtonPress-1>', press)
label.bind('<B1-Motion>', drag)
label.bind('<Button-3>', lambda e: root.destroy())  # 우클릭 종료

animate()
root.mainloop()
