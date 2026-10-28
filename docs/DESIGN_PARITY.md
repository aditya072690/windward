# Design Parity Contract

This document is the contract we test against. Extracted from `design-reference/index.html` (source of truth for visuals/behaviour).

## 1. Tokens (from export :root / [data-theme="dark"])

See `frontend/src/styles/tokens.css` for verbatim values. Key notes:
- `--accent-solid` / `--accent-solid-hover` used for primary buttons and selected day (ensures white text AA)
- Dark uses `--accent-hover: #4AA8FF`
- `--display: clamp(40px, 6vw, 64px)`
- Fonts include `Inter Variable`/`Inter` in stack
- Theme persisted to `localStorage` key `ww-theme`, default system, no flash (via `public/theme-init.js`)

## 2. Component map (export → implementation)
| Export block | Component(s) | Notes |
|---|---|---|
| skip link + live region | `SkipLink`, `LiveRegion` | aria-live="polite" |
| header.nav | `NavBar`, `ThemeToggle` | sticky glass nav; Overview/Charts/Vintages; theme button; "Methodology" secondary |
| section.hero#top | `Hero`, `WindLines` | 6-path wind SVG, eyebrow, h1, lead, "Open the pilot" → #charts, "Read the methodology", meta |
| section.band#overview | `SectionHead`, `Note`, `KpiGrid`, `MetricCard` | 4 cards with delta/hint |
| section#charts | `ControlsCard`, `ViewSegmented`, `DateRail`, `DayButton`, `CutoffSlider`, `ChartCard`, `ChartLegend`, `ChartTooltip`, `DataTableRegion`, `ForecastChart`, `HorizonChart`, `HourBarsChart` | main chart + `.grid-2` of horizon/hour; each has "View as table" toggle |
| section.band#vintages | `VintageLedger` | 8-row table in `.vintage-card` |
| footer.footer | `Footer` | |
| dialog.sheet#methodology | `MethodologySheet` | native `<dialog>`, right on ≥768px, bottom on ≤767px, backdrop click + Esc |

## 3. Selectors compared in parity tests
Key selectors for computed-style/geometry parity:
- `.nav`, `.nav-inner`, `.brand`, `.nav-links a`, `.nav-actions`
- `.hero`, `.wind svg path`, `.eyebrow`, `.hero h1`, `.lead`, `.hero-actions .btn`, `.hero-meta li`
- `.section.band#overview`, `.section-head`, `.note`, `.metric-grid`, `.metric`, `.metric-label`, `.metric-value`, `.metric-unit`, `.metric-delta`, `.metric-hint`
- `.card.controls`, `.controls-row`, `.control-block`, `.control-label`, `.segmented`, `.seg-thumb`, `.segmented button`, `.rail`, `.day` (58×78+), `.cutoff`, `.cutoff-head label`, `.chip`, `input[type="range"]`, `.ticks`, `.help`
- `.chart-card`, `.chart-head h3`, `.caption`, `.chart-tools`, `.legend li`, `.sw`, `.chart-svg`, grid/axes, series classes
- `.grid-2`, `.data-table`, `.table-scroll`, `.empty`, `.chart-note`
- `.vintage-card`, `.footer`, `.sheet` (480px / bottom sheet), `.sheet-head`, `.sheet-body`

## 4. Deliberate deltas from export
| Element | Export (mock) | Implementation (real) | Rationale |
|---|---|---|---|
| Series control | Demand/Wind/Solar | View: Decision-time / Latest | Per docs/DECISIONS.md; wind-only focus, preserves structure/behavior |
| Day rail semantics | 31 Jan days | Decision dates (delivery = decision+1), default 15 Jan | A1 |
| Cutoff range | 0-42 (00:00-21:00) | 0-47 (00:00-23:30), default 09:00 | FR-03 |
| KPIs | mock values | From API with delta vs previous day at same cutoff/view | Real metrics |
| Hindsight | not present | Toggle (default ON), URL `h=1|0` | FR-05 override logged in DECISIONS.md |
| Main chart cutoff line | vertical line shown | Dropped (cutoff is on decision day) | Per spec §3.5 |
| Horizon chart | over selected window concept | Over whole January at selected cutoff, 3h buckets up to 48h | FR-09 + DECISIONS.md |
| Hero meta | "Windward model v1.4" | "1–31 January 2026 · Europe/London · Elexon BMRS" | No model |
| Note pill | "Illustrative pilot data" | "Elexon BMRS · data as of ..." from meta | Truthful |
| Footer | "Windward is a design concept..." | "Contains data from Elexon BMRS..." | Truthful |
