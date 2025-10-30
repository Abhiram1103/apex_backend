"""
Simple manual starter - Opens 3 terminal windows
No health checks, just launches the APIs
"""

import subprocess

print("\n" + "="*60)
print("🚀 LAUNCHING ALL 3 APIs")
print("="*60 + "\n")

print("Opening 3 terminal windows...\n")

# Start API 1 - Job Recommendation
print("1️⃣ Starting Job Recommendation API (Port 8000)...")
subprocess.Popen(["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList", "-NoExit", "-Command", "python main.py"])

# Start API 2 - Skill Gap
print("2️⃣ Starting Skill Gap API (Port 8001)...")
subprocess.Popen(["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList", "-NoExit", "-Command", "python skill_gap_api.py"])

# Start API 3 - Chatbot
print("3️⃣ Starting Chatbot API (Port 8002)...")
subprocess.Popen(["powershell", "-Command", "Start-Process", "powershell", "-ArgumentList", "-NoExit", "-Command", "python chatbot_api.py"])

print("\n✅ Launched 3 terminal windows!")
print("\n" + "="*60)
print("📋 NEXT STEPS")
print("="*60)
print("\n⏱️  Wait for models to load:")
print("   • Job API: ~10 seconds")
print("   • Skill Gap API: ~10 seconds")
print("   • Chatbot API: ~60-90 seconds (downloads models first time)")

print("\n✅ Look for these messages in each terminal:")
print("   • 'Uvicorn running on...'")
print("   • 'All models loaded successfully!' (Chatbot)")

print("\n🧪 Then run tests:")
print("   python test_optimized_chatbot.py")

print("\n💡 To stop: Close the terminal windows")
print("="*60 + "\n")
