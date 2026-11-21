# UX laws and layout: full reference

Each entry: what the law says, why it holds, how to apply it in a real interface, common mistakes, and a quick check.

## Doherty threshold

**What:** Productivity and satisfaction rise sharply when a system responds in under about 400 ms. Above that, users perceive waiting and their attention drifts. (Walter Doherty and Ahrvind Thadani, IBM, 1982.)

**Why:** Short delays keep the user in a flow of action and feedback. Once delay is noticeable, users start wondering whether their input registered.

**How:**
- Acknowledge every input within 100 ms: press states, focus rings, a spinner inside the button.
- Use optimistic updates for likely-to-succeed actions (see motion.md).
- For anything that takes over about 1 s, show progress: skeleton screens shaped like the final content, determinate progress bars for long tasks, streaming results.
- Prefetch on hover or intent, cache aggressively, and lazy-load what is below the fold.
- Measure INP (Interaction to Next Paint) and keep it under 200 ms.

**Avoid:** Blank screens while loading; spinners for actions that could be optimistic; a button that does nothing visible until the server replies.

**Check:** Throttle CPU 4x and network to Fast 3G. Does every click show a visible response immediately?

## Fitts's law and hit areas

**What:** The time to reach a target depends on its distance and its size: `T = a + b * log2(D / W + 1)`. Bigger and closer targets are faster and more accurate to hit. (Paul Fitts, 1954.)

**Why:** Pointing is a ballistic movement followed by corrections. Small, far targets need more corrections.

**How:**
- Make primary actions large. Minimum touch targets: 44x44 pt on iOS, 48x48 dp on Android, and at least 24x24 CSS px for WCAG 2.2 (44x44 recommended).
- Expand the hit area without changing the visual: `.icon-btn { position: relative } .icon-btn::before { content: ""; position: absolute; inset: -10px; }`.
- Put actions near where the pointer or thumb already is: confirm buttons near the content they act on, primary mobile actions in the bottom third of the screen (thumb zone).
- Screen edges and corners are effectively infinite targets for a mouse (menus at the top edge on macOS); use them for frequent actions on desktop.
- Leave at least 8 px between adjacent small targets to prevent mis-taps.

**Avoid:** Tiny icon-only buttons with no padding; destructive actions next to frequent ones; important actions in the top corners of tall phones.

**Check:** Turn on a hit-area outline (temporary `outline` on `::before`). Is every target at least 44 px?

## Hick's law

**What:** Decision time grows with the number and complexity of choices, roughly logarithmically: `T = b * log2(n + 1)`. (William Hick and Ray Hyman, 1952.)

**Why:** Every option has to be read and compared. More options also increase the chance of choosing nothing at all.

**How:**
- Limit visible choices; put rarely used options behind "More" or in settings.
- Highlight a recommended default (pre-select the most common option).
- Group long lists into labelled categories and use search for anything over about 10 items.
- Break complex tasks into steps with one decision each (onboarding, checkout).

**Avoid:** Navigation bars with 9 equal items; pricing pages with 5 plans and no recommendation; dialogs with 4 buttons.

**Check:** Count the choices on each screen. Can any be removed, grouped or defaulted?

## Miller's law

**What:** The average person can hold about 7 (plus or minus 2) items in working memory. Later research suggests closer to 4 chunks. (George Miller, 1956.)

**Why:** Working memory is small. Content that requires remembering many separate pieces overwhelms people and causes errors.

**How:**
- Chunk information: format phone numbers (`021 555 0192`), card numbers (`4242 4242 4242 4242`) and codes (`ABCD-1234`) in groups.
- Keep visible options short and grouped; use headings to break up long settings pages.
- Show, don't make people remember: keep entered data visible on review screens, show the previous step's choices in a summary.
- One-time codes: split into separate boxes or show grouped digits.

**Avoid:** Asking users to remember a code from one screen to type on another; long unbroken lists; using the "7 items" number as a hard rule for menus (it is about memory, not menu length).

**Check:** Does any task require remembering something that is no longer on screen?

## Postel's law (robustness principle)

**What:** Be conservative in what you send and liberal in what you accept. (Jon Postel, TCP specification, 1980.)

**Why:** Users type data in many valid formats. Rejecting reasonable input wastes their time and makes the product feel pedantic.

**How:**
- Accept phone numbers with spaces, dashes, brackets or a country code, then normalise.
- Accept dates in multiple formats or use a date picker; accept "tomorrow" where it makes sense.
- Trim whitespace from pasted values; ignore case in emails and codes; accept card numbers with or without spaces.
- Use the right `inputmode`, `type` and `autocomplete` attributes (`autocomplete="one-time-code"`, `inputmode="numeric"`) so the platform helps.
- Output consistently: display normalised data in one standard format.

**Avoid:** "Invalid format" errors for input that is clearly understandable; blocking paste into password or code fields.

