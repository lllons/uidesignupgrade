"""Regenerate the brand assets: python assets/brand/make_brand.py  (needs Pillow)
Mark: a black squircle with a white ease-in-out curve (the motion that gives the skill its name)
and a trail of four accent beads leading to the end point. Black and white, colour only as accent."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
ROOT = OUT.parents[1]
INK, PAPER, MUTED = "#0a0a0a", "#ffffff", "#737373"
ACCENTS = ("#0057ff", "#ff3d7f", "#ffb800", "#16c47f")  # blue, pink, amber, green
P0, C1, C2, P3 = (120, 372), (272, 372), (240, 150), (392, 150)  # cubic bezier in a 512 box
BEADS = ((0.52, 13), (0.63, 15), (0.74, 17), (0.85, 19))  # (t on curve, radius)


def bez(t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(P0, C1, C2, P3))


def svg():
    beads = "".join(f'<circle cx="{bez(t)[0]:.1f}" cy="{bez(t)[1]:.1f}" r="{r}" fill="{c}"/>'
                    for (t, r), c in zip(BEADS, ACCENTS))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="uidesignupgrade">'
            f'<rect width="512" height="512" rx="116" fill="{INK}"/>'
            f'<path d="M{P0[0]} {P0[1]} C{C1[0]} {C1[1]} {C2[0]} {C2[1]} {P3[0]} {P3[1]}" fill="none" stroke="{PAPER}" '
            f'stroke-width="34" stroke-linecap="round"/>{beads}<circle cx="{P3[0]}" cy="{P3[1]}" r="40" fill="{PAPER}"/></svg>\n')


def mark(size):
    s = size * 4 / 512  # draw at 4x, then downsample for clean edges
    img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size * 4 - 1, size * 4 - 1], 116 * s, fill=INK)
    h = 17 * s  # stroke as overlapping discs: smooth edges and round caps, unlike thick PIL lines
    for i in range(801):
        x, y = (v * s for v in bez(i / 800))
        d.ellipse([x - h, y - h, x + h, y + h], fill=PAPER)
    for (t, r), c in zip(BEADS, ACCENTS):
        x, y = (v * s for v in bez(t))
        d.ellipse([x - r * s, y - r * s, x + r * s, y + r * s], fill=c)
    x, y = (v * s for v in P3)
    d.ellipse([x - 40 * s, y - 40 * s, x + 40 * s, y + 40 * s], fill=PAPER)
    return img.resize((size, size), Image.LANCZOS)


def font(size, bold):
    for name in (("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def banner(w=1280, h=640):
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    m = mark(300)
    img.paste(m, (110, (h - 300) // 2), m)
    x = 470
    d.text((x, 205), "uidesignupgrade", fill=INK, font=font(76, True))
    d.text((x, 310), "UX laws, motion, typography and colour", fill=INK, font=font(34, False))
    d.text((x, 356), "for any coding agent.", fill=INK, font=font(34, False))
    for i, c in enumerate(ACCENTS):
        d.ellipse([x + i * 30, 430, x + i * 30 + 16, 446], fill=c)
    d.text((x + 140, 438), "Claude Code · Codex · Gemini CLI · Copilot · OpenCode · Cursor",
           fill=MUTED, font=font(22, False), anchor="lm")
    return img


def preview(names=(("exaggeration", 110), ("origin", 34), ("add-to-cart", 60), ("layout-shift", 110),
                   ("staggering", 26), ("peak-end", 150))):
    """Grid of before/after stills taken from the demo GIFs, each at a frame where the two sides differ."""
    shots = []
    for n, frame in names:
        with Image.open(ROOT / "assets" / f"{n}.gif") as g:
            g.seek(frame)
            shots.append((n, g.convert("RGB")))
    sw, sh = shots[0][1].size
    pad, label, top = 32, 40, 120
    w, h = pad + 2 * (sw + pad), top + 3 * (label + sh + pad)
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    img.paste(mark(56), (pad, 32), mark(56))
    d.text((pad + 76, 60), "Before / after, for every principle that moves", fill=INK, font=font(34, True), anchor="lm")
    for i, (n, im) in enumerate(shots):
        x, y = pad + (i % 2) * (sw + pad), top + (i // 2) * (label + sh + pad)
        d.ellipse([x, y + 12, x + 12, y + 24], fill=ACCENTS[i % 4])
        d.text((x + 22, y + 18), n.replace("-", " ").capitalize(), fill=INK, font=font(22, True), anchor="lm")
        img.paste(im, (x, y + label))
    return img


def covers(w=1280, h=640):
    """What's inside: one card per reference file."""
    cards = (("Motion", "Origin awareness, springs, interruptible motion, timing"),
             ("UX laws", "Fitts, Hick, Miller, Jakob, Doherty, layout shift"),
             ("Typography", "Tabular numbers, text-box trim, line length, fonts"),
             ("Colour", "OKLCH, contrast, Abney and Hunt effects, scales"),
             ("Un-slop", "Remove the generic AI look, one accent, real product"),
             ("Patterns", "Slide-in carts, password screens, App Store shots"))
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    m = mark(64)
    img.paste(m, (64, 56), m)
    d.text((148, 88), "What's inside", fill=INK, font=font(44, True), anchor="lm")
    cw, ch, gap, x0, y0 = 368, 200, 32, 64, 172
    for i, (title, body) in enumerate(cards):
        x, y = x0 + (i % 3) * (cw + gap), y0 + (i // 3) * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], 20, fill=PAPER, outline="#e5e5e5", width=2)
        d.ellipse([x + 28, y + 30, x + 46, y + 48], fill=ACCENTS[i % 4])
        d.text((x + 60, y + 39), title, fill=INK, font=font(30, True), anchor="lm")
        words, lines, line = body.split(), [], ""
        for wd in words:  # simple wrap to the card width
            trial = f"{line} {wd}".strip()
            if d.textlength(trial, font=font(22, False)) > cw - 56:
                lines.append(line)
                line = wd
            else:
                line = trial
        lines.append(line)
        for j, ln in enumerate(lines):
            d.text((x + 28, y + 84 + j * 32), ln, fill=MUTED, font=font(22, False))
    return img


if __name__ == "__main__":
    preview().save(OUT / "preview.png")
    covers().save(OUT / "covers.png")
    (OUT / "logo.svg").write_text(svg(), encoding="utf-8")
    mark(1024).save(OUT / "logo.png")
    mark(512).save(ROOT / ".claude-plugin" / "icon.png")
    banner().save(OUT / "banner.png")
    print("logo.svg, logo.png, banner.png, .claude-plugin/icon.png")
