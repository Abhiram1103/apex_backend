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
import warnings
import os

warnings.filterwarnings('ignore')

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
DATABASE_URL = "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Global variable for model only (no more in-memory cache!)
model = None

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
    # Keep alphanumeric, spaces, and important tech symbols
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
            'category': row['Category'],
            'job_role': row['Job Role'],
            'location': row['Location'],
            'job_description': row['Job Description'],
            'required_skills': row['Required Skills'],
            'min_salary': row['Min Salary'],
            'max_salary': row['Max Salary'],
            'average_salary': row['Average salary'],
            'company': row['Company']
        })
    
    cur.close()
    
    # Convert to numpy array for similarity calculation
    embeddings_array = np.array(embeddings_list)
    
    return jobs, embeddings_array


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
    """Lightweight startup - only log, no caching!"""
    print("🚀 Skill Gap Analysis API started!")
    print("✅ Using database-backed embeddings (memory efficient)")
    print("💾 Memory usage: ~100MB (vs 500MB with cache)")
    print("📊 Model loads on first request")


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
    conn = get_db_connection()
    
    try:
        # Fetch user skills
        user_skills_data = fetch_user_skills(request.user_id)
        user_skills_list = parse_skills(user_skills_data)
        
        if not user_skills_list:
            raise HTTPException(status_code=400, detail="User has no skills in database")
        
        # Create user skills text
        user_skill_text = " ".join(user_skills_list)
        cleaned_user_skills = clean_text(user_skill_text)
        
        # Get model (lazy load)
        current_model = get_model()
        
        # Generate embedding for user skills
        user_embedding = current_model.encode([cleaned_user_skills])
        
        # Fetch job embeddings from database (not from cache!)
        jobs, job_embeddings = fetch_job_embeddings_from_db(conn)
        
        if len(jobs) == 0:
            raise HTTPException(status_code=404, detail="No jobs with embeddings found")
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_embedding, job_embeddings)[0]
        
        # Create list with jobs and scores
        jobs_with_scores = []
        for i, job in enumerate(jobs):
            jobs_with_scores.append({
                **job,
                'similarity_score': similarities[i]
            })
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(jobs_with_scores)
        
        # Normalize salaries
        df['average_salary'] = pd.to_numeric(df['average_salary'], errors='coerce')
        df['min_salary'] = pd.to_numeric(df['min_salary'], errors='coerce')
        df['max_salary'] = pd.to_numeric(df['max_salary'], errors='coerce')
        df = df.dropna(subset=['average_salary'])
        
        min_salary = df['average_salary'].min()
        max_salary = df['average_salary'].max()
        
        if max_salary > min_salary:
            df['normalized_salary'] = (df['average_salary'] - min_salary) / (max_salary - min_salary)
        else:
            df['normalized_salary'] = 0.5
        
        # Calculate combined score (70% similarity, 30% salary)
        df['combined_score'] = 0.7 * df['similarity_score'] + 0.3 * df['normalized_salary']
        
        # Sort by combined score and get top N
        top_jobs = df.nlargest(request.top_n, 'combined_score')
        
        # Calculate skill gaps
        opportunities = []
        for _, job in top_jobs.iterrows():
            # Parse job required skills
            job_skills_list = parse_skills(job['required_skills'])
            
            # Calculate skill gap
            user_skills_set = set(user_skills_list)
            job_skills_set = set(job_skills_list)
            missing_skills = list(job_skills_set - user_skills_set)
            matching_skills = list(user_skills_set & job_skills_set)
            
            opportunities.append(SkillGapAnalysis(
                job_id=job['id'],
                job_role=job['job_role'],
                company=job['company'],
                avg_salary=float(job['average_salary']),
                min_salary=float(job['min_salary']),
                max_salary=float(job['max_salary']),
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
            total_jobs_analyzed=len(df)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