**Check:** Paste messy but valid input into every field. Does it work?

## Jakob's law

**What:** Users spend most of their time on other sites and apps, so they expect yours to work the same way as the ones they already know. (Jakob Nielsen.)

**Why:** Familiar patterns cost nothing to learn. Novel patterns force users to figure things out instead of getting work done.

**How:**
- Follow platform conventions: iOS back swipe and tab bar, Android back button, desktop keyboard shortcuts (Cmd/Ctrl+K for search or command palette, Esc to close).
- Logo top-left links home; account and cart top-right; search icon is a magnifying glass; settings is a gear.
- Use standard components (native selects on mobile, standard form layouts) unless you have a measured reason to deviate.
- Innovate in the product's core value, not in basic controls.

**Avoid:** Custom scroll behaviour; hamburger menus on desktop with plenty of space; reinventing checkboxes and radios.

**Check:** Could a first-time user predict what every control does from other apps they use?

## Von Restorff effect (isolation effect)

**What:** When several similar items are shown, the one that differs is the one people notice and remember. (Hedwig von Restorff, 1933.)

**Why:** Attention is drawn to contrast. Distinctiveness also aids memory.

**How:**
- Make the recommended plan, primary button or current selection visually distinct: filled vs outlined, accent colour, slightly larger, a short meaningful label ("Most popular").
- Keep only one standout per view; if everything is highlighted, nothing is.
- Do not rely on colour alone: also change weight, size, border or add an icon (accessibility).

**Avoid:** Multiple competing "primary" buttons; highlighting things for decoration.

**Check:** Squint at the screen. Does exactly one thing stand out, and is it the right one?

## Goal-gradient effect

**What:** People speed up as they get closer to a goal. (Clark Hull, 1932; confirmed in loyalty-card studies.)

**Why:** Visible progress motivates. Starting with some progress already made increases completion.

