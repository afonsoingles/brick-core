FROM python:3.13-slim

ARG GIT_SHA
ARG APP_VERSION

ENV GIT_SHA=${GIT_SHA}
ENV APP_VERSION=${APP_VERSION}
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Doppler CLI
RUN curl -Ls https://cli.doppler.com/install.sh | sh


RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen
COPY . .

EXPOSE 8000

LABEL org.opencontainers.image.source https://github.com/afonsoingles/brick-core