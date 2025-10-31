"""
Test script for the Career Chatbot API
Tests skill extraction and job recommendation integration
"""

import requests
import json

# API Configuration
API_URL = "http://localhost:8002/api/chat"
TEST_USER_ID = "cde634c5-77c0-4004-834f-4f9caec051e6"  # Replace with actual user_id


def test_chat(user_id: str, query: str, description: str, n: int = 10):
    """Test the chatbot API with a query"""
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"{'='*80}")
    print(f"User ID: {user_id}")
    print(f"Query: {query}")
    print(f"Requesting {n} job recommendations")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "user_id": user_id,
                "query": query,
                "n": n
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS")
            print(f"Message: {data['message']}")
            print(f"\nExtracted Skills ({len(data['extracted_skills'])}):")
            for skill in data['extracted_skills']:
                print(f"  • {skill}")
            
            print(f"\nSkills Saved: {data['skills_saved']}")
            
            if data['job_recommendations']:
                print(f"\nJob Recommendations ({data['total_jobs']}):")
                for i, job in enumerate(data['job_recommendations'][:5], 1):
                    print(f"\n  {i}. {job.get('Job Role', 'N/A')}")
                    print(f"     Category: {job.get('Category', 'N/A')}")
                    print(f"     Location: {job.get('Location', 'N/A')}")
                    print(f"     Similarity: {job.get('similarity_score', 0):.2%}")
                
                if data['total_jobs'] > 5:
                    print(f"\n  ... and {data['total_jobs'] - 5} more jobs")
            else:
                print(f"\n⚠️ No job recommendations returned")
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️ TIMEOUT: Request took longer than 30 seconds")
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")


def main():
    """Run all test cases"""
    print(f"\n🧪 TESTING CAREER CHATBOT API")
    print(f"API URL: {API_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    # Test 1: Multiple programming languages
    test_chat(
        user_id=TEST_USER_ID,
        query="I am proficient in Python, Java, and JavaScript. I also know React and Node.js.",
        description="Multiple Programming Languages & Frameworks",
        n=10
    )
    
    # Test 2: Data Science skills
    test_chat(
        user_id=TEST_USER_ID,
        query="I have experience with Machine Learning, TensorFlow, PyTorch, and data analysis using Pandas and NumPy.",
        description="Data Science & ML Skills",
        n=10
    )
    
    # Test 3: Full Stack Developer
    test_chat(
        user_id=TEST_USER_ID,
        query="I'm a full stack developer skilled in React, Angular, Django, Flask, PostgreSQL, and MongoDB.",
        description="Full Stack Development",
        n=10
    )
    
    # Test 4: Cloud & DevOps
    test_chat(
        user_id=TEST_USER_ID,
        query="I work with AWS, Docker, Kubernetes, Jenkins, and Terraform. I also know CI/CD pipelines.",
        description="Cloud & DevOps Skills",
        n=10
    )
    
    # Test 5: Mixed case and variations
    test_chat(
        user_id=TEST_USER_ID,
        query="I know node.js, react.js, next.js, and K8s. Also experienced with ML and NLP.",
        description="Mixed Case & Abbreviations",
        n=10
    )
    
    # Test 6: Natural conversation
    test_chat(
        user_id=TEST_USER_ID,
        query="Hey! I'm looking for jobs. I've been working with Python and machine learning for 3 years, and recently learned React for frontend development.",
        description="Natural Conversational Query",
        n=15
    )
    
    # Test 7: No skills mentioned
    test_chat(
        user_id=TEST_USER_ID,
        query="Can you show me some jobs?",
        description="No Skills Mentioned",
        n=10
    )
    
    print(f"\n{'='*80}")
    print(f"✅ ALL TESTS COMPLETED")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
