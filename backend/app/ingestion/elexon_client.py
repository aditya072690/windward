import httpx
from typing import Any, List, Optional
import logging

logger = logging.getLogger("elexon")

WINDFOR_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"
FUELHH_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream"


class ElexonClient:
    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout, headers={"User-Agent": "Windward/1.0"})

    def _log_resp(self, url: str, resp: httpx.Response, data: List[dict[str, Any]]):
        try:
            publish_times = set()
            for r in data:
                pt = r.get("publishTime") or r.get("publish_date_time") or r.get("publishDateTime")
                if pt:
                    publish_times.add(pt)
            first = data[0] if data else None
            last = data[-1] if data else None
            logger.info(
                "elexon_request url=%s status=%s rows=%s distinct_publish_times=%s first=%s last=%s",
                url,
                resp.status_code,
                len(data),
                len(publish_times),
                first,
                last,
            )
            print(
                f"[ELEXON] {url} status={resp.status_code} rows={len(data)} distinct_publishTimes={len(publish_times)}"
            )
            if first is not None:
                print(f"[ELEXON] first={first}")
            if last is not None:
                print(f"[ELEXON] last={last}")
        except Exception as e:
            logger.exception("Failed to log elexon response: %s", e)

    def fetch_windfor(
        self,
        publish_date_time_from: Optional[str] = None,
        publish_date_time_to: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        params = {}
        if publish_date_time_from:
            params["publishDateTimeFrom"] = publish_date_time_from
        if publish_date_time_to:
            params["publishDateTimeTo"] = publish_date_time_to
        url = WINDFOR_URL
        r = self.client.get(url, params=params or None)
        try:
            r.raise_for_status()
        except Exception:
            # Do not swallow errors. Show status and message.
            msg = f"Elexon WINDFOR failed: status={r.status_code} body={r.text[:500]}"
            print(msg)
            raise
        data = r.json()
        self._log_resp(str(r.url), r, data)
        return data

    def fetch_fuelhh_wind(
        self,
        publish_date_time_from: Optional[str] = None,
        publish_date_time_to: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        params = {"fuelType": "WIND"}
        if publish_date_time_from:
            params["publishDateTimeFrom"] = publish_date_time_from
        if publish_date_time_to:
            params["publishDateTimeTo"] = publish_date_time_to
        url = FUELHH_URL
        r = self.client.get(url, params=params)
        try:
            r.raise_for_status()
        except Exception:
            msg = f"Elexon FUELHH failed: status={r.status_code} body={r.text[:500]}"
            print(msg)
            raise
        data = r.json()
        self._log_resp(str(r.url), r, data)
        return data

    def close(self):
        self.client.close()
