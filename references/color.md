# Colour: full reference

Colour terms every interface builder should know, what each means in practice, and how to use it in code.

## Working colour system (start here)

- Define colours in `oklch()` (perceptually uniform) as CSS custom properties, then name them by role: `--bg`, `--fg`, `--muted`, `--border`, `--accent`, `--danger`, `--success`.
- Use a neutral scale (about 10 steps from near-white to near-black) for most of the interface and **one accent colour** for the primary action and key highlights. Red and green are for errors and success only.
- Generate tints and shades by changing OKLCH lightness while keeping chroma and hue steady.
- Check every text/background pair against WCAG contrast (see Relative luminance).

## Hue

**What:** The colour family itself: red, orange, blue. In OKLCH it is the `h` angle (0 to 360).

**Use:** Pick one accent hue for the brand. Keep semantic hues conventional (red = error, amber = warning, green = success, blue = info) so meaning is instant.

**Avoid:** Using many unrelated hues for decoration; giving the accent the same hue as the error colour.

## Chroma (saturation)

**What:** How intense or vivid a colour is, from grey (0) to fully vivid. In OKLCH it is the `c` value.

**Use:** High chroma for small accents (buttons, badges, focus rings); low chroma for large areas (backgrounds, cards) so they don't tire the eyes. Neutral greys can carry a hint of the brand hue (chroma about 0.005 to 0.02) to feel cohesive.

**Avoid:** Large saturated backgrounds behind text; vivid colours at very light or very dark lightness (they fall out of gamut).

## Tint, shade and tone

**What:** A tint is a colour mixed with white (lighter), a shade is mixed with black (darker), a tone is mixed with grey (muted).

**Use:** Build hover, pressed and subtle background variants from one base colour: tints for subtle backgrounds (selected rows, info banners), shades for pressed states and text on light backgrounds, tones for disabled or secondary states. In OKLCH, change `l` for tints and shades and lower `c` for tones; `color-mix(in oklch, var(--accent), white 85%)` also works.

**Avoid:** Mixing with white in sRGB for blues and purples (see Abney effect); hand-picking unrelated hex codes for each state.

## Analogous colours

**What:** Colours next to each other on the colour wheel (orange, amber, yellow-green).

**Use:** Harmonious, low-tension palettes for illustrations, charts with related categories, and gradients that don't look muddy. Pair an analogous set with one contrasting accent for emphasis.

**Avoid:** Analogous colours for states that must be told apart quickly (warning vs error).

## Simultaneous contrast

**What:** The same colour looks different depending on what surrounds it: grey looks darker on white and lighter on black, and takes on the opposite hue of its background.

**Use:** Test colours in context, never as isolated swatches. A border or muted text that works on white may disappear on a grey card. Re-check tokens in dark mode rather than inverting them.

**Avoid:** Judging a palette from a swatch sheet.

## Chromostereopsis

**What:** Saturated red and blue placed side by side appear to sit at different depths and seem to vibrate.

**Use:** Avoid pure saturated red text on blue backgrounds (and vice versa) in UI. If both colours must appear together, separate them with neutral space or reduce chroma.

**Avoid:** Red error text on a blue banner; blue links on a red button.

## Increased contrast mode

**What:** An operating-system accessibility setting (iOS "Increase Contrast", macOS "Increase contrast", Windows contrast themes) that asks apps for stronger contrast.

**Use:** Respond to `@media (prefers-contrast: more)` with darker text, stronger borders and fewer translucent surfaces; respect `@media (forced-colors: active)` by using system colours (`CanvasText`, `ButtonText`) and avoiding information carried only by background colour. On iOS check `accessibilityContrast == .high` / `UIAccessibility.isDarkerSystemColorsEnabled`.

**Avoid:** Translucent glass panels and light-grey text that ignore the setting.

## Gamut

**What:** The range of colours a colour space or screen can show. sRGB is the classic web gamut; Display P3 (most modern phones and Macs) shows more vivid reds and greens.

**Use:** You can use P3 colours with `color(display-p3 …)` or high-chroma `oklch()` values and provide fallbacks: `@media (color-gamut: p3) { … }`. Browsers clamp out-of-gamut OKLCH values, so test on both kinds of display.

**Avoid:** Brand colours that only look right on P3 screens; exporting assets without colour profiles.

