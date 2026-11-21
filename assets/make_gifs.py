"""Regenerate the before/after GIFs in assets/: python assets/make_gifs.py"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor for anti-aliasing
PW, PH, TOP = 240, 170, 26  # panel size and label strip height
FPS, N, MOVE = 25, 90, 60  # 3.6 s loop: 2.4 s animating, then a hold
BG, PANEL, FG, DIM = "#0b0f17", "#1a2130", "#e5e7eb", "#4b5563"
ACC, RED = "#a3e635", "#ef4444"
OUT = Path(__file__).parent
FONT = ImageFont.load_default(size=11 * S)


def lerp(a, b, t): return a + (b - a) * t
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def spring(t):  # overshoots then settles at 1
    t = clamp(t); return 1 - math.exp(-6 * t) * math.cos(9 * t)


class P:  # a drawing panel in un-scaled coordinates
    def __init__(s, d, ox): s.d, s.ox = d, ox
    def xy(s, b): return [(v + (s.ox if i % 2 == 0 else TOP)) * S for i, v in enumerate(b)]
    def rect(s, x0, y0, x1, y1, fill, r=6): s.d.rounded_rectangle(s.xy((x0, y0, x1, y1)), r * S, fill=fill)
    def dot(s, x, y, r, fill): s.d.ellipse(s.xy((x - r, y - r, x + r, y + r)), fill=fill)
    def line(s, pts, fill, w=2): s.d.line(s.xy([c for p in pts for c in p]), fill=fill, width=w * S)
    def text(s, x, y, txt, fill=FG): s.d.text(s.xy((x, y)), txt, fill=fill, font=FONT, anchor="mm")


# --- one draw function per principle: f(panel, t in 0..1, after: bool) ---

def exaggeration(p, t, a):
    dx = 14 * math.sin(t * 30) * (1 - t) if a else 0
    col = RED if (a or t > 0.5) else DIM
    for i in range(4): p.dot(84 + i * 24 + dx, 70, 7, col)
    if a: p.text(120 + dx, 100, "Wrong passcode", RED)
    elif t > 0.5: p.text(120, 100, "wrong", DIM)

def origin(p, t, a):
    p.dot(40, 130, 14, ACC)
    if a:
        k = spring(t * 1.3); cx, cy = lerp(40, 130, k), lerp(130, 70, k)
        w, h = 90 * k, 60 * k
        if k > 0.02: p.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, FG)
    elif t > 0.3: p.rect(85, 40, 175, 100, FG)

def staggering(p, t, a):
    for i in range(4):
        k = ease_out((t - (i * 0.12 if a else 0)) * 2)
        x = lerp(260, 40, k); p.rect(x, 22 + i * 32, x + 160, 44 + i * 32, FG if k > 0 else PANEL)

def squash(p, t, a):
    ph = (t * 2) % 1; y = 30 + 100 * (1 - (2 * ph - 1) ** 2)
    sq = max(0, (y - 115) / 15) if a else 0
    w, h = 18 * (1 + 0.5 * sq), 18 * (1 - 0.4 * sq)
    p.rect(30, 148, 210, 150, DIM, 1)
    p.d.ellipse(p.xy((120 - w, min(y, 130) + 18 - 2 * h, 120 + w, min(y, 130) + 18)), fill=ACC)

def rubber(p, t, a):
    pull = 60 * math.sin(math.pi * clamp(t * 1.4))
    off = (pull * 0.45) if a else 0
    for i in range(3): p.rect(50, 20 + i * 42 + off, 190, 54 + i * 42 + off, FG)
    p.dot(120, 30 + pull, 9, "#ffffff80" if pull > 1 else PANEL)

def doherty(p, t, a):
    delay = 0.08 if a else 0.75
    pressed = t > 0.05
    done = t > delay
    p.rect(60, 55, 180, 95, (ACC if done else ("#6b8f2a" if (pressed and a) else DIM)))
    p.text(120, 75, "Saved" if done else ("Saving..." if a and pressed else "Save"), BG if done else FG)
    p.text(120, 125, "80 ms" if a else "1200 ms", ACC if a else RED)

def anticipation(p, t, a):
    x = lerp(50, 190, ease(t * 1.2))
    if a and t < 0.25: x = 50 - 20 * math.sin(math.pi * t * 4)  # wind-up
    elif a: x = lerp(50, 190, ease_out((t - 0.25) * 1.6))
    p.dot(x, 75, 16, ACC)

def fitts(p, t, a):
    k = ease(t * 1.3)
    if a:
        p.rect(90, 95, 190, 135, ACC); tx, ty = 140, 115
    else:
        p.rect(205, 12, 225, 26, ACC); tx, ty = 215, 19
    cx, cy = lerp(60, tx, k), lerp(100, ty, k)
    p.d.polygon(p.xy((cx, cy, cx, cy + 14, cx + 9, cy + 10)), fill="#ffffff")

def easing(p, t, a):
    k = ease(t * 1.2) if a else clamp(t * 1.2)
    p.line([(40, 75), (200, 75)], DIM, 1); p.rect(lerp(30, 180, k), 60, lerp(60, 210, k), 90, ACC)

def hick(p, t, a):
    n = 4 if a else 9; target = 2 if a else 7; h = 120 / n
    pick = min(target, int(t * 1.4 * (n + 1)))
    for i in range(n): p.rect(70, 15 + i * h, 170, 13 + (i + 1) * h, ACC if i == pick else FG, 3)

def follow(p, t, a):
    k = ease_out(t * 1.5); x = lerp(20, 110, k)
    lag = (spring(t * 1.2) if a else k)
    p.rect(x, 35, x + 110, 115, FG)
    ix = lerp(20, 110, lag)
    for i in range(3): p.rect(ix + 12, 48 + i * 20, ix + 98 - i * 20, 58 + i * 20, DIM, 3)

def arcs(p, t, a):
    p.dot(40, 130, 12, ACC)
    for j, (tx, ty) in enumerate([(200, 30), (150, 25), (210, 90)]):
        k = ease(t * 1.3 - j * 0.1)
        if a:  # quadratic bezier through a control point
            cx, cy = 40, 30
            x = (1 - k) ** 2 * 40 + 2 * (1 - k) * k * cx + k * k * tx
            y = (1 - k) ** 2 * 130 + 2 * (1 - k) * k * cy + k * k * ty
        else: x, y = lerp(40, tx, k), lerp(130, ty, k)
        p.dot(x, y, 8, FG)

def restorff(p, t, a):
    for i in range(3):
        mid = a and i == 1; g = 6 * ease(t * 2) if mid else 0
        x0 = 18 + i * 72
        p.rect(x0 - g, 30 - g, x0 + 60 + g, 130 + g, ACC if mid else FG)
        p.rect(x0 + 10, 110, x0 + 50, 120, BG if mid else DIM, 3)

def timing(p, t, a):
    k = ease(t * (3.5 if a else 1.05)); h = 100 * k
    p.rect(60, 25, 180, 25 + max(h, 2), FG)
    p.text(120, 145, "200 ms" if a else "900 ms", ACC if a else RED)

def interruptible(p, t, a):
    tap = 0.3
    if t < tap: k = ease_out(t / 0.6)
    elif a: k = ease_out(tap / 0.6) * (1 - ease_out((t - tap) * 3))
    else:
        k = ease_out(t / 0.6) if t < 0.6 else 1 - ease((t - 0.6) * 3)
    p.rect(20, lerp(170, 50, k), 220, 175, FG, 10)
    if abs(t - tap) < 0.06: p.dot(120, 100, 10, "#ffffffaa")

def secondary(p, t, a):
    k = spring(t * 1.5); r = 18 * (1 + 0.2 * math.sin(math.pi * clamp(t * 3))) if a else 18
    col = RED if t > 0.1 else DIM
    p.dot(110, 72, r * 0.6, col); p.dot(130, 72, r * 0.6, col)
    p.d.polygon(p.xy((120 - r * 1.1, 76, 120 + r * 1.1, 76, 120, 76 + r * 1.2)), fill=col)
    if a and 0.1 < t < 0.6:
        for i in range(8):
            ang = i * math.pi / 4; d = 20 + 40 * ease_out((t - 0.1) * 2)
            p.dot(120 + d * math.cos(ang), 80 + d * math.sin(ang), 3 * (1 - (t - 0.1) * 2), ACC)

def frequency(p, t, a):
    for i, lbl in enumerate(["A", "B", "C"]): p.text(60 + i * 60, 140, lbl, FG)
    k = (1 if t > 0.1 else 0) if a else ease((t - 0.1) * 1.1)
    x = lerp(60, 180, k); p.rect(x - 22, 150, x + 22, 154, ACC, 2)
    p.rect(30, 20, 210, 120, FG if k < 0.5 else ACC)

def peak_end(p, t, a):
    k = ease(t * 1.6); p.rect(40, 70, 40 + 160 * k, 80, ACC, 4)
    if t > 0.65:
        if a:
            p.dot(120, 40, 16, ACC); p.line([(112, 40), (118, 47), (129, 33)], BG, 3)
            for i in range(10):
                ang = i * math.pi / 5; d = 25 + 35 * ease_out((t - 0.65) * 3)
                p.dot(120 + d * math.cos(ang), 40 + d * math.sin(ang), 2.5, [RED, FG, ACC][i % 3])
        else: p.text(120, 45, "done", DIM)


PRINCIPLES = [exaggeration, origin, staggering, squash, rubber, doherty, anticipation, fitts, easing,
              hick, follow, arcs, restorff, timing, interruptible, secondary, frequency, peak_end]


def render(fn):
    frames = []
    for f in range(N):
        t = min(f / MOVE, 1.0)
        img = Image.new("RGB", ((PW * 2 + 12) * S, (PH + TOP + 6) * S), BG)
        d = ImageDraw.Draw(img, "RGBA")
        for col, (label, after) in enumerate([("Before", False), ("After", True)]):
            ox = col * (PW + 12)
            d.rounded_rectangle([ox * S, TOP * S, (ox + PW) * S, (TOP + PH) * S], 10 * S, fill=PANEL)
            d.text(((ox + 8) * S, 8 * S), label, fill=ACC if after else DIM, font=FONT)
            fn(P(d, ox), t, after)
        # loop progress bar; also keeps every frame distinct so Pillow doesn't merge them below FPS
        d.rectangle([0, img.height - 2 * S, img.width * (f + 1) // N, img.height], fill=DIM)
        frames.append(img.resize((img.width // S, img.height // S), Image.LANCZOS))
    path = OUT / f"{fn.__name__.replace('_', '-')}.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=1000 // FPS, loop=0)
    return path


if __name__ == "__main__":
    for fn in PRINCIPLES: print(render(fn).name)
