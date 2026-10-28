import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any


def load_data(conn: sqlite3.Connection, actuals: List[Dict[str, Any]], forecasts: List[Dict[str, Any]]):
    cur = conn.cursor()
    ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for a in actuals:
        cur.execute(
            "INSERT OR REPLACE INTO actual_wind VALUES (?,?,?,?,?)",
            (a["start_time"], a["generation_mw"], a["settlement_date"], a["settlement_period"], ingested_at),
        )
    for f in forecasts:
        cur.execute(
            "INSERT OR IGNORE INTO wind_forecast VALUES (?,?,?,?)",
            (f["start_time"], f["publish_time"], f["generation_mw"], ingested_at),
        )
    conn.commit()
