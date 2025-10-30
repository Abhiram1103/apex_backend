"""Test script for the Skill Gap Analysis API"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health check"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_skill_gap(user_id, top_n=10):
    """Test skill gap analysis"""
    print(f"\n=== Testing Skill Gap Analysis for User: {user_id} ===")
    
    payload = {
        "user_id": user_id,
        "top_n": top_n
    }
    
    response = requests.post(
        f"{BASE_URL}/api/skill-gap",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"User ID: {data['user_id']}")
        print(f"User Skills: {', '.join(data['user_skills'])}")
        print(f"Total Jobs Analyzed: {data['total_jobs_analyzed']}")
        print(f"\nTop {len(data['top_opportunities'])} High-Paying Job Opportunities:")
        print("=" * 120)
        
        for i, opp in enumerate(data['top_opportunities'], 1):
            print(f"\n{i}. {opp['job_role']} at {opp['company']}")
            print(f"   Job ID: {opp['job_id']}")
            print(f"   Average Salary: ₹{opp['average_salary']:,.2f} LPA")
            print(f"   Similarity Score: {opp['similarity_score']:.4f}")
            print(f"   Normalized Salary: {opp['normalized_salary']:.4f}")
            print(f"   Combined Score: {opp['combined_score']:.4f}")
            print(f"   Skills You Need to Learn: {', '.join(opp['skill_gap']) if opp['skill_gap'] else 'None - You have all required skills!'}")
            print("-" * 120)
    else:
        print(f"❌ Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    print("=" * 120)
    print("Skill Gap Analysis API - Test Suite")
    print("=" * 120)
    
    # Test 1: Health Check
    health = test_health()
    
    if not health.get('model_loaded'):
        print("\n⚠️  Model not loaded yet. Please wait for the API to initialize.")
        exit(1)
    
    # Test 2: Skill Gap Analysis
    # Replace with an actual user_id from your database
    test_skill_gap(
        user_id="cde634c5-77c0-4004-834f-4f9caec051e6",
        top_n=5
    )
    
    print("\n" + "=" * 120)
    print("All tests completed!")
    print("=" * 120)
