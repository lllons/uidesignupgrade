"""Regenerate the before/after GIFs in assets/: python assets/make_gifs.py [name ...]  (needs Pillow)"""
import math
import sys
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor for anti-aliasing
FPS = 50
MOVE, HOLD, FADE = 150, 40, 15  # 3 s animating, 0.8 s hold, 0.3 s crossfade back to the first frame
N = MOVE + HOLD + FADE
PW, PH, GAP, M = 300, 230, 16, 10  # panel size, gap between panels, outer margin
W, H = M * 2 + PW * 2 + GAP, M * 2 + PH
OUT = Path(__file__).parent

BG, INK, MUTED, CARD, DARK = "#0a0a12", "#f8fafc", "#94a3b8", "#f8fafc", "#0f172a"
PINK, VIOLET, CYAN, AMBER = "#f472b6", "#8b5cf6", "#22d3ee", "#fbbf24"
EMERALD, BLUE, RED, ORANGE = "#34d399", "#60a5fa", "#f87171", "#fb923c"
BAR, BAR2 = "#94a3b8", "#cbd5e1"
RAINBOW = (PINK, AMBER, CYAN, VIOLET, EMERALD, BLUE, ORANGE)
GRAD = {False: ("#2a2a35", "#121218"), True: ("#4c1d95", "#0b2a5b")}  # panel gradients: before dull, after vivid


# --- easing -------------------------------------------------------------------------------------

def clamp(t): return max(0.0, min(1.0, t))
def lerp(a, b, t): return a + (b - a) * t
def seg(t, a, b): return clamp((t - a) / (b - a))  # local 0..1 progress of t inside [a, b]
def ease_out(t): return 1 - (1 - clamp(t)) ** 3
def ease_in(t): return clamp(t) ** 3
def ease(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def spring(t):  # 0 -> 1 with overshoot, settles by t = 1
    t = clamp(t)
    return 1 - math.exp(-7 * t) * math.cos(10 * t)


def along(t, segs):
    """Position on a path given as [(t0, t1, (x0, y0), (x1, y1)), ...] with eased segments."""
    x, y = segs[0][2]
    for t0, t1, a, b in segs:
        if t >= t0:
            k = ease(seg(t, t0, t1))
            x, y = lerp(a[0], b[0], k), lerp(a[1], b[1], k)
    return x, y


@lru_cache(None)
def font(size, bold=False):
    names = ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size * S)
        except OSError:
            pass
    return ImageFont.load_default(size * S)


def rgba(c, a=1.0):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (int(255 * clamp(a)),)


