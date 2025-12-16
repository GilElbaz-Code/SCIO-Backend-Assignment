from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised, dotenv-friendly configuration."""

    app_name: str = "SCiO Backend Exercise"
    api_v1_prefix: str = "/api/v1"
    api_key: str = Field(
        "changeme",
        description="Simple shared secret for X-API-KEY header "
                    "(obviously replace with real auth in prod).",
    )
    # Excel persistence (demo only)
    excel_path: str = "data/source.xlsx"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
