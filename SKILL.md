---
name: uidesignupgrade
description: Upgrade an app or website UI with a growing library of UX, animation, typography and "un-slop" principles (motion like origin awareness, staggering, easing and interruptible motion; UX laws like Fitts's, Hick's and Jakob's; typography details like tabular numbers, text-box trim and line length; and a checklist for removing generic AI-generated design). Use when the user runs /uidesignupgrade, or asks to make a UI feel more polished, alive, responsive, premium or less AI-generated, add micro-interactions, fix typography, pick fonts, design App Store screenshots, or audit motion and interaction quality.
---

# UI Design Upgrade

Audit the target UI (code, screenshots or a running app) against every principle below, then apply the upgrades that fit. Work in the project's existing stack and animation tools (CSS transitions, Web Animations API, Framer Motion, SwiftUI, Flutter, etc.). Do not add an animation library if the platform can already do it.

## Workflow

1. Find the interactive surfaces: buttons, menus, modals, lists, forms, navigation, errors, success states.
2. For each principle, note where it is missing or violated. Skip principles that do not apply.
3. Apply fixes, highest impact first: responsiveness (Doherty threshold, interruptible motion, layout shift) and frequent actions (frequency of use), then the un-slop checklist, typography, and motion polish.
4. Respect `prefers-reduced-motion` (or the platform equivalent): keep state changes, drop or shorten decorative motion.
5. Report a short before/after list: principle, where, what changed.

## Motion and interaction

- **Exaggeration**: push feedback further than real life so it reads instantly. A wrong password doesn't just turn red: the field or lock shakes and the error is unmistakable.
- **Origin awareness**: things grow out of whatever was tapped. A menu or modal scales and fades from its trigger (set `transform-origin` to the trigger), never pops in from nowhere.
- **Scale from 0.97, not 0**: entering dialogs and popovers start at `scale(0.97)` with `opacity: 0` and settle to 1. Scaling from 0 looks like a zoom from a dot.
- **Staggering**: bring items in one after another, not all at once. Offset list or grid items by roughly 20 to 50 ms each, and cap the total so long lists don't drag.
- **Squash and stretch / press feedback**: let elements squish on press and spring back so they feel soft, not stiff. Buttons scale to about 0.97 on `:active`.
- **Rubber banding**: pulling past the end of a scroll, carousel or drag stretches with resistance, then springs back. Never hard-stop.
- **Anticipation**: a small wind-up before a big motion tells the user what is about to happen (a slight pull-back before an element launches, a nudge before a drawer opens).
- **Staging**: direct the eye to one thing at a time. When something important changes, dim or quiet everything else instead of animating all of it.
- **Pose to pose**: design the start and end states first (the key poses), then let the transition interpolate between them. Don't improvise motion frame by frame.
- **Slow in, slow out**: nothing real starts or stops instantly. Use ease-in-out or springs, never `linear` for UI movement. Ease-out for entering, ease-in for leaving.
- **Follow-through**: details keep moving a beat after the main element stops (a card settles, its content or shadow catches up slightly later, a small overshoot).
- **Arcs**: real things move in curves, not straight lines. Animate items flying from a FAB or between positions along a curved path instead of a straight diagonal.
- **Secondary action**: a small extra motion backs up the main one. Liking a post fills the heart and adds a little particle burst.
- **Timing**: match duration to distance and importance. Micro-interactions about 100 to 200 ms, larger transitions about 200 to 400 ms; avoid anything over 500 ms for routine UI.
- **Interruptible motion**: let people change their mind mid-animation. A tap during an opening sheet reverses it from its current position; never lock input until an animation ends.
- **Directional transitions**: in steppers, wizards and carousels, Next slides content left and Back slides it right. Don't just crossfade between steps.
- **Animate to auto height**: accordions and expanding panels shouldn't snap. On the web, set `interpolate-size: allow-keywords` on `:root` so `height: auto` transitions smoothly (or measure the height in JS as a fallback).
- **Transform, not layout**: animate `transform` and `opacity`, never `top`, `left`, `width` or `height` for movement. Layout properties repaint every frame and stutter.
- **Instant theme switches**: switching light/dark fires every colour transition at once, at different speeds, and looks glitchy. Disable transitions during the swap (e.g. add a `no-transition` class for one frame).
- **Tooltip delay only once**: delay the first tooltip (about 500 to 700 ms), then show the rest instantly while the pointer moves across neighbours (`skipDelayDuration` in Radix).
- **Velocity-matched springs**: when the user flicks or drags, carry their release velocity into a spring instead of a fixed-duration tween, so the motion keeps their speed.
- **Shared element transitions**: one element grows into the next view (a thumbnail becomes the header image) so the user never loses their place. Use the View Transitions API where available.
- **Optimistic updates**: show the result immediately (the like, the saved state) and reconcile with the server after; roll back with a clear message if it fails.
- **Exaggerated, useful feedback**: animate feedback that tells the user something (added to cart, saved, copied). Don't animate decoration.
- **Frequency of use**: if people do it 50 times a day, skip or minimise the animation. Keyboard shortcuts, tab switches, command palettes and frequent toggles should be instant.
- **Peak-end rule**: people remember the best moment and the ending. Make success states and flow endings feel rewarding (a clear confirmation, a subtle celebration), and never end a flow on an error or a dead end.
- **Appeal**: the sum of the above. Motion should feel like it belongs to the brand and the product, consistent in timing and character across the app.

## UX laws and layout

- **Doherty threshold**: respond in under 400 ms or it feels like waiting. Show press state immediately, use optimistic UI, and add skeletons or progress for anything slower.
- **Fitts's law and hit areas**: bigger and closer is faster to hit. Make primary targets large and put actions near where the cursor or thumb already is. The clickable area can be bigger than the visible element: pad small icons to at least 44x44 pt (iOS) / 48x48 dp (Android) / 24x24 CSS px minimum.
- **Hick's law**: fewer choices mean faster picks. Shorten menus, group options, hide rarely used ones behind "More", and give a clear default.
- **Miller's law**: people hold about 7 (plus or minus 2) items in working memory. Chunk long content: group settings, split phone and card numbers into groups, break long forms into steps.
- **Postel's law**: be liberal in what you accept and strict in what you output. Accept phone numbers with spaces or dashes, dates in several formats and pasted text with stray whitespace, then normalise them.
- **Jakob's law**: people spend most of their time in other apps, so they expect yours to work the same way. Use familiar patterns (logo top-left links home, cart top-right, swipe to go back) unless you have a strong reason not to.
- **Von Restorff effect**: the item that looks different gets noticed. Make the recommended plan, primary action or current selection visually distinct; keep only one standout per view.
- **Progressive disclosure**: show the essentials first and reveal advanced options on demand ("Advanced settings", expandable rows).
- **Affordance**: things should look like what they do. Buttons look pressable, draggable things have a handle, links look like links.
- **Layout shift**: reserve space for images, ads, fonts and async content (`aspect-ratio`, fixed skeleton sizes, `font-display` with matched fallbacks) so nothing jumps while the user is about to click.
- **Safe areas**: keep content and controls clear of the notch, Dynamic Island and home indicator (`env(safe-area-inset-*)`, `SafeAreaView`).
- **Combobox over giant dropdowns**: for long option lists (countries, timezones) use a searchable combobox instead of a long `<select>`.
- **Inner radius = outer radius minus padding**: nested rounded corners look concentric only when the inner radius equals the outer radius minus the gap between them.
- **Group with spacing**: show relationships with proximity and whitespace before reaching for borders, boxes and dividers.
- **Align by eye, not just by pixels**: centre icons and play buttons optically (a play triangle sits slightly right of the mathematical centre), and nudge round shapes to match square ones.

## Typography

- **Kerning and tracking**: kerning adjusts space between specific letter pairs; tracking is even spacing across every letter. Add a little positive tracking to all-caps labels and tighten large headlines slightly.
- **Leading**: line height around 1.4 to 1.6 for body text, tighter (1.1 to 1.25) for large headings.
- **x-height**: fonts with a taller lowercase read better at small sizes; compare x-height when pairing or swapping fonts.
- **Line length**: aim for about 45 to 75 characters per line (around 66 is ideal). Cap text columns with `max-width: 65ch`.
- **Widows and wrapping**: avoid a single word alone on the last line. Use `text-wrap: balance` for headings and `text-wrap: pretty` for paragraphs.
- **Tabular numbers**: use `font-variant-numeric: tabular-nums` for prices, timers, tables and counters so digits don't jitter as they change.
- **Reserved bold width**: when a tab or menu item turns bold on hover or selection, reserve the bold width (e.g. a hidden bold copy via `::after { content: attr(data-text); font-weight: 700; visibility: hidden; height: 0 }`) so the row doesn't shift.
- **Text-box trim**: fonts leave room for descenders, so text in buttons and badges sits slightly off-centre. Use `text-box: trim-both cap alphabetic` (`text-box-trim` / `text-box-edge`) to centre it.
- **Underline offset**: default underlines collide with g, y and p. Use `text-underline-offset: 0.2em` (and `text-decoration-thickness`).
- **Superscript spacing**: `<sup>` pushes line height and makes rows uneven. Use `sup { line-height: 0; vertical-align: baseline; position: relative; top: -0.5em }`.
- **Fluid type**: instead of jumping sizes at breakpoints, size headlines with `clamp()`, e.g. `font-size: clamp(2rem, 1rem + 5vw, 4rem)`.
- **Small caps for acronyms**: all-caps acronyms (API, CSV, PDF) shout in running text. Use `font-variant-caps: all-small-caps`.
- **Curly quotes**: use typographic quotes and apostrophes (“ ” ‘ ’) instead of straight ones.
- **Middle truncation**: truncate file names in the middle (`Q4 board upd…final.pdf`) so the extension stays visible.
- **Auto hyphenation**: narrow columns create big gaps between words. Set `lang` on the page and `hyphens: auto`.
- **Line-clamped titles**: cap long card titles with `line-clamp: 2` (`-webkit-line-clamp`) so cards in a row stay the same height.
- **OKLCH colour**: define palettes in `oklch()` so lightness steps look even across hues and generated tints and shades stay consistent.
- **Text contrast**: body text should meet WCAG AA (4.5:1). Grey-on-grey placeholder-style body text is a common AI-design tell.

## Fonts

Pick type for the feeling you want, and avoid the fonts that make a site look AI-generated.

- **Clean Swiss look**: ABC Diatype, TWK Lausanne, Switzer, Saans, Areal, Strichpunkt Sans.
- **Friendly**: Studio Feixen Sans, PP Mori, Aeonik, Degular, GT Walsheim, Circular.
- **A bit of personality**: Apfel Grotezk, Aktiv Grotesk, ABC Favorit, Familjen Grotesk, ABC Monument Grotesk, ABC Oracle.
- **Techy**: ABC Diatype Mono, Söhne Mono, GT America Mono, IBM Plex Mono, Commit Mono, Departure Mono.
- **Vintage**: Editorial New, ABC Arizona, ABC Marist, Concrette, GT Super, Blazeface.
- **Modern serif**: Tiempos Fine, Reckless, Signifier, Canela, Luperca, Domaine Display.
- **Soft serif**: EB Garamond, Exposure, GT Alpina, Mioya, Tiempos Text, Lyon Text.
- **Fun**: Gautreaux, Hobeaux, Obviously, Absans, GT Maru, 5by7.
- **Overused in AI-generated designs (avoid as the default)**: Inter, Roboto, Arial, Instrument Serif, Fraunces, Playfair Display, Geist, Space Grotesk, Bricolage Grotesque, Instrument Sans, JetBrains Mono, Space Mono.

Many of these are commercial; check licensing, and keep the project's existing brand font if it has one.

## Un-slop checklist (removing the generic AI look)

- Delete filler badges ("New", "AI-powered", "✨") that carry no information.
- Drop redundant labels that repeat what the heading or icon already says.
- Don't italicise one random word in the headline.
- Use monospace only where it means something (code, IDs, numbers), not as decoration.
- Use a design system: consistent spacing scale, radii, colours and components.
- Show the actual product (real screenshots, real data) instead of abstract illustrations or blobs.
- Enlarge the main feature; don't give every feature the same weight.
- Make headlines specific to the product instead of vague slogans.
- Emphasise the primary call to action; one clear CTA per view.
- Add one accent colour instead of default purple gradients.
- Keep icons consistent: one icon set, one stroke weight, one size.
- Remove unnecessary embellishments: glows, gradient borders, glassmorphism and noise used for their own sake.
- Wrap headlines properly (balanced lines, no orphaned word).
- Add loading, empty and error states, not just the happy path.
- Animate useful feedback only.

## App Store screenshots

- Use the brand's real colours, not a generic purple gradient.
- One idea per headline, in as few words as possible.
- Give the headlines the brand's personality (Duolingo-style word tiles, a signature font).
- Use real imagery for depth (a photo backdrop such as a dusk coastline) and add lighting and shadows so devices feel premium.
- Run one continuous visual element across every frame (a route line, a mascot bursting into the next screenshot) so the set feels immersive.
- Split the hook across the first two slides so they read as one sentence.
- Add social proof: ratings, awards, editor's choice.

## Worked example: un-slopping a password screen

- Cut the wall of red rules and the confirm field; it stops the form yelling at the user.
- Enforce strict rules quietly and block common passwords, with one clear message when it fails.
- Offer a generated strong password so the secure path is effortless.
- Make the field outline the strength meter, and use a monospaced font so dots morph into the real characters when revealed.
- Add small touches of personality where they fit the brand: subtle sounds, a privacy blur, a mascot that looks away while the password is visible.
- Finish with a clear success state on the button (Creating account… → Account created).

## Guardrails

- Motion must explain a change or give feedback. Remove motion that does neither.
- Keep animation on `transform` and `opacity` on the web for smooth frames; avoid animating layout properties.
- Don't stack several principles on one element until it feels busy. Restraint over spectacle.
