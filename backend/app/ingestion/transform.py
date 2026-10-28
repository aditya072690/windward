from datetime import datetime, timezone
from typing import Any, Dict, List


def _parse_iso_z(s: str) -> datetime:
    # Parse UTC ISO strings
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        raise


def _to_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def transform_windfor(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        try:
            start = row.get("startTime") or row.get("start_time") or row.get("settlementDate") and None
            # BMRS typically uses startTime
            start = row.get("startTime") or row.get("start_time")
            pub = row.get("publishTime") or row.get("publish_time") or row.get("publishDateTime")
            gen = row.get("generation") if "generation" in row else row.get("generation_mw") or row.get("quantity")
            if start is None or pub is None or gen is None:
                continue
            gen_f = float(gen)
            if gen_f < 0:
                continue
            # Normalise times as UTC ISO strings
            start_dt = _parse_iso_z(str(start))
            pub_dt = _parse_iso_z(str(pub))
            out.append(
                {
                    "start_time": _to_z(start_dt),
                    "publish_time": _to_z(pub_dt),
                    "generation_mw": gen_f,
                }
            )
        except Exception:
            continue
    # Dedupe by startTime+publishTime (keep as-is after normalisation)
    seen = set()
    deduped = []
    for r in out:
        key = (r["start_time"], r["publish_time"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    # Sort for determinism
    deduped.sort(key=lambda x: (x["start_time"], x["publish_time"]))
    return deduped


def transform_fuelhh_wind(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        try:
            start = row.get("startTime") or row.get("start_time")
            gen = row.get("generation") if "generation" in row else row.get("generation_mw") or row.get("quantity")
            if start is None or gen is None:
                continue
            gen_f = float(gen)
            if gen_f < 0:
                continue
            start_dt = _parse_iso_z(str(start))
            pub = row.get("publishTime") or row.get("publish_time") or row.get("publishDateTime")
            pub_dt = _parse_iso_z(str(pub)) if pub is not None else start_dt
            out.append(
                {
                    "start_time": _to_z(start_dt),
                    "publish_time": _to_z(pub_dt),
                    "generation_mw": gen_f,
                    "settlement_date": row.get("settlementDate") or row.get("settlement_date"),
                    "settlement_period": int(row.get("settlementPeriod") or row.get("settlement_period") or 0),
                }
            )
        except Exception:
            continue
    # Sort FUELHH ascending by startTime
    out.sort(key=lambda x: (x["start_time"], x["publish_time"]))
    # Dedupe FUELHH by startTime keeping the latest publishTime
    by_start = {}
    for r in out:
        st = r["start_time"]
        cur = by_start.get(st)
        if cur is None or r["publish_time"] > cur["publish_time"]:
            by_start[st] = r
        elif r["publish_time"] == cur["publish_time"] and r["generation_mw"] != cur["generation_mw"]:
            by_start[st] = r
    deduped = list(by_start.values())
    deduped.sort(key=lambda x: x["start_time"])
    return deduped
