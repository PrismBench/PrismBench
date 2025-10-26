FROM prismbench-base:latest

# Copy requirements first for better caching
COPY pyproject.toml .python-version ./

# Install Python dependencies
RUN uv pip install -e . --system \
    && uv cache clean

# Copy the rest of the application
COPY src/ ./src/

# Set environment variables (use ARG for build-time variables if needed)
ARG ENV_FILE=.env
ENV AGENT_CONFIGS_FILE=/app/configs/agents.yml

# Expose the port the app runs on
EXPOSE 8000

WORKDIR /app
# Command to run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "5", "--max-requests", "100", "--max-requests-jitter", "15", "--timeout", "300"]