class Panel:
    """Draws in one panel's local coordinates (0..PW, 0..PH)."""

    def __init__(s, d, ox, after): s.d, s.ox, s.after = d, ox, after
    def _p(s, x, y): return ((s.ox + x) * S, (M + y) * S)
    def _box(s, x0, y0, x1, y1): return [*s._p(x0, y0), *s._p(x1, y1)]

    def rect(s, x0, y0, x1, y1, c, r=8, a=1.0, outline=None, w=0):
        if x1 - x0 < 1 or y1 - y0 < 1 or a <= 0:
            return
        r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
        s.d.rounded_rectangle(s._box(x0, y0, x1, y1), r * S, fill=rgba(c, a) if c else None,
                              outline=rgba(outline, a) if outline else None, width=int(w * S))

    def card(s, x0, y0, x1, y1, c=CARD, r=10, a=1.0):  # rect with a soft drop shadow
        s.rect(x0 + 1, y0 + 5, x1 + 1, y1 + 7, "#000000", r, 0.3 * a)
        s.rect(x0, y0, x1, y1, c, r, a)

    def ellipse(s, x, y, rx, ry, c, a=1.0, outline=None, w=0):
        if rx <= 0.3 or ry <= 0.3 or a <= 0:
            return
        s.d.ellipse(s._box(x - rx, y - ry, x + rx, y + ry), fill=rgba(c, a) if c else None,
                    outline=rgba(outline, a) if outline else None, width=int(w * S))

    def circle(s, x, y, r, c, a=1.0, outline=None, w=0): s.ellipse(x, y, r, r, c, a, outline, w)

    def arc(s, x, y, r, start, end, c, w=3, a=1.0):
        if r > 0 and a > 0:
            s.d.arc(s._box(x - r, y - r, x + r, y + r), start, end, fill=rgba(c, a), width=int(w * S))

    def line(s, pts, c, w=3, a=1.0):
        if a > 0 and len(pts) > 1:
            s.d.line([s._p(x, y) for x, y in pts], fill=rgba(c, a), width=int(w * S), joint="curve")

    def poly(s, pts, c, a=1.0, outline=None, w=0):
        s.d.polygon([s._p(x, y) for x, y in pts], fill=rgba(c, a) if c else None,
                    outline=rgba(outline, a) if outline else None, width=int(w * S))

    def text(s, x, y, txt, c=INK, size=12, bold=False, a=1.0, anchor="mm"):
        if a > 0:
            s.d.text(s._p(x, y), txt, fill=rgba(c, a), font=font(size, bold), anchor=anchor)

    def ripple(s, x, y, age):  # tap indicator; age is t since the tap
        if 0 <= age < 0.14:
            k = age / 0.14
            s.circle(x, y, 7 + 20 * ease_out(k), None, outline="#ffffff", w=2, a=1 - k)
            s.circle(x, y, 8, "#ffffff", 0.6 * (1 - k))

    def cursor(s, x, y):
        pts = [(0, 0), (0, 17), (4.5, 13), (7.5, 20), (10.5, 19), (7.5, 12.5), (12.5, 12.5)]
        s.poly([(x + px, y + py) for px, py in pts], "#ffffff", outline=DARK, w=1)

    def check(s, x, y, size, c, w=3, progress=1.0):
        pts = [(x - size, y), (x - size * 0.3, y + size * 0.7), (x + size, y - size * 0.7)]
        if progress < 1:  # draw the stroke partially
            if progress < 0.4:
                k = progress / 0.4
                pts = [pts[0], (lerp(pts[0][0], pts[1][0], k), lerp(pts[0][1], pts[1][1], k))]
            else:
                k = (progress - 0.4) / 0.6
                pts = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], k), lerp(pts[1][1], pts[2][1], k))]
        s.line(pts, c, w)

    def heart(s, x, y, size, c, a=1.0, outline=None, w=0):
        pts = []
        for i in range(48):
            th = i / 48 * 2 * math.pi
            hx = 16 * math.sin(th) ** 3
            hy = -(13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))
            pts.append((x + hx * size / 16, y + hy * size / 16))
        s.poly(pts, c, a, outline, w)

    def chrome(s, caption):
        c, label = (EMERALD, "AFTER") if s.after else (RED, "BEFORE")
        w = font(9, True).getlength(label) / S + 18
        s.rect(12, 12, 12 + w, 30, c, 9, 0.2)
        s.text(12 + w / 2, 21, label, c, 9, True)
        s.text(PW / 2, PH - 15, caption, INK if s.after else MUTED, 11, s.after)


def list_rows(p, y0, n, gap=30, h=24, off=0.0, a=1.0, x0=24, x1=276, first=0):
    for i in range(first, first + n):
        y = y0 + (i - first) * gap + off
        p.card(x0, y, x1, y + h, CARD, 8, a)
        p.circle(x0 + 14, y + h / 2, 7, RAINBOW[i % len(RAINBOW)], a)
        p.rect(x0 + 28, y + h / 2 - 4, x0 + 28 + (130, 96, 150, 80, 116)[i % 5], y + h / 2 + 4, BAR2, 4, a)


# --- one function per principle: f(panel, t in 0..1, after) -> caption ------------------------

def exaggeration(p, t, a):
    typed = int(seg(t, 0.05, 0.42) * 4.99)
    fail = t >= 0.48
    bad = a and fail
    k = seg(t, 0.48, 0.9)
    dx = 18 * math.sin(k * math.pi * 8) * (1 - k) ** 2 if bad else 0
    x, lock = 150 + dx, RED if bad else INK
    if bad:
        p.circle(x, 74, 40 * ease_out(seg(t, 0.48, 0.7)), RED, 0.25 * (1 - seg(t, 0.55, 0.8)))
    p.arc(x, 64, 9, 180, 360, lock, 3)
    p.rect(x - 13, 63, x + 13, 84, lock, 5)
    p.text(x, 104, "Enter passcode", MUTED, 11)
    for i in range(4):
        cx = 114 + i * 24 + dx
        if bad:
            p.circle(cx, 130, 7, RED)
        elif fail or i >= typed:
            p.circle(cx, 130, 7, None, outline=MUTED, w=2)
        else:
            p.circle(cx, 130, 7, VIOLET)
    if bad:
        p.text(x, 162, "Wrong passcode", RED, 13, True, seg(t, 0.48, 0.56))
    elif fail:
        p.text(150, 162, "Try again", MUTED, 10)
    return "Fails quietly" if not a else "Shake + red: impossible to miss"


