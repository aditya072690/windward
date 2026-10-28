# PRD — Windward

> Day-ahead wind intelligence for GB power buyers.
> Status: v1.0 · Audience: engineers, coding agents, reviewers · Scope: first pilot version

---

## 1. Overview

**Windward** is a web application for the day-ahead power-buying desk of a UK energy utility. It answers two questions:

1. **"What is the latest wind forecast I actually had when I had to decide?"**
2. **"How wrong are those forecasts, quantitatively, so I can size my buffer?"**

The buyer must purchase the power that wind will *not* cover (e.g. from thermal plants) one day before delivery. Wind is weather-dependent, so the decision rests entirely on forecasts. Windward makes the forecast available at decision time clear, and makes its error measurable.

## 2. Problem statement

| Pain | Consequence |
|---|---|
| Forecasts are re-published many times per day; it is easy to look at the wrong vintage | Decisions based on information that wasn't available (or was stale) at gate closure |
| Forecast error is rarely quantified in a form a trader can act on | Buffers set by gut feel; over- or under-procurement |
| Over-forecasting wind → under-buying → expensive balancing | Real cost exposure |

## 3. Users

| Persona | Needs |
|---|---|
| **Day-ahead trader (primary)** | One-glance view of the decision-time forecast; confidence in how much to trust it |
| **Head of trading / analyst** | Defensible accuracy numbers; ability to slice by time of day, horizon, day |
| **Reviewer (internal tech lead)** | Clear architecture, tested logic, reproducible data pipeline |

## 4. Goals and non-goals

**Goals**
- Show, for any decision date in January 2026, the latest national wind forecast published at or before a configurable cutoff.
- Quantify forecast accuracy against actual generation with industry-standard metrics.
- Present everything in a polished, Apple-grade interface that a non-technical stakeholder can understand in seconds.
- Ship as a Dockerised React + Python application, deployed publicly.

**Non-goals (explicitly out of scope)**
- Demand forecasting or net-load/"residual demand" calculation (no demand data in scope).
- Price data, bidding, or trade execution.
- Any data source other than Elexon BMRS `FUELHH` (actuals) and `WINDFOR` (forecasts).
- Solar or other renewables; regional (non-national) breakdown.
- Authentication, multi-tenancy, user accounts.
- Building a new forecasting model.

## 5. Data (fixed by the brief)

| Dataset | Endpoint family | Fields used |
|---|---|---|
| Actual generation | Elexon BMRS `FUELHH` stream, `fuelType = WIND` | `startTime`, `generation` (MW), `settlementDate`, `settlementPeriod` |
| Forecast generation | Elexon BMRS `WINDFOR` stream | `startTime`, `publishTime`, `generation` (MW) |

Resolution: 30 minutes. Scope: purchase decisions made in **January 2026**.

## 6. Assumptions (must be surfaced in the UI "Methodology" drawer and README)

| # | Assumption | Rationale | Configurable |
|---|---|---|---|
| A1 | A *decision date* is a date in 1–31 Jan 2026; the *delivery day* is decision date + 1 (so delivery days span 2 Jan – 1 Feb 2026) | Day-ahead purchases are made the day before delivery; "decisions made in January" | `DECISION_START`, `DECISION_END` |
| A2 | Default **cutoff = 09:00 Europe/London on the decision date** | Conservative time before typical day-ahead gate closures; the brief gives no cutoff | `DEFAULT_CUTOFF` + UI control |
| A3 | "Latest forecast available" = for each target half-hour, the forecast with the greatest `publishTime ≤ cutoff` | Direct reading of the requirement | – |
| A4 | Error `e = forecast − actual` (MW). **Positive = over-forecast** (the costly direction for a buyer) | Makes risk direction explicit | – |
| A5 | January is entirely GMT, so UTC == Europe/London; store UTC, display Europe/London | Avoids DST ambiguity but keeps code correct | – |
| A6 | Half-hours with no forecast published before the cutoff are reported as missing and excluded from metrics (coverage is reported) | Honest accounting | – |
| A7 | MAPE excludes half-hours with actual < 50 MW | MAPE explodes near zero | `MAPE_MIN_ACTUAL_MW` |
| A8 | No installed-capacity data, so "normalised" error is divided by mean actual generation of the window (nMAE) | Only data in scope | – |

## 7. Functional requirements

Priority: **P0** = must ship · **P1** = should ship · **P2** = delight, ship if time allows.

