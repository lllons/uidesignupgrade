# Audit playbook: find, detect, verify, report

Read this at the start of every run. It turns the principles into concrete steps: where to find the existing design system, which searches surface likely problems, how to rank them, how to check the result, and how to report it.

All searches use `rg` (ripgrep). Always pass the path (`.`): without one, `rg` reads standard input when the shell is not a terminal and silently finds nothing. `rg` skips `.gitignore`d folders such as `node_modules` and build output. Run them from the project root.

**No `rg`?** (common on Windows: check with `rg --version`). Don't install anything; translate each command:

| `rg` form | Fallback |
|-----------|----------|
| `rg -n "PATTERN" .` | `git grep -nE --untracked "PATTERN"` (inside a git repo; `--untracked` also searches new files) or `grep -rnE --exclude-dir={node_modules,dist,build,.git} "PATTERN" .` |
| `rg -nP` / `rg -n` with `(?!`, `\x{...}` | `git grep -nP --untracked` or `grep -rnP ...` (ERE can't do lookaheads or `\x{}`) |
| `rg -l` / `rg -c` | add `-l` / `-c` to the fallback |
| `-g "*.css"` | `git grep ... -- "*.css"` or `grep ... --include="*.css"` |
| `-g "!*.md"` | `git grep ... -- . ":!*.md"` or `grep ... --exclude="*.md"` |
| `-i` | `-i` |

If a search for something you can see in the code returns nothing, suspect the command (missing path, wrong quoting, ERE vs PCRE) before concluding the problem is absent.

## 1. Find the existing design system

Look before you write. Extend what exists; never create a second token system next to the first.

| Stack | Where tokens usually live |
|-------|---------------------------|
| Tailwind v4 | `@theme { ... }` block in the main CSS file |
| Tailwind v3 | `tailwind.config.{js,ts,cjs,mjs}` under `theme.extend` |
| Plain CSS / SCSS | `:root { --... }` custom properties, `_variables.scss`, `tokens.css` |
| shadcn/ui | CSS variables in `globals.css`, plus `components.json` |
| CSS-in-JS / MUI / Chakra | `theme.ts`, `createTheme(`, `extendTheme(` |
| React Native | `theme.ts`, `StyleSheet.create`, `useColorScheme` |
| SwiftUI | `Color` / `Font` extensions, asset catalog colour sets |
| Jetpack Compose | `Theme.kt`, `Color.kt`, `Type.kt`, `MaterialTheme(` |
| Flutter | `ThemeData(`, `ColorScheme`, `TextTheme` |

```sh
rg -n "@theme" -g "*.css" .                                  # Tailwind v4
rg -l "theme" -g "tailwind.config.*" .                       # Tailwind v3
rg -n -e "--[a-z][a-z0-9-]*:" -g "*.{css,scss}" .            # CSS custom properties
rg -n "createTheme|extendTheme|ThemeProvider" .              # CSS-in-JS
rg -n "StyleSheet.create|useColorScheme" .                   # React Native
rg -n "extension (Color|Font|ShapeStyle)" -g "*.swift" .     # SwiftUI
rg -n "MaterialTheme|lightColorScheme|darkColorScheme" -g "*.kt" .   # Compose
rg -n "ThemeData|ColorScheme|TextTheme" -g "*.dart" .        # Flutter
```

Write down, before changing anything: font families and weights, the type scale, the spacing scale, radii, shadows, colour roles (background, foreground, muted, border, accent, danger, success), motion durations and easings, and whether dark mode exists. If a category has no tokens, add a small set in the same place and style as the existing ones (motion.md "Shared tokens", color.md "Working colour system").

Then find the target look: screenshots, a Figma link, a site the user likes, or the best existing screen in the app. If the change is visual and there is no reference, ask once; if the user has none, use the strongest existing screen.

## 2. Run the detectors

Each hit is a lead, not a verdict: open the file and confirm before changing it. Linear easing on a spinner is correct; `outline: none` followed by a `:focus-visible` style is fine.

### P0: accessibility and breakage

```sh
# Focus ring removed (fine only if a :focus-visible style replaces it)
rg -n "outline:\s*(none|0)\b|outline-none" .
# Zoom disabled in the viewport meta tag
rg -n "user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0)?\b" .
# Reduced motion handled anywhere? No output = problem
rg -l "prefers-reduced-motion|useReducedMotion|motion-reduce:|accessibilityReduceMotion|disableAnimations|reduceMotion" .
# Images without width/height (layout shift)
rg -nP "<img(?![^>]*\b(width|height)=)" .
# 100vh on mobile hides content behind browser bars
rg -n "100vh|\bh-screen\b" .
# Clickable divs and spans (no keyboard or screen-reader support). -i: JSX uses onClick, HTML uses onclick
rg -niP "<(div|span|li|td|img)\b[^>]*\b(onclick|@click|v-on:click|\(click\))=" .
# Likely low-contrast text: light greys, translucent text, faded labels (confirm the real ratio in section 4)
rg -n "text-(gray|zinc|slate|neutral|stone)-(200|300|400)\b|text-(white|black)/[1-5]0\b|color:\s*#(a1a1aa|9ca3af|bbb|ccc|aaa|d1d5db)\b|opacity:\s*0?\.[1-5]\b" .
# Page background set at all? No output = text colour may land on an unexpected (even dark) canvas
rg -n "(html|body|:root)\s*\{[^}]*background|<body[^>]*\bbg-" .
```

Fixes: `:focus-visible` ring at 3:1 contrast (ux-laws.md, Affordance); remove the zoom lock; add the reduced-motion block (motion.md, Shared tokens); `width`/`height` or `aspect-ratio` (ux-laws.md, Layout shift); `100dvh` / `h-dvh` plus safe-area insets (ux-laws.md, Safe areas); `<button>` or `<a>`; a `--muted` token at 4.5:1 or more (typography.md, Text contrast); `body { background: var(--bg); color: var(--fg); }` set together.

### P1: generic AI look and design-system drift

```sh
# Purple / violet gradients
rg -n "(from|via|to)-(purple|violet|indigo|fuchsia)-|gradient\([^)]*(purple|violet|#8b5cf6|#7c3aed|#6366f1|#a855f7)" .
# Gradient text
rg -n "bg-clip-text|background-clip:\s*text" .
# Glass and glow
rg -n "backdrop-blur|backdrop-filter|blur-3xl|shadow-\[0_0_|drop-shadow-\[" .
# Filler copy
rg -ni "supercharge|unlock (your|the)|revolutioni[sz]e|seamless|next-gen|game.chang|elevate your|ai-powered|✨" .
# Generator-default fonts (fine if it is the brand font)
rg -n "\bInter\b|Geist|Space Grotesk|Instrument (Serif|Sans)|Fraunces|Playfair|Bricolage|JetBrains Mono|Space Mono" .
# Hard-coded colours per file (high counts in component files = drift)
rg -c "#[0-9a-fA-F]{3,8}\b|rgba?\(" -g "!*.svg" -g "!*.md" .
# Arbitrary pixel spacing and radii in Tailwind
rg -n "\b(p|m|gap|rounded)[trblxy]?-\[[0-9.]+px\]" .
# Emoji used as icons
rg -n "[\x{1F300}-\x{1FAFF}]" -g "!*.md" .
```

Fixes: neutral surfaces plus one accent, solid text colour, flat surfaces with depth only for real layering, specific headlines with nouns and numbers, a font chosen by feeling (typography.md, Fonts), role tokens (color.md), the spacing and radius scale, one icon set. Details for all of these are in unslop.md.

### P2 / P3: motion quality

```sh
# transition: all (animates things you didn't mean to, hurts performance)
rg -n "transition:\s*all\b|\btransition-all\b" .
# Linear easing on movement (fine for spinners and progress bars)
rg -n "(transition|animation)[^;]*\blinear\b|\bease-linear\b" .
# Entering from scale 0
rg -n "scale\(0\)|\bscale-0\b|scale:\s*0\s*[,}]" .
# Animating layout properties
rg -n "transition(-property)?:[^;]*\b(width|height|top|left|right|bottom|margin|padding)\b" .
# Long routine animations (over 500 ms), in ms or seconds (.6s, 0.8s, 1s, 1.5s)
rg -n "\bduration-(700|1000)\b|(transition|animation)[^;]*(\b([6-9][0-9]{2}|[1-9][0-9]{3})ms|(^|[^.0-9])(0?\.[6-9][0-9]*|[1-9][0-9]*(\.[0-9]+)?)s\b)" .
# Animating something that toggles display: none (the enter animation never plays)
rg -n "display:\s*none" -g "*.{css,scss}" .
# Scroll-triggered fade-ins (keep only where they explain something)
rg -n "whileInView|data-aos|animate-on-scroll" .
```

Fixes are in motion.md: exact property lists (Transform, not layout), ease-out tokens (Easing), start at 0.97, grid-rows or `interpolate-size` for height, durations under 500 ms (Timing), animate useful feedback only. A `display: none` hit matters only when the same element also has a transition or animation: fix with `@starting-style` plus `allow-discrete` (motion.md, Scale from 0.97).

### Responsive

```sh
# Large fixed text sizes with no responsive or fluid version (headlines overflow or break badly at 390 px)
rg -n "\btext-(5xl|6xl|7xl|8xl|9xl)\b|font-size:\s*([4-9][0-9]|1[0-9]{2})px" .
# Fixed-width columns that can't shrink
rg -n "\bw-\[[0-9]{3,}px\]|\bwidth:\s*[3-9][0-9]{2}px" .
```

Confirm on the 390 px screenshot: a hit is fine if a breakpoint version (`md:text-6xl`) or `clamp()` exists. Fix with `clamp()` (typography.md, Fluid type) and a breakpoint that stacks rows and sidebars.

### P2: typography

```sh
# Tabular numbers used anywhere? No output while the UI shows prices, stats or timers = problem
rg -l "tabular-nums|font-variant-numeric" .
# Balanced headings anywhere? No output = problem
rg -l "text-wrap:\s*balance|text-balance" .
# Line length limits anywhere? No output = check paragraphs for unbounded width
rg -l "max-w-prose|max-width:\s*[0-9]+ch|max-w-\[[0-9]+ch\]" .
```

Fixes: typography.md (Tabular numbers, Widows, Line length).

### Native stacks

Same ideas, stack terms (see platforms.md for each fix):

```sh
rg -n "\.animation\(\.linear|\.scaleEffect\(0\)|\.font\(\.system\(size:" -g "*.swift" .
rg -n "LinearEasing|scaleIn\(initialScale = 0f|fontSize = [0-9]+\.sp" -g "*.kt" .
rg -n "Curves\.linear|scale:\s*0\.0|fontSize:\s*[0-9]+" -g "*.dart" .
```

Hard-coded font sizes point to a missing type scale; use the platform's text styles (Dynamic Type, `MaterialTheme.typography`, `Theme.of(context).textTheme`).

### What searches can't find

Check these on the rendered UI: real text contrast on real backgrounds, target sizes, uneven spacing, misaligned edges, optical centring, hierarchy, the main feature's size, missing loading, empty and error states, and whether the motion feels right.

## 3. Rank and choose

Fix in this order; finish one level before starting the next.

| Level | What | Examples |
|-------|------|----------|
| **P0: broken** | blocks or hurts a user | contrast below WCAG AA, missing focus, targets under 44 pt (24 px CSS minimum, 44 px preferred), layout shift, zoom disabled, input blocked during animation, no reduced-motion path |
| **P1: generic or inconsistent** | the un-slop list and design-system drift | purple gradients, filler badges, vague headlines, several primary buttons, off-scale spacing, mixed radii and icon sets, missing loading/empty/error states |
| **P2: craft** | typography and colour detail | line length, tabular numbers, balanced headings, text-box trim, OKLCH ramps, concentric radii, optical alignment |
| **P3: polish** | motion and delight | origin awareness, staggering, press feedback, springs, shared-element transitions |

Scope rules:

- **Small, local, reversible changes:** do them.
- **Ask first** before changing brand fonts or colours, rewriting copy beyond obvious filler, removing features or sections, adding a dependency, or restructuring navigation. If the user isn't around, list it under "Proposed" in the report.
- A request about one area ("fix the typography") means that area, plus any P0 issue you find. Mention the rest in the report without fixing it.
- If a screen already meets a principle, leave it alone. Don't add motion to make the diff look bigger.

## 4. Verify

Code that looks right can render wrong. Check the result in the running app whenever you can.

1. **Start the app** with the project's own dev command (`package.json` scripts, the README, Xcode or Gradle).
2. **Screenshot** at 390×844 (phone) and 1440×900 (desktop), before and after. Use your browser tool if you have one; otherwise Playwright:

   ```sh
   npx playwright screenshot --viewport-size "390,844" --full-page http://localhost:3000 after-mobile.png
   npx playwright screenshot --viewport-size "1440,900" --full-page http://localhost:3000 after-desktop.png
   ```

3. **Compare** with the reference and the un-slop list: spacing off the scale, edges that don't line up, mixed radii, text sitting low in buttons, icons off-centre. Fix, then screenshot again.
4. **Quick page check (no install).** If your browser tool can run JavaScript in the page, paste this at each width. It reports low-contrast text, text on gradients or images to check by eye, targets under 24 px, horizontal overflow, and a missing page background. It's a first pass: it can't see text over images, and translucent colours are estimated.

   ```js
   (() => {
     const ctx = Object.assign(document.createElement('canvas'), { width: 1, height: 1 }).getContext('2d', { willReadFrequently: true });
     const rgb = c => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1); // canvas also parses oklch(), lab(), color()
       const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data; return [r, g, b, a / 255]; };
     const lum = c => rgb(c).slice(0, 3).map(v => (v /= 255) <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)
       .reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
     const alpha = c => rgb(c)[3];
     const bgOf = el => { for (; el; el = el.parentElement) { const s = getComputedStyle(el);
       if (s.backgroundImage !== 'none') return null; if (alpha(s.backgroundColor) > 0) return s.backgroundColor; }
       return 'rgb(255,255,255)'; };
     const r = { overflowX: document.documentElement.scrollWidth > innerWidth,
       noPageBackground: [document.documentElement, document.body].every(e => alpha(getComputedStyle(e).backgroundColor) === 0),
       lowContrast: [], checkByEye: [], smallTargets: [] };
     for (const el of document.querySelectorAll('body *')) {
       const s = getComputedStyle(el), box = el.getBoundingClientRect();
       if (!box.width || s.visibility === 'hidden') continue;
       const label = (el.textContent.trim() || el.getAttribute('aria-label') || el.tagName).slice(0, 40);
       if ([...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {
         const bg = bgOf(el);
         if (!bg) r.checkByEye.push(label);
         else {
           const [a, b] = [lum(s.color), lum(bg)];
           let ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
           if (alpha(s.color) < 1 || +s.opacity < 1) ratio = Math.min(ratio, 1 + (ratio - 1) * alpha(s.color) * s.opacity);
           const large = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.66 && +s.fontWeight >= 700);
           if (ratio < (large ? 3 : 4.5)) r.lowContrast.push({ text: label, ratio: +ratio.toFixed(2) });
         }
       }
       if (el.matches('a, button, input, select, textarea, summary, [onclick], [role=button], [tabindex]:not([tabindex="-1"])')
           && (box.width < 24 || box.height < 24)) r.smallTargets.push({ el: label, w: Math.round(box.width), h: Math.round(box.height) });
     }
     return r;
   })()
   ```

   Every array should be empty and both flags `false`. `noPageBackground: true` means the page relies on the browser's canvas colour: dark-mode browsers and embedded webviews can show your dark text on a dark canvas. Set `body { background; color }` together.

5. **Accessibility:** run Lighthouse if it's available (it downloads Chromium tooling the first time, so ask before installing it in a project that doesn't have it), then tab through each screen (focus always visible, logical order, nothing unreachable).

   ```sh
   npx lighthouse http://localhost:3000 --only-categories=accessibility --quiet --chrome-flags="--headless" --output=json --output-path=a11y.json
   ```

