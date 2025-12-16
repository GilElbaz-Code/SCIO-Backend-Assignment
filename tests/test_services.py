from decimal import Decimal

from src.infrastructure.repository import Database
from src.domain.services import ScanService


def test_create_and_list_scans() -> None:
    db = Database()  # in-mem
    svc = ScanService(db)

    svc.create_scan(content="demo", score=Decimal("0.42"))
    svc.create_scan(content="demo-2", score=Decimal("0.99"))

    scans = list(svc.list_scans(skip=0, limit=5))
    assert len(scans) == 2
    assert scans[0].id == 1
    assert scans[1].score == Decimal("0.99")
