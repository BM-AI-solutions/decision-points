import os
import shutil
from pathlib import Path

# Define directories to create
directories = [
    "frontend/css",
    "frontend/js",
    "frontend/images",
    "backend/modules",
    "backend/models",
    "backend/utils",
    "backend/routes",
    "backend/tests",
    "workers"
]

# Create directories
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Files to rename/move
files_to_move = [
    ("agent.py", "backend/legacy_agent.py"),
    ("agent_tools.py", "backend/legacy_agent_tools.py"),
    ("agent_prompts.py", "backend/legacy_agent_prompts.py")
]

# Move files
for src, dest in files_to_move:
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f"Moved {src} to {dest}")

# Create empty file if it doesn't exist
def create_empty_file(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            pass
        print(f"Created empty file: {filepath}")

# Create all required files if they don't exist yet
required_files = [
    "backend/app.py",
    "backend/config.py",
    "backend/requirements.txt",
    "backend/modules/__init__.py",
    "backend/models/__init__.py",
    "backend/utils/__init__.py",
    "backend/routes/__init__.py",
    "backend/tests/__init__.py",
    "workers/api-proxy.js",
    "frontend/index.html",
    "frontend/css/styles.css",
    "frontend/js/main.js",
    "frontend/images/logo.svg",
    "frontend/images/hero-image.svg"
]

for file in required_files:
    create_empty_file(file)

print("\nProject structure organized successfully!")
print("You can now copy the code for each file from the documentation.")