from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import psycopg2
from psycopg2.extras import RealDictCursor
import warnings
import os
from dotenv import load_dotenv
import re
import requests
from transformers import pipeline

warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Chatbot API",
    description="AI-powered career chatbot with intent recognition and job recommendations",
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

# API URLs
JOB_RECOMMENDATION_API = os.getenv("JOB_RECOMMENDATION_API", "http://localhost:8000/api/recommend")
SKILL_GAP_API = os.getenv("SKILL_GAP_API", "http://localhost:8001/api/skill-gap")

# Global variables for models
intent_classifier = None
ner_model = None
response_generator = None

# Predefined intents
INTENT_LABELS = [
    "show job recommendations",
    "analyze skill gap", 
    "ask about salary",
    "add or update skills",
    "career advice",
    "general question"
]

# Pydantic models
class ChatRequest(BaseModel):
    user_id: str
    query: str

class ChatResponse(BaseModel):
    success: bool
    user_id: str
    query: str
    intent: str
    response: str
    extracted_skills: Optional[List[str]] = None
    job_recommendations: Optional[List[Dict]] = None
    skill_gap_analysis: Optional[Dict] = None


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from user query using pattern matching and NLP"""
    # Common skill keywords and patterns
    skill_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|swift|kotlin)\b',
        r'\b(react|angular|vue|node\.?js|express|django|flask|spring|laravel)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|oracle)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible)\b',
        r'\b(machine learning|ml|deep learning|ai|artificial intelligence|nlp|computer vision)\b',
        r'\b(tensorflow|pytorch|keras|scikit-learn|pandas|numpy)\b',
        r'\b(html|css|sass|less|bootstrap|tailwind)\b',
        r'\b(git|github|gitlab|bitbucket|jira|agile|scrum)\b',
        r'\b(rest api|graphql|microservices|websockets)\b',
        r'\b(data analysis|data science|big data|hadoop|spark)\b',
        r'\b(excel|power bi|tableau|looker|data visualization)\b',
        r'\b(project management|leadership|communication|problem solving)\b'
    ]
    
    skills = []
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        skills.extend(matches)
    
    # Remove duplicates and clean
    skills = list(set([skill.strip() for skill in skills if skill.strip()]))
    
    return skills


def classify_intent(query: str) -> str:
    """Classify user intent using zero-shot classification"""
    global zero_shot_classifier
    
    candidate_labels = [
        "add_skills",           # User wants to add/update their skills
        "show_jobs",            # User wants to see job recommendations
        "skill_gap",            # User wants skill gap analysis
        "career_advice",        # User wants career guidance
        "salary_info",          # User wants salary information
        "general_query"         # General question
    ]
    
    try:
        result = zero_shot_classifier(query, candidate_labels)
        intent = result['labels'][0]
        confidence = result['scores'][0]
        
        # If confidence is low, classify as general query
        if confidence < 0.3:
            return "general_query"
        
        return intent
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "general_query"


def fetch_user_skills(user_id: str):
    """Fetch user skills from database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT skills FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result is None:
            return []
        
        skills = result['skills']
        if isinstance(skills, list):
            return skills
        elif isinstance(skills, str):
            return [s.strip() for s in skills.split(',') if s.strip()]
        return []
    except Exception as e:
        print(f"Error fetching skills: {e}")
        return []
    finally:
        conn.close()


def update_user_skills(user_id: str, new_skills: List[str]):
    """Update user skills in database"""
    conn = get_db_connection()
    try:
        # Get existing skills
        existing_skills = fetch_user_skills(user_id)
        
        # Merge with new skills (avoid duplicates)
        all_skills = list(set(existing_skills + new_skills))
        
        cursor = conn.cursor()
        query = "UPDATE users SET skills = %s WHERE user_id = %s"
        cursor.execute(query, (all_skills, user_id))
        conn.commit()
        cursor.close()
        
        return all_skills
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update skills: {str(e)}")
    finally:
        conn.close()


