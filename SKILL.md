---
name: uidesignupgrade
description: Upgrade an app or website UI with a growing library of UX, animation, typography, colour and "un-slop" principles (motion like origin awareness, staggering, easing and interruptible motion; UX laws like Fitts's, Hick's, Miller's and Jakob's; typography details like tabular numbers, text-box trim and line length; colour theory like OKLCH, contrast and perceptual scales; researched patterns like slide-in carts; and a checklist for removing generic AI-generated design). Use when the user runs /uidesignupgrade, or asks to make a UI feel more polished, alive, responsive, premium or less AI-generated, add micro-interactions, fix typography or colour, pick fonts, design App Store screenshots, or audit motion and interaction quality.
---

# UI Design Upgrade

Audit the target UI (code, screenshots or a running app) against the principles below, then apply the upgrades that fit. Work in the project's existing stack and tools (CSS, Tailwind, Framer Motion, SwiftUI, Flutter, Compose, etc.). Do not add a library if the platform can already do it.

This file is the index. **Before implementing anything in a section, read its reference file** (paths are relative to this file). The references explain what each principle is, why it works, exact values and code, common mistakes and how to check the result.

| Section | Reference | Read it when |
|---------|-----------|--------------|
| Motion and interaction | [references/motion.md](references/motion.md) | adding or changing any animation, transition or gesture |
| UX laws and layout | [references/ux-laws.md](references/ux-laws.md) | laying out screens, sizing targets, designing choices, forms and loading |
| Typography and fonts | [references/typography.md](references/typography.md) | setting or reviewing text, choosing fonts |
| Colour | [references/color.md](references/color.md) | building a palette, dark mode, charts or checking contrast |
| Un-slop checklist | [references/unslop.md](references/unslop.md) | reviewing anything that looks generic or AI-generated |
| Patterns | [references/patterns.md](references/patterns.md) | building add-to-cart, sign-up/password, App Store screenshots or pricing |

## Workflow

1. Identify the stack and the existing design tokens (colours, spacing, radii, fonts, motion). Extend them; don't invent a parallel system. If the user has reference designs, screenshots or sites they like, treat them as the target look and match their spacing, type and colour decisions rather than defaulting to generic choices.
2. Find the surfaces: buttons, menus, modals, lists, forms, navigation, loading, empty, error and success states.
3. For each section that applies, read its reference and note where principles are missing or violated. Skip what doesn't apply.
4. Fix in this order: broken responsiveness and layout shift, accessibility (contrast, targets, focus, reduced motion), the un-slop checklist, typography and colour, then motion polish.
5. Respect `prefers-reduced-motion`, `prefers-contrast` and forced colours (or the platform equivalents).
6. Verify in the running app, not just the code: open it in a real browser, screenshot it at mobile and desktop widths, and compare against the reference and these principles. Use DevTools Performance and Animations panels, a contrast checker and keyboard-only use.
7. Polish pass: look at the screenshots for things that are slightly off (uneven spacing, edges that don't line up, inconsistent radii, text that sits off-centre) and fix them. These are easy to miss and make a big difference.
8. Pre-launch check: run the un-slop checklist one last time on the finished screens to catch any remaining signs that the design was AI-generated.
9. Report a short before/after list: principle, where, what changed.

## Motion and interaction (details: references/motion.md)

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

## UX laws and layout (details: references/ux-laws.md)

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

## Typography (details: references/typography.md)

- Kerning on; tracking +0.04 to 0.08em on caps, slightly negative on big headlines; leading about 1.5 for body.
- Line length 45 to 75 characters (`max-width: 65ch`); `text-wrap: balance` on headings, `pretty` on paragraphs.
- Tabular numbers for changing or aligned numbers; reserved bold width for tabs; text-box trim in buttons.
- Underline offset, superscript `line-height: 0`, fluid type with `clamp()`, small caps for acronyms, curly quotes.
- Middle truncation for file names, `hyphens: auto` in narrow columns, line-clamped card titles.
- Text contrast at WCAG AA (4.5:1 body).
- Fonts by feeling (Swiss, friendly, personality, techy, vintage, serif, fun) and the generator-default fonts to avoid.

## Colour (details: references/color.md)

- Work in OKLCH with role-named tokens, a neutral ramp and one accent; red and green only for status.
- Terms covered: hue, chroma, tint, shade, tone, analogous colours, simultaneous contrast, chromostereopsis, increased contrast mode, gamut, Abney effect, irradiation illusion, Stevens' power law, Hunt effect, Helmholtz–Kohlrausch effect, additive colour, opacity, sequential and diverging scales, relative luminance.

## Un-slop checklist (details: references/unslop.md)

Delete filler badges, drop redundant labels, no random italic word, mono only where meaningful, use a design system, show the actual product, enlarge the main feature, specific headlines, one primary CTA, one accent colour instead of purple gradients, consistent icons, no decorative glows or glass, concentric radii, real contrast, balanced headlines, optical alignment, tabular numbers, loading/empty/error states, animate useful feedback only.

## Patterns (details: references/patterns.md)

- **Add to cart**: a drawer that slides in and stays, with photo, variant, price, Keep shopping and Checkout. Never navigate away.
- **Password and sign-up**: no red rule walls or confirm field; block common passwords; offer a generated password; outline as strength meter; mono field so dots morph into letters; clear success state.
- **App Store screenshots**: brand colour, one idea per headline, branded headline style, real depth and lighting, one continuous visual across frames, hook split over the first two slides, social proof.
- **Pricing**: two to four plans, one recommended, tabular prices, one filled CTA.

## Guardrails

- Motion must explain a change or give feedback. Remove motion that does neither.
- Don't stack several principles on one element until it feels busy. Restraint over spectacle.
- Keep the product's existing brand (fonts, colours, voice) unless the user asks to change it.
- Accessibility is never traded for style: contrast, focus visibility, target size and reduced motion come first.