def origin(p, t, a):
    for i in range(3):
        p.rect(24, 48 + i * 34, 210 - i * 40, 70 + i * 34, "#ffffff", 6, 0.08)
    bx, by, tap = 248, 168, 0.15
    final = (96, 44, 270, 144)
    if t >= tap:
        if a:
            k = spring(seg(t, tap, tap + 0.55))
            al = clamp(k * 2.5)
            box = [lerp(bx, final[0], k), lerp(by, final[1], k), lerp(bx, final[2], k), lerp(by, final[3], k)]
        else:
            al, box = seg(t, tap + 0.06, tap + 0.09), list(final)
        sx = (box[2] - box[0]) / (final[2] - final[0])
        sy = (box[3] - box[1]) / (final[3] - final[1])

        def m(x, y): return box[0] + (x - final[0]) * sx, box[1] + (y - final[1]) * sy
        p.card(*box, CARD, 12, al)
        for i, c in enumerate((CYAN, AMBER, PINK)):
            cx, cy = m(118, 68 + i * 26)
            x2, _ = m(136 + (100, 72, 88)[i], 0)
            p.circle(cx, cy, 8 * min(sx, sy), c, al)
            p.rect(cx + 16 * sx, cy - 4 * sy, x2, cy + 4 * sy, BAR2, 4, al)
    p.circle(bx, by + 3, 20, "#000000", 0.3)
    p.circle(bx, by, 20, PINK)
    p.line([(bx - 7, by), (bx + 7, by)], "#ffffff", 3)
    p.line([(bx, by - 7), (bx, by + 7)], "#ffffff", 3)
    p.ripple(bx, by, t - tap)
    return "Pops in from nowhere" if not a else "Grows out of the button"


def staggering(p, t, a):
    for i in range(5):
        s0 = 0.08 + (i * 0.08 if a else 0)
        k = ease_out(seg(t, s0, s0 + 0.3))
        list_rows(p, 42 + i * 32 + (1 - k) * 28, 1, a=k, x0=28, x1=272, first=i)
    return "Everything at once" if not a else "One after another"


def _bounce(tt): return 110 * abs(math.cos(tt * math.pi * 3.5)) * (1 - tt) ** 1.5


def squash(p, t, a):
    tt = seg(t, 0.04, 0.95)
    h = _bounce(tt)
    v = abs(_bounce(min(tt + 0.004, 1)) - _bounce(max(tt - 0.004, 0)))
    sx = sy = 1.0
    if a:
        if h < 10:
            q = (1 - h / 10) * 0.45 * (1 - tt)
            sx, sy = 1 + q, 1 - q * 0.8
        else:
            st = min(0.3, v * 0.08)
            sx, sy = 1 - st * 0.5, 1 + st
    floor, r = 182, 18
    p.line([(40, floor), (260, floor)], "#ffffff", 2, 0.15)
    sh = 1 - h / 160
    p.ellipse(150, floor + 2, 24 * sh * sx, 5 * sh, "#000000", 0.45 * sh)
    cy = floor - h - r * sy
    p.ellipse(150, cy, r * sx, r * sy, AMBER)
    p.ellipse(150 + 4 * sx, cy + 5 * sy, 12 * sx, 10 * sy, ORANGE, 0.5)
    p.ellipse(150 - 6 * sx, cy - 6 * sy, 5 * sx, 4 * sy, "#ffffff", 0.6)
    return "Rigid, like a rock" if not a else "Squash on impact, stretch in flight"


def rubber(p, t, a):
    rel = 0.55
    pull = 90 * ease(seg(t, 0.12, 0.5)) if t < rel else 0
    held = 90 * 0.42
    off = (pull * 0.42 if t < rel else held * (1 - spring(seg(t, rel, 0.95)))) if a else 0
    if off > 4:
        rot = t * 2400 % 360
        p.arc(150, 44 + off / 2, 8, rot, rot + 270, CYAN, 3, clamp(off / 30))
    list_rows(p, 46, 4, off=off)
    if 0.1 < t < rel:
        p.circle(228, 60 + pull, 13, "#ffffff", 0.35)
        p.circle(228, 60 + pull, 13, None, outline="#ffffff", w=2, a=0.8)
    p.ripple(228, 60, t - 0.1)
    return "Hard stop at the edge" if not a else "Stretches, then springs back"


