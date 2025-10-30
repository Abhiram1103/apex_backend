# Job Recommendation API

FastAPI-based job recommendation system using SBERT embeddings and cosine similarity.

## Features

- 🚀 Fast API endpoints for job recommendations
- 🤖 AI-powered matching using SBERT (all-MiniLM-L6-v2)
- 📊 384-dimensional embeddings for semantic similarity
- 🔄 Automatic caching for fast responses
- 🌐 CORS enabled for React frontend integration
- 📦 PostgreSQL database integration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data (automatic on first run):
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')
```

## Running the API

### Development Mode
```bash
python main.py
```

### Production Mode with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### 2. Health Check
```
GET /health
```
Check if the API is running and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "jobs_cached": true,
  "total_jobs": 2000
}
```

### 3. Get Job Recommendations
```
POST /api/recommend
```

**Request Body:**
```json
{
  "skills": ["python", "machine learning", "data analysis", "tensorflow"],
  "top_n": 10
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "job_id": 123,
      "job_role": "Machine Learning Engineer",
      "company": "Tech Corp",
      "category": "Data Science",
      "required_skills": "Python, ML, TensorFlow",
      "job_description": "...",
      "similarity_score": 0.87
    }
  ],
  "total_jobs_analyzed": 2000
}
```

### 4. Refresh Cache
```
POST /api/refresh-cache
```
Refresh job data from database when new jobs are added.

**Response:**
```json
{
  "success": true,
  "message": "Cache refreshed successfully",
  "total_jobs": 2000
}
```

### 5. Get Statistics
```
GET /api/stats
```
Get statistics about the cached jobs and model.

## Database Schema

The API expects a PostgreSQL table named `skill_job1` with the following columns:
- `id` (integer, primary key)
- `job_role` (text)
- `company` (text)
- `category` (text)
- `required_skills` (text)
- `job_description` (text)

**Important:** Update the table name and column names in `main.py` if your schema is different.

## Integration with React Frontend

### Example Fetch Request:
```javascript
const getRecommendations = async (userSkills) => {
  const response = await fetch('http://localhost:8000/api/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      skills: userSkills,
      top_n: 10
    })
  });
  
  const data = await response.json();
  return data.recommendations;
};
```

### Example Usage:
```javascript
const skills = ['python', 'machine learning', 'data science'];
const recommendations = await getRecommendations(skills);
console.log(recommendations);
```

## Text Preprocessing Pipeline

The API applies the same preprocessing as the notebook:
1. ✅ Combines job features (Category, Skills 3x, Description, Role, Company)
2. ✅ Removes forward slashes
3. ✅ Converts to lowercase
4. ✅ Removes punctuation and special characters
5. ✅ Removes extra whitespace
6. ✅ Removes stop words using NLTK

## Performance

- **Startup Time:** ~10-30 seconds (model loading + cache building)
- **Recommendation Response:** ~50-200ms (after cache is built)
- **Embedding Dimensions:** 384
- **Model:** sentence-transformers/all-MiniLM-L6-v2

## Notes

1. The API caches all job embeddings on startup for fast recommendations
2. Call `/api/refresh-cache` endpoint when you add new jobs to the database
3. Adjust CORS settings in production to only allow your frontend domain
4. Consider using environment variables for the database URL in production

## Troubleshooting

### Issue: Database connection fails
- Verify the database URL is correct
- Check if the database is accessible from your network
- Ensure the table and columns exist in your database

### Issue: Model loading is slow
- First-time model download can take a few minutes
- The model is cached after the first download (~90MB)

### Issue: NLTK data not found
- The API downloads NLTK data automatically on startup
- If it fails, manually run:
  ```python
  import nltk
  nltk.download('stopwords')
  nltk.download('punkt_tab')
  ```

## License

MIT