**How:** Show progress bars and step counters in multi-step flows; show how close the user is to a reward or milestone (Strava's progress-towards-goal visuals); pre-fill obvious steps so the user starts partway through ("Step 2 of 4" after account creation).

**Avoid:** Progress indicators that move backwards or stall; unclear end points.

**Check:** Can users always see how far they are from finishing?

## Progressive disclosure

**What:** Show only what most people need now; reveal advanced or rarely used options on demand.

**Why:** It reduces cognitive load for beginners while keeping power available for experts.

**How:** "Advanced settings" sections, expandable rows, "Show more" for long text, wizards for complex setup, contextual menus for secondary actions. Make the disclosure control clearly labelled and remember the user's choice.

**Avoid:** Hiding things people need often; more than two levels of nesting; disclosure controls that look like content.

**Check:** Can a new user complete the main task without opening anything? Can an expert reach every option in two clicks?

## Affordance and signifiers

**What:** An affordance is what an object lets you do; a signifier is the visible cue that tells you so. (Don Norman.)

**Why:** Users decide what to tap by looking. If a control does not look interactive, it is invisible.

**How:** Buttons look pressable (filled or outlined, with padding); links are underlined or clearly coloured in body text; draggable items have a handle and change the cursor; inputs have visible boundaries; disabled controls look disabled and explain why when hovered or focused. Use `cursor: pointer` on clickable non-link elements and visible focus rings for keyboard users.

**Avoid:** Text that looks like a button but is not; flat icons with no hit area or hover state; removing focus outlines.

**Check:** Screenshot the screen in greyscale. Can you identify every interactive element?

## Layout shift

**What:** Content moving unexpectedly after it has rendered, usually because images, ads, fonts or async content load late.

**Why:** It causes misclicks (the user taps a button that moves away), breaks reading, and hurts Core Web Vitals (CLS should be under 0.1).

**How:**
- Always set `width` and `height` attributes or `aspect-ratio` on images, videos and iframes.
- Reserve space for async content with skeletons the same size as the final content.
- Use `font-display: swap` with a fallback font matched using `size-adjust`, `ascent-override` and `descent-override`, or `font-display: optional`.
- Use `scrollbar-gutter: stable` so pages don't shift when a scrollbar appears.
- Insert new content below the viewport or behind a "Show new items" button, never above what the user is reading.
- Reserve bold width on tabs (see typography.md) and tabular numbers on changing values.

**Avoid:** Banners that push content down after load; images without dimensions; spinners replaced by taller content.

**Check:** Record a page load in DevTools Performance with Layout Shift Regions enabled.

## Safe areas

**What:** The parts of a screen not covered by the notch, Dynamic Island, rounded corners, home indicator or system bars.

**Why:** Controls under the home indicator or behind the notch are hard or impossible to use, and content clipped by rounded corners looks broken.

**How:** Web: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` and pad with `env(safe-area-inset-top)` etc. (`padding-bottom: max(16px, env(safe-area-inset-bottom))`). React Native: `SafeAreaView` / `react-native-safe-area-context`. SwiftUI respects safe areas by default; use `.ignoresSafeArea()` only for backgrounds. Android: handle window insets (`WindowInsetsCompat`) with edge-to-edge.

**Avoid:** Fixed bottom bars without inset padding; full-bleed backgrounds that stop at the safe area.

**Check:** Test on a device or simulator with a notch and home indicator, in both orientations.

## Combobox over long dropdowns

**What:** A combobox is an input with a filterable list of options: type to narrow, arrow keys to choose, Enter to select.

**Why:** Scrolling a 200-item `<select>` (countries, timezones, currencies) is slow. Typing three letters is fast.

**How:** Use a combobox for lists over about 10 to 15 items. Follow the WAI-ARIA combobox pattern (`role="combobox"`, `aria-expanded`, `aria-activedescendant`, listbox options), or use an accessible library (Radix, React Aria, Headless UI, cmdk). Put likely choices first (detected country, recent items). Match on aliases ("UK" finds "United Kingdom").

**Avoid:** Comboboxes for 3 to 5 options (use radio buttons or a segmented control); custom dropdowns that break keyboard and screen reader support.

**Check:** Can you pick an option using only the keyboard in under three seconds?

## Concentric radii (inner = outer minus padding)

**What:** When a rounded element sits inside another rounded element, the inner radius should equal the outer radius minus the padding between them.

**Why:** Only then do the curves run parallel. Equal radii look wrong: the inner corner looks too round and the gap at the corner looks thicker.

**How:** `--outer: 16px; --pad: 8px; .outer { border-radius: var(--outer); padding: var(--pad); } .inner { border-radius: calc(var(--outer) - var(--pad)); }`. If the padding is larger than the outer radius, the inner element can be square or use a small radius.

**Avoid:** One radius token used for every nesting level.

**Check:** Zoom into the corner. Is the gap even all the way around the curve?

## Group with spacing

**What:** Use proximity and whitespace to show which things belong together, before adding borders, boxes or dividers (Gestalt law of proximity).

**Why:** Space is quieter than lines. Interfaces full of boxes and dividers look busy and generic.

**How:** Use a spacing scale (4, 8, 12, 16, 24, 32, 48, 64). Space within a group must be clearly smaller than space between groups (a common rule: at least 2x). Labels sit closer to their own field than to the previous field. Remove borders that spacing already explains.

**Avoid:** Equal spacing everywhere; cards inside cards inside cards; dividers between every row.

**Check:** Blur the screenshot. Do the groups still read as groups?

## Optical alignment

**What:** Align and centre things by how they look, not by their mathematical bounding boxes.

**Why:** Shapes have different visual weight. A play triangle centred by its box looks too far left; a circle looks smaller than a square of the same width; text in a button looks low because of descender space.

**How:** Nudge play icons right by about 5 to 10% of their width. Make circles and pointed shapes slightly larger (about 5 to 10%) than squares meant to look the same size (overshoot). Use `text-box: trim-both cap alphabetic` to centre button text. Hang punctuation and bullets outside the text block (`hanging-punctuation: first`). Align icons with the cap height of adjacent text, not the line box.

**Avoid:** Trusting the layout tool's "centred" when it looks off.

**Check:** Flip the screenshot horizontally. Does anything suddenly look off-centre?

## Redundancy gain

**What:** Information conveyed through two or more channels at once (colour and icon and text, or visuals and sound) is perceived faster and more reliably.

**Why:** If one channel is missed (colour blindness, glare, looking away), the other still gets through.

**How:** Errors use red plus an icon plus text; success uses green plus a check plus a message; a password strength meter uses colour plus the outline's length plus a word ("Strong"); optional sound or haptics reinforce key moments.

**Avoid:** Colour as the only signal (fails WCAG 1.4.1).

**Check:** View in greyscale with sound off. Is every status still clear?

## Continuity (Gestalt)

**What:** The eye follows smooth lines and perceives elements arranged along a continuous path as related, and perceives an object that transforms smoothly as the same object.

**Why:** Smooth transformation preserves identity: password dots that morph into letters read as "the same text, now revealed".

**How:** Morph rather than swap (a monospaced font lets hidden dots and revealed characters occupy the same positions); align related items along a line; carry a visual thread across screens (a route line across App Store screenshots).

**Avoid:** Hard swaps that make the user re-find their place.

**Check:** After a state change, can the user's eye stay where it was?

## Anthropomorphism

**What:** Giving interface elements human or creature-like traits: eyes, reactions, a mascot.

**Why:** People respond socially to faces. A little personality makes moments memorable and can soften friction.

**How:** Use sparingly, at low-stakes moments, and in line with the brand: a mascot that covers its eyes while the password is visible, a character reacting to an empty state. Always keep the functional UI fully usable without it.

**Avoid:** Personality in serious contexts (errors about money, health); characters that slow down tasks.

**Check:** Remove the character. Does everything still work and read clearly?
