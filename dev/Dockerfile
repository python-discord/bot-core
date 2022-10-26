ARG python_version=3.11

FROM --platform=linux/amd64 ghcr.io/chrislovering/python-poetry-base:$python_version-slim

# Install project dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only dev,main

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Install again, this time with the root project
RUN poetry install --only-root

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
