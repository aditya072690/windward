# ARCHITECTURE — Windward

## 1. System context

```
┌──────────────┐   HTTPS    ┌────────────────────┐   SQL (read-only)   ┌──────────────────┐
│  Browser     │──────────▶ │  FastAPI backend   │───────────────────▶ │ SQLite snapshot  │
│  React SPA   │ ◀────────  │  (analytics+API)   │                     │ windward.db      │
└──────────────┘   JSON     └────────▲───────────┘                     └────────▲─────────┘
                                     │ (never at request time)                  │ writes
                                     │                                 ┌────────┴─────────┐
                                     └──────── offline ───────────────▶│ Ingestion CLI    │
                                                                       │ Elexon BMRS API  │
                                                                       └──────────────────┘
```

**Key idea:** the dataset is historical and immutable (Jan 2026). We ingest once, bundle a validated SQLite snapshot, and serve everything from it. The deployed app has **no runtime dependency** on Elexon, so the demo cannot fail because of an upstream outage or rate limit.

## 2. Components

| Component | Tech | Responsibility |
|---|---|---|
| Frontend | React 18, TypeScript (strict), Vite, Tailwind CSS (token-driven), TanStack Query, Recharts, Framer Motion | UI, URL state, charts, a11y. No business logic beyond formatting |
| Backend API | Python 3.12, FastAPI, Pydantic v2, pandas/numpy | Validation, decision-forecast selection, metrics, risk band |
| Data layer | SQLite (stdlib `sqlite3`, read-only URI at runtime) | Typed repository functions returning DataFrames |
| Ingestion | `httpx`, tenacity-style retry, Typer CLI | Fetch → validate → upsert → write `ingest_runs` + integrity report |
| Packaging | Docker (multi-stage), docker-compose, nginx | Local/prod parity |
| Hosting | Vercel (two projects: static frontend, Python serverless API) | Public demo |
| CI | GitHub Actions | Lint, types, tests, audit, docker build |

## 3. Repository layout (target)

```
/
├── README.md
├── DESIGN.md
├── docker-compose.yml
├── Makefile
├── .github/workflows/ci.yml
├── .env.example
├── docs/
│   ├── PRD.md  ARCHITECTURE.md  DATABASE.md  DESIGN_SYSTEM.md
│   ├── CODE_STYLE.md  SECURITY.md  TESTING.md  PLAN.md  VIDEO_SCRIPT.md
├── backend/
│   ├── pyproject.toml          # ruff, mypy, pytest config
│   ├── Dockerfile
│   ├── vercel.json
│   ├── api/index.py            # Vercel entry: `from app.main import app`
│   ├── app/
│   │   ├── main.py             # app factory, CORS, routers, error handlers
│   │   ├── config.py           # pydantic-settings
│   │   ├── core/               # time.py, errors.py, logging.py
│   │   ├── api/v1/             # meta.py decision.py accuracy.py evolution.py export.py health.py
│   │   ├── schemas/            # Pydantic response/request models
│   │   ├── services/           # decision.py metrics.py accuracy.py risk.py baseline.py
│   │   ├── repository/         # db.py queries.py
│   │   └── ingestion/          # elexon_client.py transform.py loader.py cli.py
│   ├── data/windward.db        # committed, validated snapshot
│   └── tests/                  # unit/ api/ ingestion/ fixtures/
└── frontend/
    ├── package.json  vite.config.ts  tailwind.config.ts  tsconfig.json
    ├── Dockerfile  nginx.conf  vercel.json
    └── src/
        ├── app/                # App.tsx, providers, shell
        ├── features/           # brief/ forecast/ accuracy/ evolution/ methodology/ presentation/
        ├── components/ui/      # Button, Card, Segmented, Slider, Sheet, Tooltip, Kbd, Skeleton...
        ├── components/charts/  # ForecastChart, ErrorBars, Histogram, Heatmap, Horizon...
        ├── hooks/              # useUrlState, useDecision, useAccuracy, useHotkeys
        ├── lib/                # api.ts, format.ts, time.ts, types.ts
        ├── styles/             # tokens.css, globals.css
        └── test/               # setup, msw handlers, fixtures
```

