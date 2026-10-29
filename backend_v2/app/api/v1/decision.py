from fastapi import APIRouter, HTTPException
from ...config import settings
from ...services.data_service import ds
from ...domain.vintage import select_and_score_day
from ...domain.metrics import compute_mae_bias
from ...domain.timeutil import LONDON


router = APIRouter(tags=["decision"])


def _compute_summary(points):
    # compute summary in units expected
    errors = []
    peak_mw = None
    peak_time = None
    energy_mwh = 0.0
    for p in points:
        f = p.get("forecast_mw")
        a = p.get("actual_mw")
        if isinstance(f, (int, float)):
            if peak_mw is None or f > peak_mw:
                peak_mw = float(f)
                peak_time = p.get("start_time")
            energy_mwh += float(f) * 0.5  # half hour
        if isinstance(f, (int, float)) and isinstance(a, (int, float)):
            errors.append((float(f), float(a)))
    mae = sum(abs(f - a) for f, a in errors) / len(errors) if errors else None
    bias = sum(f - a for f, a in errors) / len(errors) if errors else None
    if mae is None or peak_mw is None or peak_mw == 0:
        acc = None
    else:
        acc = max(0.0, 100.0 - (mae / peak_mw) * 100.0)
    return {
        "peak_mw": peak_mw,
        "peak_time": peak_time,
        "mae_mw": round(mae, 6) if mae is not None else None,
        "bias_mw": round(bias, 6) if bias is not None else None,
        "accuracy_pct": round(acc, 3) if acc is not None else None,
        "energy_gwh": round(energy_mwh / 1000.0, 3),
        "n_scored": len(errors),
    }


@router.get("/decision-forecast")
def decision_forecast(decision_date: str, cutoff: str = "09:00", view: str = "decision"):
    try:
        # delivery day is decision_date + 1
        from datetime import date, timedelta
        ddate = (date.fromisoformat(decision_date) + timedelta(days=1)).isoformat()
        forecasts = ds.get_forecasts_for_period()
        actuals_list = ds.get_actuals_for_period()
        actuals = {a["start_time"]: a["generation_mw"] for a in actuals_list if a["settlement_date"] == ddate}
        points = select_and_score_day(decision_date, ddate, cutoff, forecasts, actuals)
        # add error_mw and horizon_h
        for p in points:
            f = p.get("forecast_mw")
            a = p.get("actual_mw")
            if isinstance(f, (int, float)) and isinstance(a, (int, float)):
                p["error_mw"] = float(f) - float(a)
            else:
                p["error_mw"] = None
            try:
                from datetime import datetime
                ps = p.get("publish_time")
                st = p.get("start_time")
                if ps and st:
                    pdt = datetime.fromisoformat(ps.replace("Z", "+00:00"))
                    sdt = datetime.fromisoformat(st.replace("Z", "+00:00"))
                    p["horizon_h"] = round((sdt - pdt).total_seconds() / 3600.0, 2)
                else:
                    p["horizon_h"] = None
            except Exception:
                p["horizon_h"] = None
        metrics = compute_mae_bias(points)
        summary = _compute_summary(points)
        return {"decision_date": decision_date, "delivery_date": ddate, "cutoff": cutoff, "view": view, "points": points, "summary": summary, **metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
