# Use official base Python image (Alpine = small & fast)
FROM python:3.10-alpine

# Prevent bytecode files + unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required by Poetry and Python packages
RUN apk add --no-cache curl gcc musl-dev libffi-dev openssl-dev

# Install Poetry (via install script)
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy poetry files and install dependencies (cache-friendly)
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the app
COPY ./src .

# Clean up any __pycache__
RUN find . -type d -name '__pycache__' -exec rm -rf {} +

# Expose the port (if your app listens on one)
EXPOSE 3000

# Run the app
ENTRYPOINT ["python", "main.py"]
