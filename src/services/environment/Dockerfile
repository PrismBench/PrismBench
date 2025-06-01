FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for configuration files and test outputs
RUN mkdir -p /app/configs /app/test_outputs

# Set environment variables
ARG ENV_FILE=.env
ENV PYTHONPATH=/app \
    CONFIG_FILE_PATH=/app/configs/agents.yml \
    TEST_OUTPUT_DIR=/app/test_outputs

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "5", "--max-requests", "100", "--max-requests-jitter", "15", "--timeout", "30"]