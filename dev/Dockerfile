ARG python_version=3.14-slim

FROM python:$python_version AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/

ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy

# Install project dependencies
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --no-install-project --frozen --group dev

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Install again, this time with the root project
RUN uv pip install "pydis_core[all]@."

WORKDIR /app/dev
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
