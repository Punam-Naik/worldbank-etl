
CREATE TABLE IF NOT EXISTS public.world_bank_observations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    country_code VARCHAR(3) NOT NULL,
    country_name VARCHAR(100) NOT NULL,

    indicator_code VARCHAR(30) NOT NULL,
    indicator_name TEXT NOT NULL,

    year INTEGER NOT NULL,
    value NUMERIC(30, 6),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_world_bank_observation
        UNIQUE (country_code, indicator_code, year),

    CONSTRAINT chk_observation_year
        CHECK (year BETWEEN 1900 AND 2100),

    CONSTRAINT chk_country_code_length
        CHECK (LENGTH(country_code) = 3)
);

CREATE INDEX IF NOT EXISTS idx_wb_country_indicator
ON public.world_bank_observations
(country_code, indicator_code);

CREATE INDEX IF NOT EXISTS idx_wb_year
ON public.world_bank_observations (year);
