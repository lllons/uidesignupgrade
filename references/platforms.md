# Platform equivalents

The other references show CSS first. This file maps the most-used fixes to each stack so you can apply them without a new library. Use the project's existing animation library if it has one (Framer Motion, Reanimated, Motion One); otherwise use the platform built-ins below. Token values come from motion.md "Shared tokens".

## Easing (ease-out for entering)

| Stack | Code |
|-------|------|
| CSS | `transition: transform 200ms cubic-bezier(0.23, 1, 0.32, 1);` |
| Tailwind v4 | `@theme { --ease-out-ui: cubic-bezier(0.23, 1, 0.32, 1); }` then `ease-out-ui` |
| Tailwind v3 | `theme.extend.transitionTimingFunction: { 'out-ui': 'cubic-bezier(0.23, 1, 0.32, 1)' }` then `ease-out-ui` |
| Framer Motion | `transition={{ duration: 0.2, ease: [0.23, 1, 0.32, 1] }}` |
| SwiftUI | `.animation(.timingCurve(0.23, 1, 0.32, 1, duration: 0.2), value: state)` |
| Compose | `tween(durationMillis = 200, easing = CubicBezierEasing(0.23f, 1f, 0.32f, 1f))` |
| Flutter | `curve: const Cubic(0.23, 1, 0.32, 1), duration: const Duration(milliseconds: 200)` |
| React Native (Reanimated) | `withTiming(v, { duration: 200, easing: Easing.bezier(0.23, 1, 0.32, 1) })` |

## Reduced motion

| Stack | Code |
|-------|------|
| CSS | `@media (prefers-reduced-motion: reduce) { ... }` |
| Tailwind | `motion-safe:animate-...`, `motion-reduce:transition-none` |
| Framer Motion | wrap the app in `<MotionConfig reducedMotion="user">`, or `useReducedMotion()` |
| SwiftUI | `@Environment(\.accessibilityReduceMotion) var reduceMotion` |
| Compose | `Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f` |
| Flutter | `MediaQuery.disableAnimationsOf(context)` |
| React Native | Reanimated `useReducedMotion()`, or `AccessibilityInfo.isReduceMotionEnabled()` |

When reduced motion is on, replace movement and scale with a short opacity fade; keep the feedback.

## Press feedback (scale to 0.97)

| Stack | Code |
|-------|------|
| CSS | `button:active { transform: scale(0.97); }` with a 120 ms transition |
| Tailwind | `active:scale-[0.97] transition-transform duration-100` |
| Framer Motion | `whileTap={{ scale: 0.97 }}` |
| SwiftUI | `ButtonStyle` with `.scaleEffect(configuration.isPressed ? 0.97 : 1)` and `.animation(.easeOut(duration: 0.12), value: configuration.isPressed)` |
| Compose | `val pressed by interactionSource.collectIsPressedAsState()` then `Modifier.graphicsLayer { scaleX = if (pressed) 0.97f else 1f; scaleY = scaleX }` (animate with `animateFloatAsState`) |
| Flutter | `AnimatedScale(scale: pressed ? 0.97 : 1, duration: 120ms)` driven by `onTapDown` / `onTapUp` / `onTapCancel` |
| React Native | `<Pressable style={({ pressed }) => ({ transform: [{ scale: pressed ? 0.97 : 1 }] })}>` |

## Enter from 0.97 with a fade

| Stack | Code |
|-------|------|
| CSS | `@starting-style { .menu.open { opacity: 0; transform: scale(0.97); } }` on an element with an opacity/transform transition. If it toggles `display: none`, also transition `display ... allow-discrete` (full snippet: motion.md, Scale from 0.97) |
| Framer Motion | `initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.97 }}` |
| SwiftUI | `.transition(.scale(scale: 0.97).combined(with: .opacity))` |
| Compose | `AnimatedVisibility(enter = fadeIn() + scaleIn(initialScale = 0.97f), exit = fadeOut() + scaleOut(targetScale = 0.97f))` |
| Flutter | `FadeTransition` + `ScaleTransition` with a `Tween(begin: 0.97, end: 1.0)` |

