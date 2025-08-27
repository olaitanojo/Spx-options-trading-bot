# Multi-stage build for SPX Options Trading Bot
# Production-ready Python application with security best practices

ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim as builder

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Metadata
LABEL maintainer="olaitanojo" \
      description="SPX Options Trading Bot - Advanced algorithmic trading system" \
      version="${VERSION}" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}" \
      org.opencontainers.image.title="SPX Options Trading Bot" \
      org.opencontainers.image.description="Advanced algorithmic trading system for SPX options" \
      org.opencontainers.image.source="https://github.com/olaitanojo/Spx-options-trading-bot" \
      org.opencontainers.image.vendor="olaitanojo" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-prod.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-prod.txt

# Production stage
FROM python:${PYTHON_VERSION}-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid app --shell /bin/bash --create-home app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY requirements.txt requirements-prod.txt ./

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data /app/tmp && \
    chown -R app:app /app && \
    chmod -R 755 /app && \
    chmod -R 777 /app/logs /app/data /app/tmp

# Install health check dependencies
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Switch to non-root user
USER app

# Set runtime environment variables
ENV PYTHONPATH=/app/src \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    METRICS_ENABLED=true \
    PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000 8080 9000

# Define volume mounts
VOLUME ["/app/logs", "/app/data"]

# Entry point with proper signal handling
ENTRYPOINT ["python", "-m", "src.main"]

# Default command arguments
CMD ["--config", "config/production.yml", "--port", "8000"]
