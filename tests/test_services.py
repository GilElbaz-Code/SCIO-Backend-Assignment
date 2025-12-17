"""
Unit tests for AnalysisService business logic.
Tests the scan report generation with various filters and formatting rules.
"""

import pytest
from datetime import datetime

from src.domain.models import Algo, Widget, Scan, ScanResult, ScanReportRow
from src.domain.services import AnalysisService
from src.infrastructure.repository import Database


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_db() -> Database:
    """Create an empty in-memory database."""
    return Database()


@pytest.fixture
def populated_db() -> Database:
    """Create a database with test data."""
    db = Database()

    # Add algorithms
    db.add_algo(Algo(id=1, name="Corn Moisture Algo", version=1))
    db.add_algo(Algo(id=2, name="Wheat Protein Algo", version=2))

    # Add widgets with parameter configurations
    db.add_widget(Widget(
        id=1,
        name="Corn Scanner",
        algo_id=1,
        param_config={
            "moisture": {"name": "moisture", "display_name": "Moisture", "unit": "%"},
            "protein": {"name": "protein", "display_name": "Protein", "unit": "float_2_dig"},
        },
        param_order=["moisture", "protein"],
    ))
    db.add_widget(Widget(
        id=2,
        name="Wheat Scanner",
        algo_id=2,
        param_config={
            "protein": {"name": "protein", "display_name": "Protein", "unit": "%"},
            "starch": {"name": "starch", "display_name": "Starch", "unit": "float_1_dig"},
        },
        param_order=["protein", "starch"],
    ))

    # Add scans with results
    db.add_scan(Scan(
        id=1,
        user_id="user_001",
        device_id="device_A",
        widget_id=1,
        algo_id=1,
        sampled_at=datetime(2024, 1, 15, 10, 30, 0),
        results=[
            ScanResult(parameter_name="moisture", predicted_value=14.5),
            ScanResult(parameter_name="protein", predicted_value=8.234),
        ]
    ))
    db.add_scan(Scan(
        id=2,
        user_id="user_001",
        device_id="device_A",
        widget_id=1,
        algo_id=1,
        sampled_at=datetime(2024, 1, 16, 11, 0, 0),
        results=[
            ScanResult(parameter_name="moisture", predicted_value=15.2),
            ScanResult(parameter_name="protein", predicted_value=7.891),
        ]
    ))
    db.add_scan(Scan(
        id=3,
        user_id="user_002",
        device_id="device_B",
        widget_id=2,
        algo_id=2,
        sampled_at=datetime(2024, 1, 15, 14, 0, 0),
        results=[
            ScanResult(parameter_name="protein", predicted_value=12.5),
            ScanResult(parameter_name="starch", predicted_value=68.73),
        ]
    ))

    return db


@pytest.fixture
def service(populated_db: Database) -> AnalysisService:
    """Create an AnalysisService with populated test data."""
    return AnalysisService(populated_db)


# ---------------------------------------------------------------------------
# Test: get_scan_report - Basic Functionality
# ---------------------------------------------------------------------------

class TestGetScanReportBasic:
    """Tests for basic report generation functionality."""

    def test_get_all_reports_returns_all_scans(self, service: AnalysisService):
        """Verify that calling without filters returns all scans."""
        reports = list(service.get_scan_report())

        assert len(reports) == 3
        assert all(isinstance(r, ScanReportRow) for r in reports)

    def test_empty_database_returns_empty_list(self, empty_db: Database):
        """Verify empty database returns empty report."""
        svc = AnalysisService(empty_db)
        reports = list(svc.get_scan_report())

        assert reports == []

    def test_report_contains_correct_widget_name(self, service: AnalysisService):
        """Verify widget name is correctly resolved."""
        reports = list(service.get_scan_report(user_id="user_001"))

        assert all(r.widget_name == "Corn Scanner" for r in reports)

    def test_report_contains_correct_algo_name(self, service: AnalysisService):
        """Verify algo name is correctly resolved."""
        reports = list(service.get_scan_report(user_id="user_002"))

        assert reports[0].algo_name == "Wheat Protein Algo"


