# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Set default environment variables (can be overridden at runtime)
# MongoDB Configuration - REQUIRED
ENV USE_MONGODB=true \
    MONGODB_URI=mongodb://localhost:27017 \
    MONGODB_DATABASE=gamification \
    MONGODB_USERNAME=admin \
    MONGODB_PASSWORD=changeme \
    MONGODB_AUTH_SOURCE=admin

# API Configuration - REQUIRED (set these when running container)
ENV TEAMBOOK_BEARER_TOKEN="" \
    DATASIGHT_BEARER_TOKEN=""

# Application Configuration
ENV SERVICE_LINE_ID=449 \
    MAX_WEEKS_TO_KEEP=5 \
    AUTO_REFRESH_ENABLED=false \
    REFRESH_INTERVAL_HOURS=168

# Streamlit Configuration
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
