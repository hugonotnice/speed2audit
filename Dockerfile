# ==============================================================================
# Speed2Audit - Multi-Agent Mystery Shopper Platform
# ==============================================================================
FROM python:3.12-slim

# Install uv from Astral's official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    CHAINLIT_HOST=0.0.0.0 \
    CHAINLIT_PORT=8000

WORKDIR /app

# Copy dependency specifications first for layer caching
COPY pyproject.toml uv.lock README.md LICENSE /app/

# Install runtime dependencies with uv
RUN uv sync --frozen --no-dev

# Copy application source code
COPY src /app/src

# Expose ports for Chainlit Cockpit (8000) and Arize Phoenix (6006)
EXPOSE 8000 6006

# Run Speed2Audit Cockpit
CMD ["uv", "run", "chainlit", "run", "src/speed2audit/app.py", "--host", "0.0.0.0", "--port", "8000"]
