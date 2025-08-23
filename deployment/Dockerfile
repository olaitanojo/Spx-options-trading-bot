# Multi-stage Docker build for SPX Options Trading Bot
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
COPY deployment/requirements-prod.txt /tmp/

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements-prod.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    TZ=America/New_York

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN groupadd -r trading && useradd -r -g trading -d /app -s /bin/bash trading

# Create application directories
RUN mkdir -p /app/logs /app/data /app/config && \
    chown -R trading:trading /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=trading:trading . .

# Copy deployment configurations
COPY --chown=trading:trading deployment/config/ ./config/
COPY --chown=trading:trading deployment/scripts/ ./scripts/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Health check
COPY deployment/healthcheck.py ./
RUN chmod +x healthcheck.py

# Switch to non-root user
USER trading

# Expose ports
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python healthcheck.py

# Default command
CMD ["python", "scripts/start_production.py"]
