#!/bin/bash
# Script to install all required dependencies

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing additional dependencies for ADK..."
pip install python-dateutil

echo "Dependencies installed successfully."
