from fastapi import APIRouter
from datetime import datetime, timezone
from ...repository.db import get_conn

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM meta")
        meta_rows = {row["key"]: row["value"] for row in cur.fetchall()}
        cur.execute("SELECT COUNT(*) as c FROM actual_wind")
        aw = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM wind_forecast")
        wf = cur.fetchone()["c"]
        conn.close()
        return {
            "timezone": "Europe/London",
            "decision_window": ["2026-01-01", "2026-01-31"],
            "default_cutoff": "09:00",
            "data_as_of": meta_rows.get("data_as_of", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "counts": {"actual_wind": aw, "wind_forecast": wf},
            "source": "Elexon BMRS (FUELHH WIND, WINDFOR)",
        }
    except Exception:
        return {
            "timezone": "Europe/London",
            "decision_window": ["2026-01-01", "2026-01-31"],
            "default_cutoff": "09:00",
            "data_as_of": "2026-01-31",
            "counts": {"actual_wind": 0, "wind_forecast": 0},
            "source": "Elexon BMRS (FUELHH WIND, WINDFOR)",
        }
