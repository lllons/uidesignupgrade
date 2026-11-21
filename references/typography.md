# Typography: full reference

Each entry: what it is, why it matters, how to implement it (CSS first, platform notes where they differ), mistakes, and a check.

## Kerning

**What:** Adjusting the space between specific pairs of letters (AV, To, Wa) so the spacing looks even.

**Why:** Letter shapes leave uneven gaps. Without kerning, headlines look patchy.

**How:** Good fonts ship kerning tables; make sure they are on: `font-kerning: normal` (default in most browsers) and `text-rendering: optimizeLegibility` for large headlines only. Hand-kern logos and very large display text in the design tool, not in CSS.

**Avoid:** `font-kerning: none`; letter-spacing hacks on individual characters.

**Check:** Look at the headline upside down. Do any gaps between letters stand out?

## Tracking (letter-spacing)

**What:** Uniform spacing added or removed across every letter in a run of text.

**Why:** Small text and all-caps need more air to stay legible; large display text looks better slightly tighter.

**How:** All-caps labels and eyebrows: `letter-spacing: 0.04em` to `0.08em`. Body text: leave at 0 (most fonts are designed for it). Headlines above about 32 px: `-0.01em` to `-0.03em`. Use `em` so it scales with font size.

**Avoid:** Positive tracking on lowercase body text; tight tracking on small text; tracking in `px`.

**Check:** Are uppercase labels readable at a glance? Do big headlines look like a solid shape?

## Leading (line height)

**What:** The vertical distance between lines of text.

**Why:** Too tight and lines collide; too loose and the eye loses the next line.

**How:** Body text `line-height: 1.5` (1.4 to 1.6). Headings 1.1 to 1.25, tighter as size grows. UI labels and buttons 1.2 or `1` with text-box trim. Use unitless values so they scale. Longer lines need slightly more leading.

**Avoid:** One line height for everything; `line-height` in `px` on responsive text.

**Check:** Can you read three lines of body text and land on the next line without effort?

## x-height

**What:** The height of lowercase letters (literally the height of "x") relative to the capitals.

**Why:** Fonts with a large x-height look bigger and stay legible at small sizes. Two fonts at the same `font-size` can look very different.

**How:** Compare x-heights when pairing fonts or picking a fallback. Use `font-size-adjust: from-font` (or a number such as `0.5`) to keep fallback fonts the same apparent size. Prefer larger x-heights for dense UI and small text.

**Avoid:** Pairing a tiny-x-height serif with a huge-x-height sans at the same size.

**Check:** Set both fonts side by side at 14 px. Do they look the same size?

## Line length (measure)

**What:** The number of characters per line.

**Why:** Long lines make it hard to find the start of the next line; short lines break rhythm and create too many hyphens. About 66 characters is the classic ideal for comfortable reading.

**How:** `max-width: 65ch` on text containers (45 to 75 characters for body, shorter for captions). On wide screens, add whitespace or a second column instead of stretching text.

**Avoid:** Full-width paragraphs on desktop (often 120+ characters per line).

**Check:** Count the characters on a typical line of body text on a large monitor.

## Widows, orphans and wrapping

**What:** A widow or orphan is a single word (or very short line) left alone at the end of a paragraph or heading.

**Why:** It looks unfinished and creates uneven rag; in headings it can change emphasis.

**How:** Headings: `text-wrap: balance` (evens out line lengths). Paragraphs: `text-wrap: pretty` (avoids a short last line). For important headlines, use a non-breaking space (`&nbsp;`) between the last two words as a fallback.

**Avoid:** Fixing wraps with manual `<br>` tags (they break at other screen sizes).

**Check:** Resize the window. Do headings ever end on a lone word?

## Tabular numbers

**What:** Digits that all have the same width (tabular figures), as opposed to proportional figures where a 1 is narrower than an 8.

**Why:** In counters, timers, prices, tables and anything that updates, proportional digits make numbers jitter and columns misalign.

**How:** `font-variant-numeric: tabular-nums;` on numeric cells, timers, live counters and totals. Right-align numeric columns. In SwiftUI `.monospacedDigit()`; in Flutter `FontFeature.tabularFigures()`.

**Avoid:** Tabular numbers in running prose (proportional figures read better there).

**Check:** Watch a counter tick up. Does anything move sideways?

## Reserved bold width

**What:** Preventing layout shift when text changes weight (a tab becomes bold when active, a menu item when hovered).

**Why:** Bold text is wider. When one tab gets bolder, every tab after it moves, which looks broken and can move a target out from under the pointer.

