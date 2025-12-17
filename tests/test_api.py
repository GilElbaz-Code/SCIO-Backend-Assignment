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

    # Add algorithms
    db.add_algo(Algo(id=1, name="Corn Algo", version=1))
    db.add_algo(Algo(id=2, name="Soybean Algo", version=1))

    # Add widgets
    db.add_widget(Widget(
        id=1,
        name="Corn Widget",
        algo_id=1,
        param_config={
            "moisture": {"name": "moisture", "display_name": "Moisture", "unit": "%"},
        },
        param_order=["moisture"],
    ))
    db.add_widget(Widget(
        id=2,
        name="Soybean Widget",
        algo_id=2,
        param_config={
            "oil": {"name": "oil", "display_name": "Oil", "unit": "float_2_dig"},
            "protein": {"name": "protein", "display_name": "Protein", "unit": "float_2_dig"},
        },
        param_order=["oil", "protein"],
    ))

    # Add scans
    db.add_scan(Scan(
        id=1,
        user_id="ariel",
        device_id="d1",
        widget_id=1,
        algo_id=1,
        sampled_at=datetime(2025, 11, 20, 13, 2, 5),
        results=[ScanResult(parameter_name="moisture", predicted_value=16.5)],
    ))
    db.add_scan(Scan(
        id=2,
        user_id="ariel",
        device_id="d2",
        widget_id=2,
        algo_id=2,
        sampled_at=datetime(2025, 11, 30, 10, 27, 33),
        results=[
            ScanResult(parameter_name="oil", predicted_value=14.5),
            ScanResult(parameter_name="protein", predicted_value=22.0),
        ],
    ))
    db.add_scan(Scan(
        id=3,
        user_id="dan",
        device_id="d1",
        widget_id=2,
        algo_id=2,
        sampled_at=datetime(2025, 11, 13, 11, 59, 4),
        results=[
            ScanResult(parameter_name="oil", predicted_value=12.3),
            ScanResult(parameter_name="protein", predicted_value=12.5),
        ],
    ))

    return db


@pytest.fixture
def client(test_db: Database) -> TestClient:
    """Create test client with injected test database."""
    app.state.analysis_service = AnalysisService(db=test_db)
    return TestClient(app)


class TestGetAllReportsEndpoint:
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
        assert len(data) == 3

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

    def test_results_field_contains_formatted_string(self, client: TestClient):
        """Verify results field contains properly formatted string."""
        response = client.get("/api/v1/reports")
        data = response.json()

        results = data[0]["results"]
        assert "{" in results
        assert "Moisture" in results


class TestGetReportsByUserEndpoint:
    """Tests for GET /api/v1/reports/by-user/{user_id} endpoint."""

    def test_filter_by_user_id_returns_200(self, client: TestClient):
        """Verify endpoint returns 200 OK."""
        response = client.get("/api/v1/reports/by-user/ariel")
        assert response.status_code == 200

    def test_filter_by_user_id_returns_correct_data(self, client: TestClient):
        """Verify user_id filter returns only scans for that user."""
        response = client.get("/api/v1/reports/by-user/ariel")
        data = response.json()
        assert len(data) == 2
        assert all(r["user_id"] == "ariel" for r in data)

    def test_filter_by_different_user(self, client: TestClient):
        """Verify filtering by different user returns different data."""
        response = client.get("/api/v1/reports/by-user/dan")
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "dan"

    def test_filter_by_nonexistent_user_returns_empty(self, client: TestClient):
        """Verify filtering by non-existent user returns empty list."""
        response = client.get("/api/v1/reports/by-user/nobody")
        data = response.json()
        assert data == []


