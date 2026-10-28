CREATE TABLE IF NOT EXISTS actual_wind (
  start_time        TEXT PRIMARY KEY,
  generation_mw     REAL NOT NULL CHECK (generation_mw >= 0),
  settlement_date   TEXT NOT NULL,
  settlement_period INTEGER NOT NULL CHECK (settlement_period BETWEEN 1 AND 50),
  ingested_at       TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS wind_forecast (
  start_time     TEXT NOT NULL,
  publish_time   TEXT NOT NULL,
  generation_mw  REAL NOT NULL CHECK (generation_mw >= 0),
  ingested_at    TEXT NOT NULL,
  PRIMARY KEY (start_time, publish_time)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_forecast_publish ON wind_forecast (publish_time);

CREATE TABLE IF NOT EXISTS ingest_runs (
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

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
) WITHOUT ROWID;
