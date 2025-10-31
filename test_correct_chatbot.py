"""
Test script for the correct lightweight chatbot API
Run this to verify the chatbot is working correctly
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8002/api/chat"

# Test cases
test_cases = [
    {
        "name": "Job Recommendations",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "Show me job recommendations",
            "top_n": 3
        },
        "expected_intent": "show_jobs"
    },
    {
        "name": "Show Me Jobs",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "show me jobs",
            "top_n": 3
        },
        "expected_intent": "show_jobs"
    },
    {
        "name": "Find Jobs",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "find jobs for me",
            "top_n": 3
        },
        "expected_intent": "show_jobs"
    },
    {
        "name": "Skill Gap",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "What skills should I learn?",
            "top_n": 3
        },
        "expected_intent": "show_skill_gap"
    },
    {
        "name": "Career Advice",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "Give me career advice",
            "top_n": 3
        },
        "expected_intent": "career_advice"
    },
    {
        "name": "Update Skills",
        "payload": {
            "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
            "query": "My skills are Python, JavaScript, React, and AWS",
            "top_n": 3
        },
        "expected_intent": "update_skills"
    }
]

print("=" * 80)
print("TESTING CORRECT LIGHTWEIGHT CHATBOT API")
print("=" * 80)
print(f"API URL: {API_URL}")
print("=" * 80)

# Test each case
passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"Query: {test['payload']['query']}")
    print(f"Expected Intent: {test['expected_intent']}")
    
    try:
        response = requests.post(API_URL, json=test['payload'], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            actual_intent = data.get('intent')
            
            print(f"Actual Intent: {actual_intent}")
            print(f"Success: {data.get('success')}")
            print(f"Response: {data.get('response')[:100]}..." if len(data.get('response', '')) > 100 else f"Response: {data.get('response')}")
            
            # Check if has data/jobs/skill_gaps
            if data.get('data'):
                if 'jobs' in data['data']:
                    print(f"Jobs Found: {data['data'].get('total_count', 0)}")
                elif 'skill_gaps' in data['data']:
                    print(f"Skill Gaps Found: {data['data'].get('total_count', 0)}")
            
            # Check extracted skills
            if data.get('extracted_skills'):
                print(f"Extracted Skills: {', '.join(data['extracted_skills'][:5])}")
            
            # Check if intent matches
            if actual_intent == test['expected_intent']:
                print("✅ PASSED - Intent matched!")
                passed += 1
            else:
                print(f"❌ FAILED - Expected '{test['expected_intent']}' but got '{actual_intent}'")
                failed += 1
        else:
            print(f"❌ FAILED - Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED - Could not connect to server. Is it running?")
        failed += 1
    except Exception as e:
        print(f"❌ FAILED - Error: {str(e)}")
        failed += 1

# Summary
print(f"\n{'='*80}")
print("TEST SUMMARY")
print(f"{'='*80}")
print(f"Total Tests: {len(test_cases)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
print(f"{'='*80}")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! Chatbot is working correctly!")
else:
    print(f"\n⚠️  {failed} test(s) failed. Please check the output above.")
