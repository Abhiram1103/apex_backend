import requests
import os

# Test the Resume Parser API

API_URL = "http://localhost:8003"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_parse_resume(file_path, user_id=None):
    """Test resume parsing"""
    print(f"Testing resume parsing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}\n")
        return
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {}
        if user_id:
            data['user_id'] = user_id
        
        response = requests.post(f"{API_URL}/parse-resume", files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

def test_get_user_skills(user_id):
    """Test getting user skills"""
    print(f"Testing get user skills: {user_id}")
    response = requests.get(f"{API_URL}/users/{user_id}/skills")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Resume Parser API - Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health Check
    try:
        test_health_check()
    except Exception as e:
        print(f"Health check failed: {e}\n")
    
    # Test 2: Parse Resume (provide your own resume file path)
    # Uncomment and update with actual resume file path
    # test_parse_resume("path/to/resume.pdf", user_id="test_user_123")
    
    # Test 3: Get User Skills
    # Uncomment after creating a user
    # test_get_user_skills("test_user_123")
    
    print("\nNote: Update file paths and user IDs in test_api.py to run full tests")
