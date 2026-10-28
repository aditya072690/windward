# DATABASE — Windward

## 1. Choice and rationale

**SQLite**, single file `backend/data/windward.db`.

- The dataset is **historical and immutable** (January 2026): ~1.5k actual rows and a few hundred thousand forecast rows at most.
- Opened **read-only** at runtime (`file:...?mode=ro`, `uri=True`) → no write path to attack, no connection pool, safe on serverless.
- Written only by the ingestion CLI. The validated file is committed to the repo so a reviewer can run everything offline.
- Scaling path (not built): PostgreSQL/TimescaleDB with the same logical schema.

## 2. Conventions

- Timestamps stored as **TEXT ISO-8601 UTC, second precision, `Z` suffix** (`2026-01-16T13:30:00Z`). Lexicographic order == chronological order, so range queries use the index directly.
- Power in **MW** as `REAL`.
- `PRAGMA foreign_keys=ON; PRAGMA journal_mode=OFF` for the read-only snapshot (WAL during ingestion only).
- Schema version tracked with `PRAGMA user_version`.

## 3. Schema (DDL)

```sql
-- Actual national wind generation (FUELHH, fuelType = WIND)
CREATE TABLE actual_wind (
  start_time        TEXT PRIMARY KEY,           -- target half-hour start, UTC
  generation_mw     REAL NOT NULL CHECK (generation_mw >= 0),
  settlement_date   TEXT NOT NULL,              -- YYYY-MM-DD (GB settlement day)
  settlement_period INTEGER NOT NULL CHECK (settlement_period BETWEEN 1 AND 50),
  ingested_at       TEXT NOT NULL
) WITHOUT ROWID;

-- Every published wind forecast vintage (WINDFOR)
CREATE TABLE wind_forecast (
  start_time     TEXT NOT NULL,                 -- target half-hour start, UTC
  publish_time   TEXT NOT NULL,                 -- when this vintage was created, UTC
  generation_mw  REAL NOT NULL CHECK (generation_mw >= 0),
  ingested_at    TEXT NOT NULL,
  PRIMARY KEY (start_time, publish_time)
) WITHOUT ROWID;

CREATE INDEX idx_forecast_publish ON wind_forecast (publish_time);

-- Provenance of the snapshot
CREATE TABLE ingest_runs (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at      TEXT NOT NULL,
  finished_at     TEXT,
  dataset         TEXT NOT NULL CHECK (dataset IN ('FUELHH','WINDFOR')),
  window_start    TEXT NOT NULL,
  window_end      TEXT NOT NULL,
  rows_fetched    INTEGER NOT NULL,
  rows_loaded     INTEGER NOT NULL,
  rows_rejected   INTEGER NOT NULL,
  source_url      TEXT NOT NULL,
  status          TEXT NOT NULL CHECK (status IN ('ok','failed'))
);

-- Single-row metadata
CREATE TABLE meta (
  key TEXT PRIMARY KEY, value TEXT NOT NULL      -- data_as_of, schema_version, source_note
) WITHOUT ROWID;
```

`WITHOUT ROWID` with the composite primary key already provides the covering index `(start_time, publish_time)` needed by the decision query.

## 4. Key queries

**Decision-time forecast (latest vintage ≤ cutoff, per target half-hour)**

```sql
SELECT f.start_time, f.publish_time, f.generation_mw
FROM wind_forecast AS f
JOIN (
  SELECT start_time, MAX(publish_time) AS publish_time
  FROM wind_forecast
  WHERE start_time >= :day_start
    AND start_time <  :day_end
    AND publish_time <= :cutoff_utc      -- inclusive boundary
  GROUP BY start_time
) AS latest
  ON latest.start_time = f.start_time
 AND latest.publish_time = f.publish_time
ORDER BY f.start_time;
```

**Range version** (accuracy over many days): the service calls the same query per delivery day with that day's cutoff (`decision_date @ HH:MM London → UTC`), or runs one query with a `VALUES`-derived cutoff table. Either way it must stay per-day-cutoff correct.

**All vintages for horizon analysis**

```sql
SELECT f.start_time, f.publish_time, f.generation_mw, a.generation_mw AS actual_mw
FROM wind_forecast f
JOIN actual_wind a USING (start_time)
WHERE f.start_time >= :start AND f.start_time < :end;
```

**Evolution for one target**

```sql
SELECT publish_time, generation_mw FROM wind_forecast
WHERE start_time = :target ORDER BY publish_time;
```

## 5. Ingestion contract

1. Verify endpoint/parameter names against the live Elexon BMRS OpenAPI document (do not hard-code from memory).
2. Fetch in **bounded date chunks** (e.g. 1–3 days) to respect API limits; retry with exponential backoff + jitter on 429/5xx; fail loudly otherwise.
3. Filter `fuelType == "WIND"` for FUELHH.
4. **Transform:** parse to UTC, round-trip validate, cast to float, drop exact duplicates, reject rows with null/negative generation (counted in `rows_rejected`, logged).
5. **Idempotent load:** `INSERT ... ON CONFLICT DO UPDATE` keyed on the primary keys. Re-running yields the same DB.
6. Write `ingest_runs` and `meta.data_as_of`.
7. Run the **integrity report** (below) and exit non-zero if a hard check fails.

**Fetch windows (defaults, verify):**
- FUELHH: target times `2026-01-02T00:00Z` → `2026-02-02T00:00Z`.
- WINDFOR: publish times from `2025-12-29T00:00Z` (long-horizon vintages for 2 Jan targets) → `2026-02-01T00:00Z`.

## 6. Data-quality checks (integrity report)

| Check | Severity |
|---|---|
| `actual_wind` has exactly 48 rows per delivery day for 2 Jan–1 Feb 2026 | hard |
| No duplicate PKs; all timestamps on :00/:30 | hard |
| Every delivery day has ≥ 1 forecast vintage ≤ 09:00 London on D-1 for ≥ 95 % of its half-hours | warn |
| `0 ≤ generation_mw ≤ 30000` (sanity upper bound) | hard |
| `publish_time < start_time` for ≥ 99 % of rows (forecast precedes target) | warn |
| Row counts + min/max timestamps printed and stored in `meta` | info |

The same checks run as a pytest (`test_snapshot_integrity`) against the committed DB.

## 7. Migrations

Tiny and explicit: `backend/app/repository/migrations/001_init.sql`, applied by the ingestion CLI when `user_version < 1`. No ORM, no Alembic — the schema is three tables and read-only in production.

## 8. Size and performance expectations

| Table | Rows (est.) | Notes |
|---|---|---|
| `actual_wind` | ≈ 1,500 | one per half-hour |
| `wind_forecast` | 10⁵ – 10⁶ | many vintages per target; fits comfortably in a few tens of MB |

Decision query touches ≤ 48 groups via the PK index → sub-10 ms. If the snapshot exceeds ~100 MB, keep only vintages with horizon ≤ 72 h and document it.

## 9. Backup and refresh

Snapshot is regenerated by `make ingest` (→ `python -m app.ingestion.cli --from 2025-12-29 --to 2026-02-02`). The committed file is the source of truth for the demo; the CLI output hash is logged in `ingest_runs`.
