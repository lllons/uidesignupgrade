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
PW, PH, GAP, M = 300, 212, 16, 10  # panel size, gap between panels, outer margin
W, H = M * 2 + PW * 2 + GAP, M * 2 + PH
OUT = Path(__file__).parent

# Monochrome system: white surfaces, black foreground, one accent; red/green only for error/success.
BG, CARD, LINE, SUBTLE = "#ffffff", "#ffffff", "#e5e5e5", "#f5f5f5"
DARK = INK = "#0a0a0a"
MUTED, G300, G400, G600 = "#737373", "#d4d4d4", "#a3a3a3", "#525252"
ACCENT, ACCENT_SOFT = "#0057ff", "#e6eeff"
EMERALD, RED = "#16a34a", "#dc2626"
# legacy names used by the demos, mapped onto the system
PINK, VIOLET, CYAN, AMBER, BLUE, ORANGE = ACCENT, DARK, G600, G400, ACCENT, G300
BAR, BAR2 = G400, LINE
RAINBOW = (DARK, G400, ACCENT, G300, G600, MUTED, G300)


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

    def card(s, x0, y0, x1, y1, c=CARD, r=10, a=1.0):  # hairline border + barely-there shadow, no glow
        s.rect(x0, y0 + 2, x1, y1 + 3, "#000000", r, 0.05 * a)
        s.rect(x0, y0, x1, y1, c, r, a, outline=LINE if c == CARD else None, w=1)

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
            s.circle(x, y, 7 + 20 * ease_out(k), None, outline=DARK, w=2, a=0.5 * (1 - k))
            s.circle(x, y, 8, DARK, 0.15 * (1 - k))

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

    def chrome(s):  # plain labels, no badge pills; the explanation lives in the README, not in the GIF
        s.text(14, 21, "After" if s.after else "Before", DARK if s.after else MUTED, 11, s.after, anchor="lm")


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
        p.rect(24, 48 + i * 34, 210 - i * 40, 70 + i * 34, "#000000", 6, 0.04)
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
    p.circle(bx, by + 2, 20, "#000000", 0.08)
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
    p.line([(40, floor), (260, floor)], "#000000", 2, 0.15)
    sh = 1 - h / 160
    p.ellipse(150, floor + 2, 24 * sh * sx, 5 * sh, "#000000", 0.45 * sh)
    cy = floor - h - r * sy
    p.ellipse(150, cy, r * sx, r * sy, ACCENT)
    p.ellipse(150 + 4 * sx, cy + 5 * sy, 12 * sx, 10 * sy, "#003db3", 0.35)
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
        p.circle(228, 60 + pull, 13, DARK, 0.08)
        p.circle(228, 60 + pull, 13, None, outline=DARK, w=2, a=0.5)
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
        col, label = DARK, "Save"
    elif t < done:
        col, label = ACCENT, ""
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
        p.text((btn[0] + btn[2]) / 2, (btn[1] + btn[3]) / 2 - 1, "Done!" if hit else "Buy now", "#ffffff", 13, True)
    cx, cy = along(t, segs)
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - click)
    if hit:
        p.text(150, 196 if not big else 80, f"{(click - 0.06) * 3:.1f} s to hit", EMERALD if a else RED, 11, True)
    return "Small and far away" if not a else "Big and close to the cursor"


