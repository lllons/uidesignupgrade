# Un-slop checklist: full reference

Generated interfaces share recognisable tells. Each item below explains the tell, why it hurts, and what to do instead. Run this list on any UI that was produced quickly or by a model.

## How to run it

- **Start from references.** Ask for (or find) reference designs, screenshots or sites the user likes, and match their decisions. Generic output comes from designing without a target.
- **Judge the rendered page, not the code.** Open it in a real browser, screenshot it at mobile and desktop widths, and review the screenshots against this list. Many tells (uneven spacing, misaligned edges, off-centre text) are only visible when rendered.
- **Polish pass.** Fix the small things that look slightly off: spacing that isn't on the scale, edges that don't line up, mixed radii, icons that sit low.
- **Pre-launch check.** Before the page goes live, go through every item below on the final screens.

## Delete filler badges

**Tell:** "New", "AI-powered", "✨ Beta", "Featured" pills on headings and cards that carry no real information.
**Why it hurts:** Badges are meant to signal something unusual. When everything has one, they become noise and make the page feel like a template.
**Do instead:** Remove them. Keep a badge only when it changes a decision (a real "New" on a feature released this week, a status like "Overdue").

## Drop redundant labels

**Tell:** A section titled "Features" with an eyebrow saying "FEATURES" above it; an icon of an envelope labelled "Email" next to an email address; "Click here" buttons.
**Why it hurts:** Repetition costs reading time and pushes real content down.
**Do instead:** Say each thing once. Let headings, icons and context do their jobs; label buttons with the action ("Export CSV").

## Don't italicise one random word

**Tell:** "Build *faster* with our platform" with one word in a serif italic.
**Why it hurts:** It is one of the most recognisable generator signatures and rarely means anything.
**Do instead:** Set the headline in one style. Use emphasis only when the sentence actually needs stress.

## Use monospace only where it means something

**Tell:** Mono fonts for headings, labels and body copy to look "technical".
**Why it hurts:** Mono is harder to read in long runs and loses its signal value (code, data, IDs).
**Do instead:** Use mono for code, keys, IDs, timestamps and aligned numeric data only.

## Use a design system

**Tell:** Slightly different paddings, radii, shadows and greys on every component.
**Why it hurts:** Inconsistency reads as unfinished even when users can't say why.
**Do instead:** Define tokens (spacing scale 4/8/12/16/24/32/48, two or three radii, one shadow scale, a neutral colour ramp, one accent) and use them everywhere. Reuse components instead of restyling them per page.

## Show the actual product

**Tell:** Abstract blobs, 3D shapes, stock illustrations or empty device mockups where the product should be.
**Why it hurts:** Visitors want to see what they get. Vague visuals feel evasive.
**Do instead:** Real screenshots with realistic data, short screen recordings, the actual UI cropped to the relevant part.

## Enlarge the main feature

**Tell:** A grid of six equal feature cards.
**Why it hurts:** Equal weight means no hierarchy; nothing is memorable.
**Do instead:** Make the one feature that sells the product large (a big visual, its own section), and group the rest smaller.

## Make headlines specific

**Tell:** "Unlock your potential", "The future of work", "Supercharge your workflow".
**Why it hurts:** They could describe any product, so they describe none.
**Do instead:** Say what the product does and for whom, with concrete nouns and numbers ("Send invoices in 30 seconds and get paid twice as fast").

## Emphasise the primary call to action

**Tell:** Three equally styled buttons in the hero; "Learn more" next to "Get started" with the same weight.
**Why it hurts:** Users hesitate when they can't tell which action matters (Hick's law, Von Restorff effect).
**Do instead:** One filled primary button per view; secondary actions as outlined or text buttons.

## Add one accent colour (and lose the purple gradient)

**Tell:** Violet-to-blue gradients, gradient text, gradient borders.
**Why it hurts:** It is the default output of most generators, so it signals "generated" instantly.
**Do instead:** A neutral interface (black, white, greys) with one accent colour used sparingly for the primary action and key highlights. Use semantic red and green only for errors and success.

## Keep icons consistent

**Tell:** Icons from three different sets with different stroke widths, sizes and corner styles; emoji mixed with line icons.
**Why it hurts:** It looks patched together.
**Do instead:** One icon set (Lucide, Phosphor, SF Symbols, Material Symbols), one stroke width, one size per context, aligned to the text's cap height.

## Remove unnecessary embellishments

**Tell:** Glows, glassmorphism, noise textures, gradient borders, floating orbs and drop shadows on everything.
**Why it hurts:** Decoration competes with content and dates quickly.
**Do instead:** Flat surfaces separated by spacing and hairline borders. Add depth only where it explains hierarchy (a modal above a page).

## Inner radius = outer radius minus padding

**Tell:** A rounded button inside a rounded card with the same radius, so the corners don't nest.
**Why it hurts:** The mismatch is subtle but makes components feel off.
**Do instead:** `inner = outer - padding` (see ux-laws.md, Concentric radii).

## Improve text contrast

**Tell:** Light grey body text on white or dark grey on black.
**Why it hurts:** Hard to read, fails accessibility, looks washed out.
**Do instead:** Body text at 4.5:1 or better; reserve muted colour for genuinely secondary text (see typography.md).

## Wrap headlines properly

**Tell:** A headline with one word alone on the last line, or awkward breaks that split phrases.
**Do instead:** `text-wrap: balance` on headings; rewrite to fit if needed.

## Align by eye, not just by pixels

**Tell:** A play icon that looks off-centre in its circle, text that sits low in its button.
**Do instead:** Optical alignment and text-box trim (see ux-laws.md and typography.md).

## Use tabular numbers

**Tell:** Prices and stats that wobble as they update; misaligned numeric columns.
**Do instead:** `font-variant-numeric: tabular-nums` on numbers that change or line up.

## Add loading, empty and error states

**Tell:** Only the happy path exists: blank screens while loading, nothing when a list is empty, raw error text.
**Why it hurts:** Real users hit these states constantly.
**Do instead:** Skeletons shaped like the content; empty states that explain what goes here and offer the first action; errors in plain language with a way to recover.

## Animate useful feedback only

**Tell:** Everything fades and slides in on scroll; hover effects on non-interactive cards.
**Do instead:** Animate the things that confirm actions and explain changes (added to cart, saved, moved), and keep the rest still (see motion.md).

## Typography defaults

**Tell:** Inter or another generator-default font everywhere, centred everything, huge hero text with tiny body text.
**Do instead:** Choose a font for the product's feeling (see typography.md, Fonts), left-align body text, use a modest type scale.
