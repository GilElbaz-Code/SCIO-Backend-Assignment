"""
API package: creates the FastAPI app, wires up lifespan
initialisation, and mounts the v1 router.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import router
from src.domain.services import AnalysisService
from src.infrastructure.repository import Database
from src.settings import get_settings

_cfg = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise DB + services once; tear down gracefully on shutdown."""
    db = Database(_cfg)
    app.state.analysis_service = AnalysisService(db=db)
    yield  # ---- application runs ----
    # Cleanup: close db pools, flush telemetry, etc.


app = FastAPI(
    title=_cfg.app_name,
    version="0.1.0",
    lifespan=lifespan,
    openapi_url=f"{_cfg.api_v1_prefix}/openapi.json",
)

app.include_router(router, prefix=_cfg.api_v1_prefix)  # /api/v1/...

__all__ = ["app"]
