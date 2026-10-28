from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo
from ..repository.db import get_conn
from ..core.time import decision_cutoff_to_utc, LONDON


def _parse_z(s: str) -> datetime:
    if s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _to_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_decision_forecast(decision_date: str, cutoff: str = "09:00", view: str = "decision") -> Dict[str, Any]:
    # delivery day is decision_date + 1
    d0 = datetime.fromisoformat(decision_date).date()
    d1 = d0 + timedelta(days=1)
    delivery_date = d1.isoformat()
    day_start = f"{delivery_date}T00:00:00Z"
    day_end = f"{d1 + timedelta(days=1)}T00:00:00Z"

    conn = get_conn()
    cur = conn.cursor()

    # Load all forecasts for the window (will be normalized/expanded in memory)
    cur.execute(
        """
        SELECT start_time, publish_time, generation_mw
        FROM wind_forecast
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time, publish_time
        """,
        (f"{(d0).isoformat()}T00:00:00Z", f"{(d1 + timedelta(days=2)).isoformat()}T00:00:00Z"),
    )
    forecast_rows = [dict(r) for r in cur.fetchall()]

    if view == "latest":
        cutoff_utc = None
    else:
        cutoff_dt = decision_cutoff_to_utc(decision_date, cutoff)
        cutoff_utc = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get actuals for delivery day
    cur.execute(
        "SELECT start_time, generation_mw FROM actual_wind WHERE start_time >= ? AND start_time < ? ORDER BY start_time",
        (day_start, day_end),
    )
    actual_map = {row["start_time"]: float(row["generation_mw"]) for row in cur.fetchall() if row["generation_mw"] is not None}
    conn.close()

    # Build forecast map on 48 half-hour grid for delivery day
    # If forecasts are hourly, expand: HH:00 uses hour HH value; HH:30 interpolates between HH and HH+1 (linear)
    delivery_start_dt = _parse_z(day_start)
    # Load hourly candidates if any
    points = []
    vintage_times = []

    # Try to detect: group forecasts by hour start
    # Get all forecast candidates for delivery day window
    candidates_by_hour = {}  # hour_start -> list of (publish_time, gen_mw)
    for r in forecast_rows:
        st = r["start_time"]
        # consider any forecast that could apply? we need per cutoff selection
        pass

    # Better approach: build per (hour_start, publish_time) and also per half-hour; support both
    # Collect all hourly and half-hourly
    all_fc = []
    for r in forecast_rows:
        try:
            all_fc.append(
                {
                    "start_time": r["start_time"],
                    "publish_time": r["publish_time"],
                    "generation_mw": float(r["generation_mw"]),
                }
            )
        except Exception:
            continue

    def select_for_cutoff(cutoff_utc_str: Optional[str]):
        # For each hourly startTime pick latest with publishTime <= cutoff
        # build index by hour bucket (truncate to hour)
        by_hour_pub = {}
        for f in all_fc:
            fst = _parse_z(f["start_time"])
            # check if it's on hour or half-hour
            is_hour = fst.minute == 0 and fst.second == 0
            hour_key = _to_z(fst.replace(minute=0, second=0, microsecond=0)) if (not is_hour or True) else f["start_time"]
            # treat as hourly source if minute==0? or just use hour bucket
            key = hour_key
            pt = f["publish_time"]
            if cutoff_utc_str is not None and pt > cutoff_utc_str:
                continue
            cur = by_hour_pub.get(key)
            if cur is None or pt > cur["publish_time"]:
                by_hour_pub[key] = {"publish_time": pt, "generation_mw": f["generation_mw"], "hour_start": key}
        # also check half-hourly direct
        by_half = {}
        for f in all_fc:
            fst = _parse_z(f["start_time"])
            if fst.minute in (0, 30) and fst.second == 0:  # half-hourly grid
                st_key = f["start_time"]
                pt = f["publish_time"]
                if cutoff_utc_str is not None and pt > cutoff_utc_str:
                    continue
                cur = by_half.get(st_key)
                if cur is None or pt > cur["publish_time"]:
                    by_half[st_key] = {"publish_time": pt, "generation_mw": f["generation_mw"]}
        return by_hour_pub, by_half

    by_hour_pub, by_half = select_for_cutoff(cutoff_utc)

    # Generate 48 half-hour slots for delivery day
    for i in range(48):
        slot_start_dt = delivery_start_dt + timedelta(minutes=30 * i)
        slot_start = _to_z(slot_start_dt)
        hour_start = _to_z(slot_start_dt.replace(minute=0, second=0, microsecond=0))
        next_hour_start = _to_z((slot_start_dt.replace(minute=0, second=0, microsecond=0)) + timedelta(hours=1))

        forecast_mw = None
        publish_time = None
        horizon_h = None

        # Prefer half-hourly direct match if exists
        if slot_start in by_half:
            hrow = by_half[slot_start]
            forecast_mw = hrow["generation_mw"]
            publish_time = hrow["publish_time"]
        elif hour_start in by_hour_pub:
            # Expansion: slot HH:00 uses its hour's value. Slot HH:30 uses linear interpolation between this hour and next hour
            hrow = by_hour_pub[hour_start]
            if slot_start_dt.minute == 0:
                forecast_mw = hrow["generation_mw"]
                publish_time = hrow["publish_time"]
            else:  # :30 - interpolate between this hour and next hour
                next_h = by_hour_pub.get(next_hour_start)
                if next_h is not None:
                    # linear interpolation
                    v0 = float(hrow["generation_mw"])
                    v1 = float(next_h["generation_mw"])
                    forecast_mw = v0 + (v1 - v0) * 0.5
                    # use the later/latest publish time relevant to this slot? or the hour's publish time
                    publish_time = hrow["publish_time"] if hrow["publish_time"] >= next_h["publish_time"] else next_h["publish_time"]
                else:
                    # fallback: carry the hour's value
                    forecast_mw = hrow["generation_mw"]
                    publish_time = hrow["publish_time"]
        else:
            forecast_mw = None
            publish_time = None

        if forecast_mw is not None and publish_time is not None:
            try:
                pt = _parse_z(publish_time)
                st = _parse_z(slot_start)
                horizon_h = (st - pt).total_seconds() / 3600.0
            except Exception:
                horizon_h = None
            vintage_times.append(publish_time)
        else:
            horizon_h = None

        actual_mw = actual_map.get(slot_start)
        if forecast_mw is not None and actual_mw is not None and isinstance(forecast_mw, (int, float)) and isinstance(actual_mw, (int, float)):
            error_mw = float(forecast_mw) - float(actual_mw)
        else:
            error_mw = None

        # Never pass NaN or undefined to the chart
        if isinstance(forecast_mw, float) and (forecast_mw != forecast_mw):
            forecast_mw = None
        if isinstance(actual_mw, float) and (actual_mw != actual_mw):
            actual_mw = None
        if isinstance(error_mw, float) and (error_mw != error_mw):
            error_mw = None

        points.append(
            {
                "start_time": slot_start,
                "forecast_mw": forecast_mw,
                "publish_time": publish_time,
                "horizon_h": horizon_h,
                "actual_mw": actual_mw,
                "error_mw": error_mw,
                "conservative_mw": None,
            }
        )

    # summary
    forecasts_vals = [p["forecast_mw"] for p in points if p["forecast_mw"] is not None and isinstance(p["forecast_mw"], (int, float))]
    actuals_scored = [(p["forecast_mw"], p["actual_mw"]) for p in points if p["forecast_mw"] is not None and p["actual_mw"] is not None and isinstance(p["forecast_mw"], (int, float)) and isinstance(p["actual_mw"], (int, float))]
    missing = sum(1 for p in points if p["forecast_mw"] is None)
    if forecasts_vals:
        mean_mw = sum(forecasts_vals) / len(forecasts_vals)
        peak_mw = max(forecasts_vals)
        peak_idx = next(i for i, p in enumerate(points) if p["forecast_mw"] == peak_mw)
        peak_time = points[peak_idx]["start_time"]
        min_mw = min(forecasts_vals)
        min_idx = next(i for i, p in enumerate(points) if p["forecast_mw"] == min_mw)
        min_time = points[min_idx]["start_time"]
        energy_gwh = (sum(forecasts_vals) * 0.5) / 1000.0
    else:
        mean_mw = peak_mw = min_mw = energy_gwh = 0.0
        peak_time = min_time = None
    if actuals_scored:
        mae_mw = sum(abs(f - a) for f, a in actuals_scored) / len(actuals_scored)
        bias_mw = sum(f - a for f, a in actuals_scored) / len(actuals_scored)
        mean_actual = sum(a for _, a in actuals_scored) / len(actuals_scored)
        nmae = (mae_mw / mean_actual) if mean_actual > 0 else 0.0
        accuracy_pct = max(0.0, 100.0 - nmae * 100.0)
        n_scored = len(actuals_scored)
    else:
        mae_mw = bias_mw = nmae = accuracy_pct = 0.0
        n_scored = 0
    summary = {
        "mean_mw": round(mean_mw, 1),
        "peak_mw": round(peak_mw, 1),
        "peak_time": peak_time,
        "min_mw": round(min_mw, 1),
        "min_time": min_time,
        "energy_gwh": round(energy_gwh, 1),
        "vintage_min": min(vintage_times) if vintage_times else None,
        "vintage_max": max(vintage_times) if vintage_times else None,
        "missing_points": missing,
        "mae_mw": round(mae_mw, 1),
        "bias_mw": round(bias_mw, 1),
        "nmae": round(nmae, 6),
        "accuracy_pct": round(accuracy_pct, 1),
        "n_scored": n_scored,
    }
    return {
        "decision_date": decision_date,
        "delivery_date": delivery_date,
        "cutoff_utc": cutoff_utc,
        "view": view,
        "points": points,
        "summary": summary,
        "risk": {"p90_overforecast_mw": 0.0, "history_days": 0, "method": "walk_forward"},
    }
