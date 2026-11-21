# Patterns and worked examples

Concrete, researched patterns for common screens. Use them when building or reviewing these flows.

## Add to cart: slide in, don't jump

**The question:** after tapping "Add to bag", should the shopper be sent to the cart page or see a cart that slides in over the product?

**What research found (Nielsen Norman Group shopping studies):**
- Jumping straight to the cart is fine for people buying one thing.
- People shopping for several items (a speaker, then a case, then a strap) get pulled out of their flow every time: back, scroll, find their place again.
- Slide-ins fail too if they vanish after a second: shoppers aren't sure it worked, tap Add again, and find duplicates at checkout.

**Build this:**
- A drawer or sheet that slides in from the side (desktop) or bottom (mobile) and **stays** until dismissed.
- It shows confirmation ("Added to bag" with a check), the item's photo, chosen colour or variant, price and quantity stepper, the subtotal, and optionally a short "Complete the set" row of related items.
- Two clear buttons: **Keep shopping** (closes the drawer, returns focus to where the user was) and **Checkout**.
- Update the cart count in the header at the same time (with a small bump animation) so the state is visible after the drawer closes.
- Accessibility: move focus into the drawer, trap focus, close on Esc and backdrop click, return focus to the Add button on close, and announce "Added to bag" via a live region.

**Avoid:** Auto-dismissing toasts as the only confirmation; navigating away on add; disabling Add without feedback (causes double taps).

## Password and sign-up screens

The generic generated version: a wall of red rules, a confirm-password field, and a form that yells before the user has typed anything.

**Build this instead:**
1. **Cut the red rules and the confirm field.** Show requirements calmly and only when relevant; use a show/hide toggle instead of a confirm field (it prevents typos without doubling the work).
2. **Be strict but honest.** Enforce a sensible minimum length (NIST recommends at least 8, ideally 15 for single-factor) and block common and breached passwords (check against a breached-password list such as Have I Been Pwned's k-anonymity API). Show one clear message when a password fails ("This password is too common").
3. **Make the secure path effortless.** Offer a generated strong password (and support the platform's password manager with `autocomplete="new-password"` and correct `name`/`id` attributes so it can suggest and save one).
4. **Make the outline the strength meter.** The field border fills or changes colour with strength, plus a word ("Strong"), which is redundancy gain: colour, length and text all say the same thing.
5. **Morph, don't swap.** Use a monospaced font for the field so hidden dots and revealed characters occupy the same positions and the reveal is continuous.
6. **Add personality only where it fits the brand.** Subtle sounds on success, a privacy blur when the password is revealed, a mascot that looks away while the password is visible (anthropomorphism). All optional, all non-blocking.
7. **End on a clear success state.** The button goes "Create account" → "Creating account…" (spinner) → "Account created ✓".

**Never:** block paste into password fields; impose maximum lengths under 64 characters; require arbitrary composition rules that push users to `Password1!`.

## App Store screenshots

The generic generated version: a purple gradient, a vague headline per slide, a phone mockup floating in space.

**Build this instead (from Duolingo and Strava redesigns):**
- **Brand colour, not a template gradient.** Duolingo is green; Strava is orange on a real dusk photograph.
- **One idea per headline,** in as few words as possible ("learn 40+ languages for free", "Hit the trails").
- **Give the headline the brand's personality.** Duolingo spells headlines with its word tiles; Strava uses its condensed italic display face and adds its Apple award.
- **Depth and lighting.** Real photography or a lit backdrop, soft shadows under devices, consistent light direction: it reads as premium.
- **One continuous visual across all frames.** Strava runs its orange route line across every screenshot; Duolingo's mascot bursts out of one frame into the next. The set reads as one immersive panorama when scrolled.
- **Split the hook across the first two slides** so they read as one sentence ("If it's not on Strava, / it didn't happen."). Most people only see the first two.
- **Social proof.** Ratings, Editors' Choice, awards, user counts.
- **Show the real product.** Actual app screens, not abstract illustrations.

## Pricing pages

- Two to four plans maximum; one is clearly recommended (Von Restorff) with a meaningful label ("Most popular"), not a decorative badge.
- Prices in tabular figures; show the billing period next to the number.
- Make the recommended plan's call to action the only filled button.
- Put the differences in a comparison table below; keep each card to the five or six features that actually differ.
