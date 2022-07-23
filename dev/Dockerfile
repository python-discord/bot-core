FROM python:3.9-slim

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

# Install poetry
RUN pip install -U poetry

WORKDIR /app

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy the source code in last to optimize rebuilding the image
COPY . .
# Install again, this time with the root project
RUN poetry install

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
