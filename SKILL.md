---
name: uidesignupgrade
description: Upgrade an app or website UI with a growing library of UX, animation, typography, colour and "un-slop" principles (motion like origin awareness, staggering, easing and interruptible motion; UX laws like Fitts's, Hick's, Miller's and Jakob's; typography details like tabular numbers, text-box trim and line length; colour theory like OKLCH, contrast and perceptual scales; researched patterns like slide-in carts; and a checklist for removing generic AI-generated design). Includes an audit playbook (search commands, priorities, verification, report), worked examples for every mode, and Tailwind, SwiftUI, Compose, Flutter and React Native equivalents. Use when the user runs /uidesignupgrade, or asks to make a UI feel more polished, alive, responsive, premium or less AI-generated, audit or review a UI, screenshot or design PR, add micro-interactions, fix typography, colour, spacing or accessibility, pick fonts, design App Store screenshots, or audit motion and interaction quality.
---

# UI Design Upgrade

You are improving the **presentation** of an existing UI: how it looks, moves and reads. You are not changing what it does. Every run follows the same shape:

> **pick the mode → read the project → detect → rank → fix (if the mode allows) → verify → report**

This file tells you what to do and in what order. The detail lives in reference files (paths are relative to this file). **Read a reference before you change anything in its area**, and read only the ones the task touches.

| File | Read it when |
|------|--------------|
| [references/audit.md](references/audit.md) | **every run, first.** Where tokens live, ready-made search commands, priority levels, verification steps, report template |
| [references/examples.md](references/examples.md) | **every run, after audit.md: read the example for your mode.** Worked runs showing exactly what good output looks like |
| [references/platforms.md](references/platforms.md) | the project isn't plain CSS: Tailwind, Framer Motion, SwiftUI, Compose, Flutter, React Native |
| [references/motion.md](references/motion.md) | adding or changing any animation, transition or gesture |
| [references/ux-laws.md](references/ux-laws.md) | layout, target sizes, choices, forms, loading, layout shift |
| [references/typography.md](references/typography.md) | setting or reviewing text, choosing fonts |
| [references/color.md](references/color.md) | palettes, dark mode, charts, contrast |
| [references/unslop.md](references/unslop.md) | anything that looks generic or AI-generated |
| [references/patterns.md](references/patterns.md) | add-to-cart, sign-up/password, App Store screenshots, pricing |

---

## Step 0: Pick the mode

Decide the mode from the user's words **before touching any file**. The mode decides whether you may edit, and how wide you may go.

| The user says | Mode | Edit files? | Scope |
|---------------|------|-------------|-------|
| "upgrade / polish / improve the UI", or `/uidesignupgrade` alone | **Full upgrade** | yes | main screens, all areas, P0 → P3 |
| "audit", "review my UI", "what's wrong with", "rate", "critique my app" | **Audit only** | **no** | everything; output is a ranked report |
| "fix the typography / colours / animations / spacing / buttons" | **Targeted** | yes | that one area, plus any P0 you find |
| "build / design a new page, screen or component" | **New build** | yes | the new thing only, built on existing tokens |
| a screenshot, mockup, Figma frame or URL, **no code** | **Critique** | no (nothing to edit) | what is visible in the image |
| a diff, branch or PR | **Review** | no, unless asked to fix | changed lines only |
| "less AI-looking", "generic", "slop", "looks like a template" | **Un-slop** | yes | unslop.md list first, then type and colour |

Rules for choosing:

- **Ambiguous between editing and not editing?** Ask one short question ("Do you want a report, or should I make the changes?"). Every other ambiguity: pick the closest mode and say which one you picked in the first line of your reply.
- **More than one fits?** The narrower one wins. "Fix the typography on the pricing page" is Targeted, not Full upgrade.
- **No running app and no code?** You are in Critique, whatever else they said.

Examples:

| Request | Mode | Why |
|---------|------|-----|
| "Can you make our dashboard feel more premium?" | Full upgrade | broad "make it better", code present |
| "Be brutal, what's wrong with my landing page?" | Audit only | asks for judgement, not changes |
| "The numbers in the table jump around when they update" | Targeted (typography) | one concrete symptom: tabular numbers |
| "Add a settings screen that matches the rest of the app" | New build | new surface, existing system |
| *(image attached)* "thoughts?" | Critique | image only |
| "Review PR #42 for UI issues" | Review | a diff |
| "It looks like every other AI SaaS site" | Un-slop | the generic look is the complaint |

---

## Step 1: Read the project

Goal: know the existing system well enough that every change you make **extends it instead of inventing a second one**.

