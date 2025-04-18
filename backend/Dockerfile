# syntax=docker/dockerfile:1

############################
# Base image for dependencies
############################
FROM python:3.9-slim-buster AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip-tools first
RUN pip install pip-tools

# Copy only requirements.in to leverage caching
COPY requirements.in .

# Generate requirements.txt. This layer is invalidated only if requirements.in changes.
RUN pip-compile requirements.in -o requirements.txt --no-header --no-annotate

# Install dependencies using the generated requirements.txt.
# This layer is invalidated only if requirements.txt changes.
# Removed --no-cache-dir to utilize pip cache.
RUN pip install -r requirements.txt

############################
# Development image
############################
FROM base AS dev

ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Install dev dependencies (if any)
# Removed --no-cache-dir
RUN pip install flask python-dotenv

# Copy all code (for dev image, but will be mounted in compose)
# This happens after base dependencies are installed.
COPY . .

# Expose port for Flask dev server
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

############################
# Production image
############################
FROM base AS prod

ENV FLASK_ENV=production

# Copy all code
# This happens after base dependencies are installed.
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]