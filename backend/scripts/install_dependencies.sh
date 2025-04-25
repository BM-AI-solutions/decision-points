#!/bin/bash
# Script to install all required dependencies

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing additional dependencies for ADK and A2A..."
pip install python-dateutil
pip install google-ai-generativelanguage
pip install google-genai
pip install google-adk
pip install python-a2a
pip install fastapi-socketio

echo "Dependencies installed successfully."
