# SCiO Scan Analysis Backend

A FastAPI microservice for NIR crop-scan data analysis. Loads scan data from Excel files, formats predicted parameters based on widget configurations, and exposes results via REST API.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Project Structure

```
scio_backend/
├── src/
│   ├── api/
│   │   ├── __init__.py      # App factory + lifespan
│   │   ├── dependencies.py  # Dependency injection
│   │   └── v1.py            # API routes
│   ├── domain/
│   │   ├── models.py        # Domain entities
│   │   ├── schemas.py       # Pydantic DTOs
│   │   └── services.py      # Business logic
│   ├── infrastructure/
│   │   └── repository.py    # Data access layer
│   ├── utils/
│   │   └── formatting.py    # Value formatting utilities
│   └── settings.py          # Configuration
├── data/                    # Excel data files (required)
│   ├── Algo data.xlsx
│   ├── Widget data.xlsx
│   ├── Scan data.xlsx
│   └── Scan Results data.xlsx
├── tests/
│   ├── test_api.py
│   └── test_services.py
├── main.py
├── pyproject.toml
└── requirements.txt
```

## Installation

### 1. Extract the ZIP File

```bash
unzip scio_backend.zip
cd scio_backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data Files

Ensure the `data/` directory contains the required Excel files:
- `Algo data.xlsx`
- `Widget data.xlsx`
- `Scan data.xlsx`
- `Scan Results data.xlsx`

## Running the Application

### Start the Server

```bash
python main.py
```

The server starts at `http://localhost:8000`.

### Alternative: Using Uvicorn Directly

```bash
uvicorn src.api:app --host localhost --port 8000 --reload
```

The `--reload` flag enables auto-reload during development.

### Access API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/api/v1/openapi.json`
- Interactive docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports` | Get all scan reports |
| GET | `/api/v1/reports/by-user/{user_id}` | Filter by user ID |
| GET | `/api/v1/reports/by-device/{device_id}` | Filter by device ID |
| GET | `/api/v1/reports/by-date-range` | Filter by date range |
| GET | `/api/v1/reports/by-user-and-device` | Filter by user and device |

### Example Requests

```bash
# Get all reports
curl http://localhost:8000/api/v1/reports

# Filter by user
curl http://localhost:8000/api/v1/reports/by-user/user_123

# Filter by date range
curl "http://localhost:8000/api/v1/reports/by-date-range?from_date=2024-01-01&to_date=2024-12-31"
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
# API tests
pytest tests/test_api.py -v

# Service tests
pytest tests/test_services.py -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

## Environment Variables

Create a `.env` file in the project root (optional):

```env
APP_NAME=SCiO Backend Exercise
API_V1_PREFIX=/api/v1
DATA_DIR=data
```

## Deactivating Virtual Environment

When finished:

```bash
deactivate
```