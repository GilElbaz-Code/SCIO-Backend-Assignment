from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request

from src.domain.schemas import ReportRowOut
from src.domain.services import AnalysisService

router = APIRouter(tags=["Analysis"])


def _get_service(request: Request) -> AnalysisService:
    """Dependency to get the AnalysisService from app state."""
    return request.app.state.analysis_service


@router.get("/reports", response_model=list[ReportRowOut])
async def get_reports(
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        svc: AnalysisService = Depends(_get_service),
) -> list[ReportRowOut]:
    """
    Get Scan Analysis Reports filtered by user, device, or date range.

    Query Parameters:
        - user_id: Filter by user ID
        - device_id: Filter by device ID
        - from_date: Filter scans from this datetime (inclusive)
        - to_date: Filter scans until this datetime (inclusive)

    Returns:
        List of scan report rows with formatted results
    """
    data = svc.get_scan_report(user_id, device_id, from_date, to_date)

    # Map domain model to API schema
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