# ---------------------------------------------------------------------------
# Test: get_scan_report - Filtering
# ---------------------------------------------------------------------------

class TestGetScanReportFiltering:
    """Tests for report filtering functionality."""

    def test_filter_by_user_id(self, service: AnalysisService):
        """Verify filtering by user_id works correctly."""
        reports = list(service.get_scan_report(user_id="user_001"))

        assert len(reports) == 2
        assert all(r.user_id == "user_001" for r in reports)

    def test_filter_by_device_id(self, service: AnalysisService):
        """Verify filtering by device_id works correctly."""
        reports = list(service.get_scan_report(device_id="device_B"))

        assert len(reports) == 1
        assert reports[0].device_id == "device_B"

    def test_filter_by_date_range(self, service: AnalysisService):
        """Verify filtering by date range works correctly."""
        from_date = datetime(2024, 1, 15, 0, 0, 0)
        to_date = datetime(2024, 1, 15, 23, 59, 59)

        reports = list(service.get_scan_report(from_date=from_date, to_date=to_date))

        assert len(reports) == 2  # Scans 1 and 3 are on Jan 15
        for r in reports:
            assert r.sampled_at.date() == datetime(2024, 1, 15).date()

    def test_filter_by_from_date_only(self, service: AnalysisService):
        """Verify filtering with only from_date."""
        from_date = datetime(2024, 1, 16, 0, 0, 0)

        reports = list(service.get_scan_report(from_date=from_date))

        assert len(reports) == 1
        assert reports[0].sampled_at >= from_date

    def test_filter_by_to_date_only(self, service: AnalysisService):
        """Verify filtering with only to_date."""
        to_date = datetime(2024, 1, 15, 12, 0, 0)

        reports = list(service.get_scan_report(to_date=to_date))

        assert len(reports) == 1  # Only scan 1 is before noon on Jan 15

    def test_combined_filters(self, service: AnalysisService):
        """Verify multiple filters can be combined."""
        reports = list(service.get_scan_report(
            user_id="user_001",
            device_id="device_A",
            from_date=datetime(2024, 1, 16, 0, 0, 0)
        ))

        assert len(reports) == 1
        assert reports[0].user_id == "user_001"
        assert reports[0].device_id == "device_A"

    def test_filter_returns_empty_for_nonexistent_user(self, service: AnalysisService):
        """Verify filtering by non-existent user returns empty list."""
        reports = list(service.get_scan_report(user_id="nonexistent"))

        assert reports == []


# ---------------------------------------------------------------------------
# Test: Result Formatting
# ---------------------------------------------------------------------------

class TestResultFormatting:
    """Tests for result value formatting based on unit configuration."""

    def test_format_value_percentage(self):
        """Verify percentage formatting."""
        result = AnalysisService._format_value(14.5, "%")
        assert result == "14.5 %"

    def test_format_value_float_2_dig(self):
        """Verify 2 decimal places formatting."""
        result = AnalysisService._format_value(8.234, "float_2_dig")
        assert result == "8.23"

    def test_format_value_float_1_dig(self):
        """Verify 1 decimal place formatting."""
        result = AnalysisService._format_value(68.73, "float_1_dig")
        assert result == "68.7"

    def test_format_value_no_unit(self):
        """Verify formatting with no unit specified."""
        result = AnalysisService._format_value(42.0, "")
        assert result == "42.0"

    def test_format_value_unknown_unit(self):
        """Verify formatting with unknown unit falls back to string."""
        result = AnalysisService._format_value(123.456, "unknown")
        assert result == "123.456"

    def test_formatted_results_string_structure(self, service: AnalysisService):
        """Verify the formatted results string has correct structure."""
        reports = list(service.get_scan_report(user_id="user_001"))

        # Check first report's results format
        results_str = reports[0].formatted_results

        assert results_str.startswith("{")
        assert results_str.endswith("}")
        assert "Moisture:" in results_str
        assert "Protein:" in results_str

    def test_formatted_results_with_percentage_unit(self, service: AnalysisService):
        """Verify percentage values are formatted correctly in results string."""
        reports = list(service.get_scan_report(user_id="user_001"))

        # Corn Scanner uses % for moisture
        assert "14.5 %" in reports[0].formatted_results

    def test_formatted_results_with_float_2_dig_unit(self, service: AnalysisService):
        """Verify float_2_dig values are formatted correctly."""
        reports = list(service.get_scan_report(user_id="user_001"))

        # Corn Scanner uses float_2_dig for protein (8.234 -> 8.23)
        assert "8.23" in reports[0].formatted_results


