"""
api/v1.py – all v1 endpoints.
Only transport concerns live here (auth header, HTTP codes, paging).
Business logic comes from domain.services, persistence from
infrastructure.repository.  Services are injected via app.state.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.domain.schemas import ScanOut, ScanIn, ReportOut
from src.domain.services import ScanService, ReportService
from src.settings import Settings, get_settings

router = APIRouter(tags=["v1"])

# ------------------------------------------------------------------ #
# helpers – pull services from app.state
# ------------------------------------------------------------------ #
def _scan_svc(request: Request) -> ScanService:          # type: ignore
    return request.app.state.scan_service

def _report_svc(request: Request) -> ReportService:      # type: ignore
    return request.app.state.report_service

# ------------------------------------------------------------------ #
# edge-layer guard – API-key header
# ------------------------------------------------------------------ #
async def _require_key(
    x_api_key: Annotated[str, Header(alias="X-API-KEY")] = "",
    cfg: Settings = Depends(get_settings),
) -> None:
    if x_api_key != cfg.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

# ------------------------------------------------------------------ #
# routes
# ------------------------------------------------------------------ #
@router.post(
    "/scans",
    dependencies=[Depends(_require_key)],
    response_model=ScanOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_scan(payload: ScanIn, svc: ScanService = Depends(_scan_svc)):
    return svc.create_scan(content=payload.content, score=payload.score)


@router.get(
    "/scans",
    dependencies=[Depends(_require_key)],
    response_model=list[ScanOut],
)
async def list_scans(
    skip: int = 0,
    limit: int = 50,
    svc: ScanService = Depends(_scan_svc),
):
    return svc.list_scans(skip=skip, limit=limit)


@router.delete(
    "/scans/{scan_id}",
    dependencies=[Depends(_require_key)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scan(scan_id: int, svc: ScanService = Depends(_scan_svc)):
    svc.delete_scan(scan_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/reports",
    dependencies=[Depends(_require_key)],
    response_model=ReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    title: str,
    owner: str,
    svc: ReportService = Depends(_report_svc),
):
    return svc.create_report(title=title, owner=owner)