def easing(p, t, a):
    f = ease if a else clamp
    u = seg(t, 0.1, 0.8)
    p.line([(40, 130), (260, 130)], "#000000", 2, 0.12)
    for j in range(10, 0, -1):  # ghost trail: spacing shows speed
        p.circle(40 + 220 * f(seg(t - j * 0.018, 0.1, 0.8)), 130, 14, ACCENT, 0.05 * (11 - j))
    p.circle(40 + 220 * f(u), 130, 14, ACCENT)
    p.circle(36 + 220 * f(u), 126, 4, "#ffffff", 0.6)
    gx, gy, gw, gh = 196, 44, 76, 50  # mini curve graph
    p.rect(gx - 8, gy - 8, gx + gw + 8, gy + gh + 8, SUBTLE, 8)
    p.line([(gx + gw * i / 40, gy + gh - gh * f(i / 40)) for i in range(41)], ACCENT, 2, 0.9)
    p.circle(gx + gw * u, gy + gh - gh * f(u), 3.5, DARK)
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
            p.rect(86, y0 + 1, 214, y0 + h - 1, EMERALD if picked else LINE, 6)
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
    p.circle(cx + 150 + lag * 0.5, 58 + bob, 11, ACCENT)
    p.text(cx + 150 + lag * 0.5, 57 + bob, "3", "#ffffff", 10, True)
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
            p.circle(x, y + 2, 14, "#000000", 0.08)
            p.circle(x, y, 14, c)
            p.circle(x, y, 4, "#ffffff", 0.9)
    rot = math.radians(45 * ease(seg(t, tap, tap + 0.2)))
    p.circle(fab[0], fab[1] + 2, 20, "#000000", 0.08)
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
        p.text(x0 + 40, 111, "/ month", G400 if hi else MUTED, 9)
        p.rect(x0 + 14, 132, x0 + 66, 148, ACCENT if hi else BAR2, 8)
        if hi:
            p.rect(x0 + 8, 40 - g, x0 + 72, 56 - g, ACCENT, 8)
            p.text(x0 + 40, 47 - g, "Popular", "#ffffff", 8, True)
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
    p.rect(0, 0, PW, PH, "#000000", 14, 0.2 * k)
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
    p.rect(70, 46, 230, 140, ACCENT_SOFT, 10)
    p.circle(112, 78, 13, ACCENT)
    p.poly([(70, 140), (130, 92), (170, 124), (196, 104), (230, 132), (230, 140)], G300)
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
        p.heart(hx, hy, 11, None, outline=MUTED, w=2)
    if a and liked:
        k = ease_out(seg(t, tap, tap + 0.15))
        p.text(106, hy - 14 * k, "41", MUTED, 12, True, 1 - k, anchor="lm")
        p.text(106, hy + 14 * (1 - k), "42", RED, 12, True, k, anchor="lm")
    else:
        p.text(106, hy, "42" if liked else "41", RED if liked else MUTED, 12, True, anchor="lm")
    p.ripple(hx, hy, t - tap)
    return "Heart just turns red" if not a else "Pop, burst and count roll"


def frequency(p, t, a):
    taps, seq = (0.12, 0.24, 0.36), (1, 2, 0)
    colors, names = (DARK, ACCENT, G300), ("Home", "Explore", "Profile")
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
            p.text(150, 97 + dy, names[idx], "#ffffff" if idx < 2 else DARK, 16, True, al)
    p.rect(28, 160, 272, 194, SUBTLE, 14)
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
    p.poly([(74, 62), (82, 62), (82, 70)], ACCENT_SOFT)
    p.rect(94, 68, 200, 76, BAR, 4)
    p.rect(94, 82, 160, 88, BAR2, 3)
    if not (a and done):
        p.rect(58, 122, 242, 132, LINE, 5)
        p.rect(58, 122, 58 + 184 * k, 132, VIOLET, 5)
        p.text(242, 110, f"{int(k * 100)}%", MUTED, 9, anchor="rm")
        if done:
            p.text(150, 154, "Upload complete", MUTED, 10)
    else:
        m = ease(seg(t, 0.58, 0.64))
        if m < 1:
            w = lerp(184, 10, m)
            p.rect(150 - w / 2, 122, 150 + w / 2, 132, VIOLET, 5)
        r = 17 * spring(seg(t, 0.62, 0.95))
        p.circle(150, 127, r, EMERALD)
        if t >= 0.66:
            p.check(150, 127, 7, "#ffffff", 3, seg(t, 0.66, 0.76))
        p.text(150, 160, "Uploaded!", EMERALD, 13, True, seg(t, 0.68, 0.76))
        ct = seg(t, 0.62, 1.0) * 1.3
        for i in range(30):  # confetti with gravity
            ang = i * 2.39996
            spd = 60 + (i * 37) % 50
            x = 150 + math.cos(ang) * spd * ct
            y = 127 + (math.sin(ang) * spd - 60) * ct + 150 * ct * ct
            if 4 < x < PW - 4 and 4 < y < 200:
                p.rect(x - 2, y - 3.5, x + 2, y + 3.5, (ACCENT, EMERALD, DARK)[i % 3], 1, 1 - seg(t, 0.85, 1.0))
    return "Ends flat" if not a else "Ends on a win"


