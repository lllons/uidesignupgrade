---
name: uidesignupgrade
description: Upgrade an app or website UI with 18 UX and animation principles (exaggeration, origin awareness, staggering, squash and stretch, rubber banding, Doherty threshold, anticipation, Fitts's law, easing, Hick's law, follow-through, arcs, Von Restorff, timing, interruptible motion, secondary action, frequency of use, peak-end rule). Use when the user runs /uidesignupgrade, or asks to make a UI feel more polished, alive, responsive or "premium", add micro-interactions, or audit motion and interaction quality.
---

# UI Design Upgrade

Audit the target UI (code, screenshots or a running app) against the 18 principles below, then apply the upgrades that fit. Work in the project's existing stack and animation tools (CSS transitions, Web Animations API, Framer Motion, SwiftUI, Flutter, etc.). Do not add an animation library if the platform can already do it.

## Workflow

1. Find the interactive surfaces: buttons, menus, modals, lists, forms, navigation, errors, success states.
2. For each principle, note where it is missing or violated. Skip principles that do not apply.
3. Apply fixes, highest impact first: responsiveness (6, 14) and frequent actions (17), then feedback and motion polish.
4. Respect `prefers-reduced-motion` (or the platform equivalent): keep state changes, drop or shorten decorative motion.
5. Report a short before/after list: principle, where, what changed.

## The principles

1. **Exaggeration**: push feedback further than real life so it reads instantly. A wrong passcode shakes the whole lock and the dots turn red, not just a small text change.
2. **Origin awareness**: things grow out of whatever was tapped. A menu or modal scales and fades from its trigger (set `transform-origin` to the trigger), never pops in from nowhere.
3. **Staggering**: bring items in one after another, not all at once. Offset list or grid items by roughly 20 to 50 ms each, and cap the total so long lists don't drag.
4. **Squash and stretch**: let elements squish on press and stretch slightly on release so they feel soft, not stiff (e.g. a button scales to 0.96 on press and springs back).
5. **Rubber banding**: pulling past the end of a scroll or drag stretches with resistance, then springs back. Never hard-stop.
6. **Doherty threshold**: respond in under 400 ms or it feels like waiting. Show press state immediately, use optimistic UI, and add skeletons or progress for anything slower.
7. **Anticipation**: a small wind-up before a big motion tells the user what is about to happen (a slight pull-back before an element launches, a nudge before a drawer opens).
8. **Fitts's law**: bigger and closer is faster to hit. Make primary targets large (at least 44x44 pt / 24x24 CSS px), and put actions near where the cursor or thumb already is.
9. **Slow in, slow out**: nothing real starts or stops instantly. Use ease-in-out or springs, never `linear` for UI movement. Ease-out for entering, ease-in for leaving.
10. **Hick's law**: fewer choices mean faster picks. Shorten menus, group options, hide rarely used ones behind "More", and give a clear default.
11. **Follow-through**: details keep moving a beat after the main element stops (a card settles, its content or shadow catches up slightly later, a small overshoot).
12. **Arcs**: real things move in curves, not straight lines. Animate items flying from a FAB or between positions along a curved path instead of a straight diagonal.
13. **Von Restorff effect**: the item that looks different gets noticed. Make the recommended plan, primary action or current selection visually distinct; keep only one standout per view.
14. **Timing**: match duration to distance and importance. Micro-interactions about 100 to 200 ms, larger transitions about 200 to 400 ms; avoid anything over 500 ms for routine UI.
15. **Interruptible motion**: let people change their mind mid-animation. A tap during an opening sheet reverses it from its current position; never lock input until an animation ends.
16. **Secondary action**: a small extra motion backs up the main one. Liking a post fills the heart and adds a little particle burst.
17. **Frequency of use**: if people do it 50 times a day, skip or minimise the animation. Keyboard shortcuts, tab switches and frequent toggles should be instant or near-instant.
18. **Peak-end rule**: people remember the best moment and the ending. Make success states and flow endings feel rewarding (a clear confirmation, a subtle celebration), and never end a flow on an error or a dead end.

## Guardrails

- Motion must explain a change or give feedback. Remove motion that does neither.
- Keep animation on `transform` and `opacity` on the web for smooth frames; avoid animating layout properties.
- Don't stack several principles on one element until it feels busy. Restraint over spectacle.
