from datetime import datetime, timedelta
from typing import Dict, Any
from ..sources.elexon import ElexonSource
from ..config import settings


class DataService:
    def __init__(self):
        self.src = ElexonSource(cache_dir=settings.cache_dir)
        self._forecasts_cache = None
        self._actuals_cache = None

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
        return self._forecasts_cache

    def get_actuals_for_period(self):
        if self._actuals_cache is None:
            self._actuals_cache = self.src.get_actuals(settings.period_start, settings.period_end_exclusive)
        return self._actuals_cache


ds = DataService()