def mix(c1, c2, k):
    x, y = rgba(c1), rgba(c2)
    return "#" + "".join(f"{round(lerp(x[i], y[i], clamp(k))):02x}" for i in range(3))


def chevron(p, x, y, ang, c):
    p.line([(x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang))
            for px, py in ((-4, -2), (0, 2), (4, -2))], c, 2)


def scale_097(p, t, a):
    tap = 0.15
    for i in range(3):
        p.rect(24, 48 + i * 30, 200 - i * 40, 66 + i * 30, "#000000", 6, 0.04)
    sc_btn = 0.97 if a and tap <= t < tap + 0.03 else 1
    p.card(150 - 46 * sc_btn, 172 - 15 * sc_btn, 150 + 46 * sc_btn, 172 + 15 * sc_btn, VIOLET, 10)
    p.text(150, 171, "Publish", "#ffffff", 11, True)
    if t >= tap + 0.02:
        k = seg(t, tap + 0.02, tap + 0.14)
        sc, al = (lerp(0.97, 1, ease_out(k)), ease_out(k)) if a else (ease(k), 1.0)

        def m(x, y): return 150 + (x - 150) * sc, 96 + (y - 96) * sc
        p.card(*m(60, 46), *m(240, 146), CARD, 12 * sc, al)
        if sc > 0.5:
            p.text(*m(150, 68), "Publish this page?", DARK, max(4, round(12 * sc)), True, al)
        p.rect(*m(84, 84), *m(216, 90), BAR2, 3, al)
        p.rect(*m(104, 96), *m(196, 102), BAR2, 3, al)
        p.rect(*m(84, 116), *m(146, 134), LINE, 8, al)
        p.rect(*m(154, 116), *m(216, 134), VIOLET, 8, al)
    cx, cy = along(t, [(0.0, tap - 0.02, (240, 205), (160, 175))])
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - tap)
    return "Zooms up from a dot" if not a else "Scale from 0.97 + fade"


def directional(p, t, a):
    taps = ((0.15, 1, (211, 169)), (0.4, 1, (211, 169)), (0.65, -1, (89, 169)))
    step, prev, k, dirn = 0, 0, 1.0, 1
    for tt, d, _ in taps:
        if t >= tt:
            prev, step, dirn, k = step, step + d, d, ease_out(seg(t, tt, tt + 0.12))
    p.card(30, 40, 270, 190, CARD, 14)
    names, cols = ("Account", "Profile", "Invite team"), (CYAN, PINK, AMBER)
    # old step is gone before the new one is half in, so the two never overlap legibly
    for s_, al, dx in ((prev, 1 - seg(k, 0, 0.45), -dirn * 60 * k), (step, seg(k, 0.35, 1), dirn * 60 * (1 - k))):
        if al > 0.01:
            dx = dx if a else 0
            p.circle(150 + dx, 74, 16, cols[s_], al)
            p.text(150 + dx, 104, f"Step {s_ + 1}: {names[s_]}", DARK, 12, True, al)
            p.rect(96 + dx, 118, 204 + dx, 124, BAR2, 3, al)
    for i in range(3):
        p.circle(132 + i * 18, 142, 4, VIOLET if i == step else BAR2)
    p.rect(60, 158, 118, 180, LINE, 9)
    p.text(89, 168, "Back", DARK, 10, True)
    p.rect(182, 158, 240, 180, VIOLET, 9)
    p.text(211, 168, "Next", "#ffffff", 10, True)
    for tt, _, pos in taps:
        p.ripple(*pos, t - tt)
    return "Every step just fades" if not a else "Next slides left, Back slides right"


