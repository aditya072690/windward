# Windward

**Day-ahead wind intelligence for GB power buyers.**
See the latest national wind forecast that was available at your decision time, and measure how accurate those forecasts are against actual generation.

- **Live demo:** `<LIVE_URL>`
- **Demo video (unlisted):** `<VIDEO_URL>`
- **Data:** [Elexon BMRS](https://bmrs.elexon.co.uk/) — `FUELHH` (actual wind) and `WINDFOR` (wind forecast), January 2026 decisions.

---

## What it does

| Question | Answer in the app |
|---|---|
| What was the wind forecast when I had to decide? | **Decision view:** for any decision date in Jan 2026 and any cutoff, the latest forecast published at or before the cutoff, for each half-hour of tomorrow |
| How accurate are forecasts? | **Accuracy view:** MAE, RMSE, bias, nMAE, MAPE, P90 errors, by hour, by day, by distribution, by heatmap |
| Does waiting for a later forecast help? | **Horizon view:** error versus forecast age, plus how forecasts evolve toward the actual |
| How much buffer should I keep? | **Conservative (P90) line**, computed walk-forward with no look-ahead |

Highlights: Apple-inspired UI, light/dark, keyboard-first, accessible (WCAG AA), shareable URLs, CSV export, presentation mode.

## Quick start

### Option A — Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
# App:  http://localhost:8080
# API:  http://localhost:8080/api/v1/meta   (docs: http://localhost:8080/api/docs)
```

### Option B — local development

```bash
# Backend (Python 3.12)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (Node 22)
cd frontend
npm ci
npm run dev        # http://localhost:5173 (proxies /api to :8000)
```

### Refresh the data snapshot (optional)

A validated snapshot is committed at `backend/data/windward.db`, so the app runs offline. To re-fetch from Elexon:

```bash
make ingest        # python -m app.ingestion.cli --from 2025-12-29 --to 2026-02-02
```

## Key assumptions

1. A *decision date* is a day in January 2026; the *delivery day* is the next day.
2. Default cutoff is **09:00 Europe/London** on the decision date (configurable in the UI).
3. "Latest forecast available" = per half-hour, the forecast with the greatest `publishTime ≤ cutoff` (boundary inclusive).
4. Error = forecast − actual; positive means over-forecast (the costly direction for a buyer).

Full list: [`docs/PRD.md`](docs/PRD.md#6-assumptions-must-be-surfaced-in-the-ui-methodology-drawer-and-readme) and the in-app *Methodology* drawer.

## Project structure

```
.
├── README.md                 ← you are here
├── DESIGN.md                 ← product/UX design and feature set
├── docker-compose.yml        ← one-command stack (nginx + API)
├── Makefile                  ← dev/test/lint/ingest shortcuts
├── .env.example
├── .github/workflows/ci.yml  ← lint, types, tests, audit, docker build
├── docs/
│   ├── PRD.md                ← requirements, assumptions, metrics
│   ├── ARCHITECTURE.md       ← components, algorithm, API contract, ADRs
│   ├── DATABASE.md           ← SQLite schema, queries, ingestion, DQ checks
│   ├── DESIGN_SYSTEM.md      ← tokens and component specs
│   ├── CODE_STYLE.md         ← conventions
│   ├── SECURITY.md           ← threat model and controls
│   ├── TESTING.md            ← strategy, cases, gates
│   ├── PLAN.md               ← delivery plan and checklists
│   └── VIDEO_SCRIPT.md       ← two-part demo script
├── backend/
│   ├── app/                  ← FastAPI app: api/, services/, repository/, ingestion/, core/
│   ├── tests/                ← unit, api, ingestion, snapshot integrity
│   ├── data/windward.db      ← validated snapshot (read-only at runtime)
│   └── Dockerfile
└── frontend/
    ├── src/                  ← app/, features/, components/, hooks/, lib/, styles/
    └── Dockerfile
```

## API overview

`GET /api/v1/…` — `meta`, `decision-forecast`, `accuracy/{summary,by-hour,daily,distribution,by-horizon,heatmap}`, `forecast-evolution`, `export/decision-forecast.csv`, `health`, `ready`. Interactive docs at `/api/docs`. Contract details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#6-api-contract-apiv1).

## Testing

```bash
make test      # unit + integration (backend & frontend)
make e2e       # Playwright journeys
make lint      # ruff, mypy --strict, eslint, tsc, prettier
```

Strategy, golden fixtures and coverage gates: [`docs/TESTING.md`](docs/TESTING.md).

## Deployment

- **Frontend:** Vercel static project from `frontend/`.
- **Backend:** Vercel Python function from `backend/` (bundles the SQLite snapshot).
- Set `VITE_API_BASE_URL` on the frontend and `CORS_ORIGINS` on the backend. Steps in [`docs/PLAN.md`](docs/PLAN.md).

## Tech stack

React 18 · TypeScript · Vite · Tailwind · TanStack Query · Recharts · Framer Motion — Python 3.12 · FastAPI · Pydantic v2 · pandas · SQLite — Docker · GitHub Actions · Vercel.

## AI assistance disclosure

This project was built with AI coding assistance (an AI coding agent driven from the documents in this repository, with human review of design decisions, assumptions, tests and deployment). All logic was verified with the automated tests and by manual spot checks against source data.

## Data attribution

Contains data from Elexon BMRS. Check Elexon's current data licence/terms before reuse.

## Documentation index

[PRD](docs/PRD.md) · [Architecture](docs/ARCHITECTURE.md) · [Database](docs/DATABASE.md) · [Design](DESIGN.md) · [Design system](docs/DESIGN_SYSTEM.md) · [Code style](docs/CODE_STYLE.md) · [Security](docs/SECURITY.md) · [Testing](docs/TESTING.md) · [Plan](docs/PLAN.md) · [Video script](docs/VIDEO_SCRIPT.md)
