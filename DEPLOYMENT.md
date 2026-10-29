# Windward Deployment Guide

## Architecture Overview

This app has two components:
1. **Frontend** (React + Vite SPA) - Static site, can be deployed on Vercel, Netlify, Cloudflare Pages
2. **Backend v2** (FastAPI) - Persistent server that fetches from Elexon BMRS API, caches to disk, has background warmup. **Requires a persistent server** (not suitable for serverless functions due to disk cache, background threads, long startup).

The active backend is in `backend_v2/`. The `backend/` directory is legacy/mostly empty.

## Recommended Deployment

### Option 1: Vercel (Frontend) + Render/Railway/Fly.io (Backend) - Recommended

#### Deploy Backend v2 first

**Render.com (easiest):**
1. Go to https://render.com, connect your GitHub repo
2. Create a new "Web Service"
3. Connect repo `aditya072690/windward`
4. Root Directory: `backend_v2`
5. Environment: `Docker` (uses the Dockerfile we just created)
6. Add environment variables:
   - `PERIOD_START` = `2026-08-29`
   - `PERIOD_END_EXCLUSIVE` = `2026-10-29`
   - `CACHE_DIR` = `.cache/elexon`
   - `CORS_ORIGINS` = `https://your-frontend-url.vercel.app` (update after frontend deploy)
7. Deploy. Note the URL (e.g., `https://windward-api-xxx.onrender.com`)

**Railway.app:**
1. Go to https://railway.app, connect repo
2. Create new project from GitHub repo, select `backend_v2` as root
3. Railway will auto-detect Dockerfile
4. Add environment variables as above
5. Deploy and get public URL

**Fly.io:**
1. Install flyctl, run `fly launch` in `backend_v2/` directory
2. Configure env vars with `fly secrets set`
3. Deploy with `fly deploy`

#### Deploy Frontend to Vercel

1. Go to https://vercel.com, connect your GitHub repo
2. Import project `aditya072690/windward`
3. Root Directory: `frontend`
4. Framework Preset: `Vite`
5. Build Command: `npm run build` (default)
6. Output Directory: `dist` (default)
7. Add environment variable:
   - `VITE_API_BASE_URL` = `https://your-backend-url.onrender.com/api/v1` (or just `https://your-backend-url.onrender.com/api/v1`)
8. Deploy
9. Copy the frontend URL (e.g., `https://windward-xxx.vercel.app`)
10. Go back to backend and update `CORS_ORIGINS` to include this frontend URL, redeploy backend

### Option 2: Docker Compose (Self-hosted)
```bash
cp backend_v2/.env.example backend_v2/.env
# Update CORS_ORIGINS in .env if needed
docker compose -f docker-compose.prod.yml up --build
```
(You'll need to create docker-compose.prod.yml or adapt existing one)

## Environment Variables

### Backend v2
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PERIOD_START` | No | `2026-08-29` | Start of delivery period (inclusive) |
| `PERIOD_END_EXCLUSIVE` | No | `2026-10-29` | End of period (exclusive) |
| `CACHE_DIR` | No | `.cache/elexon` | Directory for Elexon API cache |
| `CORS_ORIGINS` | No | `http://localhost:5173,http://localhost:8080` | Comma-separated allowed origins |
| `TTL_SECONDS_NEW` | No | `300` | Cache TTL |
| `PORT` | No | `8000` | Port to listen on (set by hosting platform) |

### Frontend
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes (for production) | Full URL to backend API including `/api/v1` (e.g., `https://api.example.com/api/v1`). If not set, uses relative `/api/v1` path. |

## Testing Production Deployment
1. Visit frontend URL - should load without errors
2. Check browser console for errors
3. Verify data loads (charts, KPIs should show real data from Elexon)
4. Test navigation (Overview, Charts, Vintages)
5. Test Methodology dialog
6. Test on mobile viewport
7. Test refresh on any route (should not 404 - SPA rewrites configured)
8. Check Network tab - API calls should go to backend URL, not localhost
9. Verify no secrets exposed in browser
