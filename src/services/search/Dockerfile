FROM prismbench-base:latest

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    graphviz \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .python-version ./

# Install Python dependencies
RUN uv pip install -e . --system \
    && uv cache clean

# Copy the rest of the application
COPY src/ ./src/

# Set environment variables
ARG ENV_FILE=.env
ENV CONFIG_FILE_PATH=/app/configs/agents.yml \
    TEST_OUTPUT_DIR=/app/test_outputs

# Expose the port the app runs on
EXPOSE 8000

WORKDIR /app
# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
