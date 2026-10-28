import sqlite3
from pathlib import Path
from ..config import settings


def get_conn() -> sqlite3.Connection:
    db_path = Path(settings.database_path)
    # Open read-only
    conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
