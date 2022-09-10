FROM --platform=linux/amd64 python:3.10-slim

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.2.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    APP_DIR="/app"

ENV PATH="$POETRY_HOME/bin:/$APP_DIR/.venv/bin:$PATH"

# Install poetry
RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install --no-install-recommends -y curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python

# Install project dependencies
WORKDIR $APP_DIR
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Install again, this time with the root project
RUN poetry install

ENTRYPOINT ["python"]
CMD ["-m", "bot"]
