from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScanIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=4096)
    score: Decimal = Field(..., ge=0, le=1)


class ScanOut(ScanIn):
    id: int
    created_at: datetime


class ReportOut(BaseModel):
    id: int
    title: str
    owner: str
    created_at: datetime
    scans: list[ScanOut]

    model_config = ConfigDict(from_attributes=True)
