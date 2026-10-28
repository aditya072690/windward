# DESIGN — Windward

> **Design brief:** make a wind-forecast tool feel like something Apple would ship — calm, spacious, obvious. A trader should understand the answer in five seconds; a reviewer should feel craft in every pixel.
> Tokens and component specs live in `docs/DESIGN_SYSTEM.md`. This file defines the **experience**: story, layout, interactions, copy and the extra features that lift the product beyond the brief.

---

## 1. Design thesis

1. **One question per screen-height.** Each section answers a single question with one hero visual.
2. **Answer first, evidence second.** A plain-English headline sits above every chart.
3. **The decision moment is a first-class idea.** The cutoff isn't a filter; it is the main character — you "scrub through time" and watch the forecast vintage change.
4. **Honest uncertainty.** Error and risk are shown prominently and in the buyer's language (MW, cost direction), not statistician's.
5. **Delight without noise.** Springy controls, rolling numbers, a gentle wind-line hero — all disabled under reduced motion.

## 2. Page narrative (single scrolling page, sticky glass nav)

```
NavBar        Windward · Forecast · Accuracy · Horizon · Method        [☾] [Methodology]
────────────────────────────────────────────────────────────────────────────────────────
1. HERO       "Know the wind before you buy."
              Sub: Day-ahead wind forecasts, exactly as they stood when you had to decide.
              [Open the pilot ↓]   Watch how it works (▶ presentation mode)
              → live mini-brief card peeks from below (proof, not stock imagery)

2. BRIEF + STUDIO   "What did the forecast say at 09:00?"
   ┌ DateRail (31 days, sparkbars) ──────────────────────────────────────────┐
   ├ Decision Brief card ─────────────────┬ Controls ────────────────────────┤
   │ Delivery: Fri 16 Jan                 │ Cutoff  ●────────  09:00         │
   │ 6.0 GW avg · 7.4 GW peak · 144 GWh   │ [Hindsight ○]  [Conservative ○]  │
   │ "Using forecasts published 05:30–    │ Vintage chip: 08:30 (15.5 h out) │
   │  08:30. Typically over-forecasts by  │                                  │
   │  up to 0.9 GW."                      │                                  │
   ├──────────────────────────────────────┴──────────────────────────────────┤
   │ ForecastChart (48 half-hours)            [Chart | Table]  [Export CSV]  │
   └─────────────────────────────────────────────────────────────────────────┘

3. ACCURACY   "How wrong is it, really?"
   KPI row: MAE · Bias · P90 over-forecast · nMAE · Coverage   (rolling numbers)
   [Error by hour of day]  [Daily trend — click a day to jump]  [Distribution]
   [Day × hour error heatmap]

4. HORIZON    "Does waiting help?"
   Hero chart: error vs. forecast age (3-hour buckets) with the user's cutoff marked
   Insight line: "Forecasts published < 12 h ahead are X % more accurate than 36 h ahead."
   Forecast Evolution: pick a half-hour → watch every vintage converge on the actual.

5. METHOD     Short, elegant explainer + assumptions A1–A8, formulas, data lineage, attribution
6. FOOTER     Data: Elexon BMRS · Built for a pilot · version/commit · Theme toggle
```

## 3. Signature interactions

| Interaction | Behaviour | Why it impresses |
|---|---|---|
| **Cutoff scrub** | Drag the slider; the chart morphs as the chosen vintage changes; vintage chip animates ("08:30 → 05:30"); brief numbers roll | Makes the core concept tangible in one gesture |
| **Hindsight reveal** | Toggle draws the actual line left→right and fades in red/green error shading | The "aha" moment for accuracy |
| **DateRail** | Sparkbars show each day's MAE; hover previews; click or ←/→ changes day | Navigation doubles as data |
| **Brief sentence** | Generated copy updates live and is announced to screen readers | Clarity for non-technical users |
| **Evolution replay** | ▶ button animates forecasts arriving over time toward the actual | Storytelling for the video |
| **Presentation mode** | Full-screen, 6 steps, ←/→ to advance, Esc to exit (see §6) | Perfect for the 5-minute client pitch |
| **⌘K palette** | "Jump to 20 Jan", "Toggle hindsight", "Open methodology" | Power-user delight |

## 4. Features added beyond the brief (and why)

