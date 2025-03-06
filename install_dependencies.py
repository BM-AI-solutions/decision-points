# Updated install_dependencies.py
import subprocess
import sys
import os
import platform

def install_dependencies():
    """Install all required project dependencies."""
    print("Installing Python dependencies...")

    # Check Python version
    python_version = sys.version_info
    print(f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Special handling for Python 3.12+ which removed distutils
    if python_version.major == 3 and python_version.minor >= 12:
        print("Python 3.12+ detected. Installing setuptools first...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "pip", "wheel"])
        except subprocess.CalledProcessError:
            print("Error: Failed to install setuptools")
            return False

    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not in PATH")
        return False

    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        except subprocess.CalledProcessError:
            print("Error: Failed to create virtual environment")
            return False

    # Determine the pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")

    # Upgrade pip in the virtual environment
    try:
        print("Upgrading pip in virtual environment...")
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    except subprocess.CalledProcessError:
        print("Error: Failed to upgrade pip")
        return False

    # Create a modified requirements file that works with Python 3.13
    create_compatible_requirements()

    # Install dependencies from the modified requirements file
    try:
        print("Installing dependencies...")
        subprocess.check_call([pip_path, "install", "-r", "backend/requirements.txt.compatible"])
        print("Successfully installed dependencies!")

        # Print activation instructions
        if os.name == 'nt':  # Windows
            print("\nTo activate the virtual environment, run:")
            print("venv\\Scripts\\activate")
        else:  # Unix/Linux/Mac
            print("\nTo activate the virtual environment, run:")
            print("source venv/bin/activate")

        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        return False

def create_compatible_requirements():
    """Create a modified requirements file that works with Python 3.13."""
    print("Creating compatible requirements file...")

    # Define problematic packages and their compatible replacements
    replacements = {
        "numpy==1.24.4": "numpy>=1.25.0",
        "aiohttp==3.8.5": "aiohttp>=3.8.6",
        "pydantic-ai==0.0.32": "pydantic-ai>=0.0.32",
        "langchain==0.0.312": "langchain>=0.0.312",
    }

    with open("backend/requirements.txt", "r") as f:
        requirements = f.readlines()

    with open("backend/requirements.txt.compatible", "w") as f:
        # Add necessary packages for Python 3.12+
        f.write("setuptools>=68.0.0\n")
        f.write("wheel>=0.40.0\n")

        for req in requirements:
            req = req.strip()
            if not req or req.startswith("#"):
                f.write(req + "\n")
                continue

            # Replace problematic packages
            for old, new in replacements.items():
                if req.startswith(old.split("==")[0]):
                    req = new
                    break

            f.write(req + "\n")

    print("Created compatible requirements file: backend/requirements.txt.compatible")

if __name__ == "__main__":
    install_dependencies()