1. Identify the stack (framework, styling method, component library, platform).
2. Find the tokens with the commands in audit.md section 1. Write down: fonts and weights, type scale, spacing scale, radii, shadows, colour roles, motion durations and easings, dark mode yes/no.
3. Find the target look, in this order: a reference the user gave → a site or app the user named → the strongest existing screen in the project. If the change is visual and there is no reference at all, ask once; if they have none, use the strongest existing screen.

**Done when** you can name each token category (or note "none") and say what look you are matching.

> Example note to yourself: *"Next.js 15 + Tailwind v4. Tokens in `app/globals.css` `@theme`: font `--font-sans: "Söhne"`, spacing default Tailwind, radii `--radius-sm 6px / --radius 10px / --radius-lg 16px`, colours in oklch with roles bg/fg/muted/accent/danger, no motion tokens, dark mode via `.dark`. Matching: the Settings page, which is the cleanest screen."*

## Step 2: Capture "before"

If you can run the app, screenshot each screen in scope at **390 × 844** and **1440 × 900** (audit.md section 4). If you can't run it, write "Not verified: no running app" now so you don't forget it in the report.

## Step 3: List the surfaces

Write a short list of what is on screen: buttons, inputs, menus, modals, lists, cards, navigation, charts. Then the **states** for each: loading, empty, error, success, disabled, hover, focus, pressed. Mark the states that **don't exist at all**; missing states are usually the biggest wins.

## Step 4: Detect

1. Run the search commands in audit.md section 2 from the project root (always pass `.` as the path).
2. **Open every hit and confirm it before calling it a problem.** Searches find leads, not verdicts.
3. For each area that applies, read its reference and compare the rendered UI against it.
4. Check what searches can't find (contrast on real backgrounds, spacing, alignment, hierarchy) on the screenshots.

How to confirm a hit (real problem vs. false positive):

| Hit | Real problem | False positive, leave it |
|-----|--------------|--------------------------|
| `outline-none` | no `focus-visible:` style on the same element | `outline-none focus-visible:ring-2 ...` |
| `ease-linear` | a menu, card or modal that moves | a spinner, progress bar or marquee |
| `\bInter\b` | the generator default nobody chose | the documented brand font |
| `100vh` | a full-height mobile layout | a desktop-only admin view, or `100dvh` fallback next to it |
| `backdrop-blur` | decoration on a flat card | a sticky header or sheet that really overlays content |
| `scale-0` | an element entering from a dot | a collapsed element that's also `opacity-0` and never animates in |
| hex colours in a file | component files with many literals | the token file itself, SVG icons, test fixtures |

## Step 5: Rank

Put every confirmed finding in one level, then fix in order (finish P0 before starting P1):

| Level | Meaning | Typical findings |
|-------|---------|------------------|
| **P0 broken** | hurts or blocks a user | contrast below 4.5:1, no visible focus, targets under 24 px, zoom disabled, layout shift, no reduced-motion path |
| **P1 generic / inconsistent** | the AI look, or drift from the system | purple gradients, filler badges, vague headlines, three primary buttons, off-scale spacing, mixed radii, missing loading/empty/error states |
| **P2 craft** | type and colour detail | line length, tabular numbers, balanced headings, concentric radii, optical alignment |
| **P3 polish** | motion and delight | origin awareness, stagger, press feedback, springs |

**Do it yourself vs. ask first:**

| Do it (small, local, reversible) | Ask first, or list under "Proposed" |
|----------------------------------|-------------------------------------|
| fix contrast by using an existing darker token | change the brand font or brand colour |
| add `:focus-visible`, `tabular-nums`, `text-wrap: balance` | rewrite copy beyond deleting obvious filler ("Supercharge your workflow") |
| replace `transition: all` with exact properties | remove a section, feature or page |
| add a missing empty state that uses existing components | add a dependency (animation lib, font, icon set) |
| add motion tokens in the existing token file | restructure navigation or information architecture |

## Step 6: Fix (Full upgrade, Targeted, New build, Un-slop only)

- **Change the token, not the call sites.** If twenty buttons have the wrong radius, fix `--radius` once.
- **Reuse existing components.** Don't restyle a button locally on one page.
- **Use what's installed.** CSS and the platform can do almost everything here; no new libraries without asking.
- **Every animation you add** gets a reduced-motion path and animates only `transform` and `opacity`.
- **Stay in presentation.** Styles, tokens, semantic markup and UI states only. Never touch data fetching, state management or business rules.
- **Keep diffs reviewable.** Group by principle. Don't reformat or rename code you aren't changing.

Good vs. bad fixes:

