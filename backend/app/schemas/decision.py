from pydantic import BaseModel
from typing import List, Optional


class DecisionPoint(BaseModel):
    start_time: str
    forecast_mw: Optional[float] = None
    publish_time: Optional[str] = None
    horizon_h: Optional[float] = None
    actual_mw: Optional[float] = None
    error_mw: Optional[float] = None
    conservative_mw: Optional[float] = None


class DecisionSummary(BaseModel):
    mean_mw: float
    peak_mw: float
    peak_time: Optional[str] = None
    min_mw: float
    min_time: Optional[str] = None
    energy_gwh: float
    vintage_min: Optional[str] = None
    vintage_max: Optional[str] = None
    missing_points: int
    mae_mw: float = 0.0
    bias_mw: float = 0.0
    nmae: float = 0.0
    accuracy_pct: float = 0.0
    n_scored: int = 0


class DecisionRisk(BaseModel):
    p90_overforecast_mw: float = 0.0
    history_days: int = 0
    method: str = "walk_forward"


class DecisionForecastResponse(BaseModel):
    decision_date: str
    delivery_date: str
    cutoff_utc: Optional[str] = None
    view: str = "decision"
    points: List[DecisionPoint]
    summary: DecisionSummary
    risk: DecisionRisk
