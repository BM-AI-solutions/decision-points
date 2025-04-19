# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed (e.g., for build tools)
# Add any other dependencies if required by your Python packages
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the backend requirements file first to leverage Docker cache
COPY backend/requirements.txt ./backend/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend application code into the container
COPY ./backend ./backend

# Copy the frontend application code (optional, but good for context if needed later)
COPY ./frontend ./frontend

# Copy other root files if necessary (e.g., .env.example)
COPY ./.env.example ./.env.example

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (optional, can be set in docker-compose.yml)
# Set to production by default
ENV FLASK_ENV=production
# Set the port the app runs on
ENV PORT=5000

# Run app.py when the container launches using Gunicorn
# Assumes 'app' is the Flask application instance within 'backend/app.py'
# Use 0.0.0.0 to ensure the server is accessible externally
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]