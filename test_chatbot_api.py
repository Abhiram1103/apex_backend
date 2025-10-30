"""Test script for Career Chatbot API"""
import requests
import json

BASE_URL = "http://localhost:8002"

def test_health():
    """Test health check"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_chat(user_id, query):
    """Test chat endpoint"""
    print(f"\n{'='*100}")
    print(f"User Query: {query}")
    print('='*100)
    
    payload = {
        "user_id": user_id,
        "query": query
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"Intent Detected: {data['intent']}")
        print(f"\nBot Response:\n{data['response']}")
        
        if data.get('extracted_skills'):
            print(f"\nExtracted Skills: {', '.join(data['extracted_skills'])}")
        
        if data.get('job_recommendations'):
            print(f"\n💼 Job Recommendations: {len(data['job_recommendations'])} jobs found")
            for i, job in enumerate(data['job_recommendations'][:3], 1):
                print(f"  {i}. Job ID: {job['job_id']}, Score: {job['similarity_score']:.4f}")
        
        if data.get('skill_gap_analysis'):
            print(f"\n📊 Skill Gap Analysis: Available in response data")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    print("="*100)
    print("Career Chatbot API - Test Suite")
    print("="*100)
    
    # Health check
    health = test_health()
    
    if not health.get('model_loaded'):
        print("\n⚠️  Model not loaded yet. Please wait for the API to initialize.")
    
    # Test user ID - replace with actual user_id from your database
    test_user_id = "cde634c5-77c0-4004-834f-4f9caec051e6"
    
    # Test 1: Add skills
    test_chat(
        user_id=test_user_id,
        query="I know Python, Machine Learning, and TensorFlow"
    )
    
    # Test 2: Show jobs
    test_chat(
        user_id=test_user_id,
        query="Show me job recommendations"
    )
    
    # Test 3: Add more skills and show jobs
    test_chat(
        user_id=test_user_id,
        query="I also know React, JavaScript, and want to see available jobs"
    )
    
    # Test 4: Career advice
    test_chat(
        user_id=test_user_id,
        query="What should I do to advance my career?"
    )
    
    # Test 5: Skill gap
    test_chat(
        user_id=test_user_id,
        query="What skills do I need to learn for better opportunities?"
    )
    
    # Test 6: Salary info
    test_chat(
        user_id=test_user_id,
        query="Tell me about salary ranges for data scientists"
    )
    
    print("\n" + "="*100)
    print("All tests completed!")
    print("="*100)