**How:**

```css
.tab { display: inline-grid; }
.tab::after {
  content: attr(data-text);   /* same label, set in the markup */
  font-weight: 700;
  visibility: hidden;
  height: 0;
  overflow: hidden;
  grid-area: 1 / 1;           /* stack under the visible text */
}
.tab > span { grid-area: 1 / 1; }
```

Alternatives: use a variable font and change `font-weight` within a width-stable family, or use colour or an underline for the active state instead of weight.

**Avoid:** Changing weight on hover in navigation without reserving width.

**Check:** Click through every tab. Nothing else moves.

## Text-box trim

**What:** Trimming the extra space above capitals and below the baseline that fonts reserve for accents and descenders.

**Why:** That space makes text in buttons, badges and icons sit slightly low, so "centred" text looks off-centre and padding looks uneven.

**How:** `text-box: trim-both cap alphabetic;` (longhands `text-box-trim: trim-both; text-box-edge: cap alphabetic;`). Now padding is measured from the cap height to the baseline. Supported in Chromium and Safari; harmless where unsupported. Fallback: tweak `padding-top`/`padding-bottom` per font.

**Avoid:** Fixing it with negative margins tied to one font.

**Check:** Zoom into a button. Is the space above the capitals equal to the space below the baseline?

## Underline offset

**What:** Controlling the distance and thickness of text underlines.

**Why:** Default underlines sit tight against the baseline and cut through descenders (g, j, p, q, y), which hurts legibility.

**How:** `text-underline-offset: 0.2em; text-decoration-thickness: 0.06em;` (or `from-font`). `text-decoration-skip-ink: auto` is default in modern browsers. Underline links in body text so they are recognisable without colour.

**Avoid:** Using `border-bottom` as a fake underline (breaks on wrapped lines).

**Check:** Underline a word like "typography". Do the descenders stay readable?

## Superscript spacing

**What:** Keeping `<sup>` (footnote markers, ®, ¹) from pushing lines apart.

**Why:** Browsers raise superscript by increasing the line box, so lines with a footnote marker are taller than the rest.

**How:**

```css
sup, sub { line-height: 0; position: relative; vertical-align: baseline; }
sup { top: -0.5em; }
sub { bottom: -0.25em; }
```

Or use `font-variant-position: super` where the font supports real superscript glyphs.

**Avoid:** Leaving default `vertical-align: super` in body copy.

**Check:** Are lines with footnote markers the same height as lines without?

## Fluid type

**What:** Font sizes that scale smoothly with the viewport instead of jumping at breakpoints.

**Why:** Breakpoint jumps make headlines suddenly too big or too small at in-between widths.

**How:** `font-size: clamp(2rem, 1rem + 5vw, 4rem);` (minimum, preferred, maximum). Always include a `rem` part in the middle value so browser zoom still works. Use a type scale (for example 1.25 ratio) for the min and max values. Apply mainly to headings; body text can stay fixed or scale gently.

**Avoid:** Pure `vw` font sizes (break zoom and accessibility); clamp on body text with a huge range.

**Check:** Drag the window from 320 px to 1920 px. Does the headline grow smoothly and stay within bounds?

## Small caps for acronyms

**What:** Setting runs of capitals (API, CSV, PDF, NASA) in small capitals so they match the height of lowercase text.

**Why:** Full-size capitals in running text shout and create dark blotches in a paragraph.

