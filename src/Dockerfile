# Enterprise Compliance Filter - Production Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Labels for metadata
LABEL maintainer="Joe3566" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="enterprise-compliance-filter" \
      org.label-schema.description="AI-powered content compliance system" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/Joe3566/enterprise-compliance-filter" \
      org.label-schema.schema-version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-minimal.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent && \
    pip install --no-cache-dir psycopg2-binary redis && \
    pip cache purge

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    FLASK_ENV=production \
    PORT=5000

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Create necessary directories
RUN mkdir -p /var/log/compliance-filter /tmp/uploads /app/cache && \
    chown -R appuser:appuser /var/log/compliance-filter /tmp/uploads /app

# Copy application files
COPY --chown=appuser:appuser . .

# Remove development files
RUN rm -rf tests/ docs/ *.md requirements-dev.txt .git* __pycache__/ *.pyc

# Health check
COPY --chown=appuser:appuser healthcheck.py /app/
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python healthcheck.py || exit 1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE $PORT

# Use tini as init system
ENTRYPOINT ["tini", "--"]

# Default command
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:application"]

# Development stage (optional)
FROM production as development

USER root

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy

# Copy development requirements
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Switch back to appuser
USER appuser

# Override command for development
CMD ["python", "run_secure_demo.py"]