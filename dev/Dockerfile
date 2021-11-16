FROM python:3.9-slim

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

ENTRYPOINT ["/bin/bash"]
CMD ["./docker-entrypoint.sh"]

# Install poetry
RUN pip install -U poetry

RUN mkdir bot
WORKDIR /bot

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Copy the source code in last to optimize rebuilding the image
COPY . .
