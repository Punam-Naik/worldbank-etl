# World Bank Data ETL Pipeline

A containerized, automated ETL pipeline that extracts historical population data from the World Bank Indicators API, transforms and validates the records using Python, and loads them into PostgreSQL.

The project demonstrates an end-to-end data engineering workflow covering API integration, data transformation, database loading, automated testing, containerization, and CI/CD.

## Project Overview

The pipeline retrieves historical population observations for India from the World Bank Open Data API.

It processes the API response through a structured ETL workflow:

1. **Extract:** Retrieve historical observations from the World Bank API, including API pagination and retry handling.
2. **Transform:** Flatten nested API responses into structured records.
3. **Validate:** Check required fields, data types, year ranges, negative values, and duplicate records.
4. **Load:** Insert records into PostgreSQL using batch loading and UPSERT operations.

The pipeline is designed to be repeatable, testable, and containerized.

## Dataset Scope

| Attribute | Value |
|---|---|
| Data source | World Bank Indicators API |
| Country | India |
| Country code | IND |
| Indicator | Population, total |
| Indicator code | SP.POP.TOTL |
| Historical period | 2000–2024 |
| Data frequency | Annual |
| Target database | PostgreSQL |

**Data grain:** One observation per country, indicator, and year.

**Expected observations:** Up to 25 annual records for the configured period, subject to source availability.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.10 |
| Data source | World Bank Indicators API |
| HTTP requests | Requests |
| Configuration | python-dotenv |
| Database | PostgreSQL |
| Database integration | psycopg2 |
| Data loading | Batch inserts using execute_values |
| Containerization | Docker |
| Container orchestration | Docker Compose |
| Testing | Pytest |
| Test coverage | pytest-cov |
| Version control | Git and GitHub |
| CI/CD | GitHub Actions |
| Container registry | GitHub Container Registry (GHCR) |

## Architecture

```text
                 World Bank API
                       |
                       v
                Python Extract
              (Pagination / Retry)
                       |
                       v
                 Transformation
              (JSON Flattening)
                       |
                       v
                   Validation
          (Schema / Data Quality Checks)
                       |
                       v
                 PostgreSQL
                (Batch Loading)
                       |
                       v
                UPSERT Strategy
```

### CI/CD Workflow

```text
              GitHub Repository
                      |
                      v
                GitHub Actions
                      |
                      v
              Install Dependencies
                      |
                      v
                 Unit Tests
                      |
                      v
            PostgreSQL Integration Tests
                      |
                      v
                 Docker Build
                      |
                      v
              Publish to GHCR
```

The GitHub Actions workflow runs tests before publishing the Docker image. Pull requests run the build and tests without publishing an image.

## Key Engineering Features

### 1. API Extraction

- Integrates with the World Bank Indicators API.
- Supports paginated API responses.
- Implements configurable request timeouts.
- Includes retry handling for transient request failures.
- Supports configurable country, indicator, and historical date range.

### 2. Data Transformation

- Converts nested API JSON responses into structured records.
- Extracts country and indicator metadata.
- Converts year values into integers.
- Normalizes indicator values into numeric values.
- Handles null observations.

### 3. Data Validation

The validation layer checks:

- Required fields.
- Valid year ranges.
- Negative indicator values.
- Duplicate country-indicator-year combinations.
- Data consistency before database loading.

### 4. PostgreSQL Loading

- Uses PostgreSQL for persistent storage.
- Supports batch inserts through `execute_values`.
- Uses parameterized SQL identifiers for configurable table and schema names.
- Implements UPSERT using the unique key:

  `country_code + indicator_code + year`

- Updates existing observations instead of creating duplicate records.
- Uses database transactions with commit and rollback handling.

### 5. Automated Testing

The project includes unit tests and PostgreSQL integration tests.

**Unit tests** cover configuration, extraction, transformation, validation, logging, and pipeline behavior.

**Integration tests** verify actual PostgreSQL connectivity, inserts, UPSERT behavior, duplicate handling, and transaction rollback.

### 6. Containerization

Docker and Docker Compose provide a reproducible execution environment.

The Compose configuration includes:

- PostgreSQL 16.
- Python ETL application.
- Database health checks.
- Persistent PostgreSQL storage.
- Environment-based configuration.
- Database initialization through the SQL schema.

