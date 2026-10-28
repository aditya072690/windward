from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(tags=["export"])


@router.get("/export/decision-forecast.csv")
def export_csv(decision_date: str = Query(...), cutoff: str = Query("09:00")):
    content = "start_time,forecast_mw,publish_time,horizon_h,actual_mw,error_mw\n"
    return Response(content=content, media_type="text/csv")
