
FROM python:3.10-slim

# Prevent Python from writing bytecode files
ENV PYTHONDONTWRITEBYTECODE=1

# Stream logs directly to container output
ENV PYTHONUNBUFFERED=1

# Application source location
ENV PYTHONPATH=/app/src

WORKDIR /app

# Install dependencies first to improve Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Create a non-root application user
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Run the ETL pipeline
CMD ["python", "-m", "worldbank_etl.pipeline"]
