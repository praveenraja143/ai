"""
Quick test script to verify Ollama setup
Run this after installing Ollama and pulling a model
"""
import sys
import requests

def test_ollama():
    print("🔍 Testing Ollama Setup...\n")
    
    # Test 1: Check if Ollama is running
    print("[1/3] Checking if Ollama service is running...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running!")
        else:
            print("❌ Ollama service returned error")
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Ollama service is NOT running!")
        print("\nTo start Ollama, run in a new terminal:")
        print("  ollama serve")
        return False
    
    # Test 2: List available models
    print("\n[2/3] Checking available models...")
    try:
        data = response.json()
        models = data.get("models", [])
        if models:
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model['name']}")
        else:
            print("❌ No models found!")
            print("\nTo download a model, run:")
            print("  ollama pull mistral")
            return False
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False
    
    # Test 3: Test generation with first available model
    print("\n[3/3] Testing AI generation...")
    try:
        model_name = models[0]["name"]
        print(f"Using model: {model_name}")
        
        test_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "Say 'Hello! I am working correctly.' in one sentence.",
                "stream": False
            },
            timeout=30
        )
        
        if test_response.status_code == 200:
            result = test_response.json()
            answer = result.get("response", "")
            print(f"✅ AI Response: {answer.strip()}")
        else:
            print("❌ Failed to generate response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing generation: {e}")
        return False
    
    # All tests passed!
    print("\n" + "="*50)
    print("🎉 SUCCESS! Ollama is ready to use!")
    print("="*50)
    print("\nYou can now run the main application:")
    print("  python app.py")
    print("\nOr use the start script:")
    print("  start.bat")
    return True

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