def doherty(p, t, a):
    tap = 0.18
    resp = tap + (0.027 if a else 0.4)  # 1 t unit = 3 s, so 80 ms vs 1200 ms
    done = tap + (0.12 if a else 0.4)
    cx, cy = along(t, [(0.02, tap - 0.02, (60, 190), (172, 106))])
    sc = 0.94 if a and tap <= t < tap + 0.03 else 1
    w, h = 64 * sc, 20 * sc
    if t < resp:
        col, label = "#475569", "Save"
    elif t < done:
        col, label = VIOLET, ""
    else:
        col, label = EMERALD, "Saved"
    p.card(150 - w, 100 - h, 150 + w, 100 + h, col, 12)
    if label == "Saved":
        p.check(124, 100, 6, "#ffffff", 3, seg(t, done, done + 0.06))
        p.text(160, 99, label, "#ffffff", 13, True)
    elif label:
        p.text(150, 99, label, "#ffffff", 13, True)
    else:
        rot = t * 2400 % 360
        p.arc(150, 100, 8, rot, rot + 270, "#ffffff", 3)
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - tap)
    if t >= tap:
        ms = int((min(t, resp) - tap) * 3000)
        col = MUTED if t < resp else (EMERALD if a else RED)
        p.text(150, 160, f"first response: {ms} ms", col, 11, t >= resp)
    return "Nothing happens for 1.2 s" if not a else "Instant feedback"


def anticipation(p, t, a):
    start, target = (66, 130), (232, 84)

    def pos(tt):
        if not a:
            u, sc = ease(seg(tt, 0.12, 0.5)), 1.0
        elif tt < 0.3:
            w = ease_out(seg(tt, 0.08, 0.3))
            u, sc = -0.15 * w, 1 - 0.15 * w
        else:
            u, sc = lerp(-0.15, 1, ease(seg(tt, 0.3, 0.62))), lerp(0.85, 1, ease_out(seg(tt, 0.3, 0.4)))
        return lerp(start[0], target[0], u), lerp(start[1], target[1], u), sc

    arrive = 0.62 if a else 0.5
    p.circle(*target, 26, None, outline=EMERALD, w=3, a=0.8)
    if t >= arrive:
        k = seg(t, arrive, arrive + 0.2)
        p.circle(*target, 26 + 18 * ease_out(k), None, outline=EMERALD, w=3, a=1 - k)
    for j in range(5, 0, -1):  # motion trail
        x, y, sc = pos(t - j * 0.012)
        p.rect(x - 20 * sc, y - 14 * sc, x + 20 * sc, y + 14 * sc, BLUE, 6, 0.06 * (6 - j))
    x, y, sc = pos(t)
    p.card(x - 20 * sc, y - 14 * sc, x + 20 * sc, y + 14 * sc, BLUE, 6)
    p.line([(x - 13 * sc, y - 7 * sc), (x, y + 2 * sc), (x + 13 * sc, y - 7 * sc)], "#ffffff", 2)
    return "Just leaves" if not a else "Winds up, then goes"


def fitts(p, t, a):
    start = (64, 176)
    if a:
        btn, segs, click = (104, 120, 224, 160), [(0.06, 0.3, start, (170, 142))], 0.33
    else:
        btn = (258, 42, 276, 54)
        segs, click = [(0.06, 0.48, start, (283, 36)), (0.5, 0.68, (283, 36), (266, 47))], 0.72
    hit = t >= click
    big = a
    p.card(*btn, EMERALD if hit else BLUE, 10 if big else 4)
    if big:
        p.text((btn[0] + btn[2]) / 2, (btn[1] + btn[3]) / 2 - 1, "Done!" if hit else "Buy now", DARK, 13, True)
    cx, cy = along(t, segs)
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - click)
    if hit:
        p.text(150, 196 if not big else 80, f"{(click - 0.06) * 3:.1f} s to hit", EMERALD if a else RED, 11, True)
    return "Small and far away" if not a else "Big and close to the cursor"


