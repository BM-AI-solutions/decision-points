# syntax=docker/dockerfile:1

# Single-stage Dockerfile for Web Search Agent (Local Development)

# Use the same base Python image as the main backend
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure Python can find modules in the mounted volume structure
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies (if any specific to the agent are needed)
# RUN apt-get update && apt-get install -y --no-install-recommends <packages> && rm -rf /var/lib/apt/lists/*

# Copy the main requirements file from the parent directory and install dependencies
# Assumes WebSearchAgent dependencies AND ADK are included in the main requirements.txt
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary source code for context within the image build.
# This will be largely overwritten by volume mounts in docker-compose.yml for local dev,
# but helps ensure imports might work if run standalone.
# Copying selectively to keep image smaller if run without volumes.
COPY ../__init__.py ./backend/__init__.py
COPY ../app/__init__.py ./backend/app/__init__.py
COPY ../app/config.py ./backend/app/
COPY ../utils ./backend/utils/
COPY agents/__init__.py ./backend/agents/__init__.py
COPY agents/web_search_agent.py ./backend/agents/web_search_agent.py

# Expose the default port the agent's A2A server will listen on
EXPOSE 8080

# Default command to run the agent's A2A server
# This will likely be overridden by the command in docker-compose.yml for development.
# Assumes the agent script itself starts the server (e.g., using FastAPI/Uvicorn or ADK's server).
CMD ["python", "backend/agents/web_search_agent.py", "--port", "8080"]