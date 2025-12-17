from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import Iterable, Optional

from src.domain.models import Scan, Algo, Widget, ScanResult
from src.settings import Settings


class Database:
    """
    In-memory database that loads data from CSV files.
    Acts as the data access layer (repository pattern).
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._scans: dict[int, Scan] = {}
        self._algos: dict[int, Algo] = {}
        self._widgets: dict[int, Widget] = {}

        if settings:
            self._bootstrap(settings)

    def _bootstrap(self, s: Settings) -> None:
        """Load all CSVs and link them in memory."""
        if not s.widget_data_path.exists():
            print(f"Warning: Data file not found: {s.widget_data_path}")
            return

        self._load_algos(s.algo_data_path)
        self._load_widgets(s.widget_data_path)
        self._load_scans(s.scan_data_path)
        self._load_scan_results(s.scan_results_path)

    def _load_algos(self, path) -> None:
        """Load algorithm definitions from Excel."""
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            self._algos[row["id"]] = Algo(
                id=row["id"],
                name=row["name"],
                version=row["version"]
            )

    def _load_widgets(self, path) -> None:
        """Load widget definitions from Excel."""
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            param_conf = self._parse_widget_params(row["parameters"])
            # Parse param_order if present
            param_order = self._parse_param_order(row.get("param_order", "[]"))
            self._widgets[row["id"]] = Widget(
                id=row["id"],
                name=row["name"],
                algo_id=row["algo_id"],
                param_config=param_conf,
                param_order=param_order,
            )

    def _load_scans(self, path) -> None:
        """Load scan records from Excel."""
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            scan = Scan(
                id=row["id"],
                user_id=row["user_id"],
                device_id=row["device_id"],
                widget_id=row["widget_id"],
                algo_id=row["algo_id"],
                sampled_at=pd.to_datetime(row["sampled_at"]).to_pydatetime(),
                results=[],
            )
            self._scans[scan.id] = scan

    def _load_scan_results(self, path) -> None:
        """Load scan results from Excel and attach to parent scans."""
        df = pd.read_excel(path)
        for _, row in df.iterrows():
            scan = self._scans.get(row["scan_id"])
            if scan:
                scan.results.append(
                    ScanResult(
                        parameter_name=str(row["parameter_name"]).strip(),
                        predicted_value=row["predicted_value"],
                    )
                )

    @staticmethod
    def _parse_widget_params(raw_str: str) -> dict[str, dict[str, str]]:
        """
        Parse custom widget parameter format.
        Input: "[{name: moisture, display_name: Moisture, unit: %}]"
        Output: {'moisture': {'name': 'moisture', 'display_name': 'Moisture', 'unit': '%'}}
        """
        items = {}
        raw_str = raw_str.strip("[]")
        objects = raw_str.split("}")

        for obj in objects:
            if not obj.strip():
                continue
            obj = obj.replace("{", "").replace("\n", "").strip()
            entry = {}
            for part in obj.split(","):
                part = part.strip()
                if ":" in part:
                    k, v = part.split(":", 1)
                    entry[k.strip()] = v.strip()

            if "name" in entry:
                items[entry["name"]] = entry

        return items

    @staticmethod
    def _parse_param_order(raw_str: str) -> list[str]:
        """
        Parse parameter order list.
        Input: "[protein, moisture]"
        Output: ['protein', 'moisture']
        """
        if pd.isna(raw_str):
            return []
        raw_str = str(raw_str).strip("[]")
        if not raw_str:
            return []
        return [p.strip() for p in raw_str.split(",") if p.strip()]

    # --------------------------------------------------------------------- #
    # Data Access Methods
    # --------------------------------------------------------------------- #
    def list_scans(
            self,
            user_id: Optional[str] = None,
            device_id: Optional[str] = None,
            from_date: Optional[datetime] = None,
            to_date: Optional[datetime] = None,
    ) -> Iterable[Scan]:
        """
        Filter scans based on criteria.

        Args:
            user_id: Filter by user ID
            device_id: Filter by device ID
            from_date: Filter scans from this date (inclusive)
            to_date: Filter scans until this date (inclusive)

        Returns:
            Filtered list of Scan objects
        """
        results = list(self._scans.values())

        if user_id:
            results = [s for s in results if s.user_id == user_id]
        if device_id:
            results = [s for s in results if s.device_id == device_id]
        if from_date:
            results = [s for s in results if s.sampled_at >= from_date]
        if to_date:
            results = [s for s in results if s.sampled_at <= to_date]

        return results

    def get_widget(self, widget_id: int) -> Optional[Widget]:
        """Get widget by ID."""
        return self._widgets.get(widget_id)

    def get_algo(self, algo_id: int) -> Optional[Algo]:
        """Get algorithm by ID."""
        return self._algos.get(algo_id)

    # --------------------------------------------------------------------- #
    # Methods for testing (add data programmatically)
    # --------------------------------------------------------------------- #
    def add_algo(self, algo: Algo) -> None:
        """Add an algorithm to the database."""
        self._algos[algo.id] = algo

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to the database."""
        self._widgets[widget.id] = widget

    def add_scan(self, scan: Scan) -> None:
        """Add a scan to the database."""
        self._scans[scan.id] = scan