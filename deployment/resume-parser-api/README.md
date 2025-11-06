# Resume Parser API 📄

FastAPI service that extracts skills from resumes using custom NLP patterns and saves them to Supabase database.

## Features

✅ Parse PDF, DOCX, DOC, TXT resumes  
✅ Extract 600+ technical skills using regex patterns  
✅ Fallback to spaCy NLP for additional extraction  
✅ Save skills to PostgreSQL database  
✅ Retrieve user skills from database  
✅ CORS enabled for web integration  
✅ UUID-based user identification

## API Endpoints

### 1. Health Check
```
GET /
GET /health
```

### 2. Parse Resume
```
POST /parse-resume
```
**Parameters:**
- `file` (multipart/form-data): Resume file (PDF/DOCX/TXT)
- `uuid` (form-data, optional): User UUID to save skills

**Example (curl - PowerShell):**
```powershell
curl -X POST "http://localhost:8003/parse-resume" `
  -F "file=@C:\path\to\resume.pdf" `
  -F "uuid=cde634c5-77c0-4004-834f-4f9caec051e6"
```

**Example (curl - Bash):**
```bash
curl -X POST "http://localhost:8003/parse-resume" \
  -F "file=@/path/to/resume.pdf" \
  -F "uuid=cde634c5-77c0-4004-834f-4f9caec051e6"
```

**Response:**
```json
{
  "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
  "skills": ["Python", "Machine Learning", "SQL", "React", "Docker", "AWS"],
  "message": "Skills extracted successfully: 6 skills found. Skills updated for user cde634c5-77c0-4004-834f-4f9caec051e6",
  "success": true
}
```

### 3. Get User Skills
```
GET /users/{uuid}/skills
```

**Example:**
```bash
curl "http://localhost:8003/users/cde634c5-77c0-4004-834f-4f9caec051e6/skills"
```

**Response:**
```json
{
  "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
  "skills": ["Python", "Machine Learning", "SQL", "React", "Docker", "AWS"],
  "message": "Skills retrieved successfully",
  "success": true
}
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Required NLP Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Setup Database
Create `users` table in Supabase:
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    skills TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Run API
```bash
# Development
uvicorn main:app --reload --port 8003

# Production
python main.py
```

## Supported File Formats

- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Text (`.txt`)

## Skill Categories Detected

The API can detect **600+ skills** across 18 categories:

1. **Programming Languages**: Python, Java, JavaScript, TypeScript, C++, C#, Go, Rust, etc.
2. **Web Frameworks**: React, Angular, Vue, Django, Flask, Express, Spring, Laravel, etc.
3. **Databases**: SQL, MySQL, PostgreSQL, MongoDB, Redis, Oracle, etc.
4. **Cloud & DevOps**: AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Terraform, etc.
5. **AI/ML**: Machine Learning, Deep Learning, TensorFlow, PyTorch, NLP, Computer Vision, etc.
6. **Mobile Development**: Android, iOS, React Native, Flutter, Swift, Kotlin, etc.
7. **Testing**: Jest, Pytest, Selenium, Cypress, JUnit, etc.
8. **Version Control**: Git, GitHub, GitLab, Bitbucket, etc.
9. **API Technologies**: REST, GraphQL, gRPC, WebSocket, Microservices, etc.
10. **Frontend**: HTML, CSS, Sass, Webpack, TypeScript, Responsive Design, etc.
11. **Backend**: Node.js, Express, API Development, Microservices, etc.
12. **Data Tools**: Tableau, Power BI, Excel, Apache Spark, Kafka, ETL, etc.
13. **Blockchain**: Ethereum, Solidity, Web3, Smart Contracts, etc.
14. **Game Development**: Unity, Unreal Engine, C++, 3D Modeling, etc.
15. **Security**: Cybersecurity, Penetration Testing, OAuth, JWT, Encryption, etc.
16. **Methodologies**: Agile, Scrum, Kanban, DevOps, CI/CD, TDD, etc.
17. **Soft Skills**: Communication, Leadership, Problem Solving, etc.
18. **Other Technologies**: Linux, Bash, Shell Scripting, Design Patterns, OOP, etc.

## How It Works

### Extraction Process:

1. **Upload Resume**: User uploads resume file via API
2. **Text Extraction**: 
   - PDF: PyPDF2 extracts text from all pages
   - DOCX: docx2txt extracts formatted text
   - TXT: Direct text file reading
3. **Skill Detection**: 
   - **Primary Method**: Regex pattern matching (600+ patterns)
   - **Fallback Method**: spaCy NLP for noun phrase extraction
4. **Skill Normalization**: 
   - Convert variations (e.g., "reactjs" → "React")
   - Remove duplicates
   - Title case formatting
5. **Database Storage**: Save skills to users table (upsert)
6. **Return Response**: Return extracted skills list

### Skill Normalization Examples:

```
"reactjs", "react.js", "react" → "React"
"nodejs", "node.js" → "Node.js"
"k8s" → "Kubernetes"
"ml" → "Machine Learning"
"aws" → "AWS"
```

## Database Schema

**Table:** `users`

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | User UUID (Primary Key) |
| skills | TEXT | Comma-separated skills |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## Testing

### Method 1: Interactive Docs (Recommended)
1. Open browser: http://localhost:8003/docs
2. Click "Try it out" on `/parse-resume`
3. Upload your resume file
4. Enter UUID (optional)
5. Click "Execute"

### Method 2: PowerShell (curl)
```powershell
curl -X POST "http://localhost:8003/parse-resume" `
  -F "file=@C:\Users\YourName\Documents\resume.pdf" `
  -F "uuid=test-user-123"
