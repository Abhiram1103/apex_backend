# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Verify Database Connection

Make sure your PostgreSQL database is accessible and contains the `skill_job1` table with the following columns:
- `id`
- `job_role`
- `company`
- `category`
- `required_skills`
- `job_description`

### Step 3: Start the API Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

The API will start at: `http://localhost:8000`

### Step 4: Test the API

Open another terminal and run:
```bash
python test_api.py
```

Or visit the interactive API docs at: `http://localhost:8000/docs`

### Step 5: Integrate with React Frontend

See `react_example.jsx` for a complete React component example.

---

## 📝 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/recommend` | POST | Get job recommendations |
| `/api/refresh-cache` | POST | Refresh job cache |
| `/api/stats` | GET | Get statistics |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

---

## 🔧 Configuration

### Option 1: Using .env file (Recommended for Production)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the values in `.env` file

### Option 2: Using Environment Variables

```bash
export DATABASE_URL="postgresql://user:pass@host:port/database"
export ALLOWED_ORIGINS="http://localhost:3000"
```

---

## 🧪 Testing the API

### Using cURL:

```bash
# Health Check
curl http://localhost:8000/health

# Get Recommendations
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["python", "machine learning", "data science"],
    "top_n": 10
  }'
```

### Using Python:

```python
import requests

# Get recommendations
response = requests.post(
    "http://localhost:8000/api/recommend",
    json={
        "skills": ["python", "machine learning"],
        "top_n": 5
    }
)

recommendations = response.json()
print(recommendations)
```

### Using JavaScript/Fetch:

```javascript
fetch('http://localhost:8000/api/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    skills: ['python', 'machine learning'],
    top_n: 10
  })
})
.then(response => response.json())
.then(data => console.log(data.recommendations));
```

---

## 📊 How It Works

1. **Startup**: 
   - Loads SBERT model (all-MiniLM-L6-v2)
   - Fetches all jobs from database
   - Preprocesses job descriptions
   - Generates 384-dimensional embeddings
   - Caches embeddings for fast retrieval

2. **Request Processing**:
   - Receives user skills
   - Cleans and preprocesses skills
   - Generates embedding for user profile
   - Calculates cosine similarity with all jobs
   - Returns top N matches sorted by similarity

3. **Response Time**:
   - First request (cold start): ~10-30 seconds
   - Subsequent requests: ~50-200ms

---

## 🎯 Example Use Cases

### Use Case 1: Career Recommendations
```json
{
  "skills": ["python", "data analysis", "statistics", "sql"],
  "top_n": 10
}
```

### Use Case 2: Skill Gap Analysis
```json
{
  "skills": ["javascript", "react"],
  "top_n": 20
}
```

### Use Case 3: Job Transition
```json
{
  "skills": ["project management", "agile", "scrum", "leadership"],
  "top_n": 15
}
```

---

## 🔍 Troubleshooting

### Problem: API takes too long to start
**Solution**: This is normal on first startup. The API needs to:
- Download SBERT model (~90MB)
- Download NLTK data
- Load all jobs from database
- Generate embeddings

### Problem: Database connection error
**Solution**: 
- Check if database URL is correct
- Verify table name is `skill_job1`
- Ensure column names match the schema

### Problem: CORS error in React
**Solution**: 
- Update `ALLOWED_ORIGINS` in `.env` or main.py
- Make sure your React app URL is included

### Problem: Low similarity scores
**Solution**: 
- This is normal - scores above 0.5 indicate good matches
- Ensure skills are spelled correctly
- Use multiple related skills for better matching

---

## 🚀 Deployment

### Deploy to Render/Railway/Heroku:

1. Add a `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Set environment variables in your hosting platform

3. Make sure `requirements.txt` is up to date

### Deploy with Docker:

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t job-recommender-api .
docker run -p 8000:8000 job-recommender-api
```

---

## 📚 Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Sentence Transformers: https://www.sbert.net/
- NLTK Documentation: https://www.nltk.org/

---

## 💡 Pro Tips

1. **Batch Processing**: If you have multiple users, consider implementing batch embedding generation
2. **Caching Strategy**: Use Redis for distributed caching in production
3. **Monitoring**: Add logging and monitoring for production environments
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Authentication**: Add JWT authentication for secure access

---

Need help? Check out the full README.md or create an issue!
