# TESTING — Windward

Goal: **prove the two things the client cares about are correct** — (1) the decision-time forecast selection and (2) the accuracy metrics — and keep the rest of the stack boringly reliable.

## 1. Pyramid

| Layer | Tools | Scope |
|---|---|---|
| Unit (backend) | pytest, pytest-cov, hypothesis | `services/*`, `core/time.py`, `ingestion/transform.py` |
| API / contract | FastAPI `TestClient`, schemathesis (optional) | Every route, status codes, schemas |
| Data integrity | pytest against committed DB | Snapshot health checks |
| Unit/component (frontend) | Vitest, React Testing Library, MSW | Hooks, formatters, components, chart wrappers |
| E2E | Playwright (Chromium + WebKit) | Core journeys, keyboard, dark mode |
| Accessibility | `@axe-core/playwright`, `eslint-plugin-jsx-a11y` | WCAG AA checks |
| Performance | Lighthouse CI | Budgets from PRD NFRs |
| Static | ruff, mypy --strict, tsc --noEmit, eslint, prettier --check | Every commit |

## 2. Golden fixtures

`backend/tests/fixtures/` holds **hand-built, tiny** datasets whose answers are computed by hand and documented in comments:

- `golden_small.sql` — 1 delivery day, 4 half-hours, 3 vintages each, so selection and errors are trivially checkable.
- `golden_metrics.csv` — 10 paired values with expected MAE/RMSE/bias/percentiles written next to them.

## 3. Backend test cases (minimum)

**Decision selection (`services/decision.py`)**
1. Picks the vintage with max `publish_time` ≤ cutoff.
2. **Boundary:** vintage with `publish_time == cutoff` **is included**; `cutoff + 1 s` is **excluded**.
3. Ignores later vintages even if "better".
4. No vintage ≤ cutoff → point returned with `forecast_mw = null`, counted in `missing_points`.
5. Always returns exactly 48 slots for a normal day (explicit nulls, not dropped rows).
6. Cutoff local→UTC conversion correct (assert with a non-GMT date in a unit test of `core/time.py` to prove DST-safety, even though data is January).
7. Horizon hours computed as `(start_time − publish_time)`.
8. Hypothesis property: for any random set of vintages, chosen `publish_time` ≤ cutoff and no unchosen vintage ≤ cutoff has a larger `publish_time`.

**Metrics (`services/metrics.py`)**
1. MAE, RMSE, bias match golden values to 1e-9.
2. Sign convention: over-forecast ⇒ positive bias.
3. MAPE excludes `actual < MAPE_MIN_ACTUAL_MW`; all-excluded ⇒ `null`, not a crash/NaN in JSON.
4. Percentiles (P50/P90/P95) use a documented method (linear interpolation, numpy default) — test with known array.
5. Empty input ⇒ well-defined nulls and `n = 0`.
6. Coverage = `n / expected`.

**Risk band (`services/risk.py`)**
1. **No look-ahead:** modifying errors on/after the target day does not change the band.
2. < 3 prior days ⇒ `null` + `history_days` reported.
3. Result floored at 0 and never negative `conservative_mw`.

**Horizon analysis** — bucket edges inclusive/exclusive as documented; vintages beyond 48 h are excluded or in an "other" bucket exactly as the spec says.

**API**
- 200 + schema-valid for each route (validate with the Pydantic response model).
- 400 for out-of-window date; 422 for malformed date/cutoff/bin; 404 for unknown route.
- `Cache-Control` and `ETag` present; conditional request returns 304.
- CORS: allowed origin echoed; disallowed origin not.
- Write-protection: attempting `INSERT` via the runtime connection raises.

**Ingestion** (HTTP mocked with `respx`)
- Chunked fetch covers the full window without gaps/overlaps.
- Retries on 429/503 then succeeds; raises after max attempts.
- Filters non-WIND fuel types; rejects bad rows and counts them.
- Idempotent: running twice leaves identical row counts and hashes.

**Snapshot integrity** — implements every check in `docs/DATABASE.md §6`.

## 4. Frontend test cases (minimum)

- `format.ts`: MW/GW/GWh formatting, signed error, percentages, London time display.
- `useUrlState`: parses valid state, rejects invalid, writes back without history spam.
- `CutoffControl`: arrow keys step 30 min; announces value via `aria-valuetext`; clamps range.
- `DecisionBrief`: renders loading skeleton, success, error + retry (MSW).
- `ForecastChart`: renders 48 points, hides actual until Hindsight is on, shows "missing" gaps.
- `MetricCard`: tooltip text accessible; null → "—".
- Table-view toggle presents the same numbers as the chart.
- Snapshot tests only for design tokens (avoid brittle DOM snapshots).

## 5. E2E journeys (Playwright)

1. **Load → default view:** brief visible, chart rendered, no console errors, LCP < 2.5 s.
2. **Change date** via rail and via ←/→; URL updates; brief changes.
3. **Change cutoff** to 06:00 and 12:00; chosen vintage range in the brief changes accordingly.
4. **Hindsight on/off:** actual line + error shading toggles.
5. **Accuracy section:** KPIs present; clicking a day in the trend selects that decision date.
6. **Methodology drawer:** opens with `?`/button, traps focus, closes with Esc.
7. **Dark mode:** toggle, persists on reload.
8. **Deep link:** `?d=2026-01-20&c=10:30&h=1` restores state.
9. **Mobile viewport (iPhone 14):** no horizontal scroll; controls usable.
10. **Axe scan** on each major state: zero serious/critical violations.

## 6. Coverage and quality gates

| Gate | Threshold |
|---|---|
| Backend line coverage (`services/`, `core/`) | ≥ 90 % |
| Backend overall | ≥ 80 % |
| Frontend (`lib/`, `hooks/`, `features/`) | ≥ 80 % |
| mypy --strict / tsc strict | 0 errors |
| ruff / eslint | 0 errors, 0 warnings |
| Lighthouse (Perf/A11y/BP/SEO) | ≥ 95 / 95 / 95 / 90 |
| E2E | all green on Chromium + WebKit |

## 7. Commands

```bash
make test            # backend + frontend unit/integration
make test-backend    # cd backend && pytest --cov=app --cov-report=term-missing
make test-frontend   # cd frontend && npm run test -- --coverage
make e2e             # cd frontend && npx playwright test
make lint            # ruff, mypy, eslint, tsc, prettier --check
make audit           # pip-audit, npm audit
```

## 8. CI pipeline (`.github/workflows/ci.yml`)

Jobs: `backend` (lint → types → tests+cov → pip-audit) · `frontend` (lint → types → tests → build → npm audit) · `e2e` (compose up → Playwright) · `docker` (build both images) · `secrets` (gitleaks). All required to be green before the deploy step.

## 9. Manual QA checklist (before recording the video)

- [ ] Fresh clone → `docker compose up --build` works with no extra steps
- [ ] Deployed URL opened in **incognito** loads with data
- [ ] Every number in the demo can be traced to the CSV export
- [ ] Spot-check 3 half-hours by hand against the Elexon web UI/API
- [ ] Light and dark mode both look right; reduced-motion honoured
- [ ] Mobile Safari viewport reviewed

## 10. Requirement traceability

Each test file header lists the FR/NFR IDs it covers (e.g. `# Covers: FR-02, FR-03`). `docs/PLAN.md` includes a final traceability pass.
