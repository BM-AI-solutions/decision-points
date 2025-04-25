# syntax=docker/dockerfile:1

# Use the same base Python image as the main backend
FROM python:3.10 AS base

WORKDIR /app

# Install system dependencies (if any specific to the agent are needed)
# RUN apt-get update && apt-get install -y --no-install-recommends <packages> && rm -rf /var/lib/apt/lists/*

# Copy the main requirements file and install dependencies
# Assumes WebSearchAgent dependencies are included in the main requirements.txt
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary source code, maintaining directory structure for imports
# Copy the root package init
COPY ../__init__.py ./backend/__init__.py
# Copy the app package init and config
COPY ../app/__init__.py ./backend/app/__init__.py
COPY ../app/config.py ./backend/app/config.py
# Copy the agents package init and the specific agent code
COPY agents/__init__.py ./backend/agents/__init__.py
COPY agents/agent_web_search.py ./backend/agents/agent_web_search.py

# Set PYTHONPATH to ensure the 'backend' package is discoverable
ENV PYTHONPATH=/app

# Expose the port the agent will listen on (defaulting to 8080 for ADK serve)
EXPOSE 8080

# Command to run the agent using adk api_server
# Corrected: Removed invalid --host argument
CMD ["adk", "api_server", "backend.agents.agent_web_search:WebSearchAgent", "--port", "8080"]