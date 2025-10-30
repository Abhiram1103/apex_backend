from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
from psycopg2.extras import RealDictCursor
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
import os

warnings.filterwarnings('ignore')

# Download NLTK data on startup
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except:
    pass

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

# Global variables for model and cached data
model = None
job_data_cache = None
job_embeddings_cache = None

# Pydantic models for request/response
class UserSkills(BaseModel):
    user_id: str
    top_n: Optional[int] = 10

class JobRecommendation(BaseModel):
    job_id: str
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
    - Removing stop words
    """
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text)
    text = text.replace('/', ' ')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return ' '.join(filtered_text)
    except:
        return text


def create_combined_features(row):
    """Create combined features from job data"""
    category = str(row.get('Category', ''))
    required_skills = str(row.get('Required Skills', ''))
    job_description = str(row.get('Job Description', ''))
    job_role = str(row.get('Job Role', ''))
    company = str(row.get('Company', ''))
    
    # Weight required skills 3x
    combined = f"{category} {required_skills} {required_skills} {required_skills} {job_description} {job_role} {company}"
    return combined


def fetch_jobs_from_db():
    """Fetch all jobs from the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = 'SELECT * FROM "Job Roles"'
        cursor.execute(query)
        jobs = cursor.fetchall()
        cursor.close()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")
    finally:
        conn.close()


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


def preprocess_jobs(jobs):
    """Preprocess jobs data and create embeddings"""
    df = pd.DataFrame(jobs)
    df['combined_features'] = df.apply(create_combined_features, axis=1)
    df['combined_features'] = df['combined_features'].apply(clean_text)
    return df


@app.on_event("startup")
async def startup_event():
    """Load model and cache job data on startup"""
    global model, job_data_cache, job_embeddings_cache
    
    print("🚀 Starting Job Recommendation API...")
    print("Loading SBERT model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded successfully!")
    
    print("Fetching and preprocessing jobs from database...")
    try:
        jobs = fetch_jobs_from_db()
        job_data_cache = preprocess_jobs(jobs)
        
        print("Generating embeddings for all jobs...")
        job_texts = job_data_cache['combined_features'].tolist()
        job_embeddings_cache = model.encode(job_texts, show_progress_bar=False)
        
        print(f"✅ Successfully cached {len(job_data_cache)} jobs with embeddings!")
    except Exception as e:
        print(f"⚠️ Warning: Could not cache jobs on startup: {str(e)}")
        job_data_cache = None
        job_embeddings_cache = None


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
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "jobs_cached": job_data_cache is not None,
        "total_jobs": len(job_data_cache) if job_data_cache is not None else 0
    }


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
            {"job_id": "uuid", "similarity_score": 0.85},
            ...
        ],
        "total_jobs_analyzed": 500
    }
    """
    global model, job_data_cache, job_embeddings_cache
    
    if not user_skills.user_id:
        raise HTTPException(status_code=400, detail="user_id cannot be empty")
    
    if user_skills.top_n < 1 or user_skills.top_n > 100:
        raise HTTPException(status_code=400, detail="top_n must be between 1 and 100")
    
    if model is None or job_data_cache is None or job_embeddings_cache is None:
        raise HTTPException(
            status_code=503, 
            detail="Model or job data not loaded. Please wait or try /api/refresh-cache"
        )
    
    try:
        user_skills_data = fetch_user_skills(user_skills.user_id)
        
        if isinstance(user_skills_data, list):
            user_skill_text = " ".join(user_skills_data)
        else:
            user_skill_text = str(user_skills_data)
        
        cleaned_user_skills = clean_text(user_skill_text)
        user_embedding = model.encode([cleaned_user_skills])
        similarities = cosine_similarity(user_embedding, job_embeddings_cache)[0]
        
        df_with_scores = job_data_cache.copy()
        df_with_scores['similarity_score'] = similarities
        top_jobs = df_with_scores.nlargest(user_skills.top_n, 'similarity_score')
        
        recommendations = []
        for _, job in top_jobs.iterrows():
            recommendations.append(JobRecommendation(
                job_id=str(job.get('id', '')),
                similarity_score=float(job['similarity_score'])
            ))
        
        return RecommendationResponse(
            success=True,
            recommendations=recommendations,
            total_jobs_analyzed=len(job_data_cache)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.post("/api/refresh-cache")
async def refresh_cache():
    """Refresh the job data cache from database"""
    global job_data_cache, job_embeddings_cache, model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        print("Refreshing job cache...")
        jobs = fetch_jobs_from_db()
        job_data_cache = preprocess_jobs(jobs)
        
        job_texts = job_data_cache['combined_features'].tolist()
        job_embeddings_cache = model.encode(job_texts, show_progress_bar=False)
        
        return {
            "success": True,
            "message": "Cache refreshed successfully",
            "total_jobs": len(job_data_cache)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache refresh failed: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get statistics about the recommendation system"""
    if job_data_cache is None:
        return {"message": "No data cached yet"}
    
    return {
        "total_jobs": len(job_data_cache),
        "categories": job_data_cache['Category'].value_counts().to_dict() if 'Category' in job_data_cache.columns else {},
        "embedding_dimensions": 384,
        "model": "all-MiniLM-L6-v2"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
