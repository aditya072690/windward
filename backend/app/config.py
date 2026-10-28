from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_path: str = "data/windward.db"
    decision_start: str = "2026-01-01"
    decision_end: str = "2026-01-31"
    default_cutoff: str = "09:00"
    mape_min_actual_mw: float = 50.0
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    log_level: str = "INFO"

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
