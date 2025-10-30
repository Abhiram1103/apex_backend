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
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

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

# CORS middleware for React frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
)

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
    
    # Remove forward slashes
    text = text.replace('/', ' ')
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters (keep only alphanumeric and spaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove stop words
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return ' '.join(filtered_text)
    except:
        # Fallback if NLTK data is not available
        return text


def create_combined_features(row):
    """Create combined features from job data"""
    category = str(row.get('Category', ''))
    required_skills = str(row.get('Required Skills', ''))
    job_description = str(row.get('Job Description', ''))
    job_role = str(row.get('Job Role', ''))
    company = str(row.get('Company', ''))
    
    # Weight required skills 3x as in the notebook
    combined = f"{category} {required_skills} {required_skills} {required_skills} {job_description} {job_role} {company}"
    return combined


def fetch_jobs_from_db():
    """Fetch all jobs from the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Adjust the table name and column names based on your actual database schema
        query = """
            SELECT * FROM "Job Roles"
        """
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
        query = """
            SELECT skills FROM users WHERE user_id = %s
        """
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
    
    # Create combined features
    df['combined_features'] = df.apply(create_combined_features, axis=1)
    
    # Clean text
    df['combined_features'] = df['combined_features'].apply(clean_text)
    
    return df


@app.on_event("startup")
async def startup_event():
    """Load model and cache job data on startup"""
    global model, job_data_cache, job_embeddings_cache
    
    print("Loading SBERT model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully!")
    
    print("Fetching and preprocessing jobs from database...")
    try:
        jobs = fetch_jobs_from_db()
        job_data_cache = preprocess_jobs(jobs)
        
        # Generate embeddings for all jobs
        print("Generating embeddings for all jobs...")
        job_texts = job_data_cache['combined_features'].tolist()
        job_embeddings_cache = model.encode(job_texts, show_progress_bar=False)
        
        print(f"Successfully cached {len(job_data_cache)} jobs with embeddings!")
    except Exception as e:
        print(f"Warning: Could not cache jobs on startup: {str(e)}")
        job_data_cache = None
        job_embeddings_cache = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Job Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/api/recommend (POST)",
            "refresh_cache": "/api/refresh-cache (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
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
    
    Parameters:
    - user_id: User ID to fetch skills from database
    - top_n: Number of top recommendations to return (default: 10)
    """
    global model, job_data_cache, job_embeddings_cache
    
    # Validate inputs
    if not user_skills.user_id:
        raise HTTPException(status_code=400, detail="user_id cannot be empty")
    
    if user_skills.top_n < 1 or user_skills.top_n > 100:
        raise HTTPException(status_code=400, detail="top_n must be between 1 and 100")
    
    # Check if model and cache are loaded
    if model is None or job_data_cache is None or job_embeddings_cache is None:
        raise HTTPException(
            status_code=503, 
            detail="Model or job data not loaded. Please wait or try /api/refresh-cache"
        )
    
    try:
        # Fetch user skills from database
        user_skills_data = fetch_user_skills(user_skills.user_id)
        
        # Convert skills to string if it's a list or array
        if isinstance(user_skills_data, list):
            user_skill_text = " ".join(user_skills_data)
        else:
            user_skill_text = str(user_skills_data)
        
        # Clean the user skills text
        cleaned_user_skills = clean_text(user_skill_text)
        
        # Generate embedding for user skills
        user_embedding = model.encode([cleaned_user_skills])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_embedding, job_embeddings_cache)[0]
        
        # Add similarity scores to dataframe
        df_with_scores = job_data_cache.copy()
        df_with_scores['similarity_score'] = similarities
        
        # Get top N recommendations
        top_jobs = df_with_scores.nlargest(user_skills.top_n, 'similarity_score')
        
        # Format response
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
    """
    Refresh the job data cache from database
    Useful when new jobs are added to the database
    """
    global job_data_cache, job_embeddings_cache, model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        print("Refreshing job cache...")
        jobs = fetch_jobs_from_db()
        job_data_cache = preprocess_jobs(jobs)
        
        # Generate embeddings for all jobs
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


@app.get("/api/debug/columns")
async def debug_columns():
    """Debug endpoint to see actual column names from database"""
    if job_data_cache is None:
        return {"message": "No data cached yet"}
    
    # Get column names and sample data
    columns = list(job_data_cache.columns)
    sample_row = job_data_cache.iloc[0].to_dict() if len(job_data_cache) > 0 else {}
    
    return {
        "columns": columns,
        "sample_data": {k: str(v)[:100] for k, v in sample_row.items()}  # Truncate long values
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
