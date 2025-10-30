"""
Start all three APIs in sequence with health checks
"""

import subprocess
import time
import requests
import sys

APIS = [
    {
        "name": "Job Recommendation API",
        "file": "main.py",
        "port": 8000,
        "health_url": "http://localhost:8000/"
    },
    {
        "name": "Skill Gap API",
        "file": "skill_gap_api.py",
        "port": 8001,
        "health_url": "http://localhost:8001/"
    },
    {
        "name": "Chatbot API (Optimized)",
        "file": "chatbot_api.py",
        "port": 8002,
        "health_url": "http://localhost:8002/health"
    }
]

def check_health(url, timeout=5):
    """Check if API is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_api(api_info):
    """Start an API in a new terminal window"""
    print(f"\n🚀 Starting {api_info['name']}...")
    print(f"   File: {api_info['file']}")
    print(f"   Port: {api_info['port']}")
    
    # Start in new PowerShell window
    file_name = api_info['file']
    cmd = f"Start-Process powershell -ArgumentList '-NoExit', '-Command', 'python {file_name}'"
    subprocess.Popen(["powershell", "-Command", cmd], shell=True)
    
    # Wait for API to start
    print(f"   Waiting for API to start", end="")
    
    # Chatbot needs more time for model loading (first run)
    max_wait = 90 if 'chatbot' in api_info['file'].lower() else 30
    for i in range(max_wait):
        time.sleep(1)
        print(".", end="", flush=True)
        
        if check_health(api_info['health_url']):
            print(f" ✅\n   {api_info['name']} is ready!")
            return True
    
    print(f" ⚠️\n   {api_info['name']} didn't respond within {max_wait}s")
    return False

def main():
    print("="*60)
    print("🚀 STARTING ALL APIs")
    print("="*60)
    
    print("\n📋 This will start 3 APIs in separate terminal windows:")
    for api in APIS:
        print(f"   • {api['name']} (Port {api['port']})")
    
    print("\n⚠️  Note: Models will download on first run (~200MB total)")
    print("⏱️  Chatbot API may take 30-60s to load models\n")
    
    input("Press Enter to continue...")
    
    started = []
    
    for api in APIS:
        if start_api(api):
            started.append(api)
        else:
            print(f"\n❌ Failed to start {api['name']}")
            print("   Check if port is already in use or if there are errors")
            break
    
    print("\n" + "="*60)
    print("📊 STATUS SUMMARY")
    print("="*60)
    
    if len(started) == len(APIS):
        print("\n✅ All APIs started successfully!\n")
        
        print("🧪 You can now test:")
        print(f"   • Job Recommendations: http://localhost:8000/docs")
        print(f"   • Skill Gap Analysis: http://localhost:8001/docs")
        print(f"   • Chatbot: http://localhost:8002/docs")
        
        print("\n📝 Run comprehensive test:")
        print("   python test_optimized_chatbot.py")
        
    else:
        print(f"\n⚠️ Only {len(started)}/{len(APIS)} APIs started")
        print("   Please check the terminal windows for errors")
    
    print("\n💡 To stop all APIs: Close the terminal windows")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