def smooth_height(p, t, a):
    t_open, t_close = 0.15, 0.6
    if a:
        k = ease(seg(t, t_open, t_open + 0.12)) - ease(seg(t, t_close, t_close + 0.12))
    else:
        k = 1.0 if t_open <= t < t_close else 0.0
    ext = 48 * k
    p.card(40, 40, 260, 144 + ext, CARD, 12)
    for i, q in enumerate(("How do refunds work?", "Can I change plans later?", "Do you offer a free trial?")):
        y = 48 + i * 30 + (ext if i else 0)
        if i:
            p.rect(52, y - 1, 248, y, LINE, 0)
        p.text(56, y + 15, q, DARK, 10, i == 0 and k > 0.5, anchor="lm")
        chevron(p, 240, y + 15, math.pi * k if i == 0 else 0, DARK)
    if ext > 8:
        al = clamp((ext - 8) / 30)
        p.rect(56, 82, 236, 88, BAR2, 3, al)
        p.rect(56, 94, 200, 100, BAR2, 3, al)
        if ext > 30:
            p.rect(56, 106, 170, 112, BAR2, 3, al)
    p.ripple(200, 63, t - t_open)
    p.ripple(200, 63, t - t_close)
    return "Snaps open, rows jump" if not a else "Animates to its natural height"


def theme_switch(p, t, a):
    taps = (0.15, 0.55)

    def dark_k(dur):  # 0 = light, 1 = dark
        v = 0.0
        for i, tt in enumerate(taps):
            if t >= tt:
                to = 1.0 if i % 2 == 0 else 0.0
                v = lerp(1 - to, to, 1.0 if dur == 0 else ease(seg(t, tt, tt + dur)))
        return v
    kb, kt, kc = (dark_k(d) for d in ((0, 0, 0) if a else (0.1, 0.04, 0.17)))  # bg 300 ms, text 120 ms, chart 500 ms
    p.card(36, 40, 264, 190, mix(CARD, "#171717", kb), 14)
    p.text(56, 62, "Revenue this week", mix(MUTED, MUTED, kt), 10, anchor="lm")
    p.text(56, 86, "$48,210", mix(DARK, "#ffffff", kt), 20, True, anchor="lm")
    for i, h in enumerate((20, 34, 26, 44, 38, 52, 30, 60, 48, 70)):
        c = mix(ACCENT, "#5c8dff", kc) if i == 9 else mix(BAR2, G600, kc)
        p.rect(58 + i * 19, 176 - h, 70 + i * 19, 176, c, 3)
    knob = dark_k(0.04)
    p.rect(222, 54, 252, 70, mix(BAR2, VIOLET, knob), 8)
    p.circle(lerp(230, 244, knob), 62, 6, "#ffffff")
    for tt in taps:
        p.ripple(237, 62, t - tt)
    return "Each part fades at its own speed" if not a else "Swap the whole theme instantly"


def tooltip_delay(p, t, a):
    labels, glyphs = ("Bold", "Italic", "Underline", "Strike", "Link", "Code"), ("B", "I", "U", "S", "#", "</>")
    xs = [66 + i * 34 for i in range(6)]
    hover = ((0.1, 0), (0.45, 1), (0.55, 2), (0.65, 3), (0.75, 4))
    segs = [(0.0, 0.1, (150, 205), (xs[0], 122))]
    segs += [(hover[j - 1][0] + 0.02, hover[j][0], (xs[hover[j - 1][1]], 122), (xs[hover[j][1]], 122)) for j in range(1, 5)]
    cur, since = -1, 0.0
    for tt, i in hover:
        if t >= tt:
            cur, since = i, t - tt
    delay = 0.2  # 600 ms
    p.card(48, 96, 252, 132, CARD, 10)
    for i, (x, g) in enumerate(zip(xs, glyphs)):
        if i == cur:
            p.rect(x - 13, 101, x + 13, 127, LINE, 6)
        p.text(x, 113, g, DARK, 12, True)
    if cur >= 0 and (since >= delay or (a and cur > 0)):
        x, lbl = xs[cur], labels[cur]
        w = font(10).getlength(lbl) / S + 16
        al = 1.0 if (a and cur > 0) else seg(since, delay, delay + 0.03)
        p.rect(x - w / 2, 68, x + w / 2, 88, DARK, 6, al)
        p.poly([(x - 5, 88), (x + 5, 88), (x, 93)], DARK, al)
        p.text(x, 77, lbl, "#ffffff", 10, a=al)
    p.cursor(*along(t, segs))
    return "Waits 600 ms on every button" if not a else "Skips the delay once one is open"


