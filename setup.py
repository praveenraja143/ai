"""
Automated Setup Script for Educational AI Platform
Installs dependencies and configures the system
"""
import subprocess
import sys
import platform
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(command, description, check=True):
    """Run a shell command with error handling"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True


def install_ollama():
    """Install Ollama based on the operating system"""
    print_header("Installing Ollama")
    
    system = platform.system()
    
    if system == "Windows":
        print("📥 Please install Ollama manually:")
        print("   1. Visit: https://ollama.ai/download")
        print("   2. Download Ollama for Windows")
        print("   3. Run the installer")
        print("   4. After installation, run: ollama serve")
        print("\nPress Enter after you've installed Ollama...")
        input()
        return True
    
    elif system == "Darwin":  # macOS
        print("Installing Ollama on macOS...")
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama",
            check=False
        )
    
    elif system == "Linux":
        print("Installing Ollama on Linux...")
        return run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama",
            check=False
        )
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False


def check_ollama_running():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def start_ollama():
    """Start Ollama service"""
    print_header("Starting Ollama Service")
    
    if check_ollama_running():
        print("✅ Ollama is already running")
        return True
    
    system = platform.system()
    
    if system == "Windows":
        print("Please start Ollama manually:")
        print("   Run: ollama serve")
        print("\nPress Enter after starting Ollama...")
        input()
        return check_ollama_running()
    else:
        # On Unix systems, try to start in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        import time
        time.sleep(3)
        return check_ollama_running()


def pull_model(model_name="mistral"):
    """Download the LLM model"""
    print_header(f"Downloading Model: {model_name}")
    
    print(f"⏳ Downloading {model_name} (this may take several minutes)...")
    print("   Model size: ~4-7 GB")
    
    return run_command(
        f"ollama pull {model_name}",
        f"Downloading {model_name}",
        check=False
    )


def install_python_dependencies():
    """Install Python packages"""
    print_header("Installing Python Dependencies")
    
    # Upgrade pip
    run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip",
        check=False
    )
    
    # Install requirements
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python packages"
    )


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    dirs = ["videos", "temp"]
    for dir_name in dirs:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    return True


def verify_installation():
    """Verify that everything is installed correctly"""
    print_header("Verifying Installation")
    
    checks = {
        "Python packages": False,
        "Ollama running": False,
        "Model available": False
    }
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import manim
        checks["Python packages"] = True
        print("✅ Python packages installed")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
    
    # Check Ollama
    if check_ollama_running():
        checks["Ollama running"] = True
        print("✅ Ollama is running")
        
        # Check model
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any("mistral" in m["name"] for m in models):
                    checks["Model available"] = True
                    print("✅ Model is available")
                else:
                    print("❌ Model not found")
        except:
            print("❌ Could not check models")
    else:
        print("❌ Ollama is not running")
    
    return all(checks.values())


def main():
    """Main setup process"""
    print_header("Educational AI Platform - Setup")
    print("This script will install and configure all dependencies.")
    print("Estimated time: 10-20 minutes (depending on internet speed)")
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Install Python dependencies
    if not install_python_dependencies():
        print("\n⚠️  Failed to install Python dependencies")
        print("   Please run manually: pip install -r requirements.txt")
    
    # Step 4: Install Ollama
    print("\n" + "=" * 60)
    print("Do you want to install Ollama? (y/n)")
    print("(Skip if already installed)")
    print("=" * 60)
    choice = input("> ").lower()
    
    if choice == 'y':
        install_ollama()
    
    # Step 5: Start Ollama
    if not start_ollama():
        print("\n⚠️  Could not start Ollama")
        print("   Please start manually: ollama serve")
    
    # Step 6: Download model
    if check_ollama_running():
        print("\n" + "=" * 60)
        print("Which model would you like to use?")
        print("1. mistral (7B - Recommended)")
        print("2. llama3 (8B - High quality)")
        print("3. phi3 (3.8B - Lightweight)")
        print("=" * 60)
        choice = input("> ").strip()
        
        model_map = {
            "1": "mistral",
            "2": "llama3",
            "3": "phi3"
        }
        
        model = model_map.get(choice, "mistral")
        pull_model(model)
    
    # Step 7: Verify installation
    if verify_installation():
        print_header("Setup Complete! 🎉")
        print("Everything is ready to go!")
        print("\nTo start the application:")
        print("   python app.py")
        print("\nThen open your browser to:")
        print("   http://localhost:8000")
    else:
        print_header("Setup Incomplete")
        print("Some components failed to install.")
        print("Please check the errors above and try again.")
        print("\nFor manual setup, see README.md")


if __name__ == "__main__":
    main()