def call_job_recommendation_api(user_id: str, top_n: int = 10):
    """Call the job recommendation API"""
    try:
        response = requests.post(
            JOB_RECOMMENDATION_API,
            json={"user_id": user_id, "top_n": top_n},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('recommendations', [])
        else:
            return None
    except Exception as e:
        print(f"Error calling job recommendation API: {e}")
        return None


def call_skill_gap_api(user_id: str, top_n: int = 5):
    """Call the skill gap analysis API"""
    try:
        response = requests.post(
            SKILL_GAP_API,
            json={"user_id": user_id, "top_n": top_n},
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error calling skill gap API: {e}")
        return None


def generate_conversational_response(query: str) -> str:
    """Generate conversational response using AI for general queries"""
    global conversational_pipeline
    
    if conversational_pipeline is None:
        return "I'm your career assistant! I can help you with job recommendations, skill gap analysis, and career advice. What would you like to know?"
    
    try:
        # Use conversational AI
        response = conversational_pipeline(query, max_length=150, do_sample=True, temperature=0.7)
        generated_text = response[0]['generated_text']
        
        # Clean up the response
        if query.lower() in generated_text.lower():
            generated_text = generated_text.replace(query, "").strip()
        
        return generated_text if generated_text else "I'm here to help with your career! What would you like to know?"
    except Exception as e:
        print(f"Conversational AI error: {e}")
        return "I'm your career assistant! I can help you find jobs, analyze skill gaps, and provide career guidance. What would you like to know?"


def generate_response(intent: str, query: str, user_id: str, extracted_skills: List[str] = None, 
                     jobs: List = None, skill_gap_data: Dict = None) -> str:
    """Generate appropriate response based on intent"""
    
    if intent == "add_skills":
        if extracted_skills:
            skills_str = ", ".join(extracted_skills)
            return f"Great! I've added the following skills to your profile: {skills_str}. You can now get personalized job recommendations based on your skills! Would you like to see job recommendations or analyze skill gaps?"
        else:
            return "I'd be happy to add skills to your profile! Please tell me what skills you have. For example: 'I know Python, JavaScript, and React'."
    
    elif intent == "show_jobs":
        if jobs:
            if len(jobs) > 0:
                return f"Based on your skills, I found {len(jobs)} job recommendations for you! I've included the details in the response. Would you like to analyze skill gaps for high-paying jobs?"
            else:
                return "I couldn't find any matching jobs right now. Try adding more skills to your profile for better recommendations!"
        else:
            user_skills = fetch_user_skills(user_id)
            if not user_skills or len(user_skills) == 0:
                return "You don't have any skills in your profile yet. Please tell me what skills you have, for example: 'I know Python and React'."
            else:
                return "I'm having trouble fetching job recommendations right now. Please try again in a moment."
    
    elif intent == "skill_gap":
        if skill_gap_data and skill_gap_data.get('success'):
            opportunities = skill_gap_data.get('top_opportunities', [])
            if opportunities:
                top_job = opportunities[0]
                skill_gap = top_job.get('skill_gap', [])
                
                response = f"I've analyzed high-paying job opportunities for you!\n\n"
                response += f"🎯 Top Opportunity: {top_job.get('job_role')} at {top_job.get('company')}\n"
                response += f"💰 Salary: ₹{top_job.get('average_salary', 0):,.2f} LPA\n"
                response += f"📊 Match Score: {top_job.get('combined_score', 0):.2%}\n\n"
                
                if skill_gap:
                    response += f"📚 Skills you need to learn: {', '.join(skill_gap[:5])}\n"
                else:
                    response += "✅ Great news! You already have all the required skills for this role!\n"
                
                response += f"\nI found {len(opportunities)} total opportunities. Check the full analysis in the response data!"
                return response
            else:
                return "I couldn't find skill gap data. Make sure you have skills in your profile first."
        else:
            return "I'm analyzing skill gaps for high-paying jobs. Let me fetch that information for you..."
    
    elif intent == "career_advice":
        # Use conversational AI for career advice
        career_context = f"As a career advisor, {query}"
        advice = generate_conversational_response(career_context)
        
        return f"{advice}\n\nI can also help you:\n- Analyze your skill gaps for high-paying jobs\n- Show personalized job recommendations\n- Track your career progress\n\nWhat would you like to explore?"
    
    elif intent == "salary_info":
        # Get skill gap data which includes salary information
        skill_gap_data = call_skill_gap_api(user_id, top_n=10)
        
        if skill_gap_data and skill_gap_data.get('success'):
            opportunities = skill_gap_data.get('top_opportunities', [])
            if opportunities:
                salaries = [opp.get('average_salary', 0) for opp in opportunities]
                avg_salary = sum(salaries) / len(salaries)
                max_salary = max(salaries)
                
                response = f"Based on your skills, here's the salary information:\n\n"
                response += f"💰 Average Salary Range: ₹{avg_salary:,.2f} LPA\n"
                response += f"🎯 Top Salary Potential: ₹{max_salary:,.2f} LPA\n\n"
                response += f"These are based on {len(opportunities)} jobs matching your profile. "
                response += "Want to see the full skill gap analysis to maximize your earning potential?"
                
                return response
        
        return "Salary information varies by role, experience, and location. To get personalized salary insights, make sure you have skills added to your profile, then I can analyze opportunities for you!"
    
    else:  # general_query
        # Use conversational AI for general queries
        response = generate_conversational_response(query)
        
        # Add helpful suggestions
        response += "\n\nI can help you with:\n✨ Job recommendations\n✨ Skill gap analysis\n✨ Career advice\n✨ Salary insights\n\nWhat would you like to explore?"
        
        return response


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global zero_shot_classifier, conversational_pipeline
    
    print("Loading AI models...")
    try:
        print("1. Loading zero-shot classification model...")
        zero_shot_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        print("   ✓ Intent classifier loaded")
        
        print("2. Loading conversational model...")
        try:
            conversational_pipeline = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium"
            )
            print("   ✓ Conversational AI loaded")
        except Exception as e:
            print(f"   ⚠ Conversational model not loaded: {e}")
            conversational_pipeline = None
        
        print("✓ All models loaded successfully!")
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Using fallback intent detection...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Career Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": zero_shot_classifier is not None
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user query and respond based on intent
    
    Parameters:
    - user_id: User ID
    - query: User's message/query
    """
    
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="query cannot be empty")
    
    try:
        # Classify intent
        intent = classify_intent(request.query)
        print(f"Detected intent: {intent}")
        
        # Extract skills from query
        extracted_skills = extract_skills_from_text(request.query)
        print(f"Extracted skills: {extracted_skills}")
        
        # Initialize response data
        updated_skills = None
        job_recommendations = None
        skill_gap_data = None
        
        # If skills are mentioned and intent is about skills or jobs, update database
        if extracted_skills and intent in ["add_skills", "show_jobs"]:
            updated_skills = update_user_skills(request.user_id, extracted_skills)
            print(f"Updated user skills: {updated_skills}")
        
        # Handle different intents
        if intent == "show_jobs":
            # Call job recommendation API
            job_recommendations = call_job_recommendation_api(request.user_id, top_n=10)
        
        elif intent == "skill_gap":
            # Call skill gap analysis API
            skill_gap_data = call_skill_gap_api(request.user_id, top_n=5)
        
        elif intent == "salary_info":
            # Call skill gap API to get salary information
            skill_gap_data = call_skill_gap_api(request.user_id, top_n=10)
        
        # Generate response
        response_text = generate_response(
            intent=intent,
            query=request.query,
            user_id=request.user_id,
            extracted_skills=extracted_skills,
            jobs=job_recommendations,
            skill_gap_data=skill_gap_data
        )
        
        return ChatResponse(
            success=True,
            user_id=request.user_id,
            query=request.query,
            intent=intent,
            response=response_text,
            extracted_skills=extracted_skills if extracted_skills else None,
            job_recommendations=job_recommendations,
            skill_gap_analysis=skill_gap_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
