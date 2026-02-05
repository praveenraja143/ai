import requests
import time
import json

def test():
    print("Direct Ollama Test...")
    start = time.time()
    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate", 
            json={
                "model": "mistral:latest", 
                "prompt": "Say '2+2=4' and nothing else.", 
                "stream": False
            }, 
            timeout=60
        )
        elapsed = time.time() - start
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json().get('response')}")
        print(f"Time taken: {elapsed:.1f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()
