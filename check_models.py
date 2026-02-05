"""
Quick script to check if Ollama models are installed
"""
import requests
import sys

def check_models():
    print("=" * 50)
    print("  OLLAMA MODEL STATUS CHECKER")
    print("=" * 50)
    print()
    
    try:
        # Check Ollama service
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code != 200:
            print("❌ Ollama service is not responding")
            return False
        
        data = response.json()
        models = data.get("models", [])
        
        if not models:
            print("📥 STATUS: No models installed yet")
            print()
            print("The model is still downloading...")
            print("Please wait for the download to complete.")
            print()
            print("To download manually, run:")
            print('  "%LOCALAPPDATA%\\Programs\\Ollama\\ollama.exe" pull mistral')
            return False
        
        # Models found!
        print(f"✅ STATUS: {len(models)} model(s) installed!")
        print()
        print("Installed models:")
        for i, model in enumerate(models, 1):
            name = model.get("name", "unknown")
            size = model.get("size", 0)
            size_gb = size / (1024**3)
            print(f"  {i}. {name} ({size_gb:.2f} GB)")
        
        print()
        print("=" * 50)
        print("🎉 Ready to use! Run: start.bat")
        print("=" * 50)
        return True
        
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama")
        print("Make sure Ollama desktop app is running")
        return False

if __name__ == "__main__":
    success = check_models()
    sys.exit(0 if success else 1)
