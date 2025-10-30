"""Quick test for the API"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test recommendation
print("Testing job recommendations...")
payload = {
    "skills": ["python", "machine learning", "data science"],
    "top_n": 3
}

try:
    response = requests.post(
        f"{BASE_URL}/api/recommend",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success! Found {len(data['recommendations'])} recommendations")
        print(f"Total jobs analyzed: {data['total_jobs_analyzed']}\n")
        
        for i, job in enumerate(data['recommendations'], 1):
            print(f"{i}. {job['job_role']} at {job['company']}")
            print(f"   Job ID: {job['job_id']}")
            print(f"   Category: {job['category']}")
            print(f"   Match Score: {job['similarity_score']:.4f}")
            print()
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Failed to connect: {e}")
