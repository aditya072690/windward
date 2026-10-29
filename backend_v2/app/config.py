from pydantic_settings import BaseSettings
from datetime import date, timedelta


class Settings(BaseSettings):
    period_start: str = "2026-08-29"
    period_end_exclusive: str = "2026-10-29"
    cache_dir: str = ".cache/elexon"
    ttl_seconds_new: int = 300
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    @property
    def delivery_day_min(self) -> str:
        return self.period_start

    @property
    def delivery_day_max(self) -> str:
        return (date.fromisoformat(self.period_end_exclusive) - timedelta(days=1)).isoformat()

    @property
    def decision_day_min(self) -> str:
        return (date.fromisoformat(self.delivery_day_min) - timedelta(days=1)).isoformat()

    @property
    def decision_day_max(self) -> str:
        return (date.fromisoformat(self.delivery_day_max) - timedelta(days=1)).isoformat()

    def cors_origins_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
