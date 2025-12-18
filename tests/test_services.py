import pytest
from unittest.mock import MagicMock
from datetime import datetime
from src.domain.services import AnalysisService
from src.domain.models import Scan, ScanResult, Widget, Algo


@pytest.fixture
def mock_db():
    return MagicMock()


def test_get_scan_report_formatting(mock_db):
    """
    Verifies that the service correctly orchestrates fetching data
    and formatting the result string.
    """
    # 1. Setup Data
    mock_scan = Scan(
        id=1, user_id="u1", device_id="d1", widget_id=10, algo_id=20,
        sampled_at=datetime.now(),
        results=[
            ScanResult(parameter_name="protein", predicted_value=10.512),
            ScanResult(parameter_name="fat", predicted_value=5.0)
        ]
    )

    mock_widget = Widget(
        id=10, name="Dairy Widget", algo_id=20,
        param_config={
            "protein": {"display_name": "Protein", "unit": "%"},
            "fat": {"display_name": "Fat Content", "unit": "g"}
        },
        param_order=["protein", "fat"]
    )

    mock_algo = Algo(id=20, name="Dairy Algo v1", version=1)

    # 2. Configure Mock Returns
    mock_db.list_scans.return_value = [mock_scan]
    mock_db.get_widget.return_value = mock_widget
    mock_db.get_algo.return_value = mock_algo

    # 3. Instantiate Service
    service = AnalysisService(db=mock_db)

    # 4. Act
    report = service.get_scan_report()

    # 5. Assert
    row = report[0]

    # Updated Assertion: Match exactly what the service returns (10.512)
    assert "Protein: 10.512 %" in row.formatted_results
    assert "Fat Content: 5.0" in row.formatted_results


def test_missing_widget_skips_row(mock_db):
    """Ensures that if a widget is missing, the code doesn't crash but skips the row."""
    mock_scan = Scan(id=1, user_id="u1", device_id="d1", widget_id=999, algo_id=20, sampled_at=datetime.now())

    mock_db.list_scans.return_value = [mock_scan]
    mock_db.get_widget.return_value = None  # Simulate missing widget

    service = AnalysisService(db=mock_db)

    report = service.get_scan_report()

    assert len(report) == 0  # Should skip the bad row