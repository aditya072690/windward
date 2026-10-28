import httpx
from typing import Any, List


WINDFOR_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"
FUELHH_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream"


class ElexonClient:
    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout, headers={"User-Agent": "Windward/1.0"})

    def fetch_windfor(self) -> List[dict[str, Any]]:
        r = self.client.get(WINDFOR_URL)
        r.raise_for_status()
        return r.json()

    def fetch_fuelhh_wind(self) -> List[dict[str, Any]]:
        r = self.client.get(FUELHH_URL, params={"fuelType": "WIND"})
        r.raise_for_status()
        return r.json()

    def close(self):
        self.client.close()
