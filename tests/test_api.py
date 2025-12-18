from unittest.mock import MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

from src.api import app
from src.api.dependencies import get_analysis_service
from src.domain.models import ScanReportRow

client = TestClient(app)

def test_get_all_reports_success():
    """
    Test that the API correctly calls the service and serializes the result.
    Uses dependency_overrides to MOCK the service layer.
    """
    # 1. Create a Mock Service
    mock_service = MagicMock()
    
    # 2. Define what the mock returns (Domain Objects)
    mock_data = [
        ScanReportRow(
            sampled_at=datetime(2023, 1, 1, 12, 0, 0),
            user_id="user_1",
            device_id="dev_1",
            widget_name="Standard Widget",
            algo_name="V1 Algo",
            formatted_results="{Fat: 10%}"
        )
    ]
    mock_service.get_scan_report.return_value = mock_data

    # 3. Override the dependency
    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    try:
        # 4. Act
        response = client.get("/api/v1/reports")

        # 5. Assert
        assert response.status_code == 200
        json_data = response.json()
        assert len(json_data) == 1
        assert json_data[0]["user_id"] == "user_1"
        assert json_data[0]["results"] == "{Fat: 10%}"
        
        # Verify the service was called exactly once
        mock_service.get_scan_report.assert_called_once()
        
    finally:
        # 6. Clean up overrides
        app.dependency_overrides = {}

def test_get_reports_by_user_passes_param():
    """Test that the user_id param is correctly passed to the service."""
    mock_service = MagicMock()
    mock_service.get_scan_report.return_value = [] # Return empty list
    
    app.dependency_overrides[get_analysis_service] = lambda: mock_service

    try:
        client.get("/api/v1/reports/by-user/u123")
        
        # Verify service was called with user_id="u123"
        mock_service.get_scan_report.assert_called_once_with(user_id="u123")
    finally:
        app.dependency_overrides = {}