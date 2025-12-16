from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal

from src.domain.models import Scan, Report
from src.infrastructure.repository import Database


class ScanService:
    def __init__(self, db: Database) -> None:
        self._db = db

    # ---------------- public API ---------------- #
    def create_scan(self, *, content: str, score: Decimal) -> Scan:
        return self._db.create_scan(content=content, score=score, dt=datetime.utcnow())

    def list_scans(self, *, skip: int, limit: int) -> Iterable[Scan]:
        return self._db.list_scans(skip=skip, limit=limit)

    def delete_scan(self, scan_id: int) -> None:
        self._db.delete_scan(scan_id)


class ReportService:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create_report(self, title: str, owner: str) -> Report:
        return self._db.create_report(title=title, owner=owner)