def easing(p, t, a):
    f = ease if a else clamp
    u = seg(t, 0.1, 0.8)
    p.line([(40, 130), (260, 130)], "#ffffff", 2, 0.12)
    for j in range(10, 0, -1):  # ghost trail: spacing shows speed
        p.circle(40 + 220 * f(seg(t - j * 0.018, 0.1, 0.8)), 130, 14, CYAN, 0.05 * (11 - j))
    p.circle(40 + 220 * f(u), 130, 14, CYAN)
    p.circle(36 + 220 * f(u), 126, 4, "#ffffff", 0.6)
    gx, gy, gw, gh = 196, 44, 76, 50  # mini curve graph
    p.rect(gx - 8, gy - 8, gx + gw + 8, gy + gh + 8, "#ffffff", 8, 0.07)
    p.line([(gx + gw * i / 40, gy + gh - gh * f(i / 40)) for i in range(41)], CYAN, 2, 0.9)
    p.circle(gx + gw * u, gy + gh - gh * f(u), 3.5, "#ffffff")
    return "Linear: robotic" if not a else "Ease in, ease out: natural"


def hick(p, t, a):
    if a:
        items, target, dwell = (("Home", CYAN), ("Search", PINK), ("Share", AMBER), ("Settings", VIOLET)), 2, 0.06
    else:
        names = ("Home", "Search", "Library", "Downloads", "Settings", "Profile", "Share", "Help", "About")
        items, target, dwell = tuple((nm, RAINBOW[i % 7]) for i, nm in enumerate(names)), 6, 0.07
    n, top, bot, start = len(items), 44, 188, 0.1
    h = (bot - top) / n
    idx = min(target, int((t - start) / dwell)) if t >= start else -1
    picked_t = start + (target + 1) * dwell + 0.03
    picked = t >= picked_t
    p.card(80, top - 6, 220, bot + 6, CARD, 12)
    for i, (lbl, c) in enumerate(items):
        y0 = top + i * h
        if i == idx:
            p.rect(86, y0 + 1, 214, y0 + h - 1, EMERALD if picked else "#e2e8f0", 6)
        p.circle(100, y0 + h / 2, min(5, h / 3.5), c)
        p.text(112, y0 + h / 2, lbl, DARK, 11 if a else 9, a and i == idx, anchor="lm")
    if picked:
        p.text(252, 21, f"{(picked_t - start) * 3:.1f} s", EMERALD if a else RED, 12, True)
    return "9 choices: slow to scan" if not a else "4 choices: quick pick"


def follow(p, t, a):
    k1 = ease_out(seg(t, 0.08, 0.45))
    cx = lerp(24, 126, k1)
    if a:
        lag = (spring(seg(t, 0.12, 0.85)) - k1) * 102 * 0.35
        k = seg(t, 0.4, 0.95)
        bob = -9 * math.sin(math.pi * 3 * k) * (1 - k)
    else:
        lag = bob = 0
    p.card(cx, 56, cx + 150, 164, CARD, 14)
    ix = cx + lag
    p.circle(ix + 28, 84, 12, PINK)
    p.rect(ix + 48, 77, ix + 128, 85, BAR, 4)
    p.rect(ix + 48, 90, ix + 108, 96, BAR2, 3)
    p.rect(ix + 16, 110, ix + 134, 152, CYAN, 8, 0.35)
    p.circle(ix + 40, 124, 6, AMBER)
    p.circle(cx + 150 + lag * 0.5, 58 + bob, 11, AMBER)
    p.text(cx + 150 + lag * 0.5, 57 + bob, "3", DARK, 10, True)
    return "Everything stops dead" if not a else "Details settle a beat later"


def arcs(p, t, a):
    fab, tap = (64, 170), 0.1
    for j, (tx, ty, c) in enumerate(((150, 54, PINK), (226, 62, AMBER), (246, 134, CYAN))):
        def pt(u):
            if a:  # quadratic bezier: rise first, then swing over
                return ((1 - u) ** 2 * fab[0] + 2 * (1 - u) * u * fab[0] + u * u * tx,
                        (1 - u) ** 2 * fab[1] + 2 * (1 - u) * u * ty + u * u * ty)
            return lerp(fab[0], tx, u), lerp(fab[1], ty, u)
        u = ease(seg(t, tap + j * 0.06, tap + j * 0.06 + 0.4))
        if u > 0:
            p.line([pt(u * i / 30) for i in range(31)], c, 2, 0.35)
            x, y = pt(u)
            p.circle(x, y + 3, 14, "#000000", 0.25)
            p.circle(x, y, 14, c)
            p.circle(x, y, 4, "#ffffff", 0.9)
    rot = math.radians(45 * ease(seg(t, tap, tap + 0.2)))
    p.circle(fab[0], fab[1] + 3, 20, "#000000", 0.3)
    p.circle(*fab, 20, VIOLET)
    for ang in (rot, rot + math.pi / 2):
        dx, dy = 7 * math.cos(ang), 7 * math.sin(ang)
        p.line([(fab[0] - dx, fab[1] - dy), (fab[0] + dx, fab[1] + dy)], "#ffffff", 3)
    p.ripple(*fab, t - tap)
    return "Straight lines: mechanical" if not a else "Curved paths: natural"