# ---------------------------------------------------------------------------
# Test: Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_scan_with_missing_widget_is_skipped(self, populated_db: Database):
        """Verify scans with non-existent widget are skipped."""
        # Add scan with non-existent widget_id
        populated_db.add_scan(Scan(
            id=99,
            user_id="user_003",
            device_id="device_X",
            widget_id=999,  # Non-existent
            algo_id=1,
            sampled_at=datetime(2024, 1, 20, 10, 0, 0),
            results=[]
        ))

        svc = AnalysisService(populated_db)
        reports = list(svc.get_scan_report(user_id="user_003"))

        assert len(reports) == 0

    def test_scan_with_missing_algo_is_skipped(self, populated_db: Database):
        """Verify scans with non-existent algo are skipped."""
        # Add scan with non-existent algo_id
        populated_db.add_scan(Scan(
            id=99,
            user_id="user_003",
            device_id="device_X",
            widget_id=1,
            algo_id=999,  # Non-existent
            sampled_at=datetime(2024, 1, 20, 10, 0, 0),
            results=[]
        ))

        svc = AnalysisService(populated_db)
        reports = list(svc.get_scan_report(user_id="user_003"))

        assert len(reports) == 0

    def test_scan_with_empty_results(self, populated_db: Database):
        """Verify scan with no results returns empty formatted string."""
        populated_db.add_scan(Scan(
            id=99,
            user_id="user_003",
            device_id="device_X",
            widget_id=1,
            algo_id=1,
            sampled_at=datetime(2024, 1, 20, 10, 0, 0),
            results=[]  # Empty results
        ))

        svc = AnalysisService(populated_db)
        reports = list(svc.get_scan_report(user_id="user_003"))

        assert len(reports) == 1
        assert reports[0].formatted_results == "{}"

    def test_parameter_not_in_widget_config_uses_raw_name(self, populated_db: Database):
        """Verify unknown parameter uses raw name as display name."""
        populated_db.add_scan(Scan(
            id=99,
            user_id="user_003",
            device_id="device_X",
            widget_id=1,
            algo_id=1,
            sampled_at=datetime(2024, 1, 20, 10, 0, 0),
            results=[
                ScanResult(parameter_name="unknown_param", predicted_value=42.0)
            ]
        ))

        svc = AnalysisService(populated_db)
        reports = list(svc.get_scan_report(user_id="user_003"))

        assert "unknown_param:" in reports[0].formatted_results

    def test_param_order_is_respected(self, populated_db: Database):
        """Verify parameters are displayed in the order specified by param_order."""
        # Corn Scanner has param_order=["moisture", "protein"]
        reports = list(populated_db._scans.values())
        svc = AnalysisService(populated_db)

        reports = list(svc.get_scan_report(user_id="user_001"))
        # First result should have Moisture before Protein
        first_result = reports[0].formatted_results
        moisture_pos = first_result.find("Moisture")
        protein_pos = first_result.find("Protein")
        assert moisture_pos < protein_pos, f"Expected Moisture before Protein in {first_result}"


# ---------------------------------------------------------------------------
# Test: Integration with Repository
# ---------------------------------------------------------------------------

class TestRepositoryIntegration:
    """Tests verifying correct integration with Database repository."""

    def test_service_delegates_filtering_to_repository(self, populated_db: Database):
        """Verify service correctly passes filters to repository."""
        svc = AnalysisService(populated_db)

        # This implicitly tests that the service correctly passes
        # all filter parameters to the repository
        reports = list(svc.get_scan_report(
            user_id="user_001",
            device_id="device_A",
            from_date=datetime(2024, 1, 1),
            to_date=datetime(2024, 12, 31)
        ))

        assert len(reports) == 2
        assert all(r.user_id == "user_001" and r.device_id == "device_A" for r in reports)