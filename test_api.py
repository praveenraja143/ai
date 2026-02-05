"""
Test script to diagnose API issues
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Educational AI Platform API")
print("=" * 60)

# Test 1: Health Check
print("\n[1/3] Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"✅ Health check: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Direct Ollama Test
print("\n[2/3] Testing Ollama directly...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    print(f"✅ Ollama is running: {response.status_code}")
    models = response.json()
    print(f"   Available models: {[m['name'] for m in models.get('models', [])]}")
except Exception as e:
    print(f"❌ Ollama test failed: {e}")

# Test 3: Ask Question (with timeout)
print("\n[3/3] Testing /api/ask endpoint...")
print("   Sending question: 'What is baye's theroem?'")
print("   This may take 30-60 seconds...")

try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={"question": "What is 2+2?"},
        headers={"Content-Type": "application/json"},
        timeout=90  # 90 second timeout
    )
    elapsed = time.time() - start_time
    
    print(f"✅ Request completed in {elapsed:.1f} seconds")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Task ID: {data.get('task_id')}")
        print(f"   Answer preview: {data.get('answer', '')[:100]}...")
    else:
        print(f"   Error: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"❌ Request timed out after 90 seconds")
    print("   This suggests Ollama is taking too long to respond")
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
