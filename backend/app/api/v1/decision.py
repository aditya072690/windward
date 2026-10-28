from fastapi import APIRouter, Query
from ...services.decision import get_decision_forecast

router = APIRouter(tags=["decision"])


@router.get("/decision-forecast")
def decision_forecast(
    decision_date: str = Query(...),
    cutoff: str = Query("09:00"),
    view: str = Query("decision"),
):
    return get_decision_forecast(decision_date=decision_date, cutoff=cutoff, view=view)
