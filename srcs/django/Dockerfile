# Stage 1: Build stage
FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
	postgresql-client \
	libpq-dev \
	build-essential \
	gcc \
	g++ \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
	pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production stage
FROM python:3.10-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	postgresql-client \
	libpq5 \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt-get clean \
	&& apt-get purge -y --auto-remove

# Copy wheels from builder stage and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip && \
	pip install --no-cache /wheels/* && \
	rm -rf /wheels

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
	mkdir -p /app/media /app/logs && \
	chown -R appuser:appuser /app

# Copy project files
COPY . .

# Set permissions and ownership for entrypoint
RUN chmod +x entrypoint.py && \
	chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
	CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

# Run entrypoint
CMD ["python", "entrypoint.py"]
