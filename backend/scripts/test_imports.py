#!/usr/bin/env python3
"""
Test script to check if all required modules can be imported.
"""

import sys
import importlib

# List of modules to test
modules = [
    "google.generativeai",
    "google.adk",
    "google.adk.agents",
    "google.adk.models",
    "google.adk.cli.web",
    "python_a2a",
]

def test_imports():
    """Test if all required modules can be imported."""
    success = True
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
