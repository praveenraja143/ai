"""
Complete Diagnostic Script for Educational AI Platform
Run this to identify all issues with your setup
"""
import subprocess
import sys
import requests
import os
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_file_exists(filename):
    """Check if a required file exists"""
    exists = Path(filename).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def run_test(description, test_func):
    """Run a test and print results"""
    print(f"\n🔍 {description}")
    try:
        result = test_func()
        if result:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")
        return result
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

print_section("EDUCATIONAL AI PLATFORM - DIAGNOSTIC TOOL")
print("This script will identify all issues with your setup.\n")

all_checks = []

# ============================================================
# CHECK 1: Required Files
# ============================================================
print_section("CHECK 1: Required Files")

required_files = [
    "app.py",
    "llm_engine.py",
    "animation_generator.py",
    "simple_video_generator.py",
    "config.py",
    "index.html",
    "script.js",
    "style.css",
    "requirements.txt"
]

files_ok = True
for file in required_files:
    if not check_file_exists(file):
        files_ok = False

all_checks.append(("Required Files", files_ok))

# ============================================================
# CHECK 2: Python Version
# ============================================================
print_section("CHECK 2: Python Version")

version = sys.version_info
print(f"Python version: {version.major}.{version.minor}.{version.micro}")

python_ok = version.major >= 3 and version.minor >= 10
if python_ok:
    print("✅ Python 3.10+ detected")
else:
    print("❌ Python 3.10+ required")

all_checks.append(("Python Version", python_ok))

# ============================================================
# CHECK 3: Python Packages
# ============================================================
print_section("CHECK 3: Python Packages")

required_packages = [
    "fastapi",
    "uvicorn",
    "requests",
    "cv2",  # opencv-python
    "numpy"
]

packages_ok = True
for package in required_packages:
    try:
        if package == "cv2":
            import cv2
            print(f"✅ opencv-python (cv2)")
        else:
            __import__(package)
            print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - NOT INSTALLED")
        packages_ok = False

all_checks.append(("Python Packages", packages_ok))

# ============================================================
# CHECK 4: Ollama Installation
# ============================================================
print_section("CHECK 4: Ollama Installation")

def check_ollama_installed():
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            return True
    except:
        pass
    print("❌ Ollama not installed")
    return False

ollama_installed = check_ollama_installed()
all_checks.append(("Ollama Installed", ollama_installed))

# ============================================================
# CHECK 5: Ollama Running
# ============================================================
print_section("CHECK 5: Ollama Service Running")

def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
    except:
        pass
    print("❌ Ollama service is NOT running")
    print("   Start it with: ollama serve")
    return False

ollama_running = check_ollama_running()
all_checks.append(("Ollama Running", ollama_running))

# ============================================================
# CHECK 6: Models Available
# ============================================================
print_section("CHECK 6: AI Models Available")

models_ok = False
if ollama_running:
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        models = data.get("models", [])
        
        if models:
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model['name']}")
            
            # Check for mistral specifically
            has_mistral = any("mistral" in m["name"].lower() for m in models)
            if has_mistral:
                print("\n✅ Mistral model found!")
                models_ok = True
            else:
                print("\n⚠️  Mistral model not found")
                print("   Download with: ollama pull mistral")
        else:
            print("❌ No models found")
            print("   Download mistral with: ollama pull mistral")
    except Exception as e:
        print(f"❌ Error checking models: {e}")
else:
    print("⏭️  Skipped (Ollama not running)")

all_checks.append(("Models Available", models_ok))

# ============================================================
# CHECK 7: Directories
# ============================================================
print_section("CHECK 7: Required Directories")

required_dirs = ["videos", "temp"]
dirs_ok = True

for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"✅ {dir_name}/")
    else:
        print(f"⚠️  {dir_name}/ - creating...")
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ Created {dir_name}/")

all_checks.append(("Directories", True))

# ============================================================
# CHECK 8: Test LLM Generation
# ============================================================
print_section("CHECK 8: Test LLM Generation")

if ollama_running and models_ok:
    try:
        print("Testing generation with Mistral...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": "Say 'Hello, I am working!' in one sentence.",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            print(f"✅ LLM Response: {answer[:100]}...")
            llm_ok = True
        else:
            print(f"❌ LLM returned status {response.status_code}")
            llm_ok = False
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        llm_ok = False
else:
    print("⏭️  Skipped (prerequisites not met)")
    llm_ok = False

all_checks.append(("LLM Generation", llm_ok))

# ============================================================
# FINAL SUMMARY
# ============================================================
print_section("DIAGNOSTIC SUMMARY")

print("\nResults:")
for check_name, passed in all_checks:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} - {check_name}")

all_passed = all(passed for _, passed in all_checks)

print("\n" + "=" * 70)
if all_passed:
    print("🎉 ALL CHECKS PASSED! Your system is ready!")
    print("=" * 70)
    print("\nTo start the application:")
    print("  1. Run: python app.py")
    print("  2. Open: http://localhost:8000")
else:
    print("⚠️  SOME CHECKS FAILED")
    print("=" * 70)
    print("\n📋 NEXT STEPS:\n")
    
    for check_name, passed in all_checks:
        if not passed:
            print(f"❌ {check_name}:")
            
            if check_name == "Required Files":
                print("   → Make sure llm_engine.py is in your project folder")
            
            elif check_name == "Python Version":
                print("   → Install Python 3.10 or higher from python.org")
            
            elif check_name == "Python Packages":
                print("   → Run: pip install -r requirements.txt")
                print("   → Or: python -m pip install fastapi uvicorn requests opencv-python numpy")
            
            elif check_name == "Ollama Installed":
                print("   → Download from: https://ollama.ai/download")
                print("   → Install Ollama for Windows")
            
            elif check_name == "Ollama Running":
                print("   → Open a new terminal")
                print("   → Run: ollama serve")
                print("   → Keep it running in the background")
            
            elif check_name == "Models Available":
                print("   → Run: ollama pull mistral")
                print("   → Wait for download to complete (~4GB)")
            
            elif check_name == "LLM Generation":
                print("   → Make sure Ollama is running: ollama serve")
                print("   → Try running: ollama run mistral")
            
            print()

print("\n💡 TIP: Run this diagnostic again after fixing issues!")
print("=" * 70)