6. **Motion:** check durations in the DevTools Animations panel; emulate `prefers-reduced-motion: reduce` (DevTools > Rendering) and confirm feedback still happens without movement; click quickly during transitions to confirm they reverse instead of queueing. To prove an enter animation actually plays, read the computed style about 60 ms after opening: `opacity` should be between 0 and 1, not already 1.
7. **Layout shift:** reload with network throttling; nothing should jump. CLS alone can read near 0 when nothing sits below the late content, so also measure the container itself:

   ```js
   const h = () => Math.round(document.querySelector('#orders').getBoundingClientRect().height); // your late-loading container
   const before = h(); await new Promise(r => setTimeout(r, 3000)); ({ before, after: h() })   // must be equal
   ```

   A skeleton row must match the height of a **loaded** row, including its tallest child (a 44 px icon button makes the row 44 px plus padding).
8. **Narrow widths:** at 390 px, `overflowX` from step 4 must be `false`, sidebars and stat rows must stack, and headlines should fit in about four lines without breaking words.
9. **Dark mode**, if the app supports it.

Native apps: screenshots from the simulator or emulator (`xcrun simctl io booted screenshot out.png`, `adb exec-out screencap -p > out.png`), Accessibility Inspector or Android Accessibility Scanner, and the platform's reduce-motion and larger-text settings.

If you can't run the app, say so in the report and list what is unverified. Never claim a visual result you didn't see.

## 5. Report

End with a short report in this shape:

```md
## UI upgrade: <screen or area>

Reference: <what you matched, or "existing <screen>">
Verified: <screenshots at 390 and 1440, Lighthouse a11y score, keyboard pass>
Not verified: <what, and why>

| Level | Principle | Where | Change |
|-------|-----------|-------|--------|
| P0 | Text contrast | `Card.tsx` muted text | #9ca3af → --muted (5.1:1) |
| P1 | One accent colour | hero, pricing | removed violet gradient; accent on primary CTA only |
| P3 | Origin awareness | `Menu.tsx` | scales from the trigger, 200 ms ease-out |

Proposed, needs your OK: <brand font change, copy rewrite, new dependency>
```

List only what changed and what needs a decision; skip principles that were already met.