```

### Method 3: Python Script
```python
import requests

url = "http://localhost:8003/parse-resume"

with open("resume.pdf", "rb") as f:
    files = {"file": f}
    data = {"uuid": "test-user-123"}
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### Method 4: Postman
1. Open Postman
2. Create POST request: `http://localhost:8003/parse-resume`
3. Body → form-data
4. Add `file` (File type) → Select resume
5. Add `uuid` (Text) → Enter UUID
6. Send

## Error Handling

### Invalid File Type
```json
{
  "detail": "Invalid file type. Allowed types: .pdf, .docx, .doc, .txt"
}
```

### No Skills Found
```json
{
  "detail": "No skills found in resume. Please ensure the resume contains technical skills."
}
```

### File Extraction Error
```json
{
  "detail": "Could not extract meaningful text from resume"
}
```

### Database Error
```json
{
  "detail": "Database operation failed: [error details]"
}
```

## Deployment (Render)

### 1. Create `render.yaml`
```yaml
services:
  - type: web
    name: resume-parser-api
    env: python
    buildCommand: "pip install -r requirements.txt && python -m spacy download en_core_web_sm"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
```

### 2. Runtime File
File: `runtime.txt`
```
python-3.11.9
```

## Memory Usage

- **Base**: ~80MB
- **With spaCy Model**: ~150MB
- **Peak Usage**: ~200MB
- **Total**: Well under 512MB limit ✅

## Performance

- **PDF Parsing**: 1-2 seconds
- **DOCX Parsing**: < 1 second
- **Skill Extraction**: < 500ms
- **Database Save**: < 100ms
- **Total**: 2-4 seconds per resume

## Technology Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| PyPDF2 | PDF text extraction |
| docx2txt | DOCX text extraction |
| spaCy | NLP fallback (noun phrases) |
| PostgreSQL | Database storage |
| Regex | Primary skill detection |

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **OpenAPI JSON**: http://localhost:8003/openapi.json

## Notes

✅ **No dependency on pyresparser** (incompatible with Python 3.13)  
✅ **Custom regex patterns** for accurate skill detection  
✅ **600+ skills** detected across 18 categories  
✅ **UUID-based** user identification  
✅ **Upsert logic** - creates or updates user records  
✅ **Cross-platform** compatible (Windows, Mac, Linux)  

## Example Workflow

```
1. User uploads resume.pdf with uuid=abc-123
   ↓
2. API extracts text from PDF
   ↓
3. Regex patterns find: Python, React, Docker, AWS, SQL
   ↓
4. Skills normalized: ["Python", "React", "Docker", "AWS", "SQL"]
   ↓
5. Saved to database: users.id=abc-123, skills="Python, React, Docker, AWS, SQL"
   ↓
6. Return response with extracted skills
```

## Support

For issues or questions:
1. Check logs: Terminal where uvicorn is running
2. Test endpoints: Visit `/docs` for interactive testing
3. Verify database: Check Supabase users table
4. Check file format: Ensure PDF/DOCX is not corrupted
