from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")


def to_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def london_day_bounds_utc(delivery_date: str):
    d = datetime.fromisoformat(delivery_date).date()
    start_local = datetime(d.year, d.month, d.day, 0, 0, tzinfo=LONDON)
    # London day is 00:00-00:00 local; but delivery starts at 23:00Z prev day in BST? 
    # We need slots covering the full London settlement day; per requirements slots every 30min from start to end giving 48 normally, 50 on 2026-10-25
    # Compute by iterating local day
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    # But actual slot start is often previous day 23:00Z on BST? Check: london day bounds as local midnight crossing gives correct count
    return start_utc, end_utc


def decision_cutoff_to_utc(decision_date: str, cutoff_hhmm: str):
    hh, mm = map(int, cutoff_hhmm.split(":"))
    d = datetime.fromisoformat(decision_date).date()
    local_dt = datetime(d.year, d.month, d.day, hh, mm, tzinfo=LONDON)
    return local_dt.astimezone(timezone.utc)
