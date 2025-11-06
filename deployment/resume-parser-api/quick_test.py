"""
Simple test for Resume Parser API
"""
import requests

API_URL = "http://localhost:8003"

# Test 1: Health Check
print("=" * 60)
print("Test 1: Health Check")
print("=" * 60)
try:
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Health check passed!\n")
except Exception as e:
    print(f"❌ Health check failed: {e}\n")

# Test 2: Parse Resume with UUID
print("=" * 60)
print("Test 2: Parse Resume (provide your own resume file)")
print("=" * 60)
print("To test resume parsing, use one of these methods:")
print()
print("Method 1: Using curl (PowerShell)")
print('curl -X POST "http://localhost:8003/parse-resume" `')
print('  -F "file=@C:\\path\\to\\your\\resume.pdf" `')
print('  -F "uuid=test-user-123"')
print()
print("Method 2: Using Postman")
print("  1. Open Postman")
print("  2. POST http://localhost:8003/parse-resume")
print("  3. Body -> form-data")
print("  4. Add 'file' (File type) -> Select your resume")
print("  5. Add 'uuid' (Text) -> Enter your UUID")
print("  6. Send")
print()
print("Method 3: Visit http://localhost:8003/docs")
print("  1. Try out the /parse-resume endpoint")
print("  2. Upload your resume file")
print("  3. Enter UUID (optional)")
print("  4. Execute")
print()

# Test 3: Get User Skills (after uploading)
print("=" * 60)
print("Test 3: Get User Skills")
print("=" * 60)
print("After uploading a resume, test retrieval with:")
print('curl "http://localhost:8003/users/test-user-123/skills"')
print()

print("=" * 60)
print("API Documentation Available At:")
print(f"  Interactive Docs: {API_URL}/docs")
print(f"  ReDoc: {API_URL}/redoc")
print("=" * 60)
