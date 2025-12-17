"""
Integration tests for the API endpoints.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.api import app
from src.domain.models import Algo, Widget, Scan, ScanResult
from src.domain.services import AnalysisService
from src.infrastructure.repository import Database


@pytest.fixture
def test_db() -> Database:
    """Create a test database with sample data."""
    db = Database()

    db.add_algo(Algo(id=1, name="Corn Algo", version=1))
    db.add_widget(Widget(
        id=1,
        name="Corn Widget",
        algo_id=1,
        param_config={
            "moisture": {"name": "moisture", "display_name": "Moisture", "unit": "%"},
        },
        param_order=["moisture"],
    ))
    db.add_scan(Scan(
        id=1,
        user_id="test_user",
        device_id="test_device",
        widget_id=1,
        algo_id=1,
        sampled_at=datetime(2024, 1, 15, 10, 0, 0),
        results=[ScanResult(parameter_name="moisture", predicted_value=15.5)],
    ))

    return db


@pytest.fixture
def client(test_db: Database) -> TestClient:
    """Create test client with injected test database."""
    app.state.analysis_service = AnalysisService(db=test_db)
    return TestClient(app)


class TestReportsEndpoint:
    """Tests for GET /api/v1/reports endpoint."""

    def test_get_reports_returns_200(self, client: TestClient):
        """Verify endpoint returns 200 OK."""
        response = client.get("/api/v1/reports")
        assert response.status_code == 200

    def test_get_reports_returns_list(self, client: TestClient):
        """Verify endpoint returns a list."""
        response = client.get("/api/v1/reports")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_get_reports_response_schema(self, client: TestClient):
        """Verify response matches expected schema."""
        response = client.get("/api/v1/reports")
        data = response.json()

        report = data[0]
        assert "sampled_at" in report
        assert "user_id" in report
        assert "device_id" in report
        assert "widget_name" in report
        assert "algo_name" in report
        assert "results" in report

    def test_filter_by_user_id(self, client: TestClient):
        """Verify user_id filter works."""
        response = client.get("/api/v1/reports?user_id=test_user")
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "test_user"

    def test_filter_by_nonexistent_user_returns_empty(self, client: TestClient):
        """Verify filtering by non-existent user returns empty list."""
        response = client.get("/api/v1/reports?user_id=nobody")
        data = response.json()
        assert data == []

    def test_filter_by_device_id(self, client: TestClient):
        """Verify device_id filter works."""
        response = client.get("/api/v1/reports?device_id=test_device")
        data = response.json()
        assert len(data) == 1
        assert data[0]["device_id"] == "test_device"

    def test_filter_by_date_range(self, client: TestClient):
        """Verify date range filter works."""
        response = client.get(
            "/api/v1/reports",
            params={
                "from_date": "2024-01-01T00:00:00",
                "to_date": "2024-01-31T23:59:59",
            }
        )
        data = response.json()
        assert len(data) == 1

    def test_results_field_contains_formatted_string(self, client: TestClient):
        """Verify results field contains properly formatted string."""
        response = client.get("/api/v1/reports")
        data = response.json()

        results = data[0]["results"]
        assert "{" in results
        assert "Moisture" in results
        assert "15.5 %" in results