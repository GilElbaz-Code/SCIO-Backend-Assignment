from datetime import datetime
from typing import Iterable, Optional, TYPE_CHECKING

import src.utils.formatting as _formatting
from src.domain.models import ScanReportRow

if TYPE_CHECKING:
    from src.infrastructure.repository import Database


class AnalysisService:
    """
    Business logic for scan analysis operations.
    Handles report generation with proper formatting based on widget configuration.
    """

    def __init__(self, db: "Database") -> None:
        self._db = db

    def get_scan_report(
            self,
            user_id: Optional[str] = None,
            device_id: Optional[str] = None,
            from_date: Optional[datetime] = None,
            to_date: Optional[datetime] = None,
    ) -> Iterable[ScanReportRow]:
        """
        Generate scan analysis report filtered by criteria.

        Args:
            user_id: Filter by user ID
            device_id: Filter by device ID
            from_date: Filter scans from this date (inclusive)
            to_date: Filter scans until this date (inclusive)

        Returns:
            Iterable of ScanReportRow with formatted results
        """
        scans = self._db.list_scans(user_id=user_id, device_id=device_id, from_date=from_date, to_date=to_date)
        report = []

        for scan in scans:
            widget = self._db.get_widget(widget_id=scan.widget_id)
            algo = self._db.get_algo(algo_id=scan.algo_id)

            if not widget or not algo:
                continue

            formatted_results = self._format_scan_results(
                results=scan.results,
                param_config=widget.param_config,
                param_order=widget.param_order,
            )

            report.append(
                ScanReportRow(
                    sampled_at=scan.sampled_at,
                    user_id=scan.user_id,
                    device_id=scan.device_id,
                    widget_name=widget.name,
                    algo_name=algo.name,
                    formatted_results=formatted_results,
                )
            )

        return report

    def _format_scan_results(
            self,
            results: list,
            param_config: dict[str, dict[str, str]],
            param_order: list[str] = None,
    ) -> str:
        """
        Format scan results based on widget parameter configuration.

        Args:
            results: List of ScanResult objects
            param_config: Widget parameter display configuration
            param_order: Optional ordering of parameters for display

        Returns:
            Formatted string like "{Protein: 12.50, Moisture: 22.1 %}"
        """
        # Create a lookup dict for results by parameter name
        results_by_name = {r.parameter_name: r for r in results}

        # Determine the order of parameters
        if param_order:
            # Use specified order, then append any not in the order
            ordered_names = list(param_order)
            for r in results:
                if r.parameter_name not in ordered_names:
                    ordered_names.append(r.parameter_name)
        else:
            # Use the order they appear in results
            ordered_names = [r.parameter_name for r in results]

        formatted_parts = []
        for param_name in ordered_names:
            res = results_by_name.get(param_name)
            if not res:
                continue

            conf = param_config.get(res.parameter_name, {})
            display_name = conf.get("display_name", res.parameter_name)
            unit = conf.get("unit", "")

            val_str = _formatting.format_value(value=res.predicted_value, unit=unit)
            formatted_parts.append(f"{display_name}: {val_str}")

        return "{" + ", ".join(formatted_parts) + "}"
