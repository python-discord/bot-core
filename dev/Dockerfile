FROM --platform=linux/amd64 ghcr.io/chrislovering/python-poetry-base:3.10-slim


# Install project dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Install again, this time with the root project
RUN poetry install

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
