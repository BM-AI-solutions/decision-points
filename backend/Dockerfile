# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=development
ENV DISABLE_KAFKA=true

# Expose port for Uvicorn server
EXPOSE 8000

# The actual code will be mounted as a volume in development
# This is just a placeholder for the Docker build to succeed
RUN mkdir -p /app/app

# Command will be overridden in docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
