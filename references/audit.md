# Audit playbook: find, detect, verify, report

Read this at the start of every run. It turns the principles into concrete steps: where to find the existing design system, which searches surface likely problems, how to rank them, how to check the result, and how to report it.

All searches use `rg` (ripgrep). Always pass the path (`.`): without one, `rg` reads standard input when the shell is not a terminal and silently finds nothing. `rg` skips `.gitignore`d folders such as `node_modules` and build output. Without `rg`, use `git grep -nE` (or `grep -rnE --exclude-dir=node_modules`) with the same pattern; patterns marked `-P` need `git grep -nP` or `grep -rnP`. Run them from the project root.

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
# Clickable divs and spans (no keyboard or screen-reader support)
rg -nP "<(div|span)\b[^>]*\bonClick=" .
```

Fixes: `:focus-visible` ring at 3:1 contrast (ux-laws.md, Affordance); remove the zoom lock; add the reduced-motion block (motion.md, Shared tokens); `width`/`height` or `aspect-ratio` (ux-laws.md, Layout shift); `100dvh` / `h-dvh` plus safe-area insets (ux-laws.md, Safe areas); `<button>` or `<a>`.

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
# Long routine animations (over 500 ms)
rg -n "\bduration-(700|1000)\b|(transition|animation)[^;]*\b([6-9][0-9]{2}|[1-9][0-9]{3})ms" .
# Scroll-triggered fade-ins (keep only where they explain something)
rg -n "whileInView|data-aos|animate-on-scroll" .
```

Fixes are in motion.md: exact property lists (Transform, not layout), ease-out tokens (Easing), start at 0.97, grid-rows or `interpolate-size` for height, durations under 500 ms (Timing), animate useful feedback only.

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
4. **Accessibility:** run Lighthouse and fix every contrast and label failure, then tab through each screen (focus always visible, logical order, nothing unreachable).

   ```sh
   npx lighthouse http://localhost:3000 --only-categories=accessibility --quiet --chrome-flags="--headless" --output=json --output-path=a11y.json
   ```

5. **Motion:** check durations in the DevTools Animations panel; emulate `prefers-reduced-motion: reduce` (DevTools > Rendering) and confirm feedback still happens without movement; click quickly during transitions to confirm they reverse instead of queueing.
6. **Layout shift:** reload with network throttling; nothing should jump (Lighthouse also reports CLS).
7. **Dark mode and narrow widths**, if the app supports them.

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
