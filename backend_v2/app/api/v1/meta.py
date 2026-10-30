from fastapi import APIRouter, HTTPException
from ...config import settings
from ...services.data_service import ds


router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta():
    try:
        actuals = None
        forecasts = None
        try:
            actuals = ds.get_actuals_for_period()
        except Exception:
            actuals = None
        try:
            forecasts = ds.get_forecasts_for_period()
        except Exception:
            forecasts = None
        # Find latest settlement_date in actuals
        latest_date = None
        if actuals:
            dates = []
            for a in actuals:
                try:
                    dates.append(a["settlement_date"])
                except Exception:
                    continue
            if dates:
                latest_date = max(dates)
        delivery_max = latest_date or settings.delivery_day_max
        decision_max = None
        if delivery_max:
            from datetime import date, timedelta
            decision_max = (date.fromisoformat(delivery_max) - timedelta(days=1)).isoformat()
        delivery_min = settings.delivery_day_min
        decision_min = settings.decision_day_min
        return {
            "timezone": "Europe/London",
            "decision_window": [decision_min, decision_max or settings.decision_day_max],
            "delivery_day_min": delivery_min,
            "delivery_day_max": delivery_max,
            "period_start": settings.period_start,
            "period_end_exclusive": settings.period_end_exclusive,
            "data_as_of": delivery_max,
            "counts": {"actual_wind": len(actuals) if actuals is not None else None, "wind_forecast": len(forecasts) if forecasts is not None else None},
            "source": "Elexon BMRS live API",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