## Abney effect

**What:** Adding white to a colour (or desaturating it) shifts its perceived hue. Blue mixed with white in sRGB drifts towards purple.

**Use:** Generate tints in OKLCH (or OKLab with `color-mix(in oklch, …)`), which keeps the hue stable, instead of mixing in sRGB or HSL.

**Avoid:** HSL-generated tint scales for blues (they turn lavender).

## Irradiation illusion

**What:** Light shapes on a dark background look larger and bolder than identical dark shapes on a light background.

**Use:** In dark mode, reduce font weight slightly (for example 400 → 350 with a variable font) or use a slightly lighter weight for white text, and reduce icon stroke weight, so text doesn't look bloated. Thin light text on dark can also bleed, so don't go too light.

**Avoid:** Using identical type settings for light and dark themes without checking.

## Stevens' power law

**What:** Perceived intensity is not linear in physical intensity. Doubling the amount of light does not look twice as bright.

**Use:** Build greyscale and colour ramps with perceptually even lightness steps (OKLCH `l` in equal increments), not equal steps in RGB or hex values. Charts that encode numbers as colour intensity should use perceptual scales.

**Avoid:** Neutral ramps made by stepping hex values evenly (the light end bunches up and the dark end jumps).

## Hunt effect

**What:** Colours look more saturated as they get brighter, and duller in dim conditions.

**Use:** Colours that look right in a bright light theme can look washed out in dark mode, and very bright colours on dark backgrounds can look neon. Tune accent chroma separately for light and dark themes.

**Avoid:** Reusing the exact light-theme accent in dark mode without adjustment.

## Helmholtz–Kohlrausch effect

**What:** Saturated colours look brighter than a grey of the same measured luminance. A vivid blue and a vivid yellow can have the same lightness value but look very different in brightness.

**Use:** Don't rely only on a luminance number to judge visual weight. Check saturated accents by eye, and balance a vivid accent with surrounding neutrals. When vivid colours carry text, verify contrast with both a calculator and your eyes.

**Avoid:** Assuming two colours with the same OKLCH `l` will look equally heavy in a chart.

## Additive colour

**What:** Screens mix light (red, green, blue) rather than pigment. Adding all three gives white; this is why RGB is the native model for screens.

**Use:** Expect blends and overlays to behave like light: `mix-blend-mode: screen` lightens, `multiply` darkens. Print (subtractive CMYK) colours will not match screen colours exactly.

**Avoid:** Expecting a brand colour picked on screen to print identically.

## Opacity

**What:** How transparent a layer is. A colour at 40% opacity is blended with whatever is behind it.

**Use:** Use opacity for overlays, scrims behind modals (black at 30 to 50%), and disabled states. For text and borders, prefer solid colours from the neutral scale: semi-transparent text changes colour on every background and can fail contrast.

**Avoid:** Translucent text over images; stacking several translucent layers (unpredictable colours).

## Sequential scale

**What:** A colour scale from light to dark (or low to high chroma) in one hue, used for ordered data with one direction (low → high), like GitHub's contribution graph.

**Use:** Heatmaps, density maps, intensity. Use 5 to 9 perceptually even steps generated in OKLCH. The lightest step should still be distinguishable from the background.

**Avoid:** Rainbow scales for ordered data (they imply false boundaries).

## Diverging scale

**What:** Two sequential scales meeting at a neutral midpoint, for data with a meaningful centre (profit vs loss, above vs below average, temperature anomalies).

**Use:** Two contrasting hues (for example blue and orange, which is colour-blind safe) with a light neutral midpoint at the meaningful value (zero, average, target).

**Avoid:** Red–green diverging scales (hard for common colour blindness); a diverging scale for data with no natural midpoint.

## Relative luminance

**What:** The perceived brightness of a colour on a scale from 0 (black) to 1 (white), computed from linearised RGB. WCAG contrast ratios are built from it: `(L1 + 0.05) / (L2 + 0.05)`.

**Use:** Body text needs at least 4.5:1 against its background, large text and UI components 3:1. Compute it with a tool or a library (`culori`, `colorjs.io`); the newer APCA model is a useful second opinion for dark mode. Choose white or black text on a coloured button by comparing luminance, not by eye.

**Avoid:** Assuming a colour is accessible because it "looks dark enough".