def staging(p, t, a):
    k = ease(seg(t, 0.2, 0.45))
    pulse = math.sin(math.pi * seg(t, 0.2, 0.5))
    cards = ((30, 44, 144, 112, PINK), (156, 44, 270, 112, CYAN), (30, 124, 144, 192, AMBER), (156, 124, 270, 192, EMERALD))
    focus = 1
    order = [i for i in range(4) if i != focus] + [focus]
    for i in order:
        x0, y0, x1, y1, c = cards[i]
        if a:
            g, al = (8 * k, 1.0) if i == focus else (0, 1 - 0.65 * k)
        else:
            g, al = 4 * pulse, 1.0
        p.card(x0 - g, y0 - g, x1 + g, y1 + g, CARD, 12, al)
        p.circle(x0 + 20, y0 + 20, 9, c, al)
        p.rect(x0 + 36, y0 + 16, x1 - 16, y0 + 24, BAR, 4, al)
        p.rect(x0 + 14, y0 + 40, x1 - 30, y0 + 46, BAR2, 3, al)
        p.rect(x0 + 14, y0 + 52, x1 - 50, y0 + 58, BAR2, 3, al)
    return "Everything competes for attention" if not a else "One thing at a time"


def layout_shift(p, t, a):
    load, click = 0.4, 0.45
    loaded = t >= load
    text_y = 134 if (a or loaded) else 66
    p.card(40, 36, 260, 196, CARD, 12)
    p.rect(56, 46, 200, 56, BAR, 4)
    if a:
        p.rect(56, 64, 244, 124, SUBTLE, 8)
    if loaded:
        al = seg(t, load, load + 0.08) if a else 1.0
        p.rect(56, 64, 244, 124, ACCENT_SOFT, 8, al)
        p.circle(92, 84, 9, ACCENT, al)
        p.poly([(56, 124), (110, 94), (150, 114), (190, 96), (244, 120), (244, 124)], G300, al)
    for i, w in enumerate((180, 160, 120)):
        p.rect(56, text_y + i * 10, 56 + w, text_y + i * 10 + 5, BAR2, 3)
    btn_y = text_y + 36
    hit = t >= click and a
    p.rect(56, btn_y, 140, btn_y + 20, EMERALD if hit else VIOLET, 10)
    p.text(98, btn_y + 9, "Read more", "#ffffff", 10, True)
    target = (100, 180) if a else (100, 112)
    cx, cy = along(t, [(0.05, 0.38, (220, 205), target)])
    p.cursor(cx, cy)
    p.ripple(cx, cy, t - click)
    if t >= click:
        p.text(250, 21, "Clicked" if a else "Missed!", EMERALD if a else RED, 12, True, anchor="rm")
    return "Image loads, button jumps away" if not a else "Space reserved, nothing moves"