def restorff(p, t, a):
    if a:
        segs, click = [(0.1, 0.38, (150, 205), (150, 140))], 0.42
    else:
        segs = [(0.1, 0.3, (150, 205), (62, 140)), (0.32, 0.5, (62, 140), (238, 140)), (0.52, 0.68, (238, 140), (150, 140))]
        click = 0.72
    for i, price in enumerate(("$5", "$12", "$29")):
        x0, hi = 22 + i * 88, a and i == 1
        g = 6 * spring(seg(t, 0.05, 0.4)) if hi else 0
        p.card(x0 - g, 50 - g, x0 + 80 + g, 168 + g, VIOLET if hi else CARD, 12)
        if t >= click and i == 1:
            p.rect(x0 - g - 3, 47 - g, x0 + 83 + g, 171 + g, None, 14, outline=EMERALD, w=3)
        p.text(x0 + 40, 90, price, "#ffffff" if hi else DARK, 18, True)
        p.text(x0 + 40, 111, "/ month", "#e9d5ff" if hi else "#64748b", 9)
        p.rect(x0 + 14, 132, x0 + 66, 148, AMBER if hi else BAR2, 8)
        if hi:
            p.rect(x0 + 8, 40 - g, x0 + 72, 56 - g, AMBER, 8)
            p.text(x0 + 40, 47 - g, "POPULAR", DARK, 8, True)
    cx, cy = along(t, segs)
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - click)
    return "Nothing stands out: users hesitate" if not a else "The pick stands out"


def timing(p, t, a):
    tap, dur = 0.1, (0.067 if a else 0.3)  # 200 ms vs 900 ms
    ready = tap + dur
    k = ease(seg(t, tap, ready))
    p.card(90, 40, 210, 66, CARD, 10)
    p.text(140, 52, "Sort by", DARK, 11, True)
    ang = math.pi * k  # chevron flips from down to up as the menu opens
    p.line([(186 + px * math.cos(ang) - py * math.sin(ang), 53 + px * math.sin(ang) + py * math.cos(ang))
            for px, py in ((-4, -2), (0, 2), (4, -2))], DARK, 2)
    hgt = 112 * k
    pick = ready + 0.16
    if hgt > 2:
        p.card(90, 72, 210, 72 + hgt, CARD, 10)
        for i, (lbl, c) in enumerate((("Newest", CYAN), ("Popular", PINK), ("Price", AMBER), ("Rating", VIOLET))):
            y = 86 + i * 26
            if y + 8 < 72 + hgt:
                if i == 1 and t >= pick:
                    p.rect(96, y - 10, 204, y + 10, EMERALD, 6, 0.3)
                p.circle(106, y, 5, c)
                p.text(118, y, lbl, DARK, 10, anchor="lm")
    cx, cy = along(t, [(0.0, tap - 0.01, (240, 190), (176, 54)), (ready + 0.02, pick - 0.01, (176, 54), (160, 112))])
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - tap)
    p.ripple(cx, cy, t - pick)
    p.text(256, 21, "200 ms" if a else "900 ms", EMERALD if a else RED, 12, True)
    return "Sluggish: you wait for it" if not a else "Snappy: ready when you are"


def interruptible(p, t, a):
    tap = 0.32

    def open_k(tt): return ease_out(seg(tt, 0.08, 0.6))
    if not a:
        k = open_k(t) if t < 0.62 else 1 - ease(seg(t, 0.62, 0.85))
    elif t < tap:
        k = open_k(t)
    else:
        k = open_k(tap) * (1 - ease_out(seg(t, tap, tap + 0.25)))
    list_rows(p, 46, 4)
    p.rect(0, 0, PW, PH, "#000000", 14, 0.45 * k)
    y = lerp(198, 72, k)
    if y < 194:
        p.rect(16, y, 284, 198, CARD, 16)
        p.rect(140, y + 8, 160, y + 12, BAR2, 2)
        for i, c in enumerate((PINK, CYAN, AMBER)):
            if y + 26 + i * 30 < 190:
                p.circle(40, y + 32 + i * 30, 8, c)
                p.rect(56, y + 28 + i * 30, 56 + (150, 110, 130)[i], y + 36 + i * 30, BAR2, 4)
    p.ripple(150, 48, t - tap)
    return "Ignores the tap, finishes first" if not a else "Reverses the moment you tap"


