"""
Test script for the Job Recommendation API
Run this after starting the FastAPI server
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_recommendation(user_id, top_n=10):
    """Test the recommendation endpoint"""
    print(f"\n=== Testing Recommendations for User ID: {user_id} ===")
    
    payload = {
        "user_id": user_id,
        "top_n": top_n
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recommend",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal Jobs Analyzed: {data['total_jobs_analyzed']}")
        print(f"\nTop {len(data['recommendations'])} Recommendations:")
        print("-" * 100)
        
        for i, job in enumerate(data['recommendations'], 1):
            print(f"\n{i}. Job ID: {job['job_id']}")
            print(f"   Similarity Score: {job['similarity_score']:.4f}")
            print("-" * 100)
    else:
        print(f"Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def test_stats():
    """Test the stats endpoint"""
    print("\n=== Testing Stats Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_refresh_cache():
    """Test the cache refresh endpoint"""
    print("\n=== Testing Cache Refresh ===")
    response = requests.post(f"{BASE_URL}/api/refresh-cache")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    print("=" * 100)
    print("Job Recommendation API - Test Suite")
    print("=" * 100)
    
    # Test 1: Health Check
    health = test_health_check()
    
    if not health.get('model_loaded'):
        print("\n⚠️  Model not loaded yet. Please wait for the API to initialize.")
        exit(1)
    
    # Test 2: Get Statistics
    test_stats()
    
    # Test 3: Test with a sample user_id
    # Replace with an actual user_id from your database
    test_recommendation(
        user_id="cde634c5-77c0-4004-834f-4f9caec051e6",
        top_n=5
    )
    
    print("\n" + "=" * 100)
    print("All tests completed!")
    print("=" * 100)
