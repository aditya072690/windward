# SECURITY — Windward

Windward handles **public, non-personal market data**, has **no authentication and no user data**, and its database is **read-only at runtime**. The threat model is therefore modest, but we still ship production-grade hygiene — this is part of what the tech-lead review will check.

## 1. Assets and threats

| Asset | Threat | Control |
|---|---|---|
| API availability | Abuse / scraping / DoS | Cache headers, bounded queries, input limits, platform rate-limiting; optional `slowapi` (documented as best-effort on serverless) |
| Data integrity | Tampering | Read-only DB URI; snapshot committed; integrity test in CI |
| Clients | XSS / clickjacking / MIME sniffing | Strict CSP and security headers; React escaping; no `dangerouslySetInnerHTML` |
| Supply chain | Malicious/vulnerable deps | Lockfiles, Dependabot, `pip-audit`, `npm audit`, pinned Docker base images |
| Secrets | Leakage | None required; `.env` git-ignored; `.env.example` only; secret scanning in CI |
| Author privacy | De-anonymisation of submission | Anonymous repo name, no personal names/emails in README, code, or commit metadata |

## 2. Backend controls

- **Validation:** every query parameter parsed by Pydantic (types, ranges). `decision_date` clamped to the configured window; `cutoff` regex `^([01]\d|2[0-3]):[0-5]\d$`; `bucket_h` and `bin_mw` bounded; reject anything else with 422.
- **SQL:** parameterised queries only. **Never** string-format SQL. Table/column names are constants.
- **DB access:** `sqlite3.connect("file:...?mode=ro", uri=True)`; no write statements in the runtime package (enforced by a test that greps for `INSERT|UPDATE|DELETE|DROP` outside `ingestion/`).
- **CORS:** explicit allowlist from `CORS_ORIGINS`; no wildcard with credentials; only `GET`/`OPTIONS`.
- **Headers (API):** `X-Content-Type-Options: nosniff`, `Cache-Control` as designed, `Referrer-Policy: no-referrer`.
- **Errors:** generic messages to clients, `request_id` for correlation, stack traces only in logs.
- **Ingestion SSRF/egress:** the client is hard-coded to the Elexon base URL; host allowlist asserted in code; TLS verification always on; timeouts on every request.
- **Resource limits:** max date range = window length; response sizes bounded by design (≤ a few thousand points).

## 3. Frontend controls

- **CSP (via `vercel.json` / nginx):**
  `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' <API_ORIGIN>; frame-ancestors 'none'; base-uri 'self'; form-action 'self'` (inline styles only if a charting lib requires it; remove otherwise).
- Other headers: `X-Content-Type-Options`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (camera/mic/geolocation off), HSTS (on host).
- No third-party scripts, analytics, or CDN fonts (fonts self-hosted).
- URL state parsed and validated (reject invalid dates/times, fall back to defaults) — never injected into the DOM unsanitised.

## 4. Containers

- Multi-stage builds; final images contain only runtime artefacts.
- **Non-root user**, read-only root filesystem where possible, `no-new-privileges`.
- Pinned base images (`python:3.12-slim`, `node:22-alpine`, `nginx:stable-alpine`) by tag + digest where practical.
- `.dockerignore` excludes `.git`, `node_modules`, `.env`, tests.
- Healthchecks defined in compose.

## 5. CI security gates

- `pip-audit` and `npm audit --omit=dev --audit-level=high` fail the build on high/critical.
- `gitleaks` (or equivalent) secret scan.
- Dependabot weekly for pip, npm, docker, github-actions.
- CodeQL (optional P2) for Python + JS.

## 6. Privacy and compliance

- No cookies, no PII, no tracking. A dark-mode preference may use `localStorage` (documented).
- Data attribution: contains data from Elexon BMRS; state the licence/terms in README and Methodology drawer (agent must check current Elexon data licence wording).

## 7. Security checklist (Definition of Done)

- [ ] No secrets in repo/history; `.env.example` only
- [ ] All inputs validated; fuzz test for query params passes
- [ ] DB opened read-only; test proves writes fail
- [ ] CSP + headers verified in deployed response (`curl -I`)
- [ ] Docker runs as non-root
- [ ] Audits clean (no high/critical)
- [ ] Repo, commits, README contain no personal identifiers
- [ ] CORS allowlist contains only the deployed frontend + localhost

## 8. Known limitations (state honestly in the review)

- No authentication: appropriate for public data, not for client-proprietary data. Production would add SSO/OIDC, audit logs, and per-tenant authorisation.
- Serverless platforms offer limited in-process rate limiting; rely on platform controls.