class TestGetReportsByDeviceEndpoint:
    """Tests for GET /api/v1/reports/by-device/{device_id} endpoint."""

    def test_filter_by_device_id_returns_200(self, client: TestClient):
        """Verify endpoint returns 200 OK."""
        response = client.get("/api/v1/reports/by-device/d1")
        assert response.status_code == 200

    def test_filter_by_device_id_returns_correct_data(self, client: TestClient):
        """Verify device_id filter returns only scans for that device."""
        response = client.get("/api/v1/reports/by-device/d1")
        data = response.json()
        assert len(data) == 2
        assert all(r["device_id"] == "d1" for r in data)

    def test_filter_by_different_device(self, client: TestClient):
        """Verify filtering by different device returns different data."""
        response = client.get("/api/v1/reports/by-device/d2")
        data = response.json()
        assert len(data) == 1
        assert data[0]["device_id"] == "d2"

    def test_filter_by_nonexistent_device_returns_empty(self, client: TestClient):
        """Verify filtering by non-existent device returns empty list."""
        response = client.get("/api/v1/reports/by-device/d99")
        data = response.json()
        assert data == []


class TestGetReportsByDateRangeEndpoint:
    """Tests for GET /api/v1/reports/by-date-range endpoint."""

    def test_filter_by_date_range_returns_200(self, client: TestClient):
        """Verify endpoint returns 200 OK."""
        response = client.get(
            "/api/v1/reports/by-date-range",
            params={
                "from_date": "2025-11-01T00:00:00",
                "to_date": "2025-11-30T23:59:59",
            }
        )
        assert response.status_code == 200

    def test_filter_by_date_range_returns_correct_data(self, client: TestClient):
        """Verify date range filter works correctly."""
        response = client.get(
            "/api/v1/reports/by-date-range",
            params={
                "from_date": "2025-11-13T00:00:00",
                "to_date": "2025-11-30T23:59:59",
            }
        )
        data = response.json()
        # Should include scans from 11/13, 11/20, and 11/30
        assert len(data) == 3

    def test_filter_by_date_range_excludes_out_of_range(self, client: TestClient):
        """Verify date range filter excludes scans outside range."""
        response = client.get(
            "/api/v1/reports/by-date-range",
            params={
                "from_date": "2025-12-01T00:00:00",
                "to_date": "2025-12-31T23:59:59",
            }
        )
        data = response.json()
        assert len(data) == 0

    def test_filter_by_from_date_only(self, client: TestClient):
        """Verify filtering by from_date only works."""
        response = client.get(
            "/api/v1/reports/by-date-range",
            params={"from_date": "2025-11-20T00:00:00"}
        )
        data = response.json()
        assert len(data) == 2  # Scans from 11/20 and 11/30

    def test_filter_by_to_date_only(self, client: TestClient):
        """Verify filtering by to_date only works."""
        response = client.get(
            "/api/v1/reports/by-date-range",
            params={"to_date": "2025-11-20T23:59:59"}
        )
        data = response.json()
        assert len(data) == 2  # Scans from 11/13 and 11/20


class TestGetReportsByUserAndDeviceEndpoint:
    """Tests for GET /api/v1/reports/by-user-and-device endpoint."""

    def test_filter_by_user_and_device_returns_200(self, client: TestClient):
        """Verify endpoint returns 200 OK."""
        response = client.get(
            "/api/v1/reports/by-user-and-device",
            params={"user_id": "ariel", "device_id": "d1"}
        )
        assert response.status_code == 200

    def test_filter_by_user_and_device_returns_correct_data(self, client: TestClient):
        """Verify combined filter returns only matching scans."""
        response = client.get(
            "/api/v1/reports/by-user-and-device",
            params={"user_id": "ariel", "device_id": "d1"}
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "ariel"
        assert data[0]["device_id"] == "d1"

    def test_filter_by_user_and_device_no_match_returns_empty(self, client: TestClient):
        """Verify non-matching combination returns empty list."""
        response = client.get(
            "/api/v1/reports/by-user-and-device",
            params={"user_id": "ariel", "device_id": "d99"}
        )
        data = response.json()
        assert data == []

    def test_filter_by_different_user_device_combination(self, client: TestClient):
        """Verify filtering works for different user-device combinations."""
        response = client.get(
            "/api/v1/reports/by-user-and-device",
            params={"user_id": "dan", "device_id": "d1"}
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "dan"
        assert data[0]["device_id"] == "d1"