**How:** `abbr, .acronym { font-variant-caps: all-small-caps; letter-spacing: 0.02em; }` Only use fonts with real small caps (check the font's OpenType features: `smcp`, `c2sc`); synthesised small caps look thin.

**Avoid:** Small caps in UI labels, buttons or headings that are deliberately uppercase.

**Check:** Does a paragraph full of acronyms have an even texture?

## Curly quotes and proper punctuation

**What:** Using typographic quotes and apostrophes (“ ” ‘ ’), real dashes (– —) and ellipses (…) instead of typewriter characters (" ' -- ...).

**Why:** Straight quotes look mechanical and unfinished; they are a tell of text pasted straight from code or AI output.

**How:** Write the correct characters in content, or use a smart-quotes transform in the CMS or build step. In CSS, `quotes: "“" "”" "‘" "’";` with `<q>`. Use the right style for the locale (« » in French, „ “ in German).

**Avoid:** Straight quotes in UI copy; "--" instead of an en or em dash.

**Check:** Search the UI strings for `"` and `'` characters.

## Middle truncation

**What:** Shortening long strings by removing the middle instead of the end: `Q4 board upd…final.pdf`.

**Why:** For file names, URLs and identifiers, the end carries meaning (the extension, the version). End truncation hides it.

**How:** CSS can only truncate the end (`text-overflow: ellipsis`). Split the string: keep the extension in its own non-shrinking element.

```css
.file { display: flex; min-width: 0; }
.file .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file .ext { flex-shrink: 0; }
```

Or truncate in JS to a fixed number of characters keeping the first and last parts. Show the full name in a tooltip or `title`.

**Avoid:** Truncating names so heavily that two files look identical.

**Check:** Do two similar long file names remain distinguishable?

## Auto hyphenation

**What:** Letting the browser break long words at syllable boundaries.

**Why:** In narrow columns (mobile, cards, sidebars), justified or ragged text gets huge gaps or very uneven lines without hyphenation.

**How:** Set the language on the document (`<html lang="en">`) and `hyphens: auto;` on body text in narrow containers. Optionally tune with `hyphenate-limit-chars: 6 3 2`. Avoid hyphenating headings.

**Avoid:** `hyphens: auto` without a `lang` attribute (does nothing); hyphenating UI labels.

**Check:** Look at a narrow card on a phone. Are there any rivers of white space?

## Line-clamped titles

**What:** Limiting a block of text to a fixed number of lines with an ellipsis.

**Why:** In grids of cards, one long title makes that card taller and breaks the row alignment.

**How:**

```css
.card-title {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}
```

Reserve the height for the full number of lines (`min-height: calc(2 * 1.25em)`) so short titles keep cards aligned too. Show the full title on hover or in the detail view.

**Avoid:** Clamping body text people need to read; clamping to 1 line when titles are usually long.

**Check:** Do cards with short and long titles line up?

## Text contrast

**What:** The luminance difference between text and its background.

**Why:** Low-contrast grey text is hard to read for many people and in sunlight, and it is one of the most common tells of generated designs.

**How:** WCAG AA: 4.5:1 for body text, 3:1 for large text (24 px, or 18.66 px bold) and for UI components and focus indicators. Use the theme's foreground for body text and reserve muted grey for genuinely secondary text, still meeting 4.5:1. Check with a contrast tool or the browser DevTools picker. Support `prefers-contrast: more` and Windows forced colours.

**Avoid:** Light grey on white for body copy; text over busy images without an overlay.

**Check:** Run an accessibility audit (Lighthouse, axe) and fix every contrast failure.

---

# Fonts

Choose type for the feeling you want. These lists come from working designers; many are commercial, so check licensing, and keep the project's existing brand font if it has one.

| Feeling | Fonts |
|---------|-------|
| Clean Swiss look | ABC Diatype, TWK Lausanne, Switzer, Saans, Areal, Strichpunkt Sans |
| Friendly | Studio Feixen Sans, PP Mori, Aeonik, Degular, GT Walsheim, Circular |
| A bit of personality | Apfel Grotezk, Aktiv Grotesk, ABC Favorit, Familjen Grotesk, ABC Monument Grotesk, ABC Oracle |
| Techy | ABC Diatype Mono, Söhne Mono, GT America Mono, IBM Plex Mono, Commit Mono, Departure Mono |
| Vintage | Editorial New, ABC Arizona, ABC Marist, Concrette, GT Super, Blazeface |
| Modern serif | Tiempos Fine, Reckless, Signifier, Canela, Luperca, Domaine Display |
| Soft serif | EB Garamond, Exposure, GT Alpina, Mioya, Tiempos Text, Lyon Text |
| Fun | Gautreaux, Hobeaux, Obviously, Absans, GT Maru, 5by7 |

**Overused in AI-generated designs (don't pick them by default):** Inter, Roboto, Arial, Instrument Serif, Fraunces, Playfair Display, Geist, Space Grotesk, Bricolage Grotesque, Instrument Sans, JetBrains Mono, Space Mono. They are good fonts; the problem is that they are the default choice of every generator, so they make a product look generic. Use them when there is a reason (an existing brand, a specific need), not as a reflex.

**How to apply fonts well:**
- Use one family for UI and at most one contrasting family for display or editorial text.
- Load only the weights you use (usually 2 or 3); self-host with `font-display: swap` and a metric-matched fallback to avoid layout shift.
- Free alternatives with similar feelings when licensing is a blocker: Switzer and Satoshi (Swiss), General Sans (friendly), EB Garamond (soft serif), IBM Plex Mono and Commit Mono (techy) are free.
