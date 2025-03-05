import subprocess
import sys
import os

def install_dependencies():
    """Install all required project dependencies."""
    print("Installing Python dependencies...")

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
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")

    # Install dependencies from requirements.txt
    try:
        subprocess.check_call([pip_path, "install", "-r", "backend/requirements.txt"])
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

if __name__ == "__main__":
    install_dependencies()