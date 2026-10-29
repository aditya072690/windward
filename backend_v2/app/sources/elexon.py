import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import DataSource
from ..config import settings


WINDFOR_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"
FUELHH_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream"


def _iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


class ElexonSource(DataSource):
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        _ensure_dir(self.cache_dir)
        headers = {"Accept": "application/json", "User-Agent": "Windward/1.0"}
        self.client = httpx.Client(timeout=httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=10.0), headers=headers)

    def _cache_path(self, dataset: str, f: str, t: str) -> Path:
        return self.cache_dir / f"{dataset}_{f}_{t}.json"

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(6),
    )
    def _fetch(self, url: str, params: Dict[str, Any]):
        start = time.time()
        resp = self.client.get(url, params=params)
        dur = (time.time() - start) * 1000
        if resp.status_code == 429 or resp.status_code >= 500:
            raise httpx.HTTPStatusError(f"Retryable {resp.status_code}", request=resp.request, response=resp)
        if resp.status_code != 200:
            body = resp.text[:300]
            raise RuntimeError(f"Elexon request failed: status={resp.status_code} body={body}")
        ctype = resp.headers.get("content-type", "")
        if "json" not in ctype.lower():
            body = resp.text[:300]
            raise RuntimeError(f"Elexon non-json response: status={resp.status_code} content-type={ctype} body={body}")
        data = resp.json()
        if not isinstance(data, list):
            body = json.dumps(data)[:300]
            raise RuntimeError(f"Elexon unexpected response shape: {body}")
        print(f"[elexon] {url} {resp.status_code} rows={len(data)} bytes={len(resp.content)} duration_ms={dur:.1f}")
        return resp, data

    def get_forecasts(self, publish_from: str = None, publish_to: str = None) -> List[Dict[str, Any]]:
        # whole period first
        pf_start = datetime(2026, 8, 26, 0, 0, tzinfo=timezone.utc)
        pf_end = datetime(2026, 10, 29, 0, 0, tzinfo=timezone.utc)
        cp = self._cache_path("WINDFOR", _iso_z(pf_start).replace(":", ""), _iso_z(pf_end).replace(":", ""))
        if cp.exists():
            try:
                data = json.load(open(cp))
                return self._normalize_windfor(data)
            except Exception:
                pass
        try:
            params = {"publishDateTimeFrom": _iso_z(pf_start), "publishDateTimeTo": _iso_z(pf_end)}
            resp, data = self._fetch(WINDFOR_URL, params)
            try:
                _ensure_dir(cp)
                json.dump(data, open(cp, "w"))
            except Exception:
                pass
            return self._normalize_windfor(data)
        except Exception as e:
            body = str(e)
            if "status=400" in body:
                # chunk
                merged = []
                cur = pf_start
                chunk = timedelta(days=7)
                while cur < pf_end:
                    cend = min(cur + chunk, pf_end)
                    ccp = self._cache_path("WINDFOR", _iso_z(cur).replace(":", ""), _iso_z(cend).replace(":", ""))
                    if ccp.exists():
                        merged.extend(json.load(open(ccp)))
                    else:
                        try:
                            params = {"publishDateTimeFrom": _iso_z(cur), "publishDateTimeTo": _iso_z(cend)}
                            _, d2 = self._fetch(WINDFOR_URL, params)
                            json.dump(d2, open(ccp, "w"))
                            merged.extend(d2)
                        except Exception:
                            if chunk.days > 1:
                                chunk = timedelta(days=max(1, chunk.days // 2))
                                continue
                            raise
                    cur = cend
                return self._normalize_windfor(merged)
            raise

    def _normalize_windfor(self, data: List[Dict[str, Any]]):
        out = []
        seen = set()
        for r in data:
            try:
                st = r["startTime"]
                pt = r["publishTime"]
                gen = float(r["generation"])
                key = (st, pt)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"start_time": st, "publish_time": pt, "generation_mw": gen})
            except Exception:
                continue
        return out

    def get_actuals(self, settlement_from: str = None, settlement_to: str = None) -> List[Dict[str, Any]]:
        sf = settlement_from or settings.period_start
        st_to = settlement_to or settings.period_end_exclusive
        pf_start = datetime(2026, 8, 28, 22, 0, tzinfo=timezone.utc)
        pf_end = datetime(2026, 10, 29, 1, 0, tzinfo=timezone.utc)
        cp = self._cache_path("FUELHH", _iso_z(pf_start).replace(":", ""), _iso_z(pf_end).replace(":", ""))
        if cp.exists():
            try:
                data = json.load(open(cp))
            except Exception:
                data = None
        else:
            data = None
        if data is None:
            try:
                params = {"publishDateTimeFrom": _iso_z(pf_start), "publishDateTimeTo": _iso_z(pf_end), "fuelType": "WIND"}
                _, data = self._fetch(FUELHH_URL, params)
                try:
                    json.dump(data, open(cp, "w"))
                except Exception:
                    pass
            except Exception:
                merged = []
                cur = pf_start
                chunk = timedelta(days=7)
                while cur < pf_end:
                    cend = min(cur + chunk, pf_end)
                    ccp = self._cache_path("FUELHH", _iso_z(cur).replace(":", ""), _iso_z(cend).replace(":", ""))
                    if ccp.exists():
                        merged.extend(json.load(open(ccp)))
                    else:
                        try:
                            params = {"publishDateTimeFrom": _iso_z(cur), "publishDateTimeTo": _iso_z(cend), "fuelType": "WIND"}
                            _, d2 = self._fetch(FUELHH_URL, params)
                            json.dump(d2, open(ccp, "w"))
                            merged.extend(d2)
                        except Exception:
                            if chunk.days > 1:
                                chunk = timedelta(days=max(1, chunk.days // 2))
                                continue
                            raise
                    cur = cend
                data = merged
        return self._normalize_fuelhh(data, sf, st_to)

    def _normalize_fuelhh(self, data: List[Dict[str, Any]], sf: str, st_to: str):
        by_start = {}
        for r in data:
            try:
                st = r["startTime"]
                pt = r["publishTime"]
                sd = r.get("settlementDate")
                sp = r.get("settlementPeriod")
                gen = float(r["generation"])
                cur = by_start.get(st)
                if cur is None or pt > cur["publish_time"]:
                    by_start[st] = {"start_time": st, "publish_time": pt, "generation_mw": gen, "settlement_date": sd, "settlement_period": int(sp) if sp is not None else 0}
            except Exception:
                continue
        out = []
        for st, rec in by_start.items():
            sd = rec.get("settlement_date")
            if not sd:
                continue
            if sd < sf or sd >= st_to:
                continue
            out.append(rec)
        out.sort(key=lambda x: x["start_time"])
        return out
