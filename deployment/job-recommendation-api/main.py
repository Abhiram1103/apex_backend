from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
from psycopg2.extras import RealDictCursor
import warnings
import os

warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(
    title="Job Recommendation API",
    description="AI-powered job recommendation system using SBERT embeddings",
    version="1.0.0"
)

# CORS middleware - Allow requests from Vercel frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://your-frontend.vercel.app")
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite local development
    "https://*.vercel.app",   # All Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database configuration from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Global variable for model only (no more in-memory cache!)
model = None

# Pydantic models for request/response
class UserSkills(BaseModel):
    user_id: str
    top_n: Optional[int] = 10

class JobRecommendation(BaseModel):
    job_id: str
    Job_Role: str
    Category: str
    Location: str
    Required_Skills: str
    Min_Salary: Optional[float] = None
    Max_Salary: Optional[float] = None
    similarity_score: float

class RecommendationResponse(BaseModel):
    success: bool
    recommendations: List[JobRecommendation]
    total_jobs_analyzed: int


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def clean_text(text):
    """
    Clean text by:
    - Removing forward slashes
    - Converting to lowercase
    - Removing punctuation and special characters
    - Removing extra whitespace
    - Removing stop words (simple list, no NLTK needed)
    """
    if not text or text is None:
        return ""
    
    text = str(text)
    text = text.replace('/', ' ')
    text = text.lower()
    # Keep alphanumeric, spaces, and important tech symbols like + and #
    text = re.sub(r'[^a-z0-9\s+#]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Simple stopword removal (no NLTK required)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 
                 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                 'would', 'should', 'could', 'may', 'might', 'must', 'can'}
    
    words = text.split()
    filtered_words = [w for w in words if w not in stopwords and len(w) > 1]
    
    return ' '.join(filtered_words) if filtered_words else text


def fetch_user_skills(user_id: str):
    """Fetch user skills from the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT skills FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        
        return result['skills']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user skills: {str(e)}")
    finally:
        conn.close()


def get_model():
    """Lazy load model on first use"""
    global model
    if model is None:
        print("🚀 Loading SBERT model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully!")
    return model


def fetch_job_embeddings_from_db(conn):
    """Fetch job embeddings from database (memory efficient!)"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Fetch all jobs with embeddings
    cur.execute("""
        SELECT 
            id,
            "Category",
            "Job Role",
            "Location",
            "Job Description",
            "Required Skills",
            "Min Salary",
            "Max Salary",
            "Average salary",
            "Company",
            embedding
        FROM "Job Roles"
        WHERE embedding IS NOT NULL
    """)
    
    jobs = []
    embeddings_list = []
    
    for row in cur.fetchall():
        # Convert embedding bytes back to numpy array
        embedding = np.frombuffer(row['embedding'], dtype=np.float32)
        embeddings_list.append(embedding)
        
        # Store job data
        jobs.append({
            'id': str(row['id']),
            'Category': row['Category'],
            'Job Role': row['Job Role'],
            'Location': row['Location'],
            'Job Description': row['Job Description'],
            'Required Skills': row['Required Skills'],
            'Min Salary': row['Min Salary'],
            'Max Salary': row['Max Salary'],
            'Average salary': row['Average salary'],
            'Company': row['Company']
        })
    
    cur.close()
    
    # Convert to numpy array for similarity calculation
    embeddings_array = np.array(embeddings_list)
    
    return jobs, embeddings_array


@app.on_event("startup")
async def startup_event():
    """Lightweight startup - only log, no caching!"""
    print("🚀 Job Recommendation API started!")
    print("✅ Using database-backed embeddings (memory efficient)")
    print("💾 Memory usage: ~100MB (vs 500MB with cache)")
    print("📊 Model loads on first request")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Job Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "recommend": "/api/recommend (POST)",
            "refresh_cache": "/api/refresh-cache (POST)",
            "stats": "/api/stats (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Job Roles" WHERE embedding IS NOT NULL')
        job_count = cur.fetchone()[0]
        cur.close()
        
        return {
            "status": "healthy",
            "model_loaded": model is not None,
            "using_database_embeddings": True,
            "total_jobs_with_embeddings": job_count,
            "memory_optimized": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        conn.close()


@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_jobs(user_skills: UserSkills):
    """
    Generate job recommendations based on user ID
    
    Request Body:
    {
        "user_id": "user123",
        "top_n": 10
    }
    
    Response:
    {
        "success": true,
        "recommendations": [
            {
                "job_id": "uuid",
                "Job_Role": "Data Scientist",
                "Category": "Data Science",
                "Location": "Bangalore",
                "Required_Skills": "Python, Machine Learning, SQL",
                "Min_Salary": 800000,
                "Max_Salary": 1500000,
                "similarity_score": 0.85
            },
            ...
        ],
        "total_jobs_analyzed": 500
    }
    """
    conn = get_db_connection()
    
    try:
        # Get user skills from database
        user_skill_text = fetch_user_skills(user_skills.user_id)
        
        # Clean user skills
        cleaned_user_skills = clean_text(user_skill_text)
        
        if not cleaned_user_skills:
            raise HTTPException(status_code=400, detail="User has no valid skills")
        
        # Get model (lazy load)
        current_model = get_model()
        
        # Generate embedding for user skills
        user_embedding = current_model.encode([cleaned_user_skills])
        
        # Fetch job embeddings from database (not from cache!)
        jobs, job_embeddings = fetch_job_embeddings_from_db(conn)
        
        if len(jobs) == 0:
            raise HTTPException(status_code=404, detail="No jobs with embeddings found")
        
        # Calculate similarities
        similarities = cosine_similarity(user_embedding, job_embeddings)[0]
        
        # Get top N recommendations
        top_n = min(user_skills.top_n, len(jobs))
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = [
            JobRecommendation(
                job_id=str(jobs[i]['id']),
                Job_Role=str(jobs[i].get('Job Role', 'N/A')),
                Category=str(jobs[i].get('Category', 'N/A')),
                Location=str(jobs[i].get('Location', 'N/A')),
                Required_Skills=str(jobs[i].get('Required Skills', 'N/A')),
                Min_Salary=float(jobs[i]['Min Salary']) if jobs[i].get('Min Salary') is not None else None,
                Max_Salary=float(jobs[i]['Max Salary']) if jobs[i].get('Max Salary') is not None else None,
                similarity_score=float(similarities[i])
            )
            for i in top_indices
            if similarities[i] > 0  # Only include positive similarities
        ]
        
        return RecommendationResponse(
            success=True,
            recommendations=recommendations,
            total_jobs_analyzed=len(jobs)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
    finally:
        conn.close()


@app.get("/api/stats")
async def get_stats():
    """Get statistics about the recommendation system"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Get total jobs with embeddings
        cur.execute('SELECT COUNT(*) FROM "Job Roles" WHERE embedding IS NOT NULL')
        total_jobs = cur.fetchone()[0]
        
        # Get category distribution
        cur.execute('SELECT "Category", COUNT(*) as count FROM "Job Roles" GROUP BY "Category" ORDER BY count DESC LIMIT 10')
        categories = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        
        return {
            "total_jobs": total_jobs,
            "top_categories": categories,
            "embedding_dimensions": 384,
            "model": "all-MiniLM-L6-v2",
            "memory_optimized": True,
            "using_database_storage": True
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
