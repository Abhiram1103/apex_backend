# Resume Parser API - Quick Start Guide 🚀

## ✅ API is Running!

**Base URL**: `http://localhost:8003`  
**Status**: ✅ Healthy (Database connected)

---

## 📝 How to Use

### **Option 1: Interactive Docs (Easiest!)**

1. Open your browser
2. Go to: **http://localhost:8003/docs**
3. Click on **"POST /parse-resume"**
4. Click **"Try it out"**
5. Upload your resume file
6. Enter a UUID (e.g., `test-user-123`)
7. Click **"Execute"**
8. See extracted skills in response!

---

### **Option 2: PowerShell Command**

```powershell
# Replace with your actual file path and UUID
curl -X POST "http://localhost:8003/parse-resume" `
  -F "file=@C:\Users\YourName\Documents\resume.pdf" `
  -F "uuid=your-uuid-here"
```

**Example:**
```powershell
curl -X POST "http://localhost:8003/parse-resume" `
  -F "file=@C:\Users\John\Desktop\my_resume.pdf" `
  -F "uuid=cde634c5-77c0-4004-834f-4f9caec051e6"
```

---

### **Option 3: Python Script**

```python
import requests

# Configuration
API_URL = "http://localhost:8003/parse-resume"
RESUME_PATH = "C:/Users/YourName/Documents/resume.pdf"  # Change this
USER_UUID = "your-uuid-here"  # Change this

# Upload and parse resume
with open(RESUME_PATH, 'rb') as f:
    files = {'file': f}
    data = {'uuid': USER_UUID}
    
    response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Found {len(result['skills'])} skills:")
        for skill in result['skills']:
            print(f"  • {skill}")
    else:
        print(f"❌ Error: {response.json()['detail']}")
```

---

### **Option 4: Postman**

1. Open Postman
2. Create a **POST** request
3. URL: `http://localhost:8003/parse-resume`
4. Go to **Body** tab
5. Select **form-data**
6. Add fields:
   - Key: `file` | Type: **File** | Value: Browse and select resume
   - Key: `uuid` | Type: **Text** | Value: Your UUID
7. Click **Send**
8. View extracted skills in response

---

## 📊 Example Response

```json
{
  "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
  "skills": [
    "Python",
    "Machine Learning",
    "SQL",
    "React",
    "Docker",
    "AWS",
    "Flask",
    "PostgreSQL",
    "Git",
    "REST API"
  ],
  "message": "Skills extracted successfully: 10 skills found. Skills updated for user cde634c5-77c0-4004-834f-4f9caec051e6",
  "success": true
}
```

---

## 🔍 Retrieve Saved Skills

After uploading a resume, get the saved skills:

### Browser:
```
http://localhost:8003/users/your-uuid-here/skills
```

### PowerShell:
```powershell
curl "http://localhost:8003/users/cde634c5-77c0-4004-834f-4f9caec051e6/skills"
```

### Python:
```python
import requests

uuid = "your-uuid-here"
response = requests.get(f"http://localhost:8003/users/{uuid}/skills")
print(response.json())
```

---

## 📂 Supported File Formats

- ✅ PDF (`.pdf`)
- ✅ Microsoft Word (`.docx`)
- ✅ Text Files (`.txt`)

---

## 🎯 Skills Detected (600+ Total!)

### Programming Languages
Python, Java, JavaScript, TypeScript, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, R, MATLAB, Scala, and more...

### Web Technologies
React, Angular, Vue, Django, Flask, FastAPI, Express, Node.js, Spring Boot, Laravel, ASP.NET, and more...

### Databases
SQL, MySQL, PostgreSQL, MongoDB, Redis, Oracle, Cassandra, DynamoDB, and more...

### Cloud & DevOps
AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Terraform, Ansible, CI/CD, and more...

### AI/ML
Machine Learning, Deep Learning, TensorFlow, PyTorch, NLP, Computer Vision, Keras, scikit-learn, and more...

### And 13+ more categories!

---

## ⚠️ Troubleshooting

### Issue: "No skills found"
**Solution**: Ensure your resume contains technical skills. Try different file formats.

### Issue: "Could not extract text"
**Solution**: Check if PDF is readable (not scanned image). Try DOCX format.

### Issue: "Database error"
**Solution**: Check database connection in main.py. Verify Supabase credentials.

### Issue: API not responding
**Solution**: Check if server is running: `http://localhost:8003/health`

---

## 📚 Full Documentation

- **Interactive API Docs**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **README**: See `README.md` for complete details

---

## 💡 Tips

1. **Better Results**: Ensure resume has a clear "Skills" section
2. **Multiple Formats**: Try both PDF and DOCX for best extraction
3. **UUID Management**: Use actual user UUIDs from your database
4. **Batch Processing**: Loop through multiple resumes with Python script
5. **Validation**: Check extracted skills match resume content

---

## 🔗 Quick Links

- Health Check: http://localhost:8003/health
- API Docs: http://localhost:8003/docs
- Test Endpoint: http://localhost:8003/

---

**Ready to extract skills from resumes! 🎉**
