import sqlite3
from pathlib import Path


def test_snapshot_has_data():
    db_path = Path(__file__).parent.parent / "data" / "windward.db"
    assert db_path.exists()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM actual_wind")
    assert cur.fetchone()[0] >= 1000
    cur.execute("SELECT COUNT(*) FROM wind_forecast")
    assert cur.fetchone()[0] >= 100
    conn.close()