def reserved_bold(p, t, a):
    tabs, fs = ("Overview", "Customers", "Settings"), 15
    active = 0
    for tt, i in ((0.15, 1), (0.4, 2), (0.65, 0)):
        if t >= tt:
            active = i

    def wd(s, b): return font(fs, b).getlength(s) / S
    stable = [max(wd(s, True), wd(s, False)) + 22 for s in tabs]
    widths = stable if a else [wd(s, i == active) + 22 for i, s in enumerate(tabs)]
    x = 150 - sum(widths) / 2
    p.card(x - 6, 86, x + sum(widths) + 6, 124, CARD, 10)
    for i, s in enumerate(tabs):
        if i == active:
            p.rect(x + 3, 91, x + widths[i] - 3, 119, SUBTLE, 7)
        p.text(x + widths[i] / 2, 104, s, VIOLET if i == active else G600, fs, i == active)
        x += widths[i]
    x0 = 150 - sum(stable) / 2
    centers = [x0 + sum(stable[:i]) + stable[i] / 2 for i in range(3)]
    cx, cy = along(t, [(0.02, 0.14, (150, 200), (centers[1], 108)), (0.27, 0.39, (centers[1], 108), (centers[2], 108)),
                       (0.52, 0.64, (centers[2], 108), (centers[0], 108))])
    p.cursor(cx, cy)
    for tt in (0.15, 0.4, 0.65):
        p.ripple(cx, cy, t - tt)
    return "Bold text widens, tabs shift" if not a else "Width reserved for the bold state"


def tabular_nums(p, t, a):
    v = int(lerp(1000, 48210, ease(seg(t, 0.1, 0.8))))
    s, fs = f"${v:,}", 26
    prop = {"1": 0.42, "7": 0.5, "2": 0.55, "3": 0.55, "4": 0.62, "5": 0.55, "6": 0.58, "8": 0.58, "9": 0.58, "0": 0.6}
    widths = [fs * (0.3 if ch == "," else 0.58 if ch == "$" else (0.6 if a else prop[ch])) for ch in s]
    p.card(50, 60, 250, 170, CARD, 14)
    p.text(70, 82, "Revenue", MUTED, 10, anchor="lm")
    x = 230 - sum(widths)
    for ch, w in zip(s, widths):
        p.text(x + w / 2, 118, ch, DARK, fs, True)
        x += w
    p.rect(176, 140, 230, 156, EMERALD, 8, 0.25)
    p.text(203, 147, "+12.4%", EMERALD, 9, True)
    return "Digits change width: jittery" if not a else "Tabular figures: rock steady"


def _product_page(p, count, bump=0.0):
    p.text(40, 44, "VEYND", DARK, 11, True, anchor="lm")
    p.rect(238, 36, 256, 54, None, 5, outline=DARK, w=2)  # bag icon
    if count:
        p.circle(256, 37, 7 + 3 * bump, ACCENT)
        p.text(256, 36, str(count), "#ffffff", 8, True)
    p.rect(40, 62, 260, 122, ACCENT_SOFT, 10)
    p.rect(110, 78, 190, 106, DARK, 14)  # the speaker
    p.text(40, 136, "Capsule speaker", DARK, 11, True, anchor="lm")
    p.text(260, 136, "$249", DARK, 11, True, anchor="rm")
    p.rect(40, 150, 260, 172, DARK, 11)
    p.text(150, 160, "Add to bag", "#ffffff", 10, True)
    p.text(40, 186, "Complete the set", MUTED, 9, anchor="lm")
    for i in range(3):
        p.rect(40 + i * 40, 194, 72 + i * 40, 204, SUBTLE, 4)


