import dataclasses
from datetime import datetime


@dataclasses.dataclass(slots=True)
class Algo:
    """Algorithm definition for ML prediction models."""
    id: int
    name: str
    version: int


@dataclasses.dataclass(slots=True)
class Widget:
    """
    Widget defines how scan parameters are displayed.
    param_config stores: {'moisture': {'display_name': 'Moisture', 'unit': '%'}}
    param_order defines the display order of parameters.
    """
    id: int
    name: str
    algo_id: int
    param_config: dict[str, dict[str, str]]
    param_order: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(slots=True)
class ScanResult:
    """Single parameter prediction result from a scan."""
    parameter_name: str
    predicted_value: float


@dataclasses.dataclass(slots=True)
class Scan:
    """
    Scan record containing NIR scan metadata and results.
    Results are populated from the ScanResults table.
    """
    id: int
    user_id: str
    device_id: str
    widget_id: int
    algo_id: int
    sampled_at: datetime
    results: list[ScanResult] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(slots=True)
class ScanReportRow:
    """Flattened structure for the scan analysis report output."""
    sampled_at: datetime
    user_id: str
    device_id: str
    widget_name: str
    algo_name: str
    formatted_results: str  # e.g., "{Protein: 12.5 %, Moisture: 22.10}"
