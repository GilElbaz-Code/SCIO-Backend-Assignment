from fastapi import Request
from src.domain.services import AnalysisService


def get_analysis_service(request: Request) -> AnalysisService:
    """Dependency provider that returns the AnalysisService stored on app state."""
    return request.app.state.analysis_service