```css
/* Bad: hard-coded, one call site, animates everything, no reduced motion */
.card { border-radius: 14px; transition: all .5s linear; }

/* Good: uses the scale, exact properties, eased, short */
.card {
  border-radius: var(--radius-lg);
  transition: transform var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out);
}
```

```tsx
// Bad: clickable div, no keyboard, no focus, emoji icon
<div onClick={save} className="p-1 text-xs">💾</div>

// Good: real button, 44 px target, visible focus, consistent icon, label for screen readers
<button onClick={save} aria-label="Save" className="inline-flex size-11 items-center justify-center rounded-md focus-visible:ring-2 focus-visible:ring-accent">
  <SaveIcon className="size-5" aria-hidden />
</button>
```

## Step 7: Verify in the running app

Look at the result; reading the code is not enough. Follow audit.md section 4:

1. Screenshot again at 390 and 1440; compare with "before" and the reference.
2. Lighthouse accessibility; fix every contrast and label failure.
3. Tab through every screen: focus always visible, order logical, nothing unreachable.
4. Emulate `prefers-reduced-motion: reduce`: feedback still happens without movement.
5. Click fast during transitions: they reverse, they don't queue.
6. Dark mode and narrow widths, if the app has them.

**If you can't run something, say exactly what is unverified.** Never write "looks great" about a screen you did not see.

## Step 8: Polish pass

Look at the "after" screenshots once more for things that are slightly off: uneven gaps, edges that don't line up, mismatched radii, text sitting low in buttons, icons off-centre. Fix them.

## Step 9: Un-slop check

Run the unslop.md list on the finished screens one last time. Anything still generic gets fixed or goes under "Proposed".

## Step 10: Report

Use the template in audit.md section 5. List only what changed and what needs a decision. Every row must be something you checked. See examples.md for a filled-in report for each mode.

---

## Common agent mistakes (and what to do instead)

| Mistake | Instead |
|---------|---------|
| Adding Framer Motion / GSAP / a colour package | CSS transitions, `@starting-style`, the platform's animation API |
| Hard-coding `#6b7280` in a component | use or add a role token (`--muted`) in the token file |
| Animating every hover and scroll reveal | animate feedback and state changes only; frequent actions stay instant |
| Removing focus rings "because they're ugly" | style them: `:focus-visible` ring in the accent at 3:1 contrast |
| Swapping the brand font for one from typography.md | keep the brand; propose the change instead |
| Purple gradient → teal gradient | neutral surfaces + one accent on the primary action |
| Polishing only the populated screen | design loading, empty and error states too |
| "The page now looks clean and modern" (unseen) | "Verified at 390 and 1440" or "Not verified: couldn't start the dev server" |
| A typography request turning into a redesign | fix typography + P0s; list the rest in the report |
| Editing files in Audit only or Critique mode | report only; offer to apply fixes at the end |

---

## Principle index

One-line versions so you know what exists. **Read the reference before applying any of them.**

### Motion and interaction ([motion.md](references/motion.md))

- **Exaggeration**: errors shake and turn red, not just change colour.
- **Origin awareness**: popovers and menus grow out of their trigger (`transform-origin`).
- **Scale from 0.97, not 0**: entering elements fade in from `scale(0.97)`.
- **Staggering**: list items enter 20 to 50 ms apart, capped at about 300 ms total.
- **Squash and stretch / press feedback**: buttons scale to about 0.97 on press.
- **Rubber banding**: overscroll and drag past an edge meet growing resistance, then spring back.
- **Anticipation**: a short wind-up before big motions.
- **Staging**: one focal point at a time; dim the rest.
- **Pose to pose**: design each state as a still first, then animate between states.
- **Slow in, slow out**: ease-out for entering, ease-in-out for moving, never linear for movement.
- **Follow-through**: inner parts settle a beat after the main body.
- **Arcs**: travelling elements follow curves.
- **Secondary action**: a small supporting motion reinforces the main one.
- **Timing**: 80 to 150 ms presses, 150 to 250 ms menus, 250 to 350 ms sheets; nothing routine over 500 ms.
- **Interruptible motion**: transitions reverse from where they are; never block input during animation.
- **Directional transitions**: Next slides left, Back slides right.
- **Animate to auto height**: `interpolate-size: allow-keywords` or the `grid-template-rows` 0fr→1fr trick.
- **Transform, not layout**: animate `transform` and `opacity` only.
- **Instant theme switches**: disable transitions while swapping themes.
- **Tooltip delay only once**: first tooltip waits about 600 ms, neighbours show instantly.
- **Velocity-matched springs**: gestures hand their release velocity to a spring.
- **Shared element transitions**: an element morphs into its counterpart on the next screen.
- **Optimistic updates**: show success immediately, roll back on failure.
- **Useful, exaggerated feedback**: animate confirmations, not decoration.
- **Frequency of use**: frequent and keyboard-driven actions don't animate.
- **Peak-end rule**: polish the best moment and the ending of every flow.
- **Appeal**: one consistent motion personality and token set.

