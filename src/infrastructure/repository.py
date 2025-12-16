"""
Simple in-memory repository with optional Excel bootstrap.
If you prefer SQLite, swap the implementation – service layer
will not need to change.
"""
from __future__ import annotations

import itertools
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.domain.models import Scan, Report


class Database:
    def __init__(self, excel_path: str | Path | None = None) -> None:
        self._scans: dict[int, Scan] = {}
        self._reports: dict[int, Report] = {}
        self._id_seq = itertools.count(1)

        if excel_path:
            self._bootstrap_from_excel(Path(excel_path))

    # --------------------------------------------------------------------- #
    # Bootstrap helpers
    # --------------------------------------------------------------------- #
    def _bootstrap_from_excel(self, path: Path) -> None:
        if not path.exists():
            return

        df = pd.read_excel(path)
        for _, row in df.iterrows():
            self.create_scan(
                content=str(row["content"]),
                score=Decimal(row["score"]),
                dt=row.get("created_at") or datetime.utcnow(),
            )

    # --------------------------------------------------------------------- #
    # CRUD – SCAN
    # --------------------------------------------------------------------- #
    def create_scan(self, *, content: str, score: Decimal, dt: datetime) -> Scan:
        scan_id = next(self._id_seq)
        scan = Scan(id=scan_id, content=content, score=score, created_at=dt)
        self._scans[scan_id] = scan
        return scan

    def list_scans(self, *, skip: int = 0, limit: int = 50) -> Iterable[Scan]:
        return list(self._scans.values())[skip : skip + limit]

    def delete_scan(self, scan_id: int) -> None:
        self._scans.pop(scan_id, None)

    # --------------------------------------------------------------------- #
    # Reports – trivial implementation
    # --------------------------------------------------------------------- #
    def create_report(self, title: str, owner: str) -> Report:
        report_id = next(self._id_seq)
        report = Report(
            id=report_id,
            title=title,
            owner=owner,
            scans=[],
            created_at=datetime.utcnow(),
        )
        self._reports[report_id] = report
        return report
