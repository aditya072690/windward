# PLAN — Windward delivery plan (16-hour cap)

## 1. Time budget

| Phase | Hours | Output | Exit gate |
|---|---|---|---|
| 0. Setup & discovery | 1.0 | Repo skeleton, tooling, Elexon API verified | Endpoints/params confirmed from live OpenAPI; sample data fetched |
| 1. Data & ingestion | 2.0 | `windward.db` snapshot + integrity report | All hard DQ checks pass |
| 2. Backend core | 3.0 | Decision logic, metrics, API, tests | Golden tests green; `/docs` works |
| 3. Frontend foundation | 2.0 | Tokens, shell, primitives, API layer | Hero + Brief render real data |
| 4. Frontend features | 3.5 | Forecast Studio, Accuracy, Horizon, Methodology | All P0 FRs demoable |
| 5. Polish & extras | 1.5 | P1 (and P2 if time) features, dark mode, a11y, motion | Axe clean; Lighthouse ≥ 95 |
| 6. Docker, CI, deploy | 1.5 | compose, CI, Vercel live | Incognito load works |
| 7. Docs, QA, video | 1.5 | README final, QA checklist, 2-part video | Submission form sent |
| **Total** | **16.0** | | |

If time runs short, **cut P2 first, then P1; never cut tests for P0 logic.**

## 2. Milestones and checklists

### M1 — Data trusted
- [ ] Verified FUELHH/WINDFOR endpoint paths and parameters
- [ ] Ingestion CLI idempotent, chunked, retried
- [ ] 48 actual rows per delivery day; vintages present before 09:00 for ≥ 95 % of slots
- [ ] Spot-check 3 half-hours manually vs. Elexon

### M2 — Logic proven
- [ ] Decision selection tests incl. inclusive boundary
- [ ] Metric golden tests; walk-forward no-look-ahead test
- [ ] All API routes + error mapping + cache headers

### M3 — Experience delivered
- [ ] P0: FR-01…FR-10 working end-to-end
- [ ] P1: FR-11…FR-16
- [ ] P2 (optional): FR-17…FR-20, presentation mode
- [ ] Light/dark, responsive, reduced motion

### M4 — Shippable
- [ ] `docker compose up --build` from a clean clone works
- [ ] CI green (lint, types, tests, audit, docker)
- [ ] Deployed; headers verified; incognito check done
- [ ] README placeholders `<LIVE_URL>`, `<VIDEO_URL>` replaced

## 3. Your (human) tasks vs. the agent's

| You | Coding agent |
|---|---|
| Create **anonymous** GitHub repo (random-looking name) and neutral git identity | Scaffold, implement, test, document, commit in small conventional commits |
| Provide the agent `MASTER_PROMPT.md` + all docs | Follow the prompt end-to-end |
| Connect repo to Vercel (two projects: `frontend`, `backend`), set env vars | Provide `vercel.json` files and exact env var list |
| Review numbers and wording; record video | Provide `docs/VIDEO_SCRIPT.md` aligned to real UI |
| Upload video as **Unlisted** on YouTube; fill submission form | – |

## 4. Deployment steps (Vercel)

1. Push to the anonymous repo.
2. **Backend project:** import repo → Root Directory `backend` → framework "Other" → env `CORS_ORIGINS=<frontend-url>`, `DATABASE_PATH=data/windward.db`. Confirm `/api/v1/health`.
3. **Frontend project:** import repo → Root Directory `frontend` → framework Vite → env `VITE_API_BASE_URL=https://<backend>.vercel.app/api/v1`.
4. Update backend `CORS_ORIGINS` with the final frontend URL; redeploy.
5. `curl -I` both URLs to verify security headers; open in **incognito**.
6. (Agent must re-check Vercel's current Python/FastAPI docs; adjust config if they differ.)

## 5. Submission checklist (from the brief)

- [ ] Public GitHub repo, **anonymous name**, README with structure, run steps, live link, AI-tool disclosure
- [ ] Deployed app link works with no login
- [ ] Unlisted YouTube video ≤ 10 min: **Part 1 client pitch (≤ 5 min)** + **Part 2 tech-lead review (≤ 5 min)**
- [ ] All links tested in an incognito window
- [ ] Submission form completed

## 6. Traceability pass (final hour)

For each FR/NFR in `docs/PRD.md`, tick: implemented · tested · demonstrated. Anything unticked must be listed honestly in README under "Known limitations".

## 7. Risks and contingencies

| Risk | Trigger | Response |
|---|---|---|
| Elexon API slow/limited | Ingestion > 20 min | Smaller chunks; keep only horizon ≤ 72 h; commit snapshot once |
| Vercel Python issues | Build/bundle failure | Switch backend to Docker host (Render/Fly), keep frontend on Vercel |
| Schedule slip | > 1 h behind at M2 | Drop heatmap, skill score, presentation mode, palette |
| Chart library friction | Hours lost | Fall back to simpler Recharts compositions; keep table view |
