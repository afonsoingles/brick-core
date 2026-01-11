FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Minimal system deps
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Doppler CLI
RUN curl -Ls https://cli.doppler.com/install.sh | sh

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency definitions first (layer caching)
COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen

# Copy application code
COPY . .

EXPOSE 8000