### UX laws and layout ([ux-laws.md](references/ux-laws.md))

- **Doherty threshold**: respond within 400 ms; acknowledge input within 100 ms.
- **Fitts's law and hit areas**: large, close targets; 44x44 pt / 48x48 dp minimum; expand hit areas with pseudo-elements.
- **Hick's law**: fewer, grouped choices with a clear default.
- **Miller's law**: chunk information; don't make people remember across screens.
- **Postel's law**: accept messy input, output clean data.
- **Jakob's law**: follow conventions users know from other apps.
- **Von Restorff effect**: exactly one standout per view.
- **Goal-gradient effect**: show progress towards the goal.
- **Progressive disclosure**: essentials first, advanced on demand.
- **Affordance and signifiers**: interactive things look interactive.
- **Layout shift**: reserve space for everything that loads late.
- **Safe areas**: keep controls clear of notches and home indicators.
- **Combobox over long dropdowns**: searchable lists past about 10 to 15 options.
- **Concentric radii**: inner radius = outer radius minus padding.
- **Group with spacing**: proximity before borders and boxes.
- **Optical alignment**: centre by eye (play icons, circles, button text).
- **Redundancy gain**: convey status with colour plus icon plus text.
- **Continuity**: morph instead of swapping so the eye keeps its place.
- **Anthropomorphism**: light personality at low-stakes moments only.

### Typography ([typography.md](references/typography.md))

- Kerning on; tracking +0.04 to 0.08em on caps, slightly negative on big headlines; leading about 1.5 for body.
- Line length 45 to 75 characters (`max-width: 65ch`); `text-wrap: balance` on headings, `pretty` on paragraphs.
- Tabular numbers for changing or aligned numbers; reserved bold width for tabs; text-box trim in buttons.
- Underline offset, superscript `line-height: 0`, fluid type with `clamp()`, small caps for acronyms, curly quotes.
- Middle truncation for file names, `hyphens: auto` in narrow columns, line-clamped card titles.
- Text contrast at WCAG AA (4.5:1 body).
- Fonts by feeling (Swiss, friendly, personality, techy, vintage, serif, fun) and the generator-default fonts to avoid.

### Colour ([color.md](references/color.md))

- Work in OKLCH with role-named tokens, a neutral ramp and one accent; red and green only for status.
- Terms covered: hue, chroma, tint, shade, tone, analogous colours, simultaneous contrast, chromostereopsis, increased contrast mode, gamut, Abney effect, irradiation illusion, Stevens' power law, Hunt effect, Helmholtz–Kohlrausch effect, additive colour, opacity, sequential and diverging scales, relative luminance.

### Un-slop checklist ([unslop.md](references/unslop.md))

Delete filler badges, drop redundant labels, no random italic word, mono only where meaningful, use a design system, show the actual product, enlarge the main feature, specific headlines, one primary CTA, one accent colour instead of purple gradients, consistent icons, no decorative glows or glass, concentric radii, real contrast, balanced headlines, optical alignment, tabular numbers, loading/empty/error states, animate useful feedback only.

### Patterns ([patterns.md](references/patterns.md))

- **Add to cart**: a drawer that slides in and stays, with photo, variant, price, Keep shopping and Checkout. Never navigate away.
- **Password and sign-up**: no red rule walls or confirm field; block common passwords; offer a generated password; outline as strength meter; mono field so dots morph into letters; clear success state.
- **App Store screenshots**: brand colour, one idea per headline, branded headline style, real depth and lighting, one continuous visual across frames, hook split over the first two slides, social proof.
- **Pricing**: two to four plans, one recommended, tabular prices, one filled CTA.

---

## Hard rules

1. Motion must explain a change or give feedback. Remove motion that does neither.
2. Restraint over spectacle: don't stack several principles on one element.
3. Keep the brand (fonts, colours, voice) unless the user asks to change it.
4. Accessibility is never traded for style: contrast, focus, target size and reduced motion come first.
5. Presentation only. Leave data, state and business logic alone.
6. Audit only, Critique and Review modes don't edit files unless the user then asks.
7. Every claim in the report is something you checked. Say what you couldn't verify.
