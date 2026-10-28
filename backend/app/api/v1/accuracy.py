from fastapi import APIRouter, Query
from ...repository.db import get_conn

router = APIRouter(tags=["accuracy"])


@router.get("/accuracy/daily")
def accuracy_daily(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00"), view: str = Query("decision")):
    # simplified
    return {"days": []}


@router.get("/accuracy/by-hour")
def accuracy_by_hour(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00"), view: str = Query("decision")):
    return {"hours": []}


@router.get("/accuracy/by-horizon")
def accuracy_by_horizon(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00"), bucket_h: int = 3, max_h: int = 48):
    return {"buckets": []}


@router.get("/accuracy/summary")
def accuracy_summary(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00"), view: str = Query("decision")):
    return {"mae": 0, "rmse": 0, "bias": 0, "nmae": 0, "mape": 0, "coverage": 0, "n": 0}


@router.get("/accuracy/distribution")
def accuracy_distribution(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00"), bin_mw: int = 250):
    return {"bins": [], "p50": 0, "p90": 0, "p95": 0}


@router.get("/accuracy/heatmap")
def accuracy_heatmap(start: str = Query("2026-01-01"), end: str = Query("2026-01-31"), cutoff: str = Query("09:00")):
    return {"matrix": []}


@router.get("/accuracy/ledger")
def accuracy_ledger(decision_date: str = Query(...)):
    # return 8 rows for cutoffs 00:00..21:00
    cutoffs = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    rows = []
    for c in cutoffs:
        rows.append({
            "cutoff": c,
            "vintage_min": None,
            "vintage_max": None,
            "mae_mw": None,
            "bias_mw": None,
            "peak_mw": None,
            "missing_points": None,
        })
    return {"decision_date": decision_date, "rows": rows}
