# syntax=docker/dockerfile:1

############################
# Base image for dependencies
############################
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

############################
# Development image
############################
FROM base AS dev

ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Install dev dependencies (if any)
RUN pip install --no-cache-dir flask python-dotenv

# Copy all code (for dev image, but will be mounted in compose)
COPY . .

# Expose port for Flask dev server
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

############################
# Production image
############################
FROM base AS prod

ENV FLASK_ENV=production

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]