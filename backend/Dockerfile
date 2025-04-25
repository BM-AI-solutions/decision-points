# syntax=docker/dockerfile:1

# Single-stage Dockerfile for Local Development

# Use a suitable Python base image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies (if any are still needed beyond base Python)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
# This will be overwritten by the volume mount in docker-compose.yml for local dev,
# but ensures the image is runnable standalone if needed.
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application in development mode (hot-reloading)
# This will be overridden by the command in docker-compose.yml, but serves as a default.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]