def secondary(p, t, a):
    tap = 0.2
    liked = t >= tap
    p.card(60, 36, 240, 190, CARD, 14)
    p.rect(70, 46, 230, 140, BLUE, 10)
    p.circle(112, 78, 13, AMBER)
    p.poly([(70, 140), (130, 92), (170, 124), (196, 104), (230, 132), (230, 140)], EMERALD)
    hx, hy = 88, 164
    if a and liked:
        k = seg(t, tap, tap + 0.25)
        p.circle(hx, hy, 10 + 24 * ease_out(k), None, outline=PINK, w=3 * (1 - k), a=1 - k)
        for i in range(10):
            ang = i * math.pi / 5 + 0.3
            d = 14 + 26 * ease_out(seg(t, tap, tap + 0.35))
            p.circle(hx + d * math.cos(ang), hy + d * math.sin(ang), 3 * (1 - seg(t, tap + 0.1, tap + 0.4)), RAINBOW[i % 7])
        sc = lerp(0.5, 1, spring(seg(t, tap, tap + 0.5)))
    else:
        sc = 1
    if liked:
        p.heart(hx, hy, 11 * sc, RED)
    else:
        p.heart(hx, hy, 11, None, outline="#64748b", w=2)
    if a and liked:
        k = ease_out(seg(t, tap, tap + 0.15))
        p.text(106, hy - 14 * k, "41", "#64748b", 12, True, 1 - k, anchor="lm")
        p.text(106, hy + 14 * (1 - k), "42", RED, 12, True, k, anchor="lm")
    else:
        p.text(106, hy, "42" if liked else "41", RED if liked else "#64748b", 12, True, anchor="lm")
    p.ripple(hx, hy, t - tap)
    return "Heart just turns red" if not a else "Pop, burst and count roll"


def frequency(p, t, a):
    taps, seq = (0.12, 0.24, 0.36), (1, 2, 0)
    colors, names = (CYAN, PINK, AMBER), ("Home", "Explore", "Profile")
    trans, end, prev = [], 0.0, 0
    for tt, i in zip(taps, seq):  # before: each 600 ms transition waits for the previous one
        s0 = tt if a else max(tt, end)
        d = 0 if a else 0.2
        end = s0 + d
        trans.append((s0, d, prev, i))
        prev = i
    shown_prev, shown, k = 0, 0, 1.0
    for s0, d, pi, i in trans:
        if t >= s0:
            shown_prev, shown, k = pi, i, (1.0 if d == 0 else ease(seg(t, s0, s0 + d)))
    selected = 0
    for tt, i in zip(taps, seq):
        if t >= tt:
            selected = i
    for idx, al, dy in ((shown_prev, 1 - k, 0), (shown, k, (1 - k) * 12)):
        if al > 0.01 and not (idx == shown and idx == shown_prev and al < 1):
            p.card(40, 44 + dy, 260, 150 + dy, colors[idx], 14, al)
            p.text(150, 97 + dy, names[idx], DARK, 16, True, al)
    p.rect(28, 160, 272, 194, "#ffffff", 14, 0.1)
    for i in range(3):
        x = 70 + i * 80
        p.circle(x, 172, 5, colors[i], 1 if i == selected else 0.5)
        p.text(x, 185, names[i], INK if i == selected else MUTED, 8, i == selected)
    for tt, i in zip(taps, seq):
        p.ripple(70 + i * 80, 178, t - tt)
    return "Animates every switch: laggy" if not a else "Instant: you do this all day"


