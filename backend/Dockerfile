FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for asyncpg and building C extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project definition first for better Docker layer caching
COPY pyproject.toml ./

# Install the project dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# Copy application source code
COPY . .

# Install the project itself (editable not needed in production)
RUN pip install --no-cache-dir --no-deps .

# Create a non-root user for security
RUN groupadd --gid 1000 bluadmin \
    && useradd --uid 1000 --gid bluadmin --shell /bin/bash --create-home bluadmin \
    && chown -R bluadmin:bluadmin /app

# Switch to non-root user
USER bluadmin

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health', timeout=5).raise_for_status()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info"]
