# Windward - Production Readiness Audit

## Repository Overview
- **Git repo**: https://github.com/aditya072690/windward (commit 23cb07f)
- **Structure**: Monorepo with `frontend/` (React + Vite + TypeScript) and two backend dirs (`backend/` mostly empty/cache, `backend_v2/` active FastAPI implementation)
- **Node**: v23.10.0, npm 11.7.0 (local); CI uses Node 22
- **Python**: 3.12+ required for backend_v2

## Current Architecture (as implemented)
### Frontend (`frontend/`)
- React 18, Vite 5, TypeScript 5.6, TanStack Query, no router (single page app), charts rendered via canvas
- API calls go through `src/lib/api.ts` using `import.meta.env.VITE_API_BASE_URL || '/api/v1'`
- Dev server proxies `/api` to `http://localhost:8000` (see `vite.config.ts`) - needs updating if using backend_v2 on different port
- Build passes with `tsc && vite build` (generates dist/)
- Has `vercel.json` for SPA rewrites + security headers
- Animations added to nav, responsive design present
- Uses London time handling via backend; frontend reads from `/api/v1/meta`

### Backend v2 (`backend_v2/`) - ACTIVE IMPLEMENTATION
- FastAPI app in `app/main.py`, runs with uvicorn
- **No SQLite/DB** - pulls live data from Elexon BMRS API at runtime
- Two datasets: WINDFOR (hourly forecasts, multiple publish times) and FUELHH (half-hourly actuals, filtered to WIND)
- Caches to disk under `.cache/elexon/` (cache files present)
- Background warm-up thread on startup loads forecasts/actuals
- CORS configured via `CORS_ORIGINS` env var (default includes localhost:5173, localhost:8080)
- Serves both at root and under `/api/v1/` prefixes (routes mounted twice)
- Endpoints: `/health`, `/ready`, `/api/v1/meta`, `/api/v1/decision-forecast`, `/api/v1/accuracy/*`
- Period configured via env: `PERIOD_START` (default 2026-08-29), `PERIOD_END_EXCLUSIVE` (default 2026-10-29)
- Domain logic in `app/domain/` handles London time (zoneinfo), vintage selection (bisect), hourly->half-hour interpolation, DST (50 slots on 2026-10-25)

### Backend (old) (`backend/`)
- Mostly empty; contains only cache files and pytest cache. CI workflow references `backend/` but it's not the active implementation. This is likely legacy from original design.

## Build/Lint/Test Status
- **Frontend tsc**: passes with no errors
- **Frontend build**: passes (dist generated successfully)
- **Frontend lint**: has 23 errors + 1 warning (mostly `@typescript-eslint/no-explicit-any` in various files, unused var in ThemeToggle). Not blocking build but should be addressed for production quality
- **Frontend tests**: vitest configured but no test files found (exits with code 1) - tests may not be required
- **Backend v2 import**: works with PYTHONPATH
- **Backend v2 tests**: none found in backend_v2/tests
- **Backend (old) tests/lint**: CI expects them but backend/ has no source code

## Deployment Considerations
From README and docs:
- Old design says deploy frontend to Vercel, backend (SQLite snapshot) as Vercel Python function from `backend/`
- Current implementation uses `backend_v2/` with live Elexon API calls, disk caching, background threads - this is **not suitable for serverless/Vercel Functions** (ephemeral filesystem, long startup/warmup, needs persistent cache/write access, stateful warmup). Needs a persistent server (Render, Railway, Fly.io, DigitalOcean App Platform, etc.)
- Frontend is static SPA - perfect for Vercel/Netlify/Cloudflare Pages
- CORS needs to allow the deployed frontend domain
- Frontend needs `VITE_API_BASE_URL` pointing to deployed backend URL

## Issues to Fix for Production
1. **Backend deployment**: Need to deploy `backend_v2/` as a persistent service (not serverless). Dockerfile doesn't exist for backend_v2 - need to create one.
2. **Frontend API config**: Vite dev proxy points to :8000; production needs env var. Also need to ensure API_BASE is correctly configured.
3. **CORS**: Backend needs to accept requests from deployed frontend origin
4. **Environment variables**: Need to configure properly
5. **Lint errors**: Some errors exist but don't block build - better to fix critical ones
6. **Health checks**: Backend has /health and /ready endpoints - good
7. **Security headers**: Frontend nginx.conf and vercel.json have headers; good
8. **No .env files committed**: Good (only .env.example)
9. **Docker setup**: docker-compose references old backend/ structure - may need updating or just document
