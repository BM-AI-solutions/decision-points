# syntax=docker/dockerfile:1

############################
# Builder stage
############################
FROM python:3.9-slim-buster AS builder

WORKDIR /app

# Install build tools and system dependencies needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip-tools first
RUN pip install pip-tools

# Copy requirements files
COPY requirements.in .
# Assuming requirements.txt is pre-generated or generated elsewhere
COPY requirements.txt .

# Install dependencies into a target directory
# Using --prefix=/install to isolate packages
# This installs packages into /install/lib/python3.9/site-packages
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

############################
# Development image (inherits installed deps from builder)
# Note: For local dev, volume mounts often override this,
# but it's useful for CI/CD or testing dev builds.
############################
FROM builder AS dev

ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Install any additional dev-specific dependencies directly
# These might already be in requirements.txt, but explicit install is fine too.
RUN pip install flask python-dotenv

# Copy all code (primarily for context, usually mounted in dev)
COPY . .

# Expose port for Flask dev server
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]


############################
# Production image
############################
FROM python:3.9-slim-buster AS prod

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

# Install only runtime system dependencies if absolutely necessary
# Example: RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*
# None seem needed based on current requirements.txt

# Copy installed dependencies from builder stage's install prefix
# This copies the site-packages into the default location for the prod image's python
COPY --from=builder /install/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages/
# Copy executables (like gunicorn) if they were installed into /install/bin
COPY --from=builder /install/bin /usr/local/bin/

# Copy application code
COPY . .

# Set ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

ENV FLASK_ENV=production
# Good practice for logs
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Ensure app:app points to the correct WSGI entry point (e.g., main:app if main.py is the entrypoint)
# Assuming app.py contains the Flask app instance named 'app'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]