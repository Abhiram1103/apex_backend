"""Check database column names"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("Checking database column names...")
response = requests.get(f"{BASE_URL}/api/debug/columns")

if response.status_code == 200:
    data = response.json()
    print("\n=== COLUMN NAMES IN DATABASE ===")
    for col in data['columns']:
        print(f"  - {col}")
    
    print("\n=== SAMPLE DATA (first row) ===")
    for key, value in data['sample_data'].items():
        print(f"  {key}: {value[:80]}...")
else:
    print(f"Error: {response.text}")
