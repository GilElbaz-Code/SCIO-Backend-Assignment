from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_analysis_service
from src.domain.schemas import ReportRowOut
from src.domain.services import AnalysisService

router = APIRouter(tags=["Analysis"])


@router.get("/reports", response_model=list[ReportRowOut])
async def get_all_reports(
        svc: AnalysisService = Depends(dependency=get_analysis_service),
) -> list[ReportRowOut]:
    """
    Get all Scan Analysis Reports.

    Returns:
        List of all scan report rows with formatted results
    """
    data = svc.get_scan_report()

    return [
        ReportRowOut(
            sampled_at=row.sampled_at,
            user_id=row.user_id,
            device_id=row.device_id,
            widget_name=row.widget_name,
            algo_name=row.algo_name,
            results=row.formatted_results,
        )
        for row in data
    ]


@router.get("/reports/by-user/{user_id}", response_model=list[ReportRowOut])
async def get_reports_by_user(
        user_id: str,
        svc: AnalysisService = Depends(dependency=get_analysis_service),
) -> list[ReportRowOut]:
    """
    Get Scan Analysis Reports filtered by user ID.

    Path Parameters:
        - user_id: The user ID to filter by

    Returns:
        List of scan report rows for the specified user
    """
    data = svc.get_scan_report(user_id=user_id)

    return [
        ReportRowOut(
            sampled_at=row.sampled_at,
            user_id=row.user_id,
            device_id=row.device_id,
            widget_name=row.widget_name,
            algo_name=row.algo_name,
            results=row.formatted_results,
        )
        for row in data
    ]


@router.get("/reports/by-device/{device_id}", response_model=list[ReportRowOut])
async def get_reports_by_device(
        device_id: str,
        svc: AnalysisService = Depends(dependency=get_analysis_service),
) -> list[ReportRowOut]:
    """
    Get Scan Analysis Reports filtered by device ID.

    Path Parameters:
        - device_id: The device ID to filter by

    Returns:
        List of scan report rows for the specified device
    """
    data = svc.get_scan_report(device_id=device_id)

    return [
        ReportRowOut(
            sampled_at=row.sampled_at,
            user_id=row.user_id,
            device_id=row.device_id,
            widget_name=row.widget_name,
            algo_name=row.algo_name,
            results=row.formatted_results,
        )
        for row in data
    ]


@router.get("/reports/by-date-range", response_model=list[ReportRowOut])
async def get_reports_by_date_range(
        from_date: Optional[datetime] = Query(None, description="Filter scans from this datetime (inclusive)"),
        to_date: Optional[datetime] = Query(None, description="Filter scans until this datetime (inclusive)"),
        svc: AnalysisService = Depends(dependency=get_analysis_service),
) -> list[ReportRowOut]:
    """
    Get Scan Analysis Reports filtered by date range.

    Query Parameters:
        - from_date: Filter scans from this datetime (inclusive)
        - to_date: Filter scans until this datetime (inclusive)

    Returns:
        List of scan report rows within the specified date range
    """
    data = svc.get_scan_report(from_date=from_date, to_date=to_date)

    return [
        ReportRowOut(
            sampled_at=row.sampled_at,
            user_id=row.user_id,
            device_id=row.device_id,
            widget_name=row.widget_name,
            algo_name=row.algo_name,
            results=row.formatted_results,
        )
        for row in data
    ]


@router.get("/reports/by-user-and-device", response_model=list[ReportRowOut])
async def get_reports_by_user_and_device(
        user_id: str = Query(..., description="Filter by user ID"),
        device_id: str = Query(..., description="Filter by device ID"),
        svc: AnalysisService = Depends(dependency=get_analysis_service),
) -> list[ReportRowOut]:
    """
    Get Scan Analysis Reports filtered by both user ID and device ID.

    Query Parameters:
        - user_id: Filter by user ID
        - device_id: Filter by device ID

    Returns:
        List of scan report rows for the specified user and device combination
    """
    data = svc.get_scan_report(user_id=user_id, device_id=device_id)

    return [
        ReportRowOut(
            sampled_at=row.sampled_at,
            user_id=row.user_id,
            device_id=row.device_id,
            widget_name=row.widget_name,
            algo_name=row.algo_name,
            results=row.formatted_results,
        )
        for row in data
    ]
