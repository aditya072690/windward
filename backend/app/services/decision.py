from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from ..repository.db import get_conn
from ..core.time import decision_cutoff_to_utc, LONDON


def get_decision_forecast(decision_date: str, cutoff: str = "09:00", view: str = "decision") -> Dict[str, Any]:
    # delivery day is decision_date + 1
    d0 = datetime.fromisoformat(decision_date).date()
    d1 = d0 + timedelta(days=1)
    delivery_date = d1.isoformat()
    day_start = f"{delivery_date}T00:00:00Z"
    day_end = f"{d1 + timedelta(days=1)}T00:00:00Z"
    
    conn = get_conn()
    cur = conn.cursor()
    
    if view == "latest":
        # For each half-hour, latest vintage published <= start_time
        cur.execute(
            """
            SELECT f.start_time, f.publish_time, f.generation_mw
            FROM wind_forecast AS f
            JOIN (
                SELECT start_time, MAX(publish_time) AS publish_time
                FROM wind_forecast
                WHERE start_time >= ? AND start_time < ?
                GROUP BY start_time
            ) AS latest
              ON latest.start_time = f.start_time AND latest.publish_time = f.publish_time
            ORDER BY f.start_time
            """,
            (day_start, day_end),
        )
        cutoff_utc = None
    else:
        cutoff_dt = decision_cutoff_to_utc(decision_date, cutoff)
        cutoff_utc = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        cur.execute(
            """
            SELECT f.start_time, f.publish_time, f.generation_mw
            FROM wind_forecast AS f
            JOIN (
                SELECT start_time, MAX(publish_time) AS publish_time
                FROM wind_forecast
                WHERE start_time >= ? AND start_time < ?
                  AND publish_time <= ?
                GROUP BY start_time
            ) AS latest
              ON latest.start_time = f.start_time AND latest.publish_time = f.publish_time
            ORDER BY f.start_time
            """,
            (day_start, day_end, cutoff_utc),
        )
    
    forecast_map = {row["start_time"]: row for row in cur.fetchall()}
    
    # Get actuals
    cur.execute(
        "SELECT start_time, generation_mw FROM actual_wind WHERE start_time >= ? AND start_time < ?",
        (day_start, day_end),
    )
    actual_map = {row["start_time"]: row["generation_mw"] for row in cur.fetchall()}
    conn.close()
    
    points = []
    vintage_times = []
    for i in range(48):
        start = (datetime.fromisoformat(day_start.replace('Z', '+00:00')) + timedelta(minutes=30 * i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        frow = forecast_map.get(start)
        forecast_mw = frow["generation_mw"] if frow else None
        publish_time = frow["publish_time"] if frow else None
        actual_mw = actual_map.get(start)
        if forecast_mw is not None and publish_time is not None and view == "decision" and cutoff_utc is not None:
            # compute horizon
            try:
                pt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                st = datetime.fromisoformat(start.replace('Z', '+00:00'))
                horizon_h = (st - pt).total_seconds() / 3600.0
            except Exception:
                horizon_h = None
            vintage_times.append(publish_time)
        elif forecast_mw is not None and publish_time is not None and view == "latest":
            try:
                pt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                st = datetime.fromisoformat(start.replace('Z', '+00:00'))
                horizon_h = (st - pt).total_seconds() / 3600.0
            except Exception:
                horizon_h = None
            vintage_times.append(publish_time)
        else:
            horizon_h = None
        if forecast_mw is not None and actual_mw is not None:
            error_mw = forecast_mw - actual_mw
        else:
            error_mw = None
        points.append({
            "start_time": start,
            "forecast_mw": forecast_mw,
            "publish_time": publish_time,
            "horizon_h": horizon_h,
            "actual_mw": actual_mw,
            "error_mw": error_mw,
            "conservative_mw": None,  # filled separately if needed
        })
    
    # summary
    forecasts = [p["forecast_mw"] for p in points if p["forecast_mw"] is not None]
    actuals_scored = [(p["forecast_mw"], p["actual_mw"]) for p in points if p["forecast_mw"] is not None and p["actual_mw"] is not None]
    missing = sum(1 for p in points if p["forecast_mw"] is None)
    if forecasts:
        mean_mw = sum(forecasts) / len(forecasts)
        peak_mw = max(forecasts)
        peak_idx = next(i for i, p in enumerate(points) if p["forecast_mw"] == peak_mw)
        peak_time = points[peak_idx]["start_time"]
        min_mw = min(forecasts)
        min_idx = next(i for i, p in enumerate(points) if p["forecast_mw"] == min_mw)
        min_time = points[min_idx]["start_time"]
        energy_gwh = (sum(forecasts) * 0.5) / 1000.0
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