## 4. Core algorithm — decision-time forecast

```
inputs: decision_date D, cutoff HH:MM (Europe/London)
cutoff_utc   = localize(D, HH:MM, Europe/London) → UTC
delivery_day = [D+1 00:00Z, D+2 00:00Z)         # 48 half-hours
for each target start_time t in delivery_day:
    candidates = forecasts where start_time = t AND publish_time ≤ cutoff_utc
    chosen[t]  = argmax(publish_time) over candidates   # may be empty → missing
    horizon_h  = (t − chosen[t].publish_time) in hours
join chosen with actual[t]; error = forecast − actual
```

Implementation is a single indexed SQL query (see `docs/DATABASE.md`) plus a pandas left-join onto a complete 48-slot index so missing slots are explicit (`null`), never silently dropped. The boundary is **inclusive** (`publish_time == cutoff` is allowed).

## 5. Risk-adjusted line (walk-forward)

For delivery day *d*, compute errors for decision dates strictly **before** D using the same cutoff. Group by London hour-of-day; take the 90th percentile of signed error, floored at 0 → `p90_over[h]`. `conservative_mw = max(0, forecast_mw − p90_over[hour])`. Require ≥ 3 prior days, else return `null` and `history_days` so the UI explains why. This avoids look-ahead bias and is stated as a heuristic, not a guarantee.

## 6. API contract (`/api/v1`)

All timestamps are ISO-8601 UTC with `Z`. All errors use RFC 7807-style JSON: `{ "type", "title", "status", "detail", "request_id" }`.

| Method & path | Query | Returns |
|---|---|---|
| `GET /health` · `GET /ready` | – | liveness / DB-readable |
| `GET /meta` | – | decision window, default cutoff, timezone, `data_as_of`, row counts, source attribution |
| `GET /decision-forecast` | `decision_date`, `cutoff=HH:MM` | points[48], summary, risk |
| `GET /accuracy/summary` | `start`, `end`, `cutoff` | KPI object |
| `GET /accuracy/by-hour` | same | 24 entries `{hour, mae, bias, n}` |
| `GET /accuracy/daily` | same | per-delivery-day `{date, mae, rmse, bias, n}` |
| `GET /accuracy/distribution` | same + `bin_mw=250` | bins + P50/P90/P95 |
| `GET /accuracy/by-horizon` | `start`, `end`, `bucket_h=3` | buckets `{from_h, to_h, mae, bias, n}` (all vintages) |
| `GET /accuracy/heatmap` | same as summary | matrix day × hour mean error |
| `GET /forecast-evolution` | `target_time` | vintages `[{publish_time, forecast_mw, horizon_h}]` + `actual_mw` |
| `GET /export/decision-forecast.csv` | `decision_date`, `cutoff` | CSV download |

**Example — `GET /decision-forecast?decision_date=2026-01-15&cutoff=09:00`**

```json
{
  "decision_date": "2026-01-15",
  "delivery_date": "2026-01-16",
  "cutoff_utc": "2026-01-15T09:00:00Z",
  "points": [
    {
      "start_time": "2026-01-16T00:00:00Z",
      "forecast_mw": 6123.0,
      "publish_time": "2026-01-15T08:30:00Z",
      "horizon_h": 15.5,
      "actual_mw": 5890.0,
      "error_mw": 233.0,
      "conservative_mw": 5210.0
    }
  ],
  "summary": {
    "mean_mw": 6012.4, "peak_mw": 7420.0, "peak_time": "2026-01-16T13:30:00Z",
    "min_mw": 4380.0, "min_time": "2026-01-16T04:00:00Z",
    "energy_gwh": 144.3, "vintage_min": "2026-01-15T05:30:00Z",
    "vintage_max": "2026-01-15T08:30:00Z", "missing_points": 0
  },
  "risk": { "p90_overforecast_mw": 913.0, "history_days": 13, "method": "walk_forward" }
}
```