def add_to_cart(p, t, a):
    tap, leave = 0.15, 0.6
    add_btn, keep_btn, back_btn = (150, 160), (196, 176), (52, 44)
    if not a:  # jumps to a cart page, shopper has to go Back to keep shopping
        if tap <= t < leave:
            p.text(52, 44, "‹ Back", DARK, 11, True, anchor="lm")
            p.text(150, 70, "Your bag", DARK, 14, True)
            p.rect(40, 88, 260, 124, None, 8, outline=LINE, w=1)
            p.rect(48, 94, 72, 118, DARK, 6)
            p.text(82, 106, "Capsule speaker", DARK, 10, anchor="lm")
            p.text(252, 106, "$249", DARK, 10, True, anchor="rm")
            p.rect(40, 150, 260, 172, DARK, 11)
            p.text(150, 160, "Checkout · $249", "#ffffff", 10, True)
        else:
            _product_page(p, 1 if t >= leave else 0)
        cx, cy = along(t, [(0.0, tap - 0.02, (230, 200), add_btn), (0.4, leave - 0.02, add_btn, back_btn),
                           (leave + 0.05, 0.8, back_btn, (100, 199))])
        clicks = (tap, leave)
    else:  # drawer slides in, stays until the shopper chooses
        k = ease_out(seg(t, tap, tap + 0.12)) * (1 - ease(seg(t, leave, leave + 0.1)))
        _product_page(p, 1 if t >= tap else 0, math.sin(math.pi * seg(t, leave + 0.05, leave + 0.15)))
        if k > 0.01:
            p.rect(0, 0, PW, PH, "#000000", 14, 0.25 * k)
            x = lerp(PW, 112, k)
            p.rect(x, 28, PW - 1, PH - 1, CARD, 12)
            if x < 280:
                p.circle(x + 18, 48, 7, EMERALD)
                p.check(x + 18, 48, 3.5, "#ffffff", 2)
                p.text(x + 32, 48, "Added to bag", DARK, 10, True, anchor="lm")
                p.rect(x + 12, 64, x + 40, 92, DARK, 6)
                p.text(x + 48, 72, "Capsule speaker", DARK, 9, anchor="lm")
                p.text(x + 48, 86, "Ember · $249", MUTED, 9, anchor="lm")
                bx1 = PW - 12  # buttons anchored to the drawer's right edge so they never leave the panel
                p.rect(x + 12, 140, bx1, 160, DARK, 10)
                p.text((x + 12 + bx1) / 2, 149, "Checkout", "#ffffff", 9, True)
                p.rect(x + 12, 166, bx1, 186, None, 10, outline=DARK, w=1)
                p.text((x + 12 + bx1) / 2, 175, "Keep shopping", DARK, 9, True)
        cx, cy = along(t, [(0.0, tap - 0.02, (230, 200), add_btn), (0.35, leave - 0.02, add_btn, keep_btn),
                           (leave + 0.05, 0.85, keep_btn, (120, 198))])
        clicks = (tap, leave)
    p.cursor(cx, cy)
    for c in clicks:
        p.ripple(cx, cy, t - c)
    return "Jumps to the cart, shopper loses their place" if not a else "Cart slides in and stays: keep shopping or check out"


SWATCH = (BG, DARK, MUTED, G300, G400, G600, LINE, SUBTLE, ACCENT, ACCENT_SOFT, EMERALD, RED, "#ebebeb")

PRINCIPLES = [exaggeration, origin, staggering, squash, rubber, doherty, anticipation, fitts, easing,
              hick, follow, arcs, restorff, timing, interruptible, secondary, frequency, peak_end,
              scale_097, directional, smooth_height, theme_switch, tooltip_delay, staging, layout_shift,
              reserved_bold, tabular_nums, add_to_cart]


def background():
    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img)
    for col in range(2):  # flat white panels separated by a hairline border, no gradients
        x0 = (M + col * (PW + GAP)) * S
        d.rounded_rectangle([x0, M * S, x0 + PW * S, (M + PH) * S], 14 * S, fill=BG, outline=LINE, width=S)
    return img


def render(fn):
    bg, frames, captions = background(), [], {}
    for f in range(MOVE + HOLD):
        t = min(f / (MOVE - 1), 1.0)
        img = bg.copy()
        d = ImageDraw.Draw(img, "RGBA")
        for col, after in enumerate((False, True)):
            p = Panel(d, M + col * (PW + GAP), after)
            captions[after] = fn(p, t, after)
            p.chrome()
        # loop progress bar; also keeps every frame distinct so the GIF writer can't merge frames below FPS
        d.rectangle([M * S, (H - 4) * S, (M + (W - 2 * M) * (f + 1) / N) * S, (H - 2) * S], fill=rgba(LINE))
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
    return path, captions


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for fn in PRINCIPLES:
        if not wanted or fn.__name__ in wanted:
            path, cap = render(fn)  # captions go in the README's principle column
            print(f"{path.name}\tBefore: {cap[False]}. After: {cap[True]}.")
