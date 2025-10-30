"""Comprehensive test for all chatbot intents"""
import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_chat(user_id, query, description):
    """Test chat endpoint"""
    print(f"\n{'='*100}")
    print(f"TEST: {description}")
    print(f"Query: {query}")
    print('='*100)
    
    payload = {"user_id": user_id, "query": query}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Intent: {data['intent']}")
            print(f"\n📝 Response:\n{data['response']}")
            
            if data.get('extracted_skills'):
                print(f"\n🎯 Skills: {', '.join(data['extracted_skills'])}")
            
            if data.get('job_recommendations'):
                print(f"\n💼 Jobs: {len(data['job_recommendations'])} found")
            
            if data.get('skill_gap_analysis'):
                gap = data['skill_gap_analysis']
                if gap.get('success'):
                    print(f"\n📊 Skill Gap: {gap.get('total_jobs_analyzed')} jobs analyzed")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    time.sleep(1)

if __name__ == "__main__":
    print("="*100)
    print("COMPREHENSIVE CHATBOT API TEST - ALL INTENTS")
    print("="*100)
    
    user_id = "d563e1f7-ec4e-40c8-8cd3-a49ba43f19ed"
    
    # Test 1: Add Skills Intent
    test_chat(
        user_id=user_id,
        query="I know Python, Machine Learning, TensorFlow, and Deep Learning",
        description="ADD_SKILLS - Adding technical skills"
    )
    
    # Test 2: Show Jobs Intent
    test_chat(
        user_id=user_id,
        query="Show me job recommendations based on my skills",
        description="SHOW_JOBS - Getting job recommendations"
    )
    
    # Test 3: Skill Gap Intent
    test_chat(
        user_id=user_id,
        query="What skills do I need to learn for high paying jobs?",
        description="SKILL_GAP - Analyzing skill gaps"
    )
    
    # Test 4: Salary Info Intent
    test_chat(
        user_id=user_id,
        query="What salary can I expect with my current skills?",
        description="SALARY_INFO - Getting salary information"
    )
    
    # Test 5: Career Advice Intent
    test_chat(
        user_id=user_id,
        query="How can I advance my career in data science?",
        description="CAREER_ADVICE - Getting career guidance"
    )
    
    # Test 6: General Query
    test_chat(
        user_id=user_id,
        query="What is the best programming language to learn?",
        description="GENERAL_QUERY - General question"
    )
    
    # Test 7: Mixed Intent (Add Skills + Show Jobs)
    test_chat(
        user_id=user_id,
        query="I also know React and JavaScript. Can you show me web development jobs?",
        description="MIXED - Adding skills and showing jobs"
    )
    
    # Test 8: Skill Gap with specific role
    test_chat(
        user_id=user_id,
        query="What skills do I need to become a senior machine learning engineer?",
        description="SKILL_GAP - Role-specific gap analysis"
    )
    
    print("\n" + "="*100)
    print("ALL TESTS COMPLETED!")
    print("="*100)