| # | Feature | Pri | Reasoning for the client |
|---|---|---|---|
| 1 | **Decision Brief** plain-English summary | P0 | Executives read sentences, not charts |
| 2 | **Hindsight toggle (off by default)** | P0 | Preserves the information set at decision time; avoids hindsight bias |
| 3 | **Forecast by horizon** | P0 | Directly informs *when* to trade |
| 4 | **Conservative (P90) line**, walk-forward | P1 | Converts error stats into an actionable buffer; no look-ahead |
| 5 | **Forecast evolution + replay** | P1 | Shows forecast revisions — very rarely visualised |
| 6 | **Error heatmap** | P2 | Reveals structural patterns (e.g. evening ramps) at a glance |
| 7 | **Persistence-baseline skill score** | P2 | Proves the forecast beats "yesterday's actual"; quant credibility |
| 8 | **CSV export & shareable URLs** | P1 | Fits real trading workflows |
| 9 | **Presentation mode** | P2 | Makes the demo video effortless |
| 10 | **Methodology drawer with lineage** | P0 | Trust and auditability |
| 11 | **Light/Dark, reduced-motion, keyboard-first** | P1 | Polish + accessibility signal engineering maturity |

## 5. Copy and tone

- Sentence case, short, confident, no jargon without a one-line explanation.
- Numbers always with units (`6.0 GW`, `913 MW`, `144 GWh`).
- Direction of risk is explicit: **"Over-forecast = wind came in lower than predicted"**.

| Place | Copy |
|---|---|
| Hero H1 | Know the wind before you buy. |
| Hero sub | Day-ahead wind forecasts — exactly as they stood when you had to decide. |
| Cutoff label | Decision cutoff |
| Hindsight toggle | Show what actually happened |
| Conservative toggle | Show risk-adjusted view |
| MAE hint | The typical miss, in megawatts. |
| Bias hint | Positive means forecasts ran high. |
| P90 over-forecast hint | On 9 in 10 half-hours, forecasts weren't too high by more than this. |
| Horizon insight | Newer forecasts are meaningfully sharper. |
| Empty | No forecast had been published by this cutoff. Try a later time. |
| Error | We couldn't load this view. Try again. |

## 6. Presentation mode (storyboard for the demo video)

1. **The problem** — big type: "Wind decides tomorrow's price." Brief card fades in.
2. **The decision moment** — chart for a chosen date; cutoff scrubs from 12:00 → 06:00.
3. **Hindsight** — actuals draw in; error shading appears.
4. **The number** — KPIs roll up; callout: "Typical miss: X MW. 9 in 10 over-forecasts below Y MW."
5. **Does waiting help?** — horizon curve with cutoff marker.
6. **Recommendation** — "Plan a buffer of ~Y MW at a 09:00 cutoff; revisit after the 06:00 vintage."

(Copy numbers are bound to live data, never hard-coded.)

## 7. Responsive behaviour

| Breakpoint | Behaviour |
|---|---|
| ≥ 1024 | Two-column Brief/Controls; 3-up chart grid |
| 768–1023 | Single column; controls above chart |
| < 768 | Sticky bottom control bar (date + cutoff) opens a sheet; charts full-bleed, 320 px tall; KPI cards in horizontally snapping carousel; Methodology as bottom sheet |

## 8. States

- **Loading:** skeletons with final dimensions (zero layout shift).
- **Empty:** illustration-free, calm message with a suggested action.
- **Error:** inline, section-scoped, retry button; page never white-screens.
- **Offline/slow:** stale data stays visible with subtle "Updating…" chip.

## 9. Accessibility commitments

WCAG 2.2 AA, full keyboard path (documented shortcuts below), `prefers-reduced-motion` and `prefers-color-scheme`, chart table alternatives, live-region announcements, 44 px targets, skip link.

| Shortcut | Action |
|---|---|
| `←` / `→` | Previous / next decision date |
| `[` / `]` | Cutoff −30 min / +30 min |
| `H` | Toggle hindsight |
| `C` | Toggle conservative view |
| `T` | Chart ↔ table |
| `?` | Open methodology |
| `⌘K` / `Ctrl K` | Command palette |
| `P` | Presentation mode |
| `Esc` | Close overlays |

## 10. Quality bar ("flawless" checklist)

- [ ] 8-pt rhythm everywhere; no orphan spacing values
- [ ] Every chart has title, units, plain-English takeaway and table alternative
- [ ] No layout shift (CLS < 0.02)
- [ ] 60 fps interactions on a mid-range laptop and iPhone
- [ ] Light and dark pass visual review at 360, 768, 1280, 1920 px
- [ ] All microcopy reviewed against §5
- [ ] First paint under 1.5 s on a throttled connection
- [ ] No placeholder, lorem ipsum, or stock imagery
