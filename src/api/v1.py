from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_analysis_service
from src.domain.schemas import ReportRowOut
from src.domain.models import ScanReportRow
from src.domain.services import AnalysisService

router = APIRouter(tags=["Analysis"])


def _map_to_schema(row: ScanReportRow) -> ReportRowOut:
    """
    Helper: Maps the internal Domain Model to the external API DTO.
    Keeps API logic DRY (Don't Repeat Yourself).
    """
    return ReportRowOut(
        sampled_at=row.sampled_at,
        user_id=row.user_id,
        device_id=row.device_id,
        widget_name=row.widget_name,
        algo_name=row.algo_name,
        results=row.formatted_results,
    )


@router.get("/reports", response_model=list[ReportRowOut])
async def get_all_reports(
        svc: AnalysisService = Depends(get_analysis_service),
) -> list[ReportRowOut]:
    """Get all Scan Analysis Reports."""
    data = svc.get_scan_report()
    return [_map_to_schema(row) for row in data]


@router.get("/reports/by-user/{user_id}", response_model=list[ReportRowOut])
async def get_reports_by_user(
        user_id: str,
        svc: AnalysisService = Depends(get_analysis_service),
) -> list[ReportRowOut]:
    """Get Scan Analysis Reports filtered by user ID."""
    data = svc.get_scan_report(user_id=user_id)
    return [_map_to_schema(row) for row in data]


@router.get("/reports/by-device/{device_id}", response_model=list[ReportRowOut])
async def get_reports_by_device(
        device_id: str,
        svc: AnalysisService = Depends(get_analysis_service),
) -> list[ReportRowOut]:
    """Get Scan Analysis Reports filtered by device ID."""
    data = svc.get_scan_report(device_id=device_id)
    return [_map_to_schema(row) for row in data]


@router.get("/reports/by-date-range", response_model=list[ReportRowOut])
async def get_reports_by_date_range(
        from_date: Optional[datetime] = Query(None, description="Filter from (inclusive)"),
        to_date: Optional[datetime] = Query(None, description="Filter until (inclusive)"),
        svc: AnalysisService = Depends(get_analysis_service),
) -> list[ReportRowOut]:
    """Get Scan Analysis Reports filtered by date range."""
    data = svc.get_scan_report(from_date=from_date, to_date=to_date)
    return [_map_to_schema(row) for row in data]


@router.get("/reports/by-user-and-device", response_model=list[ReportRowOut])
async def get_reports_by_user_and_device(
        user_id: str = Query(..., description="Filter by user ID"),
        device_id: str = Query(..., description="Filter by device ID"),
        svc: AnalysisService = Depends(get_analysis_service),
) -> list[ReportRowOut]:
    """Get Scan Analysis Reports filtered by user and device."""
    data = svc.get_scan_report(user_id=user_id, device_id=device_id)
    return [_map_to_schema(row) for row in data]
