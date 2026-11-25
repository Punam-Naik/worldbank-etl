# Database Design

## 1. Overview

The project uses PostgreSQL as its persistent storage layer for historical observations retrieved from the World Bank Indicators API.

The database currently consists of one main table:

`public.world_bank_observations`

Each record represents one annual observation for a specific country and indicator.

**Data grain:**

One record per country, indicator, and year.

The table uses a surrogate primary key for record identification and a composite unique constraint to prevent duplicate observations.

## 2. Table Structure

### Table: `world_bank_observations`

| Column | Data Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT | No | Auto-generated primary key |
| country_code | VARCHAR(3) | No | World Bank country code |
| country_name | VARCHAR(100) | No | Country name |
| indicator_code | VARCHAR(30) | No | World Bank indicator code |
| indicator_name | TEXT | No | Indicator description |
| year | INTEGER | No | Observation year |
| value | NUMERIC(30,6) | Yes | Recorded indicator value |
| created_at | TIMESTAMPTZ | No | Record creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update timestamp |

### Primary Key

The `id` column is the primary key.

```sql
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

PostgreSQL automatically generates a unique identifier for each inserted record.

### Composite Unique Constraint

```sql
CONSTRAINT uq_world_bank_observation
    UNIQUE (country_code, indicator_code, year)
```

This constraint ensures that the same country cannot have multiple records for the same indicator and year.

For example, the following combination must be unique:

| Country | Indicator | Year |
|---|---|---|
| IND | SP.POP.TOTL | 2020 |

This supports reliable UPSERT operations during repeated pipeline executions.

## 3. Data Integrity Constraints

The table includes three important integrity rules.

### Observation year

```sql
CHECK (year BETWEEN 1900 AND 2100)
```

Restricts observations to a reasonable year range.

### Country code length

```sql
CHECK (LENGTH(country_code) = 3)
```

Ensures that country codes contain exactly three characters.

### Required fields

The country, indicator, and year fields are declared `NOT NULL`.

The `value` field is nullable because source datasets may contain unavailable observations.

## 4. Indexing Strategy

Two additional indexes are created to support common query patterns.

### Composite index: Country and indicator

```sql
CREATE INDEX IF NOT EXISTS idx_wb_country_indicator
ON public.world_bank_observations
(country_code, indicator_code);
```

Useful for queries filtering by country and indicator.

Example:

```sql
SELECT
    year,
    value
FROM public.world_bank_observations
WHERE country_code = 'IND'
  AND indicator_code = 'SP.POP.TOTL'
ORDER BY year;
```

### Year index

```sql
CREATE INDEX IF NOT EXISTS idx_wb_year
ON public.world_bank_observations (year);
```

Supports queries that filter observations by year.

Example:

```sql
SELECT *
FROM public.world_bank_observations
WHERE year BETWEEN 2015 AND 2024;
```

PostgreSQL also creates an index to enforce the primary key and the composite unique constraint.

## 5. Loading Strategy: UPSERT

The ETL pipeline uses PostgreSQL UPSERT operations to make repeated loads safe against duplicate observations.

The conflict key is:

`country_code + indicator_code + year`

When a new observation is received:

- If the combination does not exist, a new record is inserted.
- If the combination already exists, the existing observation is updated.
- Duplicate records are prevented by the unique constraint.

This supports idempotent loading for the same source observations.

The loading implementation uses batch inserts through `psycopg2.extras.execute_values`.

## 6. Timestamp Management

The table defines two timestamp columns:

- `created_at`: defaults to the current timestamp when a record is inserted.
- `updated_at`: defaults to the current timestamp when a record is inserted.

For existing records, the UPSERT statement must explicitly update `updated_at` when a conflict occurs. The column default alone does not automatically update it.

## 7. Example Analytical Queries

### Retrieve historical population data for India

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

### Calculate year-over-year population growth

```sql
SELECT
    year,
    value AS population,
    LAG(value) OVER (ORDER BY year) AS previous_year_population,
    ROUND(
        100.0 * (
            value - LAG(value) OVER (ORDER BY year)
        ) / NULLIF(
            LAG(value) OVER (ORDER BY year), 0
        ),
        2
    ) AS growth_percentage
FROM public.world_bank_observations
WHERE country_code = 'IND'
  AND indicator_code = 'SP.POP.TOTL'
ORDER BY year;
```

## 8. Design Summary

The current database design prioritizes simplicity, data integrity, and reliable ingestion.

Key characteristics:

- Single-table observation storage.
- Surrogate primary key.
- Composite unique constraint for business-level uniqueness.
- Explicit data integrity checks.
- Indexes for common filtering patterns.
- Batch loading and UPSERT support.
- Creation and update timestamps.

The design is intentionally kept simple for the current single-country, single-indicator ETL project. More extensive analytical modelling can be explored in a separate data engineering project.