def peak_end(p, t, a):
    k = ease(seg(t, 0.05, 0.55))
    done = t >= 0.58
    p.card(40, 46, 260, 176, CARD, 14)
    p.rect(58, 62, 82, 92, BLUE, 4)
    p.poly([(74, 62), (82, 62), (82, 70)], "#bfdbfe")
    p.rect(94, 68, 200, 76, BAR, 4)
    p.rect(94, 82, 160, 88, BAR2, 3)
    if not (a and done):
        p.rect(58, 122, 242, 132, "#e2e8f0", 5)
        p.rect(58, 122, 58 + 184 * k, 132, VIOLET, 5)
        p.text(242, 110, f"{int(k * 100)}%", "#64748b", 9, anchor="rm")
        if done:
            p.text(150, 154, "Upload complete", "#64748b", 10)
    else:
        m = ease(seg(t, 0.58, 0.64))
        if m < 1:
            w = lerp(184, 10, m)
            p.rect(150 - w / 2, 122, 150 + w / 2, 132, VIOLET, 5)
        r = 17 * spring(seg(t, 0.62, 0.95))
        p.circle(150, 127, r, EMERALD)
        if t >= 0.66:
            p.check(150, 127, 7, "#ffffff", 3, seg(t, 0.66, 0.76))
        p.text(150, 160, "Uploaded!", "#059669", 13, True, seg(t, 0.68, 0.76))
        ct = seg(t, 0.62, 1.0) * 1.3
        for i in range(30):  # confetti with gravity
            ang = i * 2.39996
            spd = 60 + (i * 37) % 50
            x = 150 + math.cos(ang) * spd * ct
            y = 127 + (math.sin(ang) * spd - 60) * ct + 150 * ct * ct
            if 4 < x < PW - 4 and 4 < y < 200:
                p.rect(x - 2, y - 3.5, x + 2, y + 3.5, RAINBOW[i % 7], 1, 1 - seg(t, 0.85, 1.0))
    return "Ends flat" if not a else "Ends on a win"


SWATCH = (PINK, VIOLET, CYAN, AMBER, EMERALD, BLUE, RED, ORANGE, INK, MUTED, DARK, BAR, BAR2, "#ffffff",
          "#475569", "#64748b", "#e2e8f0", "#059669", "#e9d5ff", "#bfdbfe", "#334155")

PRINCIPLES = [exaggeration, origin, staggering, squash, rubber, doherty, anticipation, fitts, easing,
              hick, follow, arcs, restorff, timing, interruptible, secondary, frequency, peak_end]


def background():
    img = Image.new("RGB", (W * S, H * S), BG)
    size = (PW * S, PH * S)
    grad = Image.linear_gradient("L").resize(size)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], 14 * S, fill=255)
    for col, after in enumerate((False, True)):
        top, bot = GRAD[after]
        panel = Image.composite(Image.new("RGB", size, bot), Image.new("RGB", size, top), grad)
        img.paste(panel, ((M + col * (PW + GAP)) * S, M * S), mask)
    return img


def render(fn):
    bg, frames = background(), []
    for f in range(MOVE + HOLD):
        t = min(f / (MOVE - 1), 1.0)
        img = bg.copy()
        d = ImageDraw.Draw(img, "RGBA")
        for col, after in enumerate((False, True)):
            p = Panel(d, M + col * (PW + GAP), after)
            p.chrome(fn(p, t, after))
        # loop progress bar; also keeps every frame distinct so the GIF writer can't merge frames below FPS
        d.rectangle([M * S, (H - 4) * S, (M + (W - 2 * M) * (f + 1) / N) * S, (H - 2) * S], fill=rgba("#334155"))
        frames.append(img.resize((W, H), Image.LANCZOS))
    last = frames[-1]
    for i in range(FADE):  # crossfade back to the first frame for a seamless loop
        frames.append(Image.blend(last, frames[0], (i + 1) / (FADE + 1)))
    # one shared palette for every frame avoids colour flicker; big theme-colour swatches make sure
    # small saturated details get exact palette entries instead of losing out to the gradients
    picks = frames[::len(frames) // 12]
    sample = Image.new("RGB", (W, H * (len(picks) + 6)))
    for i, fr in enumerate(picks):
        sample.paste(fr, (0, H * i))
    sw = W / len(SWATCH)
    sd = ImageDraw.Draw(sample)
    for i, c in enumerate(SWATCH):
        sd.rectangle([int(i * sw), H * len(picks), int((i + 1) * sw), sample.height], fill=c)
    pal = sample.quantize(256, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = OUT / f"{fn.__name__.replace('_', '-')}.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=1000 // FPS, loop=0)
    with Image.open(path) as im:
        assert im.n_frames == N, f"{path.name}: {im.n_frames} frames, expected {N}"
    return path


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for fn in PRINCIPLES:
        if not wanted or fn.__name__ in wanted:
            print(render(fn).name)
