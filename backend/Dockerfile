# syntax=docker/dockerfile:1

############################
# Base image for dependencies
############################
FROM python:3.10 AS base

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
# RUN pip install --no-cache-dir flask python-dotenv # Removed: Dependencies should be in requirements.txt

# Copy all code (for dev image, but will be mounted in compose)
COPY . .

# Expose port for Uvicorn dev server
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

############################
# Production image
############################
FROM base AS prod

ENV FLASK_ENV=production

# Copy only necessary application files
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY utils/ ./utils/
COPY agents/ ./agents/

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Change ownership of the app directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

EXPOSE 5000

# Corrected CMD to reference the main application object within the app package
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]