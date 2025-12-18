from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised, env-driven configuration."""

    app_name: str = "SCiO Backend Exercise"
    api_v1_prefix: str = "/api/v1"

    # Data paths (assumes files live under ./data)
    data_dir: Path = Path("data")

    @property
    def widget_data_path(self) -> Path:
        return self.data_dir / "Widget data.xlsx"

    @property
    def algo_data_path(self) -> Path:
        return self.data_dir / "Algo data.xlsx"

    @property
    def scan_data_path(self) -> Path:
        return self.data_dir / "Scan data.xlsx"

    @property
    def scan_results_path(self) -> Path:
        return self.data_dir / "Scan Results data.xlsx"

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so the app only parses env once."""
    return Settings()
