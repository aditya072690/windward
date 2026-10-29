from datetime import datetime, timedelta, timezone
from .timeutil import london_day_bounds_utc, to_z, decision_cutoff_to_utc


def _parse_z(s):
    if isinstance(s, str) and s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    dt = datetime.fromisoformat(str(s))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def generate_slots(delivery_date: str):
    start_utc, end_utc = london_day_bounds_utc(delivery_date)
    slots = []
    t = start_utc
    while t < end_utc:
        slots.append(t)
        t += timedelta(minutes=30)
    return slots


def select_and_score_day(decision_date: str, delivery_date: str, cutoff: str, forecasts: list, actuals: dict):
    start_utc, end_utc = london_day_bounds_utc(delivery_date)
    if cutoff is None:
        cutoff_utc = None
    else:
        cutoff_utc = decision_cutoff_to_utc(decision_date, cutoff).strftime("%Y-%m-%dT%H:%M:%SZ")

    by_hour_pub = {}
    by_half = {}
    for r in forecasts:
        try:
            st = r["start_time"]
            pt = r["publish_time"]
            if cutoff_utc is not None and pt > cutoff_utc:
                continue
            fst = _parse_z(st)
            gen = float(r["generation_mw"])
            if fst.minute == 0 and fst.second == 0:
                hour_key = to_z(fst.replace(minute=0, second=0, microsecond=0))
                cur = by_hour_pub.get(hour_key)
                if cur is None or pt > cur["publish_time"]:
                    by_hour_pub[hour_key] = {"publish_time": pt, "generation_mw": gen}
            elif fst.minute in (0, 30) and fst.second == 0:
                cur = by_half.get(st)
                if cur is None or pt > cur["publish_time"]:
                    by_half[st] = {"publish_time": pt, "generation_mw": gen}
        except Exception:
            continue

    slots_dt = []
    t = start_utc
    while t < end_utc:
        slots_dt.append(t)
        t += timedelta(minutes=30)

    points = []
    for slot_start_dt in slots_dt:
        slot_start = to_z(slot_start_dt)
        hour_start = to_z(slot_start_dt.replace(minute=0, second=0, microsecond=0))
        next_hour_start = to_z((slot_start_dt.replace(minute=0, second=0, microsecond=0)) + timedelta(hours=1))
        forecast_mw = None
        publish_time = None
        if slot_start in by_half:
            hrow = by_half[slot_start]
            forecast_mw = hrow["generation_mw"]
            publish_time = hrow["publish_time"]
        elif hour_start in by_hour_pub:
            hrow = by_hour_pub[hour_start]
            if slot_start_dt.minute == 0:
                forecast_mw = hrow["generation_mw"]
                publish_time = hrow["publish_time"]
            else:
                next_h = by_hour_pub.get(next_hour_start)
                if next_h is not None:
                    v0 = float(hrow["generation_mw"])
                    v1 = float(next_h["generation_mw"])
                    forecast_mw = v0 + (v1 - v0) * 0.5
                    publish_time = hrow["publish_time"] if hrow["publish_time"] >= next_h["publish_time"] else next_h["publish_time"]
                else:
                    forecast_mw = hrow["generation_mw"]
                    publish_time = hrow["publish_time"]
        actual_mw = actuals.get(slot_start)
        if actual_mw is None or (isinstance(actual_mw, float) and actual_mw != actual_mw):
            actual_mw = None
        if forecast_mw is not None and isinstance(forecast_mw, float) and forecast_mw != forecast_mw:
            forecast_mw = None
        points.append({
            "start_time": slot_start,
            "forecast_mw": forecast_mw,
            "actual_mw": actual_mw,
            "publish_time": publish_time,
        })
    return points
