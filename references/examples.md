# Worked examples: one per mode

Read the example for your mode before you start. Each one shows the request, what the agent did at each step, the findings it confirmed or rejected, the actual edits, and the final report. Copy the **shape**, not the specific values: your project's tokens and screens will differ.

Contents:

1. [Full upgrade: Tailwind SaaS dashboard](#1-full-upgrade-tailwind-saas-dashboard)
2. [Audit only: landing page](#2-audit-only-landing-page)
3. [Targeted: "the numbers jump around"](#3-targeted-the-numbers-jump-around)
4. [New build: settings screen](#4-new-build-settings-screen)
5. [Critique: a screenshot, no code](#5-critique-a-screenshot-no-code)
6. [Review: a pull request](#6-review-a-pull-request)
7. [Un-slop: "looks like every AI site"](#7-un-slop-looks-like-every-ai-site)
8. [Native: SwiftUI targeted motion fix](#8-native-swiftui-targeted-motion-fix)
9. [When to stop and ask](#9-when-to-stop-and-ask)

---

## 1. Full upgrade: Tailwind SaaS dashboard

**Request:** "/uidesignupgrade make the dashboard feel more premium"

**Mode:** Full upgrade (broad request, code present). First line of the reply: *"Running a full upgrade on the dashboard; I'll fix P0 to P3 and list anything that needs your OK."*

**Step 1, read the project.**

```sh
rg -n "@theme" -g "*.css" .
# app/globals.css:3:@theme {
```

Notes: Next.js + Tailwind v4. `@theme` has `--font-sans: "Inter"` (it's in the brand guide in `docs/brand.md`, so it stays), radii `--radius-md: 8px`, `--radius-lg: 12px`, colours in hex, no motion tokens, dark mode via `.dark`. Reference: none given; the Billing page is the cleanest screen, so match that.

**Step 2, before.** Screenshots `before-390.png`, `before-1440.png` of `/dashboard`.

**Step 3, surfaces.** Stat cards (4), revenue chart, recent-orders table, filter dropdown, "New report" button, sidebar nav. States: table has **no loading state** (blank until data arrives) and **no empty state**; chart has no error state.

**Step 4, detect.** Ran audit.md section 2. Hits and verdicts:

| Hit | File | Verdict |
|-----|------|---------|
| `outline-none` | `components/ui/button.tsx:12` | **real**: no `focus-visible:` on the button |
| `outline-none` | `components/ui/input.tsx:8` | false positive: `focus-visible:ring-2` follows it |
| reduced-motion search | (no output) | **real**: no reduced-motion path anywhere |
| `transition-all` | `StatCard.tsx:20`, `Sidebar.tsx:44` | **real** |
| `bg-gradient-to-r from-violet-500 to-indigo-500` | `StatCard.tsx:9` | **real**: decorative gradient on every card |
| `tabular-nums` search | (no output) | **real**: stats and table amounts change |
| `ease-linear` | `Spinner.tsx:5` | false positive: it's a spinner |
| `\bInter\b` | `globals.css:4` | false positive: brand font |

Visual checks on the screenshots: muted text `#9ca3af` on white is 2.5:1 (fails); four stat cards each use a different accent; icon buttons in the table are 28 px.

**Step 5, rank.**

- P0: button focus ring, reduced-motion path, muted contrast, 28 px icon buttons, table loading state (layout jumps when data lands).
- P1: violet gradient cards, four accent colours, missing empty state.
- P2: tabular numbers on stats and amounts.
- P3: dropdown grows from trigger; press feedback on buttons.
- Proposed: none needed.

**Step 6, fix.** Token first:

```css
/* app/globals.css */
@theme {
  --color-muted: #6b7280;            /* was #9ca3af: 4.8:1 on white */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --dur-fast: 120ms;
  --dur-base: 200ms;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
}
```

Then the components:

```diff
- <div className="rounded-lg p-5 bg-gradient-to-r from-violet-500 to-indigo-500 text-white transition-all">
+ <div className="rounded-lg border bg-card p-5">
-   <p className="text-3xl font-semibold">{value}</p>
+   <p className="text-3xl font-semibold tabular-nums">{value}</p>
```

```diff
  // button.tsx
- "outline-none transition-all ..."
+ "outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 transition-[transform,background-color] duration-(--dur-fast) ease-(--ease-out) active:scale-[0.97] ..."
```

Table: skeleton rows with the same height as a **loaded** row (measured: 44 px button + 20 px padding = 64 px; a first try with 24 px cells made the table grow by 60 px when data landed); an empty state using the existing `EmptyState` component ("No orders yet" + "Create an order" button). Icon buttons `size-7` → `size-11` with the icon still `size-4`. Dropdown: `origin-(--radix-dropdown-menu-content-transform-origin)` plus fade from `scale-[0.97]`.

Not touched: the data hooks, the chart library, the sidebar structure.

**Step 7, verify.** After-screenshots at both widths; Lighthouse a11y 84 → 100; tabbed through: focus visible on every control; reduced motion emulated: dropdown fades without scaling; reloaded on Slow 4G: no jump when the table fills.

**Step 10, report.**

```md
## UI upgrade: Dashboard

Reference: existing Billing page
Verified: screenshots at 390 and 1440, Lighthouse a11y 84 → 100, keyboard pass, reduced motion, Slow 4G reload
Not verified: dark mode chart colours (no dark-mode seed data)

| Level | Principle | Where | Change |
|-------|-----------|-------|--------|
| P0 | Focus visibility | `button.tsx` | added focus-visible ring in accent |
| P0 | Reduced motion | `globals.css` | added reduced-motion block |
| P0 | Text contrast | `--color-muted` | #9ca3af (2.5:1) → #6b7280 (4.8:1) |
| P0 | Hit areas | order table icon buttons | 28 → 44 px |
| P0 | Layout shift | order table | skeleton rows at final height |
| P1 | One accent colour | `StatCard.tsx` | removed violet gradient and 4 accents; neutral cards |
| P1 | Empty state | order table | "No orders yet" + create button |
| P2 | Tabular numbers | stat values, amounts | `tabular-nums` |
| P3 | Origin awareness | filter dropdown | grows from trigger, 200 ms ease-out |
| P3 | Press feedback | `button.tsx` | scale 0.97 on press |

Proposed, needs your OK: none
```

---

## 2. Audit only: landing page

**Request:** "Be brutal. What's wrong with my landing page?"

**Mode:** Audit only. **Do not edit files.** First line: *"Audit only: here's what I found, ranked; nothing has been changed."*

Same steps 1 to 5 as example 1, then the report. Differences from a full upgrade:

- The "Change" column becomes "Fix", written as an instruction with values the user could apply.
- Add a "Why it matters" column only if the user seems unfamiliar with the terms.
- End with an offer, not a claim.

```md
## UI audit: Landing page (/)

Reference: none given; judged against the un-slop list and audit.md levels
Checked: screenshots at 390 and 1440, Lighthouse a11y 71, keyboard pass
Not checked: checkout flow (behind login)

| Level | Principle | Where | Fix |
|-------|-----------|-------|-----|
| P0 | Zoom disabled | `app/layout.tsx` viewport | remove `maximum-scale=1` |
| P0 | Text contrast | hero subtitle (#a1a1aa on #fafafa, 2.4:1) | use `--muted` at ≥ 4.5:1 |
| P0 | Layout shift | hero image has no width/height | add `width`/`height` or `aspect-ratio: 16/9` |
| P1 | Filler badge | "✨ New: AI-powered" pill above the headline | delete it |
| P1 | Specific headline | "Supercharge your workflow" | name the product and a number: "Close your books in 2 days, not 10" |
| P1 | One primary CTA | three filled buttons in the hero | keep "Start free"; make "Book a demo" a secondary/ghost button; drop the third |
| P1 | Show the product | abstract 3D blob as hero image | use a real product screenshot |
| P2 | Balanced headings | hero h1 leaves one word on line 2 | `text-wrap: balance` |
| P2 | Tabular numbers | pricing toggles monthly/annual and digits shift | `font-variant-numeric: tabular-nums` |

Want me to apply the P0 and P1 fixes? The headline rewrite and hero image need your input.
```

---

## 3. Targeted: "the numbers jump around"

**Request:** "The prices in the cart wiggle when the quantity changes. Fix it."

**Mode:** Targeted (typography), plus any P0 spotted on the way.

1. Read typography.md "Tabular numbers".
2. `rg -n "price|total|subtotal" -g "*.tsx" src/components/cart` → `CartLine.tsx`, `CartSummary.tsx`.
3. Confirm: proportional digits, and a `$` that sits in the same span so the whole string reflows.
4. Fix, one class each, no other changes:

```diff
- <span className="font-medium">{formatPrice(total)}</span>
+ <span className="font-medium tabular-nums">{formatPrice(total)}</span>
```

5. Noticed while there: the quantity stepper buttons are 24 px (P0 target size). Fixed it, because P0s are always in scope. Noticed too: cart drawer uses `transition-all` (P3). **Not fixed**: outside the request; mentioned in the report.

```md
## UI upgrade: Cart prices

Verified: changed quantity 1 → 12 → 1 at 390 px; digits no longer shift
| Level | Principle | Where | Change |
|-------|-----------|-------|--------|
| P2 | Tabular numbers | `CartLine.tsx`, `CartSummary.tsx` | `tabular-nums` on prices and totals |
| P0 | Hit areas | quantity stepper | 24 → 44 px |

Also noticed, not changed: cart drawer uses `transition-all` (motion, P3). Say the word if you want it fixed.
```

---

## 4. New build: settings screen

**Request:** "Add a notification settings page that matches the app."

**Mode:** New build. The principles are **constraints while building**, not an audit afterwards.

1. Read the tokens (step 1). Find the closest existing screen (`/settings/profile`) and the components it uses: `PageHeader`, `Card`, `Switch`, `Button`.
2. Build with only those components and tokens. No new colours, radii or font sizes.
3. Apply the principles as you go:
   - Group related toggles with spacing and one heading per group (ux-laws.md, Group with spacing), not a box around each row.
   - Each row: label + one-line description; the whole row is the hit area, not just the switch.
   - Progressive disclosure: "Quiet hours" options appear only when its switch is on, opening to auto height.
   - Optimistic update: the switch flips immediately, rolls back with an inline error if the save fails.
   - States: loading (skeleton rows at final height), error ("Couldn't load your settings. Retry"), saved (small "Saved" text, not a toast for every toggle; frequent action, no celebration).
4. Run the un-slop list on the result before reporting.

**Wrong** way to do this: a new `NotificationCard` with its own `rounded-2xl shadow-xl` and a gradient header, because "settings should look nice". That's a second design system.

---

## 5. Critique: a screenshot, no code

**Request:** *(attaches `onboarding.png`)* "thoughts?"

**Mode:** Critique. You can only judge what's visible. Don't mention files, classes or tokens you haven't seen. Give values the designer can use.

```md
## Critique: Onboarding step 2

1. **One focal point (P1).** The illustration, the headline and three equally bright buttons compete. Keep one filled "Continue"; make "Skip" a text button.
2. **Progress (P1).** No sign of how many steps are left. Add "Step 2 of 4" or a 4-segment bar (goal-gradient effect).
3. **Contrast (P0).** The light grey caption looks below 4.5:1 on the cream background. Darken it to roughly #5f5a52 and check with a contrast tool.
4. **Concentric radii (P2).** The card looks ~24 px radius with ~8 px padding, but the image inside is ~24 px too. Inner should be ~16 px.
5. **Headline wrap (P2).** "Pick your interests" breaks with "interests" alone on line 2. Balance it or shorten it.

Can't judge from a still: motion, focus states, tap-target sizes in points, dark mode.
```

---

## 6. Review: a pull request

**Request:** "Review PR #42 for UI issues."

**Mode:** Review. Only the changed lines. Don't edit unless asked.

1. Get the diff (`gh pr diff 42` or `git diff main...HEAD`).
2. Run the detectors on **changed files only**, then check that each hit is on a **changed line**:

```sh
git diff --name-only main...HEAD | xargs rg -n "transition-all|outline-none|scale-0|100vh|bg-clip-text"
```

3. Comment by priority, with the line and a concrete suggestion:

```md
## UI review: PR #42 (new pricing toggle)

| Level | File:line | Issue | Suggestion |
|-------|-----------|-------|------------|
| P0 | `PricingToggle.tsx:18` | `<div onClick>` toggle: no keyboard access | use `<button role="switch" aria-checked>` |
| P2 | `PlanCard.tsx:31` | price changes monthly/annual and shifts width | add `tabular-nums` |
| P3 | `PlanCard.tsx:12` | `transition-all duration-700` | `transition-[transform,opacity] duration-200 ease-out` |

Outside this diff (not blocking): the existing pricing headline is generic; worth a separate pass.
```

Don't flag code the PR didn't touch except as one "outside this diff" line.

---

## 7. Un-slop: "looks like every AI site"

**Request:** "Our homepage looks like every AI startup. Fix it."

**Mode:** Un-slop. Go through unslop.md item by item on the rendered page, then typography, then colour.

Before (typical generated hero):

```tsx
<section className="bg-gradient-to-br from-purple-600 via-violet-600 to-indigo-700 py-32 text-center">
  <span className="rounded-full bg-white/10 px-3 py-1 text-sm backdrop-blur">✨ Now with AI</span>
  <h1 className="mt-6 bg-gradient-to-r from-white to-purple-200 bg-clip-text text-6xl font-bold text-transparent">
    Supercharge your <em>workflow</em>
  </h1>
  <p className="mt-4 text-white/60">The next-gen platform to unlock your team's potential.</p>
  <div className="mt-8 flex justify-center gap-4">
    <Button>Get started</Button><Button>Book demo</Button><Button>Watch video</Button>
  </div>
</section>
```

After:

```tsx
<section className="bg-bg py-24">
  <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 lg:grid-cols-[1fr_1.2fr]">
    <div>
      <h1 className="text-5xl font-semibold tracking-tight text-fg text-balance">
        Invoices reconciled in minutes, not month-end
      </h1>
      <p className="mt-4 max-w-[55ch] text-lg text-muted text-pretty">
        Ledger matches bank lines to invoices automatically and flags the 3% that need a human.
      </p>
      <div className="mt-8 flex gap-3">
        <Button>Start free</Button>
        <Button variant="ghost">Book a demo</Button>
      </div>
    </div>
    <img src="/product/reconcile.png" width="1200" height="800" alt="Ledger's reconciliation view matching bank lines to invoices" className="rounded-lg border" />
  </div>
</section>
```

What changed, mapped to unslop.md: filler badge deleted; gradient background and gradient text → neutral surface and solid text; random italic removed; specific headline with a concrete claim; one filled CTA, one ghost, third dropped; real product screenshot instead of nothing; balanced heading, bounded paragraph width; image has dimensions (no layout shift).

**Ask first** before shipping the new headline and subtitle: copy is the user's. In the report, put the proposed copy under "Proposed, needs your OK" if they haven't approved it, and leave a neutral placeholder or the original text in the code.

---

## 8. Native: SwiftUI targeted motion fix

**Request:** "The sheet in my iOS app feels janky."

**Mode:** Targeted (motion). Read motion.md (Timing, Interruptible motion, Velocity-matched springs) and platforms.md.

```sh
rg -n "\.animation\(|withAnimation|\.transition\(" -g "*.swift" .
# Views/FilterSheet.swift:41: .animation(.linear(duration: 0.6), value: isOpen)
# Views/FilterSheet.swift:44: .transition(.scale)
```

Confirmed: linear easing, 600 ms, scaling from 0.

```diff
- .transition(.scale)
- .animation(.linear(duration: 0.6), value: isOpen)
+ .transition(.move(edge: .bottom).combined(with: .opacity))
+ .animation(reduceMotion ? .easeOut(duration: 0.15) : .spring(response: 0.35, dampingFraction: 0.8), value: isOpen)
```

with `@Environment(\.accessibilityReduceMotion) private var reduceMotion` at the top of the view.

Verify: simulator recording; tap open and close quickly (it reverses, doesn't queue); Settings > Accessibility > Motion > Reduce Motion on: sheet fades instead of sliding.

---

## 9. When to stop and ask

Stop and ask (or, if the user isn't around, put it under "Proposed") when the right fix would:

| Situation | Say something like |
|-----------|--------------------|
| change the brand font | "Your headings use Inter, which reads as a generic default. Want me to try a different face, or keep the brand font?" |
| rewrite real copy | "The headline is vague. Suggested: '...'. Use it?" |
| add a dependency | "A spring here needs Framer Motion, which isn't installed. CSS gets 90% of the way. Install it, or stay with CSS?" |
| remove a section | "The testimonials carousel has two quotes and auto-rotates. I'd replace it with two static quotes. OK?" |
| restructure navigation | "Settings is three levels deep. Moving it to the top nav changes the IA. Want that?" |
| mode is unclear | "Do you want a report, or should I make the changes?" |

Don't ask about things the skill already decides: adding focus rings, fixing contrast with an existing token, `tabular-nums`, `text-wrap: balance`, replacing `transition: all`, adding reduced-motion paths. Just do them (in modes that edit).
