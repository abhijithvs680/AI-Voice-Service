# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy
ENV PORT=8520
ENV ENV=production

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy app and install project
COPY app ./app
COPY main.py ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8520

CMD ["uv", "run", "python", "main.py"]
