# DESIGN_SYSTEM — Windward

The tokens and components that make the UI feel like it was designed by one hand. **All visual values below are implemented once as CSS variables (`src/styles/tokens.css`) and surfaced through Tailwind config. Components never contain raw colours, radii or shadows.** For product-level UX, layouts and feature design, see `DESIGN.md`.

Inspired by Apple's Human Interface Guidelines: clarity, deference (content first), depth. Implemented with original code and system fonts — no Apple assets are bundled.

---

## 1. Principles

1. **Content is the interface.** Charts and numbers are heroes; chrome recedes.
2. **Quiet confidence.** Generous whitespace, restrained colour, one accent.
3. **Depth through light, not borders.** Soft shadows, translucency, hairlines.
4. **Motion with purpose.** Springs that feel physical; nothing decorative.
5. **Everyone can use it.** AA contrast, keyboard, reduced motion, large hit targets.

## 2. Colour tokens

### Light
| Token | Value | Use |
|---|---|---|
| `--bg` | `#FBFBFD` | page background |
| `--bg-grouped` | `#F5F5F7` | section bands, inset areas |
| `--surface` | `#FFFFFF` | cards |
| `--surface-glass` | `rgba(255,255,255,0.72)` | nav, popovers (with blur) |
| `--text` | `#1D1D1F` | primary text |
| `--text-2` | `#6E6E73` | secondary text (AA on bg) |
| `--text-3` | `#86868B` | tertiary / captions (large text only) |
| `--hairline` | `rgba(0,0,0,0.08)` | borders, dividers |
| `--accent` | `#0071E3` | primary action, forecast line |
| `--accent-hover` | `#0077ED` | |
| `--focus` | `#0071E3` @ 40 % ring | focus ring |

### Dark
| Token | Value |
|---|---|
| `--bg` | `#000000` |
| `--bg-grouped` | `#0B0B0D` |
| `--surface` | `#1C1C1E` |
| `--surface-glass` | `rgba(28,28,30,0.72)` |
| `--text` | `#F5F5F7` |
| `--text-2` | `#A1A1A6` |
| `--text-3` | `#86868B` |
| `--hairline` | `rgba(255,255,255,0.12)` |
| `--accent` | `#2997FF` |

### Data-visualisation palette (semantic, same meaning in both themes)
| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--viz-forecast` | `#0071E3` | `#2997FF` | decision-time forecast |
| `--viz-actual` | `#1D1D1F` | `#F5F5F7` | actual generation |
| `--viz-conservative` | `#FF9500` | `#FF9F0A` | risk-adjusted line/band |
| `--viz-over` | `#FF3B30` | `#FF453A` | over-forecast (costly) |
| `--viz-under` | `#34C759` | `#30D158` | under-forecast |
| `--viz-vintage` | `#AEAEB2` | `#636366` | older vintages |
| `--viz-purple` | `#AF52DE` | `#BF5AF2` | extra series (e.g. P90 line) |
| `--viz-teal` | `#30B0C7` | `#40C8E0` | extra series (e.g. P50 line, horizon buckets) |
| `--viz-pink` | `#FF2D55` | `#FF375F` | extra series (e.g. P95 line) |
| `--viz-indigo` | `#5856D6` | `#5E5CE6` | extra series |
| Heatmap | diverging green ← neutral → red, centred on 0 | | |

**Rules:** colour is never the only carrier of meaning (pair with labels, patterns or shape); chart colours meet 3:1 against their background; charts may use the full viz palette (multi-colour is fine); the rest of the UI keeps its existing colours.

## 3. Typography

- **Stack:** `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter Variable", system-ui, sans-serif`. Inter Variable self-hosted (via `@fontsource-variable/inter`) as the cross-platform fallback.
- **Numerals:** `font-variant-numeric: tabular-nums` for all metrics, axes and tables.
- **Mono:** `ui-monospace, "SF Mono", Menlo` for timestamps in tooltips/code.