(Values illustrative. `actual_mw`, `error_mw`, `conservative_mw` may be `null`.)

**Validation:** `decision_date` must be inside the configured window (else `400`); malformed values `422`; `cutoff` must match `HH:MM` 00:00–23:59.

## 7. Caching & performance

- Data is immutable → responses carry `Cache-Control: public, max-age=3600, stale-while-revalidate=86400` and a weak `ETag` derived from `data_as_of` + query.
- Repository loads only the rows needed (indexed range queries). Expensive aggregates (`by-horizon`, `heatmap`) are memoised with `functools.lru_cache` keyed on `(args, db_version)`.
- Frontend: TanStack Query with `staleTime: Infinity` for the same keys; prefetch adjacent dates; code-split charts.

## 8. Error handling & observability

- Domain errors (`OutOfWindowError`, `NoDataError`) map to 4xx in one handler; unexpected errors → 500 with `request_id`, no stack traces to clients.
- Structured JSON logs (`structlog` or stdlib JSON formatter): `request_id`, route, duration, status.
- Frontend: error boundary per section; friendly retry states; no silent failures.

## 9. Configuration (env)

| Var | Default | Notes |
|---|---|---|
| `DATABASE_PATH` | `data/windward.db` | opened read-only |
| `DECISION_START` / `DECISION_END` | `2026-01-01` / `2026-01-31` | assumption A1 |
| `DEFAULT_CUTOFF` | `09:00` | assumption A2 |
| `MAPE_MIN_ACTUAL_MW` | `50` | assumption A7 |
| `CORS_ORIGINS` | `http://localhost:5173` | comma-separated allowlist |
| `LOG_LEVEL` | `INFO` | |
| Frontend `VITE_API_BASE_URL` | `/api/v1` | |

## 10. Deployment topologies

1. **Local / reviewer:** `docker compose up --build` → nginx serves SPA on `:8080`, proxies `/api` to backend `:8000`.
2. **Vercel (public demo):** two projects from one repo.
   - `frontend/` — static Vite build, SPA rewrite to `index.html`, security headers.
   - `backend/` — Python serverless function via `api/index.py`; `vercel.json` rewrites `/(.*)` → `/api/index` and `includeFiles` bundles `data/windward.db`. Frontend uses `VITE_API_BASE_URL=https://<backend>.vercel.app/api/v1`.
   - **Agent must verify current Vercel Python/FastAPI configuration in Vercel docs before finalising**, and keep bundle < 250 MB unzipped.
3. **Fallback:** same Docker images on Render/Fly if Vercel limits bite.

## 11. Architecture decision records

| ADR | Decision | Why | Trade-off |
|---|---|---|---|
| 1 | Bundle immutable SQLite snapshot | Zero ops, deterministic demo, fast | Not live; refresh via CLI |
| 2 | FastAPI + Pydantic v2 | Typed, auto OpenAPI, fast | – |
| 3 | Analytics server-side (pandas) | Single source of truth; testable; thin client | Slightly heavier serverless bundle |
| 4 | Walk-forward risk band | No look-ahead bias; credible with quants | Needs ≥ 3 days of history |
| 5 | Two Vercel projects | Reliable with each runtime's zero-config | Needs CORS + 2 URLs |
| 6 | UTC storage, London display | Correct under DST even though Jan has none | Small conversion layer |
| 7 | Hindsight off by default | Preserves the decision-moment mental model | Extra click to see actuals |

## 12. Scaling path (for the tech-lead discussion)

Move SQLite → PostgreSQL/TimescaleDB, schedule incremental ingestion (cron/queue), add Redis cache, version the API, add auth/SSO, extend to solar and regional data, track forecast skill over time with alerts when error exceeds thresholds.
