# World Bank Data ETL Pipeline

## Overview

A production-oriented ETL pipeline that extracts historical development indicators from the World Bank API, transforms and validates the data, and loads it into PostgreSQL.

## Technology Stack

- Python
- World Bank Indicators API
- PostgreSQL
- Docker & Docker Compose
- GitHub
- GitHub Actions
- Pytest

## Current Scope

- Country: India
- Indicator: Population
- Indicator code: SP.POP.TOTL
- Historical period: 2000–2024

## Architecture

World Bank API → Python Extract → Transform → Validate → PostgreSQL

## Project Status

- [x] API exploration
- [x] Source schema profiling
- [x] Exploratory extraction
- [x] Initial transformation and validation
- [ ] Production extractor
- [ ] PostgreSQL integration
- [ ] Automated tests
- [ ] Docker containerization
- [ ] GitHub CI/CD

## Local Setup

Setup and execution instructions will be added as the pipeline components are implemented.

## License

Data source: World Bank Open Data.
