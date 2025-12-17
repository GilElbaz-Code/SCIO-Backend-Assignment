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
