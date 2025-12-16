from __future__ import annotations

import dataclasses
import decimal
from datetime import datetime


@dataclasses.dataclass(slots=True)
class Scan:
    """A single scan record in the domain layer (no framework types)."""

    id: int
    content: str
    score: decimal.Decimal
    created_at: datetime


@dataclasses.dataclass(slots=True)
class Report:
    id: int
    title: str
    owner: str
    created_at: datetime
    scans: list[Scan]
