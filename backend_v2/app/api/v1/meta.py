from fastapi import APIRouter, HTTPException
from ...config import settings
from ...services.data_service import ds


router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta():
    try:
        return {
            "timezone": "Europe/London",
            "decision_window": [settings.decision_day_min, settings.decision_day_max],
            "delivery_day_min": settings.delivery_day_min,
            "delivery_day_max": settings.delivery_day_max,
            "period_start": settings.period_start,
            "period_end_exclusive": settings.period_end_exclusive,
            "data_as_of": settings.delivery_day_max,
            "counts": {"actual_wind": len(ds.get_actuals_for_period()) if ds._actuals_cache is not None else None, "wind_forecast": len(ds.get_forecasts_for_period()) if ds._forecasts_cache is not None else None},
            "source": "Elexon BMRS live API",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
