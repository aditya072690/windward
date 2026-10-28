from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")


def parse_hhmm(hhmm: str) -> tuple[int, int]:
    h, m = hhmm.split(":")
    return int(h), int(m)


def decision_cutoff_to_utc(decision_date: str, cutoff: str) -> datetime:
    h, m = parse_hhmm(cutoff)
    # decision_date is YYYY-MM-DD in London
    dt_london = datetime.fromisoformat(f"{decision_date}T{h:02d}:{m:02d}:00").replace(tzinfo=LONDON)
    return dt_london.astimezone(timezone.utc)
