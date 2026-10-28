from fastapi import APIRouter, Query

router = APIRouter(tags=["evolution"])


@router.get("/forecast-evolution")
def forecast_evolution(target_time: str = Query(...)):
    return {"target_time": target_time, "vintages": [], "actual_mw": None}
