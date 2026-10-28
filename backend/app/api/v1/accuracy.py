from fastapi import APIRouter, Query
from ...repository.db import get_conn
from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo
from ...core.time import decision_cutoff_to_utc, LONDON

router = APIRouter(tags=["accuracy"])

CUTOFFS = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]


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


def _day_bounds(decision_date: str):
    d0 = date.fromisoformat(decision_date)
    d1 = d0 + timedelta(days=1)
    return d1.isoformat(), f"{d1.isoformat()}T00:00:00Z", f"{(d1 + timedelta(days=1)).isoformat()}T00:00:00Z"


def _cutoff_utc(decision_date: str, cutoff: str | None):
    if cutoff is None:
        return None
    try:
        return decision_cutoff_to_utc(decision_date, cutoff).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def _load_window(start_date: str, end_date: str):
    s = date.fromisoformat(start_date)
    e = date.fromisoformat(end_date)
    win_start = f"{(s).isoformat()}T00:00:00Z"
    win_end = f"{(e + timedelta(days=3)).isoformat()}T00:00:00Z"

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT start_time, publish_time, generation_mw
        FROM wind_forecast
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time, publish_time
        """,
        (win_start, win_end),
    )
    forecasts = [dict(r) for r in cur.fetchall()]
    cur.execute(
        """
        SELECT start_time, generation_mw
        FROM actual_wind
        WHERE start_time >= ? AND start_time < ?
        ORDER BY start_time
        """,
        (win_start, win_end),
    )
    actuals = {r["start_time"]: float(r["generation_mw"]) for r in cur.fetchall() if r["generation_mw"] is not None}
    conn.close()
    # Normalise on load
    forecasts_sorted = sorted(forecasts, key=lambda x: (x["start_time"], x["publish_time"]))
    seen = set()
    forecasts_dedup = []
    for r in forecasts_sorted:
        key = (r["start_time"], r["publish_time"])
        if key in seen:
            continue
        seen.add(key)
        forecasts_dedup.append(r)
    return forecasts_dedup, actuals


def _select_vintage_expanded(forecasts, day_start: str, day_end: str, cutoff_utc):
    """
    Put forecasts on 48 half-hour grid.
    For each cutoff, pick per hourly startTime the latest WINDFOR record with publishTime <= cutoff.
    Expand to half-hours: slot HH:00 uses its hour's value. Slot HH:30 uses the linear interpolation
    between this hour and the next hour (fallback: carry the hour's value).
    """
    day_start_dt = datetime.fromisoformat(day_start.replace("Z", "+00:00"))
    day_end_dt = datetime.fromisoformat(day_end.replace("Z", "+00:00"))

    by_hour_pub = {}
    by_half = {}
    for r in forecasts:
        fst = datetime.fromisoformat(r["start_time"].replace("Z", "+00:00"))
        pt = r["publish_time"]
        if cutoff_utc is not None and pt > cutoff_utc:
            continue
        if fst.minute in (0, 30) and fst.second == 0:
            st_key = r["start_time"]
            cur = by_half.get(st_key)
            if cur is None or pt > cur["publish_time"]:
                by_half[st_key] = {"publish_time": pt, "generation_mw": float(r["generation_mw"])}
            continue
        hour_key = fst.replace(minute=0, second=0, microsecond=0).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cur = by_hour_pub.get(hour_key)
        if cur is None or pt > cur["publish_time"]:
            by_hour_pub[hour_key] = {"publish_time": pt, "generation_mw": float(r["generation_mw"])}

    chosen_by_slot = {}
    t = day_start_dt
    while t < day_end_dt:
        slot_start = t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        hour_start = t.replace(minute=0, second=0, microsecond=0).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        next_hour_start = (t.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        forecast_mw = None
        publish_time = None
        if slot_start in by_half:
            hrow = by_half[slot_start]
            forecast_mw = hrow["generation_mw"]
            publish_time = hrow["publish_time"]
        elif hour_start in by_hour_pub:
            hrow = by_hour_pub[hour_start]
            if t.minute == 0:
                forecast_mw = hrow["generation_mw"]
                publish_time = hrow["publish_time"]
            else:  # :30
                next_h = by_hour_pub.get(next_hour_start)
                if next_h is not None:
                    v0 = float(hrow["generation_mw"])
                    v1 = float(next_h["generation_mw"])
                    forecast_mw = v0 + (v1 - v0) * 0.5  # linear interpolation
                    publish_time = hrow["publish_time"] if hrow["publish_time"] >= next_h["publish_time"] else next_h["publish_time"]
                else:
                    forecast_mw = hrow["generation_mw"]  # fallback: carry the hour's value
                    publish_time = hrow["publish_time"]
        if forecast_mw is not None and not (isinstance(forecast_mw, float) and forecast_mw != forecast_mw):
            chosen_by_slot[slot_start] = {"generation_mw": forecast_mw, "publish_time": publish_time}
    return chosen_by_slot


def _score_expanded(decision_date: str, cutoff: str | None, forecasts, actuals):
    delivery_date, day_start, day_end = _day_bounds(decision_date)
    cutoff_utc = _cutoff_utc(decision_date, cutoff)
    chosen = _select_vintage_expanded(forecasts, day_start, day_end, cutoff_utc)

    slots = []
    t = datetime.fromisoformat(day_start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(day_end.replace("Z", "+00:00"))
    while t < end:
        slots.append(t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        t += timedelta(minutes=30)

    vintages = set()
    fc = []
    pairs = []
    for st in slots:
        row = chosen.get(st)
        if not row or row["generation_mw"] is None:
            continue
        fmw = float(row["generation_mw"])
        if isinstance(fmw, float) and fmw != fmw:  # NaN
            continue
        fc.append(fmw)
        if row.get("publish_time"):
            vintages.add(row["publish_time"])
        a = actuals.get(st)
        if a is not None and isinstance(a, (int, float)) and not (isinstance(a, float) and a != a):
            pairs.append((fmw, float(a)))

    if not fc:
        return {
            "vintage_min": None,
            "vintage_max": None,
            "mae_mw": None,
            "bias_mw": None,
            "peak_mw": None,
            "missing_points": len(slots) - len(fc),
            "n_scored": 0,
            "vintages_used": 0,
        }
    mae = sum(abs(f - a) for f, a in pairs) / len(pairs) if pairs else None
    bias = sum(f - a for f, a in pairs) / len(pairs) if pairs else None
    vintages_list = sorted(list(vintages))
    return {
        "vintage_min": vintages_list[0] if vintages_list else None,
        "vintage_max": vintages_list[-1] if vintages_list else None,
        "mae_mw": round(float(mae), 1) if mae is not None else None,
        "bias_mw": round(float(bias), 1) if bias is not None else None,
        "peak_mw": round(float(max(fc)), 1),
        "missing_points": len(slots) - len([s for s in slots if s in chosen and chosen[s].get("generation_mw") is not None]),
        "n_scored": len(pairs),
        "vintages_used": len(vintages),
    }


def _percentile(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    return float(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


@router.get("/accuracy/ledger")
def accuracy_ledger(decision_date: str = Query(...), view: str = Query("decision")):
    try:
        forecasts, actuals = _load_window(decision_date, decision_date)
        delivery_date = _day_bounds(decision_date)[0]
        if view == "latest":
            rows = [{"cutoff": "Latest", **_score_expanded(decision_date, None, forecasts, actuals)}]
        else:
            rows = [{"cutoff": c, **_score_expanded(decision_date, c, forecasts, actuals)} for c in CUTOFFS]
        return {"decision_date": decision_date, "delivery_date": delivery_date, "view": view, "rows": rows}
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/accuracy/by-hour")
def accuracy_by_hour(
    start: str = Query("2026-01-01"),
    end: str = Query("2026-01-31"),
    cutoff: str = Query("09:00"),
    view: str = Query("decision"),
):
    try:
        forecasts, actuals = _load_window(start, end)
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(exc))

    sums = [0.0] * 24
    counts = [0] * 24
    d = date.fromisoformat(start)
    last = date.fromisoformat(end)
    while d <= last:
        _, day_start, day_end = _day_bounds(d.isoformat())
        cutoff_utc = None if view == "latest" else _cutoff_utc(d.isoformat(), cutoff)
        chosen = _select_vintage_expanded(forecasts, day_start, day_end, cutoff_utc)
        for st, row in chosen.items():
            a = actuals.get(st)
            if a is None or row["generation_mw"] is None:
                continue
            try:
                dt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                local = dt.astimezone(LONDON).hour
            except Exception:
                continue
            sums[local] += float(row["generation_mw"]) - float(a)
            counts[local] += 1
        d += timedelta(days=1)

    return {
        "hours": [
            {"hour": h, "mean_signed_error_mw": round(sums[h] / counts[h], 1) if counts[h] else None, "count": counts[h]}
            for h in range(24)
        ]
    }


@router.get("/accuracy/by-horizon")
def accuracy_by_horizon(
    start: str = Query("2026-01-01"),
    end: str = Query("2026-01-31"),
    cutoff: str = Query("09:00"),
    view: str = Query("decision"),
    bucket_h: int = 3,
    max_h: int = 48,
):
    try:
        forecasts, actuals = _load_window(start, end)
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(exc))

    buckets = {}
    d = date.fromisoformat(start)
    last = date.fromisoformat(end)
    while d <= last:
        _, day_start, day_end = _day_bounds(d.isoformat())
        cutoff_utc = None if view == "latest" else _cutoff_utc(d.isoformat(), cutoff)
        chosen = _select_vintage_expanded(forecasts, day_start, day_end, cutoff_utc)
        for st, row in chosen.items():
            a = actuals.get(st)
            if a is None or row["generation_mw"] is None:
                continue
            try:
                pt = datetime.fromisoformat(str(row["publish_time"]).replace("Z", "+00:00"))
                sdt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                horizon_h = (sdt - pt).total_seconds() / 3600.0
            except Exception:
                continue
            if horizon_h < 0 or horizon_h > max_h:
                continue
            b = int(horizon_h // bucket_h) * bucket_h
            key = f"{b}-{b+bucket_h}h"
            err = abs(float(row["generation_mw"]) - float(a))
            buckets.setdefault(key, []).append(err)
        d += timedelta(days=1)

    out = []
    for b in range(0, max_h, bucket_h):
        key = f"{b}-{b+bucket_h}h"
        vals = sorted(buckets.get(key, []))
        out.append(
            {
                "bucket": key,
                "p50": round(_percentile(vals, 50), 1),
                "p90": round(_percentile(vals, 90), 1),
                "p95": round(_percentile(vals, 95), 1),
                "count": len(vals),
            }
        )
    return {"buckets": out}
