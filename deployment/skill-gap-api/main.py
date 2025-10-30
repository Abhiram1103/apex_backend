from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Set
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
    title="Skill Gap Analysis API",
    description="AI-powered skill gap analysis for high-paying jobs with ROI calculation",
    version="1.0.0"
)

# CORS middleware - Allow requests from Vercel frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://your-frontend.vercel.app")
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
class SkillGapRequest(BaseModel):
    user_id: str
    top_n: Optional[int] = 10

class SkillGapAnalysis(BaseModel):
    job_id: str
    job_role: str
    company: str
    avg_salary: float
    min_salary: float
    max_salary: float
    similarity_score: float
    normalized_salary: float
    combined_score: float
    missing_skills: List[str]
    matching_skills: List[str]

class SkillGapResponse(BaseModel):
    success: bool
    user_id: str
    user_skills: List[str]
    top_opportunities: List[SkillGapAnalysis]
    total_jobs_analyzed: int


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def clean_text(text):
    """Clean text by removing punctuation, stop words, etc."""
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


def parse_skills(skills_data):
    """Parse skills into a list"""
    if isinstance(skills_data, list):
        return [skill.strip().lower() for skill in skills_data if skill.strip()]
    elif isinstance(skills_data, str):
        skills = re.split(r'[,\s]+', skills_data)
        return [skill.strip().lower() for skill in skills if skill.strip()]
    return []


@app.on_event("startup")
async def startup_event():
    """Load model and cache job data on startup"""
    global model, job_data_cache, job_embeddings_cache
    
    print("🚀 Starting Skill Gap Analysis API...")
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
        "service": "Skill Gap Analysis API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "skill_gap": "/api/skill-gap (POST)"
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


@app.post("/api/skill-gap", response_model=SkillGapResponse)
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gap for high-paying jobs
    
    Request Body:
    {
        "user_id": "user123",
        "top_n": 10
    }
    
    Response:
    {
        "success": true,
        "user_id": "user123",
        "user_skills": ["python", "sql"],
        "top_opportunities": [
            {
                "job_id": "uuid",
                "job_role": "Data Scientist",
                "company": "Company Name",
                "avg_salary": 850000,
                "missing_skills": ["machine learning", "tensorflow"],
                ...
            }
        ],
        "total_jobs_analyzed": 500
    }
    """
    global model, job_data_cache, job_embeddings_cache
    
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id cannot be empty")
    
    if request.top_n < 1 or request.top_n > 100:
        raise HTTPException(status_code=400, detail="top_n must be between 1 and 100")
    
    if model is None or job_data_cache is None or job_embeddings_cache is None:
        raise HTTPException(
            status_code=503, 
            detail="Model or job data not loaded. Please wait"
        )
    
    try:
        # Fetch user skills
        user_skills_data = fetch_user_skills(request.user_id)
        user_skills_list = parse_skills(user_skills_data)
        
        if not user_skills_list:
            raise HTTPException(status_code=400, detail="User has no skills in database")
        
        # Create user skills text
        user_skill_text = " ".join(user_skills_list)
        cleaned_user_skills = clean_text(user_skill_text)
        
        # Generate embedding for user skills
        user_embedding = model.encode([cleaned_user_skills])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_embedding, job_embeddings_cache)[0]
        
        # Add similarity scores to dataframe
        df_with_scores = job_data_cache.copy()
        df_with_scores['similarity_score'] = similarities
        
        # Min-Max normalize the Average salary column
        df_with_scores['Average salary'] = pd.to_numeric(df_with_scores['Average salary'], errors='coerce')
        df_with_scores['Min Salary'] = pd.to_numeric(df_with_scores.get('Min Salary', 0), errors='coerce')
        df_with_scores['Max Salary'] = pd.to_numeric(df_with_scores.get('Max Salary', 0), errors='coerce')
        df_with_scores = df_with_scores.dropna(subset=['Average salary'])
        
        min_salary = df_with_scores['Average salary'].min()
        max_salary = df_with_scores['Average salary'].max()
        
        if max_salary > min_salary:
            df_with_scores['normalized_salary'] = (
                (df_with_scores['Average salary'] - min_salary) / (max_salary - min_salary)
            )
        else:
            df_with_scores['normalized_salary'] = 0.5
        
        # Calculate combined score (70% similarity, 30% salary)
        w_similarity = 0.7
        w_salary = 0.3
        df_with_scores['combined_score'] = (
            w_similarity * df_with_scores['similarity_score'] + 
            w_salary * df_with_scores['normalized_salary']
        )
        
        # Sort by combined score and get top N
        top_jobs = df_with_scores.nlargest(request.top_n, 'combined_score')
        
        # Calculate skill gaps
        opportunities = []
        for _, job in top_jobs.iterrows():
            # Parse job required skills
            job_skills_raw = str(job.get('Required Skills', ''))
            job_skills_list = parse_skills(job_skills_raw)
            
            # Calculate skill gap
            user_skills_set = set(user_skills_list)
            job_skills_set = set(job_skills_list)
            missing_skills = list(job_skills_set - user_skills_set)
            matching_skills = list(user_skills_set & job_skills_set)
            
            opportunities.append(SkillGapAnalysis(
                job_id=str(job.get('id', '')),
                job_role=str(job.get('Job Role', 'N/A')),
                company=str(job.get('Company', 'N/A')),
                avg_salary=float(job['Average salary']),
                min_salary=float(job.get('Min Salary', 0)),
                max_salary=float(job.get('Max Salary', 0)),
                similarity_score=float(job['similarity_score']),
                normalized_salary=float(job['normalized_salary']),
                combined_score=float(job['combined_score']),
                missing_skills=missing_skills,
                matching_skills=matching_skills
            ))
        
        return SkillGapResponse(
            success=True,
            user_id=request.user_id,
            user_skills=user_skills_list,
            top_opportunities=opportunities,
            total_jobs_analyzed=len(df_with_scores)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
