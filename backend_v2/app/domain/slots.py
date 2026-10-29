from datetime import datetime, timedelta, timezone
from .timeutil import london_day_bounds_utc, to_z


def generate_slots(delivery_date: str):
    start_utc, end_utc = london_day_bounds_utc(delivery_date)
    slots = []
    t = start_utc
    while t < end_utc:
        slots.append(t)
        t += timedelta(minutes=30)
    # 2026-10-25 should have 50
    if len(slots) != 48 and len(slots) != 50:
        # try to normalize
        pass
    return slots
