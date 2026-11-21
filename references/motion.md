# Motion and interaction: full reference

Read this before adding or changing any animation. Each entry says what the principle is, why it works, how to build it (with values you can copy), what to avoid, and how to check it.

## Shared tokens

Use one small set of tokens across the whole product so motion feels like one system.

```css
:root {
  /* durations */
  --dur-instant: 0ms;      /* frequent, keyboard-driven actions */
  --dur-fast: 120ms;       /* press states, hovers, toggles */
  --dur-base: 200ms;       /* menus, popovers, tooltips */
  --dur-slow: 320ms;       /* sheets, dialogs, page-level transitions */
  /* easing */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* entering: fast start, soft landing */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* moving on screen from A to B */
  --ease-in: cubic-bezier(0.55, 0, 1, 0.45);         /* leaving: only for exits */
}
```

Springs (when the platform has them): Framer Motion `{ type: "spring", stiffness: 400, damping: 30 }` for UI, `{ stiffness: 260, damping: 24 }` for larger panels. SwiftUI `.spring(response: 0.35, dampingFraction: 0.8)`. Flutter `SpringDescription(mass: 1, stiffness: 400, damping: 30)`.

Always add a reduced-motion path:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
}
```

Better still, swap movement for a short opacity fade rather than removing feedback entirely.

---

## Exaggeration

**What:** Push feedback beyond what is physically realistic so it reads in a glance. Borrowed from Disney's 12 principles: a cartoon character's reaction is bigger than a real person's.

**Why:** A small colour change on an error is easy to miss, especially in peripheral vision, for colour-blind users, or on a bright screen. Motion is detected by peripheral vision far better than colour.

**How:** On a wrong password, shake the field or the whole lock horizontally, turn the border red, and show the message. Shake keyframes: `translateX(0, -8px, 8px, -6px, 6px, -3px, 3px, 0)` over 400 ms with `--ease-out`. On mobile, pair with an error haptic (`UINotificationFeedbackGenerator().notificationOccurred(.error)` on iOS, `HapticFeedbackConstants.REJECT` on Android). Announce the error to screen readers with `aria-live="polite"` or `role="alert"`.

**Avoid:** Exaggerating success and neutral states as much as errors (save it for moments that matter); shaking more than once per attempt; shakes longer than about 500 ms.

**Check:** Squint at the screen from a metre away. Can you tell the attempt failed without reading?

## Origin awareness

**What:** An element that appears should come out of the thing that triggered it, and return there when it closes.

**Why:** It shows cause and effect. The user sees where the menu "lives", so the spatial model of the interface stays intact.

**How:** Set `transform-origin` to the trigger's position relative to the popover. Radix exposes `var(--radix-popover-content-transform-origin)` (also for dropdowns, tooltips, hover cards); Floating UI gives you the placement so you can derive it. Animate `scale(0.97) → 1` plus `opacity 0 → 1` over `--dur-base` with `--ease-out`. For a FAB that expands into a menu, scale from the FAB's centre.

**Avoid:** Centre-of-screen modals that grow from the middle when the trigger was in a corner; origin set to `center` by default on every popover.

**Check:** Open the menu in slow motion (DevTools Animations panel at 10%). Does it visibly grow from the button?

## Scale from 0.97, not 0

**What:** Entering elements start almost full size (`scale(0.97)`) and invisible, then settle to `scale(1)` while fading in.

**Why:** Nothing in the real world grows from a dot. A full scale-from-zero reads as a cheap zoom effect and makes text unreadable for most of the animation. A 3% scale plus fade gives a sense of depth and arrival without the zoom.

**How:**

```css
@keyframes enter { from { opacity: 0; transform: scale(0.97); } }
.dialog[data-state="open"] { animation: enter var(--dur-base) var(--ease-out); }
```

Exits can be faster (about 150 ms) and can skip the scale.

**Avoid:** `scale(0)`, `scale(0.5)`, bouncy overshoot on dialogs that contain forms.

**Check:** Pause mid-animation. Is the content already legible?

## Staggering

**What:** Items in a list or grid enter one after another with a small delay, rather than all at once.

**Why:** It guides the eye in reading order and makes a screen feel composed rather than dumped. It also hides the cost of loading many items.

**How:** Delay each item by 20 to 50 ms: `animation-delay: calc(var(--i) * 30ms)` with `style="--i: 3"` on each item, or Framer Motion `staggerChildren: 0.03`. Cap the total so the last item starts within about 300 ms (only stagger the first 8 to 10 items, then show the rest together). Animate opacity and a small `translateY(8px)`.

**Avoid:** Staggering on every re-render or filter change (only on first entry); staggering items the user is waiting to click; delays above 80 ms per item.

**Check:** Does the whole list finish appearing in under half a second?

## Squash and stretch / press feedback

**What:** Elements deform slightly under force: a button compresses when pressed, a ball squashes on impact and stretches as it moves fast. The total volume should feel constant.

**Why:** It communicates material and responsiveness. A button that physically reacts to a press feels like it heard you, even before anything else happens.

**How:** `button:active { transform: scale(0.97); transition: transform var(--dur-fast) var(--ease-out); }`. On release, spring back (a spring is ideal, `--ease-out` is fine). For playful elements (a like button, a toggle knob) you can squash more: scaleX 1.1, scaleY 0.9 on impact.

**Avoid:** Scaling below about 0.95 on regular buttons (feels broken); press states that only change colour; delaying the press state until a network request starts.

**Check:** Press and hold. Does the button respond within one frame?

## Rubber banding

**What:** When the user drags or scrolls past the end of the content, it keeps moving but with increasing resistance, then springs back on release.

**Why:** A hard stop feels like the interface broke. Resistance tells the user "this is the edge" while still acknowledging their input. It is native behaviour on iOS and macOS, so its absence feels foreign.

**How:** Map overscroll distance with diminishing returns. Apple's formula: `offset = (1 - 1 / ((x * 0.55 / d) + 1)) * d`, where `x` is the raw drag distance and `d` the container dimension. On release, animate back to 0 with a spring. Framer Motion: `drag="x" dragConstraints={...} dragElastic={0.2}`. For carousels, apply it at both ends.

**Avoid:** Linear overscroll (feels slippery); no spring-back; enabling it on content that should not move (fixed toolbars).

**Check:** Drag past the end slowly. The further you pull, the less it moves.

## Anticipation

**What:** A small preparatory motion in the opposite direction before a big motion.

**Why:** It tells the user something is about to happen and which way it will go, so the main motion is easier to follow.

**How:** Before a card flies to the right, pull it 5 to 10% left and scale it to about 0.95 for 100 to 150 ms, then launch with `--ease-in-out`. A send button can dip down before the paper plane flies up. Keep the wind-up short: it must not delay the user's task.

**Avoid:** Anticipation on frequent actions (it adds latency); wind-ups longer than about 150 ms.

**Check:** Does the wind-up make the direction of the next motion obvious?

## Staging

**What:** Present one idea at a time so the user's attention lands where you want it.

**Why:** When several things move or change at once, nothing gets attention. Staging comes from theatre: light the actor who is speaking.

**How:** When something important happens (a new item, an error, a completed step), animate only that element and dim, blur or hold still everything else. In a dashboard update, highlight the changed card (lift with a shadow, scale 1.02) and fade the others to about 40% opacity briefly. Sequence related changes instead of running them simultaneously.

**Avoid:** Animating every card on data refresh; multiple competing pulses or badges.

**Check:** Pause on any frame. Is there exactly one obvious focal point?

## Pose to pose

**What:** Define the key states first (closed, open, loading, done), make each one look right as a static design, then animate between them.

**Why:** Motion designed frame by frame drifts and produces in-between states that look broken. If both end states are good, the interpolation is usually good too.

**How:** Model components as explicit states (`data-state="closed|open"`, a state machine, SwiftUI state enums). Design each state in isolation. Then add one transition per state change. Use layout animation tools (Framer Motion `layout`, SwiftUI implicit animations, the View Transitions API) to interpolate between them.

**Avoid:** Chained `setTimeout` choreography; animations that depend on intermediate DOM states.

**Check:** Screenshot each state. Would each work as a still?

## Slow in, slow out (easing)

**What:** Objects accelerate as they start and decelerate as they stop. Nothing real moves at a constant speed.

**Why:** Linear motion looks robotic and makes the end abrupt. Easing makes movement feel physical and directs attention to the destination.

**How:** Entering elements use ease-out (fast start, gentle stop) so they feel responsive. Elements moving from one place to another use ease-in-out. Exiting elements use ease-in or a fast ease-out. Use springs for anything the user drags or flicks. Only use `linear` for continuous loops (spinners, progress shimmer) and for opacity crossfades.

**Avoid:** The browser default `ease` everywhere; `ease-in` on entrances (feels laggy because the start is slow).

**Check:** Plot the curve (cubic-bezier.com). Does entering motion front-load its speed?

## Follow-through and overlapping action

**What:** When the main body stops, attached parts keep moving briefly and settle afterwards.

**Why:** It adds weight and realism: real objects have parts with their own inertia.

**How:** When a card slides in and stops, let its inner content arrive 30 to 60 ms later with a slight overshoot, or let a badge bob once. Use a spring with low damping on the child (`damping: 18`) and a stiffer spring on the parent. Keep overshoot under about 5% of the distance.

**Avoid:** Overshoot on text-heavy or form content; follow-through that makes the UI feel wobbly.

**Check:** Does the element feel heavier and more settled, not jelly-like?

## Arcs

**What:** Natural movement follows curved paths, not straight lines.

**Why:** Limbs pivot and thrown objects follow parabolas. Straight diagonal motion between two points reads as mechanical.

**How:** For elements travelling between two points (items flying from a FAB, an item flying into a cart), animate X and Y with different easings (for example X with ease-out, Y with ease-in) or along a path with `offset-path: path(...)` and `offset-distance`. In Framer Motion animate `x` and `y` with separate transitions.

**Avoid:** Arcs on small UI movements (menus, tooltips) where a straight short move is clearer.

**Check:** Trace the path of the moving element. Is it a gentle curve?

## Secondary action

**What:** A smaller supporting motion that reinforces the main one.

**Why:** It adds delight and emphasis without changing the meaning. The main action stays clear; the secondary one makes it memorable.

**How:** Liking a post: the heart fills and pops (main), plus a ring and a few particles burst out and the count rolls up (secondary). Completing a task: the checkbox ticks (main), the row strikes through and fades (secondary). Keep secondary motion shorter and lower-contrast than the main one.

**Avoid:** Secondary actions on every interaction; particles on serious or frequent actions.

**Check:** Remove the secondary motion. Is the main action still fully understandable? (It must be.)

## Timing

**What:** Duration should match the distance travelled, the size of the element and how often the action happens.

**Why:** Too slow feels sluggish and blocks the user; too fast is jarring or invisible.

**How:** Press and hover 80 to 150 ms. Tooltips, small popovers 150 to 200 ms. Menus, dropdowns 180 to 250 ms. Sheets, dialogs, drawers 250 to 350 ms. Full page transitions 300 to 450 ms. Larger and further-travelling elements get the longer end. Exits are about 20 to 30% faster than entrances.

**Avoid:** Anything over 500 ms for routine UI; the same duration for a tooltip and a full-screen sheet.

**Check:** Use the feature ten times in a row. Does any animation start to feel like waiting?

## Interruptible motion

**What:** Users can change their mind mid-animation, and the animation reverses or retargets from wherever it currently is.

**Why:** Locking input until an animation finishes makes the interface feel slow and unresponsive, and punishes fast users.

**How:** In CSS, use transitions (not keyframe animations) for state toggles: transitions reverse from their current value when the state flips, keyframes restart from the beginning. In JS use springs or WAAPI animations you can retarget. Never disable buttons for the length of an animation. A tap on the backdrop of a half-open sheet should close it from its current position.

**Avoid:** `pointer-events: none` during transitions; `animationend` callbacks that gate interaction.

**Check:** Click open and immediately click close. Does it reverse smoothly without jumping?

## Directional transitions

**What:** In steppers, wizards, carousels and tab-like flows, content moves in the direction of navigation: forward slides in from the right, back slides in from the left.

**Why:** It builds a spatial model of the flow ("step 3 is to the right of step 2"), so users understand where they are.

**How:** Track the direction of the change (`+1` or `-1`). Enter: `translateX(direction * 40px) → 0` with fade. Exit: `0 → translateX(-direction * 40px)` with fade. Clip the container (`overflow: clip`). Framer Motion: `AnimatePresence custom={direction}` with variants keyed on `direction`. Respect RTL by flipping the direction.

**Avoid:** Crossfading every step (no sense of order); full-width slides on large screens (too much motion).

**Check:** Go forward then back. Does the content move in opposite directions?

## Animate to auto height

**What:** Expanding content (accordions, "show more", details) animates to its natural height instead of snapping.

**Why:** A snap makes the rows below jump, which is disorienting and loses the user's place.

**How:** Modern CSS:

```css
:root { interpolate-size: allow-keywords; }
.panel { height: 0; overflow: clip; transition: height var(--dur-base) var(--ease-out); }
.panel[data-open] { height: auto; }
```

Fallback that works everywhere: animate `grid-template-rows` from `0fr` to `1fr` on a grid wrapper with an `overflow: hidden` child. For `<details>`, style `::details-content`. In JS, measure `scrollHeight` and animate to it.

**Avoid:** Animating `max-height` to a huge value (timing becomes wrong); animating height on large, frequently toggled lists (performance).

**Check:** Open and close quickly. No jump, no delay before the content moves.

## Transform, not layout

**What:** Animate only `transform` and `opacity` (and `filter` sparingly). Never animate `top`, `left`, `width`, `height` or `margin` for movement.

**Why:** Transform and opacity are handled by the compositor on the GPU. Layout properties force the browser to recalculate layout and repaint every frame, which drops frames on mid-range phones.

**How:** Move with `translate`, resize visually with `scale`, reveal with `clip-path` or opacity. For layout changes (reordering, resizing), use the FLIP technique (First, Last, Invert, Play) or Framer Motion `layout`, which converts layout changes into transforms. Add `will-change: transform` only while animating, not permanently.

**Avoid:** `transition: all` (animates layout properties by accident); permanent `will-change` on many elements.

**Check:** DevTools Performance panel: no purple Layout bars during the animation.

## Instant theme switches

**What:** When switching light/dark (or any theme), apply the new colours instantly with transitions disabled.

**Why:** Every element has its own colour transition with its own duration, so during a switch text, backgrounds and borders change at different speeds. For a moment you get white text on a white card. It looks glitchy.

**How:** Add a class that disables transitions, change the theme, force a reflow, then remove the class on the next frame:

```js
document.documentElement.classList.add("no-transitions");
setTheme(next);
getComputedStyle(document.documentElement).opacity; // force reflow
requestAnimationFrame(() => document.documentElement.classList.remove("no-transitions"));
```

```css
.no-transitions * { transition: none !important; }
```

`next-themes` has `disableTransitionOnChange`. If you want a deliberate effect, use one View Transition crossfade for the whole page.

**Avoid:** Per-component colour transitions that fire during a theme change.

**Check:** Toggle the theme in slow motion. Is there any frame with unreadable text?

## Tooltip delay only once

**What:** The first tooltip waits before appearing; once one is open, moving to neighbouring triggers shows their tooltips instantly.

**Why:** The initial delay prevents tooltips flashing up as the pointer passes over. But once the user is clearly exploring a toolbar, making them wait again on every icon feels slow.

**How:** Initial delay about 500 to 700 ms. Skip window about 300 ms: if the pointer reaches another trigger within that time of leaving one, show immediately with no fade. Radix: `<Tooltip.Provider delayDuration={600} skipDelayDuration={300}>`. Tooltips should also appear on keyboard focus.

**Avoid:** Zero delay on the first tooltip (noisy); the same delay for every tooltip.

**Check:** Sweep the pointer across a toolbar after the first tooltip appears. Each one shows instantly.

## Velocity-matched springs

**What:** When a gesture ends (a flick, a drag release), the follow-up animation starts at the gesture's speed and decelerates naturally.

**Why:** A fixed-duration tween ignores how hard the user flicked. A fast flick followed by a slow, fixed animation feels disconnected, like the UI grabbed control from the user.

**How:** Pass the release velocity into a spring. Framer Motion does this automatically for drag; for manual animations use `animate(value, target, { type: "spring", velocity })`. SwiftUI springs inherit velocity when retargeted. UIKit: `UIView.animate(... usingSpringWithDamping:, initialSpringVelocity:)` with velocity normalised by distance. Use velocity to decide the target too: a fast flick to the side dismisses even if the distance was short.

**Avoid:** CSS transitions for gesture follow-through (they cannot take velocity).

**Check:** Flick gently, then hard. The hard flick travels faster and further.

## Shared element transitions

**What:** One element visually morphs into its counterpart on the next screen (a thumbnail grows into the hero image, a card expands into a detail page).

**Why:** It preserves context and object constancy: the user sees it is the same thing, just bigger, so they never lose their place.

**How:** Web: the View Transitions API. `document.startViewTransition(() => updateDOM())` and give the matching elements the same unique `view-transition-name` (e.g. `photo-42`). For multi-page apps, `@view-transition { navigation: auto; }`. SwiftUI: `matchedGeometryEffect` or `navigationTransition(.zoom)`. Flutter: `Hero`. Android Compose: `sharedElement()`.

**Avoid:** Duplicate `view-transition-name` values on one page (the transition fails); morphing elements that change meaning.

**Check:** Navigate back and forth. Does the element appear to physically travel?

## Optimistic updates

**What:** Show the result of an action immediately, assuming it will succeed, and reconcile with the server afterwards.

**Why:** Most actions succeed. Waiting for a round trip (often 200 to 1000 ms) before showing the result breaks the Doherty threshold for no benefit.

**How:** Update local state on click; send the request; on failure, roll back and show a clear, non-blocking error with a retry. React: `useOptimistic`. TanStack Query: `onMutate` to update the cache, `onError` to restore the snapshot, `onSettled` to refetch. Good fits: likes, toggles, reordering, renaming, adding to a list, sending a chat message (show it as "sending").

**Avoid:** Optimistic UI for payments, deletions that cannot be undone, or anything where a false success is harmful.

**Check:** Throttle the network to Slow 3G. The UI still responds instantly; a forced failure rolls back cleanly.

## Useful, exaggerated feedback

**What:** Animate feedback that tells the user something happened (added to cart, copied, saved), and make it clear enough to notice.

**Why:** Users need confirmation that their action worked. Decorative animation competes for attention; informative animation earns it.

**How:** Morph the button into its result ("Add to cart" → "Added ✓" with the price count ticking), flash a short confirmation next to where the user acted, not in a far corner. Keep it under about 1 second, then return to the resting state if the action can be repeated.

**Avoid:** Toasts in a corner for actions that happened somewhere else on screen; animations that loop or linger.

**Check:** Look only at the spot you clicked. Do you know it worked?

## Frequency of use

**What:** The more often an action is performed, the less it should animate.

**Why:** A delightful 300 ms animation becomes a tax when you see it 50 times a day. Power users notice the waiting, not the delight.

**How:** No animation for keyboard-initiated actions (shortcuts, command palette open and close, arrow-key navigation in lists). Instant tab switches in apps people live in. Keep motion for first-run, rare and celebratory moments.

**Avoid:** Animated route transitions in dashboards; animated command palettes.

**Check:** List the top five most frequent actions. Do any of them animate for more than 100 ms?

## Peak-end rule

**What:** People judge an experience mostly by its most intense moment and its ending, not by the average.

**Why:** From Kahneman's research: memory is built from peaks and endings. A smooth checkout that ends on a confusing page is remembered as bad.

**How:** Invest polish in the moments of success: the order confirmation, the completed upload, the first project created. Use a clear success state, a moment of celebration that fits the brand (a check that draws itself, a subtle confetti burst), and an obvious next step. Make error recovery feel kind.

**Avoid:** Ending flows on a blank page, a generic "Success", or an upsell modal; celebrating trivial actions.

**Check:** What is the last thing the user sees in each key flow? Is it rewarding?

## Appeal

**What:** The overall charm and consistency of motion: does it feel like one product with one personality?

**Why:** Consistent motion builds trust and recognisability. A mix of bouncy, linear and slow animations feels assembled from parts.

**How:** Use the shared tokens above everywhere. Decide the personality once (calm and precise, or playful and springy) and apply it consistently. Review motion as a whole, not component by component.

**Avoid:** Different libraries with different defaults in one app; one-off magic numbers.

**Check:** Record a screen capture of a full flow. Does the motion feel like one voice?
