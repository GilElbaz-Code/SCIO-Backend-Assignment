# SCiO Scan‑Analysis Backend (Exercise)

> **Note:** The answers to the theoretical questions (Part 1) are provided in the separate PDF file: `Exercise for Software Backend Answers - Gil Elbaz.pdf`.

This is a FastAPI micro‑service that loads SCiO NIR crop‑scan data from Excel, formats the predicted parameters, and exposes them via a clean REST API. Built as a layered architecture exercise for the SCiO backend assignment (Dec 2025).

## Features

* 🖇️ Decoupled **API / Domain / Infrastructure** layers.
* 📦 Pure **in‑memory repository** that bootstraps from four Excel files (no DB required).
* ⚡ **FastAPI** + **Uvicorn** for async performance and automatic OpenAPI docs.
* 🔎 **Pandas** parsing & lightweight result‑formatting helper.
* ✅ Comprehensive **pytest** suite (unit & integration).

## Folder Structure

```text
scio_backend/
├── src/
│   ├── api/                   # Transport layer (routers, FastAPI app)
│   │   ├── __init__.py        # App factory + lifespan
│   │   └── v1.py              # /api/v1 routes
│   ├── domain/                # Business‑logic & entities
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── infrastructure/        # Data layer (in‑memory repository)
│   │   └── repository.py
│   ├── settings.py            # Pydantic settings helper
│   └── __init__.py
├── data/                      # Excel sources (Must be present)
│   ├── Algo_data.xlsx
│   ├── Widget_data.xlsx
│   ├── Scan_data.xlsx
│   └── Scan_Results_data.xlsx
├── tests/                     # Pytest suite
│   ├── test_services.py       # Business Logic Unit Tests
│   └── test_api.py            # API Integration Tests
├── main.py                    # Application Entry Point
├── pyproject.toml             # Config
└── requirements.txt           # Dependency lock-file