| ID | Pri | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-01 | P0 | **Decision Brief**: headline card for selected decision date + cutoff | Shows delivery date, mean/peak/min forecast (MW), total energy (GWh), forecast vintage range, and one plain-English sentence. Updates < 300 ms after control change (cached) |
| FR-02 | P0 | **Forecast chart**: 48 half-hour points for the delivery day using the decision-time forecast | Exactly the forecast with max `publishTime ≤ cutoff` per half-hour; tooltip shows value + publish time + horizon |
| FR-03 | P0 | **Cutoff control** | 00:00–23:30 on decision date; default 09:00; keyboard-operable; chart + brief update live; selected vintage visible |
| FR-04 | P0 | **Decision date selection** | Only valid January dates selectable; calendar rail with all 31 days; ←/→ keys step days |
| FR-05 | P0 | **Hindsight toggle** (default off): overlay actual generation | Actuals hidden by default in Forecast view to preserve the "decision moment"; error shading appears when on |
| FR-06 | P0 | **Accuracy KPIs** over a date range at the selected cutoff | MAE, RMSE, Bias, nMAE, MAPE, P90 \|error\|, P90 over-forecast, coverage %, n; each with a one-line plain-English tooltip |
| FR-07 | P0 | **Error by hour of day** | 24 bars (Europe/London hour); shows MAE and bias |
| FR-08 | P0 | **Daily accuracy trend** | One point/bar per delivery day; click selects that decision date |
| FR-09 | P0 | **Accuracy by forecast horizon** (all vintages) | Error vs. horizon in 3-hour buckets up to 48 h; demonstrates how accuracy degrades with lead time |
| FR-10 | P0 | **Methodology drawer** | Lists assumptions A1–A8, metric formulas, data lineage, "data as of" timestamp |
| FR-11 | P1 | **Error distribution histogram** | 250 MW bins; P50/P90/P95 markers |
| FR-12 | P1 | **Forecast evolution** for one target half-hour | All vintages by publish time vs. actual; cutoff marked |
| FR-13 | P1 | **Risk-adjusted (conservative) line + band** | `max(0, forecast − P90 over-forecast by hour-of-day)` using **walk-forward** history only (no look-ahead); hidden with explanation if < 3 prior days |
| FR-14 | P1 | **CSV export** of decision-time forecast table | Columns: start_time, forecast_mw, publish_time, horizon_h, actual_mw, error_mw |
| FR-15 | P1 | **Shareable URL state** | `?d=2026-01-15&c=09:00&h=1` restores view |
| FR-16 | P1 | **Light/Dark mode** | Follows system; manual override persisted |
| FR-17 | P2 | **Error heatmap** (day × hour) | Diverging colour scale centred at 0 |
| FR-18 | P2 | **Presentation mode** | Full-screen guided story (arrow-key stepping) for demos |
| FR-19 | P2 | **Command palette (⌘K)** and keyboard shortcuts | Jump to date, toggle hindsight, open methodology |
| FR-20 | P2 | **Persistence baseline & skill score** | Baseline = actual 24 h earlier; skill = 1 − MAE_forecast / MAE_baseline |

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| Performance | API p95 < 300 ms warm; initial JS ≤ 250 KB gzip; Lighthouse Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95 |
| Accessibility | WCAG 2.2 AA; full keyboard operation; charts have a "view as table" alternative; respects `prefers-reduced-motion` and `prefers-color-scheme` |
| Reliability | Runs with **zero external calls at runtime** (data snapshot bundled); live Elexon refresh only through the ingestion CLI |
| Security | See `docs/SECURITY.md` |
| Maintainability | Typed end-to-end (mypy strict, TS strict), lint-clean, documented, tests per `docs/TESTING.md` |
| Portability | `docker compose up` runs the full stack with one command |
| Browsers | Last 2 versions of Safari, Chrome, Edge, Firefox; iOS Safari 16+ |

## 9. Metric definitions

Let `f_i` = decision-time forecast, `a_i` = actual, `e_i = f_i − a_i`, over `n` half-hours with both values.

| Metric | Formula | Meaning for the buyer |
|---|---|---|
| MAE | `mean(|e|)` | Typical miss in MW |
| RMSE | `sqrt(mean(e²))` | Penalises large misses |
| Bias | `mean(e)` | Persistent over (+) or under (−) forecasting |
| nMAE | `MAE / mean(a)` | Error relative to typical wind output |
| MAPE | `mean(|e| / a)` where `a ≥ 50 MW` | Percentage error |
| P50/P90/P95 \|e\| | percentiles of `|e|` | "9 times out of 10 the miss is below X MW" |
| P90 over-forecast | 90th percentile of `e`, floored at 0 | Suggested downside buffer |
| Coverage | `n / expected half-hours` | Data completeness |

## 10. Pilot success criteria (what the demo must show)

1. A buyer can pick a date and cutoff and see the exact forecast vintage in use within 5 seconds.
2. The accuracy page states a defensible number: *"At a 09:00 cutoff, typical error is X MW (Y% of mean wind output); 9 in 10 over-forecasts are below Z MW."*
3. The horizon view shows the practical value of waiting for later forecasts.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Elexon API shape/limits differ from assumptions | Ingestion verifies against the live OpenAPI spec first; paginates by date chunks; retries with backoff |
| Vercel Python bundle/runtime limits | Lean dependencies; bundled SQLite snapshot; fallback: containerised backend on another host |
| Ambiguity of "decisions made in January" | Assumption A1 documented and configurable |
| Scope creep from P2 items | P0 → P1 → P2 gating in `docs/PLAN.md`; 16-hour cap |

## 12. Open questions for the client (to raise in the pitch)

- What is the exact internal cutoff for your day-ahead submissions?
- Would you like error expressed against installed capacity once that data is available?
- Should the conservative buffer target P90, or a different risk appetite?

## 13. Deliverables mapping

| Brief deliverable | Where |
|---|---|
| Public repo with README | Repo root, `README.md` |
| Vercel deployment link | README + submission form |
| Unlisted YouTube video (≤10 min, 2 parts) | `docs/VIDEO_SCRIPT.md` guides it |
| AI-tool disclosure | README "AI assistance" section |
