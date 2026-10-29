from datetime import datetime, timedelta
from typing import Dict, Any
from ..sources.elexon import ElexonSource
from ..config import settings
from functools import lru_cache


class DataService:
    def __init__(self):
        self.src = ElexonSource(cache_dir=settings.cache_dir)
        self._forecasts_cache = None
        self._actuals_cache = None
        self._forecasts_by_hour_cache = None  # pre-indexed
        self._forecasts_by_half_cache = None
        self._actuals_by_date_cache = None

    def warm(self):
        # try to load all
        try:
            self._forecasts_cache = self.src.get_forecasts()
        except Exception as e:
            raise
        try:
            self._actuals_cache = self.src.get_actuals(settings.period_start, settings.period_end_exclusive)
        except Exception as e:
            raise
        # build indexes
        self._build_indexes()
        # check
        if len(self._actuals_cache) != 2930:
            raise RuntimeError(f"FUELHH filtered count {len(self._actuals_cache)} != 2930")
        # check days
        from collections import Counter
        c = Counter(r["settlement_date"] for r in self._actuals_cache)
        bad = []
        for d in self._date_range(settings.period_start, settings.delivery_day_max):
            exp = 50 if d == "2026-10-25" else 48
            if c.get(d, 0) != exp:
                bad.append((d, c.get(d, 0), exp))
        if bad:
            raise RuntimeError(f"Bad day counts: {bad}")

    def _build_indexes(self):
        from ..domain.vintage import _parse_z, to_z
        forecasts = self._forecasts_cache or []
        # index by (hour_key) -> list of (publish_time, generation_mw)
        by_hour = {}
        by_half = {}
        for r in forecasts:
            try:
                st = r["start_time"]
                pt = r["publish_time"]
                fst = _parse_z(st)
                gen = float(r["generation_mw"])
                if fst.minute == 0 and fst.second == 0:
                    hour_key = to_z(fst.replace(minute=0, second=0, microsecond=0))
                    if hour_key not in by_hour:
                        by_hour[hour_key] = []
                    by_hour[hour_key].append((pt, gen))
                elif fst.minute in (0, 30) and fst.second == 0:
                    if st not in by_half:
                        by_half[st] = []
                    by_half[st].append((pt, gen))
            except Exception:
                continue
        # sort each list by publish time
        for k in by_hour:
            by_hour[k].sort(key=lambda x: x[0])
        for k in by_half:
            by_half[k].sort(key=lambda x: x[0])
        self._forecasts_by_hour_cache = by_hour
        self._forecasts_by_half_cache = by_half
        # index actuals by date
        actuals = self._actuals_cache or []
        by_date = {}
        for a in actuals:
            sd = a["settlement_date"]
            if sd not in by_date:
                by_date[sd] = {}
            by_date[sd][a["start_time"]] = a["generation_mw"]
        self._actuals_by_date_cache = by_date

    def _date_range(self, s, e):
        d0 = datetime.fromisoformat(s).date()
        d1 = datetime.fromisoformat(e).date()
        res = []
        cur = d0
        while cur <= d1:
            res.append(cur.isoformat())
            cur += timedelta(days=1)
        return res

    def get_forecasts_for_period(self):
        if self._forecasts_cache is None:
            self._forecasts_cache = self.src.get_forecasts()
        if self._forecasts_by_hour_cache is None:
            self._build_indexes()
        return self._forecasts_cache

    def get_actuals_for_period(self):
        if self._actuals_cache is None:
            self._actuals_cache = self.src.get_actuals(settings.period_start, settings.period_end_exclusive)
        if self._actuals_by_date_cache is None:
            self._build_indexes()
        return self._actuals_cache

    def get_actuals_by_date(self, settlement_date: str):
        if self._actuals_by_date_cache is None:
            self.get_actuals_for_period()
        return self._actuals_by_date_cache.get(settlement_date, {})

    def get_forecasts_by_hour_indexed(self):
        if self._forecasts_by_hour_cache is None:
            self.get_forecasts_for_period()
        return self._forecasts_by_hour_cache

    def get_forecasts_by_half_indexed(self):
        if self._forecasts_by_half_cache is None:
            self.get_forecasts_for_period()
        return self._forecasts_by_half_cache


ds = DataService()
