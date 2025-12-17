# SCiO Backend Exercise – Gil Elbaz

A FastAPI-based backend service for retrieving and filtering NIR scan analysis reports from SCiO crop scanning devices.

## Project Structure

```
scio_project/
├── src/
│   ├── api/                    # API Layer (FastAPI routes)
│   │   ├── __init__.py         # App factory, lifespan management
│   │   └── v1.py               # API v1 endpoints
│   ├── domain/                 # Business Logic Layer
│   │   ├── models.py           # Domain entities (Algo, Widget, Scan, etc.)
│   │   ├── schemas.py          # Pydantic response schemas
│   │   └── services.py         # Business logic (AnalysisService)
│   ├── infrastructure/         # Data Layer
│   │   └── repository.py       # Data access, Excel file loading
│   ├── settings.py             # Configuration management
│   └── main.py                 # Uvicorn entry point
├── tests/
│   ├── test_services.py        # Unit tests for business logic (25 tests)
│   └── test_api.py             # Integration tests for API (8 tests)
├── data/                       # Excel data files
│   ├── Algo_data.xlsx
│   ├── Widget_data.xlsx
│   ├── Scan_data.xlsx
│   └── Scan_Results_data.xlsx
├── requirements.txt            # pip dependencies
└── pyproject.toml              # Project metadata & pytest config
```

## Architecture

The project follows a **layered architecture** with clear separation of concerns:

| Layer              | Location                 | Responsibility                                            |
|--------------------|--------------------------|-----------------------------------------------------------|
| **API**            | `src/api/`               | HTTP handling, request validation, response serialization |
| **Business Logic** | `src/domain/services.py` | Report generation, result formatting                      |
| **Data**           | `src/infrastructure/`    | Data access, Excel parsing                                |
| **Models**         | `src/domain/models.py`   | Domain entities (technology-independent)                  |

## Quick Start

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn src.api:app --reload
```

The API will be available at `http://localhost:8000`

### 4. View API documentation

- Swagger UI: http://localhost:8000/api/v1/openapi.json
- Or use: http://localhost:8000/docs (if enabled)

## API Endpoints

### GET /api/v1/reports

Retrieve scan analysis reports with optional filters.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | Filter by user ID |
| `device_id` | string | Filter by device ID |
| `from_date` | datetime | Filter scans from this date (inclusive) |
| `to_date` | datetime | Filter scans until this date (inclusive) |

**Example Requests:**

```bash
# Get all reports
curl http://localhost:8000/api/v1/reports

# Filter by user
curl http://localhost:8000/api/v1/reports?user_id=ariel

# Filter by device
curl http://localhost:8000/api/v1/reports?device_id=d1

# Filter by date range
curl "http://localhost:8000/api/v1/reports?from_date=2025-11-01T00:00:00&to_date=2025-11-30T23:59:59"

# Combined filters
curl "http://localhost:8000/api/v1/reports?user_id=ariel&device_id=d1"
```

**Example Response:**

```json
[
  {
    "sampled_at": "2025-11-20T13:02:05",
    "user_id": "ariel",
    "device_id": "d1",
    "widget_name": "Corn",
    "algo_name": "Corn",
    "results": "{Moisture: 16.5 %}"
  },
  {
    "sampled_at": "2025-11-13T11:59:04",
    "user_id": "dan",
    "device_id": "d1",
    "widget_name": "Wheat",
    "algo_name": "Wheat",
    "results": "{Protein: 12.50, Moisture: 22.1 %}"
  }
]
```

## Running Tests

```bash
# Run all tests
pytest -v

# Run only business logic tests
pytest tests/test_services.py -v

# Run only API tests
pytest tests/test_api.py -v

# Run with coverage (if pytest-cov installed)
pytest --cov=src -v
```

**Test Summary:**

- `test_services.py`: 25 unit tests covering filtering, formatting, edge cases
- `test_api.py`: 8 integration tests for the REST endpoint

## Data Model

### Entities

- **Algo**: ML algorithm definition (id, name, version)
- **Widget**: Display configuration for scan parameters (id, name, algo_id, param_config, param_order)
- **Scan**: Scan record with metadata (id, user_id, device_id, widget_id, algo_id, sampled_at)
- **ScanResult**: Individual parameter prediction (parameter_name, predicted_value)

### Result Formatting

Results are formatted based on widget configuration:

- `%` → `"14.5 %"`
- `float_2_dig` → `"8.23"` (2 decimal places)
- `float_1_dig` → `"68.7"` (1 decimal place)

Parameters are displayed in the order specified by `param_order` in the widget configuration.

## Configuration

Settings are managed via `src/settings.py` and can be overridden with environment variables or a `.env` file:

```env
APP_NAME=SCiO Backend Exercise
API_V1_PREFIX=/api/v1
DATA_DIR=data
```

## Dependencies

See `requirements.txt` for the full list. Key dependencies:

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and settings
- **Pandas**: Excel file reading
- **openpyxl**: Excel file support for pandas
- **pytest**: Testing framework
- **httpx**: HTTP client for API testing (required by FastAPI TestClient)