### 7. CI/CD and Container Publishing

GitHub Actions automates:

- Python environment setup.
- Dependency installation.
- Unit testing.
- PostgreSQL integration testing.
- Docker image building.
- Container publishing to GHCR.

The workflow publishes images for pushes to the main branch and version tags.

## Project Structure

```text
worldbank-etl/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── src/
│   └── worldbank_etl/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       ├── extract.py
│       ├── load.py
│       ├── logger.py
│       ├── pipeline.py
│       ├── transform.py
│       └── validate.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── scripts/
│   └── explore_worldbank.py
│
├── sql/
│   └── schema.sql
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10
- Git
- Docker Desktop
- Docker Compose

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd worldbank-etl
```

### 2. Configure environment variables

Create a local environment file from the example:

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local PostgreSQL credentials and application configuration.

Do not commit `.env` or expose database credentials in the repository.

### 3. Run using Docker Compose

Build and start the application:

```bash
docker compose up --build
```

Docker Compose starts PostgreSQL and runs the ETL application after the database becomes healthy.

Check running containers:

```bash
docker compose ps
```

### 4. Run the pipeline locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set the Python source directory:

```powershell
$env:PYTHONPATH = "src"
```

Execute the pipeline:

```powershell
python -m worldbank_etl.pipeline
```

## Running Tests

### Unit tests

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/unit -v
```

### PostgreSQL integration tests

Start the PostgreSQL service:

```powershell
docker compose up -d postgres
```

Configure the integration test environment:

```powershell
$env:RUN_DB_INTEGRATION_TESTS = "1"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5433"
$env:PYTHONPATH = "src"
```

Run the integration tests:

```powershell
python -m pytest tests/integration -v
```

The integration tests use a dedicated test table and do not modify the production observation table.

## Docker Image

The application image is published to GitHub Container Registry.

```bash
docker pull ghcr.io/punam-naik/worldbank-etl:latest
```

The image can be used independently of the local source-code environment, provided the required database and environment configuration are supplied.

## Example Analytical Queries

Retrieve India's historical population observations:

```sql
SELECT
    country_code,
    country_name,
    indicator_code,
    indicator_name,
    year,
    value
FROM public.world_bank_observations
WHERE country_code = 'IND'
  AND indicator_code = 'SP.POP.TOTL'
ORDER BY year;
```

Calculate year-over-year population growth:

```sql
SELECT
    year,
    value AS population,
    LAG(value) OVER (ORDER BY year) AS previous_year_population,
    ROUND(
        100.0 * (
            value - LAG(value) OVER (ORDER BY year)
        ) / NULLIF(LAG(value) OVER (ORDER BY year), 0),
        2
    ) AS growth_percentage
FROM public.world_bank_observations
WHERE country_code = 'IND'
  AND indicator_code = 'SP.POP.TOTL'
ORDER BY year;
```

## Configuration

Application configuration is managed through environment variables.

The `.env.example` file provides the required configuration structure, including:

- World Bank API settings.
- Country and indicator selection.
- Historical date range.
- HTTP timeout and retry settings.
- PostgreSQL connection details.
- Database schema and table.
- Batch loading configuration.
- Application logging level.

## Project Status

| Component | Status |
|---|---|
| API exploration and source profiling | Complete |
| Python extraction | Complete |
| Transformation and validation | Complete |
| PostgreSQL integration | Complete |
| Batch loading and UPSERT | Complete |
| Unit tests | Complete |
| PostgreSQL integration tests | Complete |
| Docker containerization | Complete |
| Docker Compose setup | Complete |
| GitHub Actions CI/CD | Complete |
| GHCR publishing | Complete |

## Future Improvements

Potential extensions for a separate project or future iteration:

- Multi-country and multi-indicator ingestion.
- Incremental data extraction.
- Apache Airflow orchestration.
- dbt-based analytical transformations.
- Azure Data Lake Storage and Databricks processing.
- Data quality monitoring and observability.

These are not part of the current implementation.

## Data Source and Licensing

Data source: [World Bank Open Data](https://data.worldbank.org/).

API documentation: [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589).

The World Bank provides its data under its applicable data-use terms. Check the source terms when redistributing data.

A separate software license should be added to this repository if you intend to grant others explicit rights to reuse or modify the project code.
