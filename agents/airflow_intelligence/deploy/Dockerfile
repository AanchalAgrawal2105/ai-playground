FROM python:3.9-slim

# Set labels
LABEL maintainer="Aanchal Agrawal" \
      version="2.0.0" \
      description="Airflow Intelligence Agent - Autonomous AI monitoring"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 agent && \
    chown -R agent:agent /app && \
    mkdir -p /app/.agent_memory && \
    chown -R agent:agent /app/.agent_memory

# Switch to non-root user
USER agent

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.core import AgentConfig; print('healthy')" || exit 1

# Expose port (if needed for future web UI)
EXPOSE 8080

# Default command - proactive monitoring
CMD ["python", "-m", "src", "proactive", "--interval", "15"]