## Origin awareness (grow from the trigger)

| Stack | Code |
|-------|------|
| CSS | `transform-origin: top left;` (Radix: `transform-origin: var(--radix-popover-content-transform-origin)`) |
| Framer Motion | `style={{ transformOrigin: "top left" }}` |
| SwiftUI | `.scaleEffect(scale, anchor: .topLeading)` or `.transition(.scale(scale: 0.97, anchor: .topLeading))` |
| Compose | `scaleIn(initialScale = 0.97f, transformOrigin = TransformOrigin(0f, 0f))` |
| Flutter | `ScaleTransition(alignment: Alignment.topLeft, ...)` |

## Shared element transitions

| Stack | Code |
|-------|------|
| CSS | View Transitions: `view-transition-name: card-42;` and `document.startViewTransition(update)` |
| Framer Motion | same `layoutId` on both elements |
| SwiftUI | `.matchedGeometryEffect(id: item.id, in: namespace)` |
| Compose | `SharedTransitionLayout` with `Modifier.sharedElement(rememberSharedContentState(key), animatedVisibilityScope)` |
| Flutter | `Hero(tag: item.id, child: ...)` |

## Tabular numbers

| Stack | Code |
|-------|------|
| CSS / Tailwind | `font-variant-numeric: tabular-nums;` / `tabular-nums` |
| SwiftUI | `.monospacedDigit()` |
| Compose | `TextStyle(fontFeatureSettings = "tnum")` |
| Flutter | `TextStyle(fontFeatures: [FontFeature.tabularFigures()])` |
| React Native | `fontVariant: ['tabular-nums']` |

## Hit targets

| Stack | Minimum and how |
|-------|-----------------|
| Web | 24×24 CSS px required (WCAG 2.2), 44×44 preferred; enlarge with a `::before` inset of negative values instead of growing the visual |
| SwiftUI | 44×44 pt: `.frame(minWidth: 44, minHeight: 44).contentShape(Rectangle())` |
| Compose | 48×48 dp: `Modifier.minimumInteractiveComponentSize()` (Material components do this already) |
| Flutter | 48×48: keep `materialTapTargetSize: MaterialTapTargetSize.padded`; wrap small icons in `IconButton` |
| React Native | 44×44: `hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}` on small `Pressable`s |

## Text that scales

| Stack | How |
|-------|-----|
| Web | `rem` for font sizes, `clamp()` for fluid headings; never disable zoom |
| SwiftUI | text styles (`.font(.body)`, `.font(.title2)`) so Dynamic Type works; `@ScaledMetric` for custom sizes |
| Compose | `MaterialTheme.typography.*` in `sp`; test at 200 % font scale |
| Flutter | `Theme.of(context).textTheme.*`; don't clamp `MediaQuery.textScalerOf` to 1 |
| React Native | leave `allowFontScaling` on; set `maxFontSizeMultiplier` only where layout truly breaks |

## Safe areas

| Stack | How |
|-------|-----|
| Web | `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` then `padding-bottom: env(safe-area-inset-bottom)` |
| SwiftUI | respected by default; use `.safeAreaInset(edge:)` for bars, `.ignoresSafeArea()` only for backgrounds |
| Compose | `Modifier.safeDrawingPadding()` or `WindowInsets.safeDrawing` (with edge-to-edge enabled) |
| Flutter | `SafeArea(child: ...)` |
| React Native | `react-native-safe-area-context` (`SafeAreaView`, `useSafeAreaInsets()`) if already installed |

## Colour in OKLCH

| Stack | How |
|-------|-----|
| Web | `oklch(L C H)` in CSS custom properties; Tailwind v4 uses OKLCH natively |
| Native | design the ramp in OKLCH (oklch.com or the project's tokens), then export to the platform format: asset catalog colour sets (iOS), `Color(0xFF...)` in `Color.kt` (Android), `Color(0xFF...)` in the theme (Flutter). Keep light and dark values together |
