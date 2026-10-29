from datetime import datetime, timedelta, timezone
from .timeutil import london_day_bounds_utc, to_z, decision_cutoff_to_utc
import bisect


def _parse_z(s):
    if isinstance(s, str) and s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    dt = datetime.fromisoformat(str(s))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def select_and_score_day_fast(decision_date: str, delivery_date: str, cutoff: str, by_hour_idx: dict, by_half_idx: dict, actuals: dict):
    start_utc, end_utc = london_day_bounds_utc(delivery_date)
    if cutoff is None:
        cutoff_utc = None
    else:
        cutoff_utc = decision_cutoff_to_utc(decision_date, cutoff).strftime("%Y-%m-%dT%H:%M:%SZ")

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
        if slot_start in by_half_idx:
            lst = by_half_idx[slot_start]
            # find latest with pt <= cutoff_utc
            if cutoff_utc is None:
                pt, gen = lst[-1]
            else:
                # bisect
                # lst sorted by pt
                # find rightmost where pt <= cutoff_utc
                # simple loop is fast enough? or bisect
                left = 0
                right = len(lst)
                while left < right:
                    mid = (left + right) // 2
                    if lst[mid][0] <= cutoff_utc:
                        left = mid + 1
                    else:
                        right = mid
                if left == 0:
                    hrow = None
                else:
                    pt, gen = lst[left - 1]
                    forecast_mw = gen
                    publish_time = pt
            if forecast_mw is not None and publish_time is None and 'pt' in dir() and 'gen' in dir():
                pass  # already set above
        if forecast_mw is None and hour_start in by_hour_idx:
            lst = by_hour_idx[hour_start]
            if cutoff_utc is None:
                pt, gen = lst[-1]
                chosen = (pt, gen)
            else:
                left = 0
                right = len(lst)
                while left < right:
                    mid = (left + right) // 2
                    if lst[mid][0] <= cutoff_utc:
                        left = mid + 1
                    else:
                        right = mid
                if left == 0:
                    chosen = None
                else:
                    chosen = lst[left - 1]
            if chosen is not None:
                pt_h = chosen[0]
                gen_h = chosen[1]
                if slot_start_dt.minute == 0:
                    forecast_mw = gen_h
                    publish_time = pt_h
                else:
                    next_lst = by_hour_idx.get(next_hour_start)
                    if next_lst is not None:
                        # find chosen for next
                        if cutoff_utc is None:
                            chosen_n = next_lst[-1]
                        else:
                            left = 0
                            right = len(next_lst)
                            while left < right:
                                mid = (left + right) // 2
                                if next_lst[mid][0] <= cutoff_utc:
                                    left = mid + 1
                                else:
                                    right = mid
                            chosen_n = next_lst[left - 1] if left > 0 else None
                        if chosen_n is not None:
                            v0 = float(gen_h)
                            v1 = float(chosen_n[1])
                            forecast_mw = v0 + (v1 - v0) * 0.5
                            publish_time = pt_h if pt_h >= chosen_n[0] else chosen_n[0]
                        else:
                            forecast_mw = gen_h
                            publish_time = pt_h
                    else:
                        forecast_mw = gen_h
                        publish_time = pt_h

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
