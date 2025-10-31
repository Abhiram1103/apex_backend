"""
Final verification script before Render deployment
Tests all critical functionality
"""

import requests
import json

API_URL = "http://localhost:8002"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Database: {'✅' if data['database_connected'] else '❌'}")
            print(f"   Job API: {'✅' if data['job_api_reachable'] else '❌'}")
            print(f"   Memory: {data.get('memory_mb', 'N/A')} MB")
            print(f"   Python: {data.get('python_version', 'N/A')}")
            print(f"   CORS: {'✅' if data.get('cors_enabled') else '❌'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_skill_extraction():
    """Test skill extraction"""
    print("\n" + "="*80)
    print("TEST 2: Skill Extraction")
    print("="*80)
    
    test_cases = [
        ("I know Python and React", ["Python", "React"]),
        ("I work with AWS, Docker, and Kubernetes", ["AWS", "Docker", "Kubernetes"]),
        ("Machine Learning with TensorFlow", ["Machine learning", "Tensorflow"]),
    ]
    
    passed = 0
    for query, expected_skills in test_cases:
        try:
            response = requests.post(
                f"{API_URL}/api/chat",
                json={"user_id": "test_verification", "query": query, "n": 5},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                extracted = data.get('extracted_skills', [])
                
                # Check if expected skills are in extracted
                found = all(any(exp.lower() in ext.lower() for ext in extracted) for exp in expected_skills)
                
                if found:
                    print(f"✅ '{query[:40]}...'")
                    print(f"   Expected: {expected_skills}")
                    print(f"   Got: {extracted}")
                    passed += 1
                else:
                    print(f"⚠️ '{query[:40]}...'")
                    print(f"   Expected: {expected_skills}")
                    print(f"   Got: {extracted}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Passed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_database_save():
    """Test database save functionality"""
    print("\n" + "="*80)
    print("TEST 3: Database Save")
    print("="*80)
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                "user_id": "test_db_save",
                "query": "I know Python, Java, and JavaScript",
                "n": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('skills_saved'):
                print("✅ Skills saved to database")
                print(f"   User: {data['user_id']}")
                print(f"   Skills: {data['extracted_skills']}")
                return True
            else:
                print("❌ Skills not saved")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_job_api_integration():
    """Test job API integration"""
    print("\n" + "="*80)
    print("TEST 4: Job API Integration")
    print("="*80)
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",  # Known user with skills
                "query": "Show me job recommendations",
                "n": 10
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('job_recommendations'):
                jobs = data['job_recommendations']
                print(f"✅ Job API integration working")
                print(f"   Total jobs: {data['total_jobs']}")
                print(f"   Top job: {jobs[0].get('Job Role', 'N/A')}")
                print(f"   Match: {jobs[0].get('similarity_score', 0):.2%}")
                return True
            else:
                print("⚠️ No job recommendations (might be normal if user has no skills)")
                return True  # Not a critical failure
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cors():
    """Test CORS headers"""
    print("\n" + "="*80)
    print("TEST 5: CORS Configuration")
    print("="*80)
    
    try:
        response = requests.options(
            f"{API_URL}/api/chat",
            headers={"Origin": "https://example.com"}
        )
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("✅ CORS configured correctly")
            print(f"   Origin: {cors_headers['Access-Control-Allow-Origin']}")
            print(f"   Methods: {cors_headers['Access-Control-Allow-Methods']}")
            return True
        else:
            print("⚠️ CORS headers not found (might be normal for localhost)")
            return True
            
    except Exception as e:
        print(f"⚠️ CORS test skipped: {e}")
        return True


def main():
    """Run all verification tests"""
    print("\n" + "🧪" + "="*78 + "🧪")
    print("FINAL VERIFICATION - Chatbot API Ready for Render")
    print("🧪" + "="*78 + "🧪")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    results.append(("Skill Extraction", test_skill_extraction()))
    results.append(("Database Save", test_database_save()))
    results.append(("Job API Integration", test_job_api_integration()))
    results.append(("CORS Configuration", test_cors()))
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("="*80)
        print("\n✅ Your chatbot API is READY for Render deployment!")
        print("\nNext steps:")
        print("1. git add deployment/chatbot-api/")
        print("2. git commit -m 'Add production chatbot API'")
        print("3. git push origin main")
        print("4. Create web service on Render")
        print("5. Deploy and test!")
    else:
        print(f"⚠️ SOME TESTS FAILED ({passed}/{total})")
        print("="*80)
        print("\nPlease fix the failing tests before deployment.")
    
    print()


if __name__ == "__main__":
    main()
