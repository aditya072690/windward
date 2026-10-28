from datetime import datetime, timezone
from typing import Any, Dict, List


def transform_windfor(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        try:
            start = row["startTime"]
            pub = row["publishTime"]
            gen = float(row["generation"])
            if gen < 0:
                continue
            out.append({"start_time": start, "publish_time": pub, "generation_mw": gen})
        except Exception:
            continue
    return out


def transform_fuelhh_wind(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        try:
            start = row["startTime"]
            gen = float(row["generation"])
            if gen < 0:
                continue
            out.append({
                "start_time": start,
                "generation_mw": gen,
                "settlement_date": row["settlementDate"],
                "settlement_period": int(row["settlementPeriod"]),
            })
        except Exception:
            continue
    return out
