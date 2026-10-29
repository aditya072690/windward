from typing import Protocol, List, Dict, Any


class DataSource(Protocol):
    def get_forecasts(self, publish_from: str, publish_to: str) -> List[Dict[str, Any]]:
        ...

    def get_actuals(self, settlement_from: str, settlement_to: str) -> List[Dict[str, Any]]:
        ...