| Style | Size / line | Weight | Tracking | Use |
|---|---|---|---|---|
| `display` | 64/68 (mobile 40/44) | 700 | −0.035em | hero headline |
| `title-1` | 40/44 | 700 | −0.03em | section titles |
| `title-2` | 28/34 | 600 | −0.02em | card titles |
| `headline` | 21/28 | 600 | −0.01em | sub-heads |
| `body-lg` | 19/28 | 400 | −0.005em | lead paragraphs |
| `body` | 17/26 | 400 | 0 | default text |
| `callout` | 15/22 | 400 | 0 | helper text |
| `caption` | 12/16 | 500 | 0.01em | labels, axis |
| `metric` | 48/52 | 600 | −0.03em | KPI numbers |

## 4. Spacing, layout, shape

- **4-pt grid.** Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128.
- **Container:** max 1120 px, side padding 24 (mobile 20). Section vertical padding 96 (mobile 56).
- **Breakpoints:** `sm 640`, `md 768`, `lg 1024`, `xl 1280`.
- **Radius:** `--r-card 24px`, `--r-control 12px`, `--r-pill 980px`, `--r-chip 8px`. Use continuous-corner feel via generous values.
- **Elevation:**
  - `--shadow-1`: `0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.04)`
  - `--shadow-2`: `0 2px 4px rgba(0,0,0,.04), 0 12px 32px rgba(0,0,0,.08)`
  - `--shadow-glass`: `0 8px 40px rgba(0,0,0,.12)`
  - Dark theme: replace shadows with `inset 0 0 0 1px var(--hairline)`.
- **Glass:** `background: var(--surface-glass); backdrop-filter: saturate(180%) blur(20px);` with solid fallback when `backdrop-filter` unsupported.

## 5. Motion

| Token | Value |
|---|---|
| `--ease-standard` | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| `--dur-fast / base / slow` | 150 / 250 / 450 ms |
| Spring (Framer) | `{ type: "spring", stiffness: 320, damping: 32, mass: 0.9 }` |

- Numbers **count up/roll** to new values (≤ 600 ms); chart lines **draw in** (path-length, 700 ms) on first view only.
- Hover: 1.00 → 1.01 scale on cards, never layout-shifting.
- Sheet/drawer: spring in from edge; scrim fades.
- `@media (prefers-reduced-motion: reduce)`: disable springs, draw-in and count-up; use opacity fades ≤ 150 ms.

## 6. Components (spec)

Every component: keyboard operable, visible focus (2 px ring `--focus`, 2 px offset), disabled/loading/error states, dark-mode parity, documented props.

## 7. Iconography

SF Symbols-like stroke style: `lucide-react`, 1.75 px stroke, 20/24 px sizes, `currentColor`. Icons never stand alone without a label or `aria-label`.

## 8. Accessibility specifics

- Text contrast ≥ 4.5:1 (≥ 3:1 for large/graphics); verified in both themes (include an automated contrast test over token pairs).
- Focus order follows visual order; skip-link "Skip to content".
- Landmarks: `header`, `main`, `section[aria-labelledby]`, `footer`.
- Dynamic updates in the Brief use `aria-live="polite"`.
- Touch targets ≥ 44×44 px; no hover-only interactions.

## 9. Tailwind mapping

```ts
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      bg: "var(--bg)", 'bg-grouped': "var(--bg-grouped)", surface: "var(--surface)", 
      'surface-glass': "var(--surface-glass)", text: "var(--text)",
      "text-2": "var(--text-2)", "text-3": "var(--text-3)", accent: "var(--accent)", 
      'accent-hover': "var(--accent-hover)", hairline: "var(--hairline)",
      'viz-forecast': "var(--viz-forecast)", 'viz-actual': "var(--viz-actual)",
      'viz-conservative': "var(--viz-conservative)", 'viz-over': "var(--viz-over)",
      'viz-under': "var(--viz-under)", 'viz-vintage': "var(--viz-vintage)",
      'viz-purple': "var(--viz-purple)", 'viz-teal': "var(--viz-teal)",
      'viz-pink': "var(--viz-pink)", 'viz-indigo': "var(--viz-indigo)",
    },
    borderRadius: { card: "var(--r-card)", control: "var(--r-control)", pill: "var(--r-pill)", chip: "var(--r-chip)" },
    boxShadow: { 1: "var(--shadow-1)", 2: "var(--shadow-2)", glass: "var(--shadow-glass)" },
    fontFamily: { sans: ["-apple-system","BlinkMacSystemFont","SF Pro Display","SF Pro Text","Inter Variable","system-ui","sans-serif"] },
  },
}
```
