"""
Quick test for the new optimized chatbot API
Tests all 6 intents with better performance
"""

import requests
import json
import time

CHATBOT_API = "http://localhost:8002/api/chat"
TEST_USER_ID = "test_user_123"

def test_intent(query: str, description: str):
    """Test a single query and measure response time"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"{'='*60}")
    print(f"Query: {query}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            CHATBOT_API,
            json={"user_id": TEST_USER_ID, "query": query},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success (Response time: {elapsed:.2f}s)")
            print(f"Intent detected: {data['intent']}")
            print(f"\nResponse:\n{data['response']}")
            
            if data.get('extracted_skills'):
                print(f"\nExtracted skills: {', '.join(data['extracted_skills'])}")
            
            if data.get('job_recommendations'):
                print(f"\nJob recommendations: {len(data['job_recommendations'])} jobs")
            
            if data.get('skill_gap_analysis'):
                print(f"\nSkill gap analysis: ✅ Available")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏱️ TIMEOUT after {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🚀 OPTIMIZED CHATBOT API TEST")
    print("="*60)
    
    # Check if API is running
    try:
        health = requests.get("http://localhost:8002/health", timeout=5)
        if health.status_code == 200:
            print("✅ API is running")
            print(f"Models loaded: {health.json()}")
        else:
            print("⚠️ API health check failed")
            return
    except:
        print("❌ API is not running. Please start it first:")
        print("   python chatbot_api.py")
        return
    
    # Test cases for all 6 intents
    tests = [
        ("I want to add Python and React to my skills", "Add Skills"),
        ("Show me job recommendations", "Show Jobs"),
        ("What skills do I need for high paying jobs?", "Skill Gap Analysis"),
        ("What's the average salary I can get?", "Salary Information"),
        ("Should I learn machine learning or web development?", "Career Advice"),
        ("Hello, how are you?", "General Query")
    ]
    
    results = []
    total_start = time.time()
    
    for query, description in tests:
        success = test_intent(query, description)
        results.append((description, success))
        time.sleep(1)  # Small delay between tests
    
    total_elapsed = time.time() - total_start
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {desc}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"Average time per test: {total_elapsed/total:.2f}s")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
