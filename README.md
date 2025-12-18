# SCiO Scan‑Analysis Backend (Exercise)

> FastAPI micro‑service that loads SCiO NIR crop‑scan data from Excel, formats the predicted parameters, and exposes
> them via a clean REST API. Built as a layered architecture exercise for the SCiO backend assignment (Dec 2025).

## Features

* 🖇️ Decoupled **API / Domain / Infrastructure** layers.
* 📦 Pure **in‑memory repository** that bootstraps from four Excel files (no DB required).
* ⚡ **FastAPI**1.x + **Uvicorn** for async performance and automatic OpenAPI docs.
* 🔎 **Pandas** parsing & lightweight result‑formatting helper.
* ✅ Comprehensive **pytest** suite (unit & integration).

## Folder Structure

```text
scio_backend/
├── src/
│   ├── api/                   # Transport layer (routers, FastAPI app)
│   │   ├── __init__.py        # App factory + lifespan
│   │   └── v1.py              # /api/v1 routes
│   ├── domain/                # Business‑logic & entities
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── infrastructure/        # Data layer (in‑memory repository)
│   │   └── repository.py
│   ├── settings.py            # Pydantic settings helper
│   └── main.py                # Convenience entry‑point
├── data/                      # Excel sources
│   ├── Algo_data.xlsx
│   ├── Widget_data.xlsx
│   ├── Scan_data.xlsx
│   └── Scan_Results_data.xlsx
├── tests/                     # Pytest suite
│   ├── test_services.py
│   └── test_api.py
├── pyproject.toml             # Poetry / build metadata
└── requirements.txt           # Lock‑file for pip installs
```

## Quick‑Start

```bash
# 1 – Create & activate venv
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2 – Install deps
pip install -r requirements.txt

# 3 – Launch the server
uvicorn src.api:app --reload     # http://localhost:8000/

# 4 – Swagger / ReDoc
open http://localhost:8000/docs
```

## Configuration

All paths can be overridden via env vars (or `.env`):

| Variable        | Default                 | Description                               |
|-----------------|-------------------------|-------------------------------------------|
| `API_V1_PREFIX` | `/api/v1`               | Route prefix                              |
| `DATA_DIR`      | `data`                  | Folder that contains the four Excel files |
| `APP_NAME`      | `SCiO Backend Exercise` | FastAPI title                             |

## API Reference

### `GET /api/v1/reports`

| Query Param | Type              | Notes                 |
|-------------|-------------------|-----------------------|
| `user_id`   | string            | Optional filter       |
| `device_id` | string            | Optional filter       |
| `from_date` | ISO 8601 datetime | Inclusive lower bound |
| `to_date`   | ISO 8601 datetime | Inclusive upper bound |

```bash
# Fetch wheat scans from device d1 during November 2025
curl "http://localhost:8000/api/v1/reports?device_id=d1&widget_name=Wheat&from_date=2025-11-01&to_date=2025-11-30"
```

Sample response:

```json
[
  {
    "sampled_at": "2025-11-20T13:02:05",
    "user_id": "ariel",
    "device_id": "d1",
    "widget_name": "Corn",
    "algo_name": "Corn",
    "results": "{Moisture: 16.5 %}"
  }
]
```

## Data Model

| Entity            | Purpose                                                  |
|-------------------|----------------------------------------------------------|
| **Algo**          | Algorithm metadata (id, name, version)                   |
| **Widget**        | UI config for parameters (`param_config`, `param_order`) |
| **Scan**          | Scan header (user, device, timestamps…)                  |
| **ScanResult**    | Individual parameter prediction                          |
| **ScanReportRow** | Flattened DTO returned by the API                        |

### Result‑Formatting Rules

* Percentages → `"{value} %"` with up to **3 decimals**.
* `float_2_dig` → two decimals wrapped in parentheses, e.g. `"(8.23)"`.
* `float_1_dig` → one decimal, e.g. `"68.7"`.

Parameter order follows `Widget.param_order`; unspecified params are sorted alphabetically.

## Testing

```bash
pytest -q                # Run all 33 tests
pytest tests/test_api.py # Only integration
pytest --cov=src         # Coverage
```


