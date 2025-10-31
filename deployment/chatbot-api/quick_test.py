"""Quick test for chatbot API"""
import requests
import json

# Test the API
url = "http://localhost:8002/api/chat"
payload = {
    "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
    "query": "I know Python, Machine Learning, React, and Node.js",
    "n": 10
}

print("Testing Chatbot API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"\nMessage: {data['message']}")
        print(f"\nExtracted Skills: {data['extracted_skills']}")
        print(f"Skills Saved: {data['skills_saved']}")
        print(f"Total Jobs: {data['total_jobs']}")
        
        if data['job_recommendations']:
            print(f"\nTop 3 Job Recommendations:")
            for i, job in enumerate(data['job_recommendations'][:3], 1):
                print(f"\n{i}. {job.get('Job Role', 'N/A')}")
                print(f"   Category: {job.get('Category', 'N/A')}")
                print(f"   Location: {job.get('Location', 'N/A')}")
                print(f"   Match: {job.get('similarity_score', 0):.2%}")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
