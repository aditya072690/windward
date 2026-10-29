from fastapi import APIRouter, HTTPException
from datetime import date, timedelta
from ...services.data_service import ds
from ...domain.vintage import select_and_score_day
from ...domain.vintage_fast import select_and_score_day_fast
from ...domain.metrics import compute_mae_bias


router = APIRouter(tags=["accuracy"])


@router.get("/accuracy/ledger")
def ledger(decision_date: str = None, view: str = "decision", cutoff: str = None, delivery_date: str = None):
    try:
        from ...config import settings
        if decision_date is None and delivery_date is not None:
            decision_date = (date.fromisoformat(delivery_date) - timedelta(days=1)).isoformat()
        if decision_date is None:
            decision_date = settings.decision_day_max
        ddate = delivery_date or (date.fromisoformat(decision_date) + timedelta(days=1)).isoformat()
        ds.get_forecasts_for_period()
        ds.get_actuals_for_period()
        by_hour_idx = ds.get_forecasts_by_hour_indexed()
        by_half_idx = ds.get_forecasts_by_half_indexed()
        actuals = ds.get_actuals_by_date(ddate)
        cutoffs = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
        rows = []
        for c in cutoffs:
            points = select_and_score_day_fast(decision_date, ddate, c, by_hour_idx, by_half_idx, actuals)
            errors = []
            peak_mw = None
            vintage_list = []
            for p in points:
                f = p.get("forecast_mw")
                a = p.get("actual_mw")
                if isinstance(f, (int, float)):
                    if peak_mw is None or f > peak_mw:
                        peak_mw = float(f)
                if p.get("publish_time"):
                    vintage_list.append(p["publish_time"])
                if isinstance(f, (int, float)) and isinstance(a, (int, float)):
                    errors.append((float(f), float(a)))
            mae_mw = sum(abs(f - a) for f, a in errors) / len(errors) if errors else None
            bias_mw = sum(f - a for f, a in errors) / len(errors) if errors else None
            vintages_used = len(set(vintage_list)) if vintage_list else None
            row = {
                "cutoff": c,
                "decision_date": decision_date,
                "delivery_date": ddate,
                "vintages_used": vintages_used,
                "mae_mw": round(mae_mw, 6) if mae_mw is not None else None,
                "bias_mw": round(bias_mw, 6) if bias_mw is not None else None,
                "peak_mw": peak_mw,
                "coverage": len([p for p in points if p.get("forecast_mw") is not None]) / len(points) if points else 0,
            }
            rows.append(row)
        return {"rows": rows, "decision_date": decision_date, "delivery_date": ddate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accuracy/by-horizon")
def by_horizon(start: str = None, end: str = None, cutoff: str = "09:00", view: str = "decision"):
    try:
        from ...config import settings
        if start is None:
            start = settings.decision_day_min
        if end is None:
            end = settings.decision_day_max
        ds.get_forecasts_for_period()
        ds.get_actuals_for_period()
        by_hour_idx = ds.get_forecasts_by_hour_indexed()
        by_half_idx = ds.get_forecasts_by_half_indexed()
        bh = {}
        for i in range((date.fromisoformat(end) - date.fromisoformat(start)).days + 1):
            ddec = (date.fromisoformat(start) + timedelta(days=i)).isoformat()
            ddate = (date.fromisoformat(ddec) + timedelta(days=1)).isoformat()
            actuals = ds.get_actuals_by_date(ddate)
            points = select_and_score_day_fast(ddec, ddate, cutoff, by_hour_idx, by_half_idx, actuals)
            for p in points:
                try:
                    from datetime import datetime
                    ps = p.get("publish_time")
                    st = p.get("start_time")
                    if ps and st:
                        pdt = datetime.fromisoformat(ps.replace("Z", "+00:00"))
                        sdt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                        h = (sdt - pdt).total_seconds() / 3600.0
                        if h < 0 or h > 72:
                            continue
                        b = int(h)
                        f = p.get("forecast_mw")
                        a = p.get("actual_mw")
                        if isinstance(f, (int, float)) and isinstance(a, (int, float)):
                            if b not in bh:
                                bh[b] = []
                            bh[b].append(abs(float(f) - float(a)))
                except Exception:
                    continue
        buckets_res = []
        for b in range(0, 73):
            vals = bh.get(b, [])
            if not vals:
                continue
            vals_sorted = sorted(vals)
            n = len(vals_sorted)
            p50 = vals_sorted[int(n * 0.5)]
            p90 = vals_sorted[min(n - 1, int(n * 0.9))]
            p95 = vals_sorted[min(n - 1, int(n * 0.95))]
            buckets_res.append({"bucket": f"{b}h", "horizon_h": b, "p50": p50, "p90": p90, "p95": p95, "count": n})
        return {"buckets": buckets_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accuracy/by-hour")
def by_hour(start: str = None, end: str = None, cutoff: str = "09:00", view: str = "decision"):
    try:
        from ...config import settings
        if start is None:
            start = settings.decision_day_min
        if end is None:
            end = settings.decision_day_max
        ds.get_forecasts_for_period()
        ds.get_actuals_for_period()
        by_hour_idx = ds.get_forecasts_by_hour_indexed()
        by_half_idx = ds.get_forecasts_by_half_indexed()
        buckets = {}
        for i in range((date.fromisoformat(end) - date.fromisoformat(start)).days + 1):
            ddec = (date.fromisoformat(start) + timedelta(days=i)).isoformat()
            ddate = (date.fromisoformat(ddec) + timedelta(days=1)).isoformat()
            actuals = ds.get_actuals_by_date(ddate)
            points = select_and_score_day_fast(ddec, ddate, cutoff, by_hour_idx, by_half_idx, actuals)
            from ...domain.timeutil import LONDON
            from datetime import datetime
            for p in points:
                try:
                    dt = datetime.fromisoformat(p['start_time'].replace('Z', '+00:00'))
                    lh = dt.astimezone(LONDON).hour
                    key = lh
                    if key not in buckets:
                        buckets[key] = []
                    f = p.get("forecast_mw")
                    a = p.get("actual_mw")
                    if isinstance(f, (int, float)) and isinstance(a, (int, float)):
                        buckets[key].append(float(f) - float(a))
                except Exception:
                    continue
        hours_res = []
        for lh in range(0, 24):
            errs = buckets.get(lh, [])
            if not errs:
                continue
            mse = sum(errs) / len(errs)
            hours_res.append({"hour": lh, "hour_london": lh, "mean_signed_error_mw": mse, "mae_mw": sum(abs(x) for x in errs)/len(errs), "bias_mw": mse, "count": len(errs)})
        if len(hours_res) == 0:
            for lh, errs in buckets.items():
                if not errs: continue
                mse = sum(errs)/len(errs)
                hours_res.append({"hour": lh, "hour_london": lh, "mean_signed_error_mw": mse, "mae_mw": sum(abs(x) for x in errs)/len(errs), "bias_mw": mse, "count": len(errs)})
            hours_res.sort(key=lambda x: x['hour'])
        return {"hours": hours_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
