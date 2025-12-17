from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ReportRowOut(BaseModel):
    """API response schema for scan analysis report rows."""
    sampled_at: datetime
    user_id: str
    device_id: str
    widget_name: str
    algo_name: str
    results: str  # Mapped from 'formatted_results' in domain model

    model_config = ConfigDict(from_attributes=True)


class AlgoOut(BaseModel):
    id: int
    name: str
    version: int

    model_config = ConfigDict(from_attributes=True)


class WidgetOut(BaseModel):
    id: int
    name: str
    algo_id: int
    param_config: dict
    param_order: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ScanResultIn(BaseModel):
    parameter_name: str
    predicted_value: float


class ScanIn(BaseModel):
    id: int
    user_id: str
    device_id: str
    widget_id: int
    algo_id: int
    sampled_at: datetime
    results: List[ScanResultIn] = []


class ScanOut(ScanIn):
    model_config = ConfigDict(from_attributes=True)
