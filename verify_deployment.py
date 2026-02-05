import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000"

def wait_for_server(timeout=30):
    print(f"Waiting for server at {BASE_URL}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                print("✅ Server is UP!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("❌ Server timed out.")
    return False

def test_video_generation():
    print("\nTesting Video Generation API...")
    payload = {"text": "Explain the concept of gravity briefly."}
    
    try:
        # Ask question
        print("Sending generation request...")
        response = requests.post(f"{BASE_URL}/api/ask", json=payload)
        
        if response.status_code != 200:
            print(f"❌ API Request Failed: {response.status_code}")
            print(response.text)
            return False
            
        data = response.json()
        task_id = data.get("task_id")
        if not task_id:
            print("❌ No task_id returned")
            return False
            
        print(f"Task ID: {task_id}")
        
        # Poll for completion
        print("Polling for completion...")
        for _ in range(60): # Wait up to 60 seconds
            status_res = requests.get(f"{BASE_URL}/api/status/{task_id}")
            if status_res.status_code == 200:
                status_data = status_res.json()
                status = status_data.get("status")
                print(f"Status: {status}")
                
                if status == "completed":
                    video_url = status_data.get("video_url")
                    print(f"✅ Video Generated! URL: {video_url}")
                    return True
                elif status == "failed":
                    error = status_data.get("error")
                    print(f"❌ Video Generation Failed: {error}")
                    return False
            time.sleep(1)
            
        print("❌ Video generation timed out.")
        return False
        
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

if __name__ == "__main__":
    if wait_for_server():
        success = test_video_generation()
        if success:
            print("\n🎉 ALL TESTS PASSED! System is ready.")
            sys.exit(0)
        else:
            print("\n⚠️ Tests Failed.")
            sys.exit(1)
    else:
        sys.exit(1)
