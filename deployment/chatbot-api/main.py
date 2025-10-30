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
    version="2.0.0"
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

# API URLs - These should point to your deployed APIs on Render
JOB_RECOMMENDATION_API = os.getenv("JOB_RECOMMENDATION_API", "https://job-recommendation-api.onrender.com/api/recommend")
SKILL_GAP_API = os.getenv("SKILL_GAP_API", "https://skill-gap-api.onrender.com/api/skill-gap")

# Global variables for lightweight models
intent_model = None
ner_model = None
response_model = None

# Predefined intents for classification
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


@app.on_event("startup")
async def startup_event():
    """Load lightweight ML models on startup"""
    global intent_model, ner_model, response_model
    
    try:
        print("Loading intent classification model (BART)...")
        intent_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        print("Loading NER model for skill extraction (BERT)...")
        ner_model = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        
        print("Loading response generation model (FLAN-T5 Small)...")
        response_model = pipeline("text2text-generation", model="google/flan-t5-small")
        
        print("✅ All models loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        raise


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def extract_skills_with_ner(message: str) -> List[str]:
    """
    Extract skills using NER model and pattern matching.
    Combines transformer-based NER with regex patterns for better accuracy.
    """
    global ner_model
    
    skills = []
    
    # 1. Use NER model to extract entities
    try:
        entities = ner_model(message)
        for ent in entities:
            # Filter for relevant entity types that might be skills
            if ent["entity_group"] in ["MISC", "ORG"] and len(ent["word"]) > 1:
                # Clean the extracted word
                cleaned = re.sub(r"[^a-zA-Z0-9+#+\-\.]", "", ent["word"])
                if len(cleaned) > 1:
                    skills.append(cleaned.lower())
    except Exception as e:
        print(f"NER extraction error: {e}")
    
    # 2. Pattern matching for common tech skills (fallback and enhancement)
    skill_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|swift|kotlin)\b',
        r'\b(react|angular|vue|node\.?js|express|django|flask|spring|laravel|fastapi)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|oracle|nosql)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible|ci/cd)\b',
        r'\b(machine learning|ml|deep learning|ai|nlp|computer vision)\b',
        r'\b(tensorflow|pytorch|keras|scikit-learn|pandas|numpy|scipy)\b',
        r'\b(html|css|sass|less|bootstrap|tailwind|jquery)\b',
        r'\b(git|github|gitlab|bitbucket|jira|agile|scrum|devops)\b',
        r'\b(rest api|graphql|microservices|websockets|api)\b',
        r'\b(data analysis|data science|big data|hadoop|spark|etl)\b',
        r'\b(excel|power bi|tableau|looker|data visualization)\b',
        r'\b(project management|leadership|communication)\b'
    ]
    
    text_lower = message.lower()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        skills.extend([m.lower() for m in matches])
    
    # Remove duplicates and return
    return list(set([s.strip() for s in skills if len(s) > 1]))


def detect_intent(message: str) -> str:
    """
    Detect user intent using zero-shot classification.
    Returns the most likely intent from INTENT_LABELS.
    """
    global intent_model
    
    try:
        result = intent_model(message, INTENT_LABELS)
        intent = result["labels"][0]
        confidence = result["scores"][0]
        
        print(f"Intent detected: {intent} (confidence: {confidence:.2f})")
        
        # Map to internal intent codes
        intent_mapping = {
            "show job recommendations": "show_jobs",
            "analyze skill gap": "skill_gap",
            "ask about salary": "salary_info",
            "add or update skills": "add_skills",
            "career advice": "career_advice",
            "general question": "general_query"
        }
        
        return intent_mapping.get(intent, "general_query")
        
    except Exception as e:
        print(f"Intent detection error: {e}")
        return "general_query"


def generate_ai_response(message: str, intent: str, context: str = "") -> str:
    """
    Generate a conversational response using FLAN-T5.
    Uses the lightweight text2text-generation model.
    """
    global response_model
    
    try:
        # Create a prompt based on intent and context
        if context:
            prompt = f"User asked: {message}\nContext: {context}\nProvide a helpful reply:"
        else:
            prompt = f"User asked: {message}\nProvide a helpful reply about careers and jobs:"
        
        response = response_model(prompt, max_new_tokens=100, num_return_sequences=1)
        return response[0]["generated_text"]
        
    except Exception as e:
        print(f"Response generation error: {e}")
        return "I understand your question. Let me help you with that."


def call_job_recommendation_api(user_id: str) -> Optional[List[Dict]]:
    """
    Call the job recommendation API (Port 8000).
    Returns: List of {job_id, similarity_score}
    """
    try:
        response = requests.post(
            JOB_RECOMMENDATION_API,
            json={"user_id": user_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recommendations", [])
        else:
            print(f"Job API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error calling job recommendation API: {e}")
        return None


def call_skill_gap_api(user_id: str) -> Optional[Dict]:
    """
    Call the skill gap analysis API (Port 8001).
    Returns: Full analysis with job details, salary info, and missing skills
    """
    try:
        response = requests.post(
            SKILL_GAP_API,
            json={"user_id": user_id},
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Skill gap API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error calling skill gap API: {e}")
        return None


def fetch_user_skills(user_id: str) -> List[str]:
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
        else:
            return []
    except Exception as e:
        print(f"Error fetching user skills: {e}")
        return []
    finally:
        conn.close()


def update_user_skills(user_id: str, new_skills: List[str]) -> bool:
    """Update user skills in database (merge with existing)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Fetch existing skills
        existing_skills = fetch_user_skills(user_id)
        
        # Merge and deduplicate
        all_skills = list(set(existing_skills + new_skills))
        
        # Update in database
        query = "UPDATE users SET skills = %s WHERE user_id = %s"
        cursor.execute(query, (all_skills, user_id))
        conn.commit()
        cursor.close()
        
        return True
    except Exception as e:
        print(f"Error updating user skills: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def generate_response(user_id: str, query: str, intent: str, skills: List[str]) -> Dict:
    """
    Generate appropriate response based on detected intent.
    Calls other APIs when needed and uses AI for conversational responses.
    """
    
    response_text = ""
    job_recs = None
    skill_gap = None
    
    # --- Intent: Show Job Recommendations ---
    if intent == "show_jobs":
        job_recs = call_job_recommendation_api(user_id)
        
        if job_recs and len(job_recs) > 0:
            response_text = f"🎯 I found {len(job_recs)} job recommendations for you based on your skills! "
            response_text += f"The top match has a {job_recs[0]['similarity_score']:.1%} compatibility score. "
            response_text += "Check the job_recommendations field for details."
        else:
            response_text = "I couldn't find any job matches right now. Try adding more skills to your profile!"
    
    # --- Intent: Skill Gap Analysis ---
    elif intent == "skill_gap":
        skill_gap = call_skill_gap_api(user_id)
        
        if skill_gap and skill_gap.get("success"):
            top_jobs = skill_gap.get("top_opportunities", [])
            if top_jobs:
                top = top_jobs[0]
                job_role = top.get("job_role", "N/A")
                missing = top.get("missing_skills", [])
                avg_salary = top.get("avg_salary", 0)
                
                response_text = f"📊 **Skill Gap Analysis:**\n\n"
                response_text += f"🎯 Top Opportunity: **{job_role}**\n"
                response_text += f"💰 Average Salary: ₹{avg_salary:,.0f}\n"
                
                if missing:
                    response_text += f"📚 Skills to Learn: {', '.join(missing[:5])}\n"
                    response_text += f"\n💡 Focus on these {len(missing)} skills to increase your chances!"
                else:
                    response_text += "✅ You have all required skills for this role!"
            else:
                response_text = "I analyzed the job market but couldn't find specific gaps. Add more skills to get better insights!"
        else:
            response_text = "Unable to analyze skill gaps right now. Please try again."
    
    # --- Intent: Salary Information ---
    elif intent == "salary_info":
        skill_gap = call_skill_gap_api(user_id)
        
        if skill_gap and skill_gap.get("success"):
            top_jobs = skill_gap.get("top_opportunities", [])
            if top_jobs:
                salaries = [job.get("avg_salary", 0) for job in top_jobs[:5]]
                avg = sum(salaries) / len(salaries)
                max_sal = max(salaries)
                
                response_text = f"💰 **Salary Insights:**\n\n"
                response_text += f"📈 Average Salary (Top 5 matches): ₹{avg:,.0f}\n"
                response_text += f"🚀 Highest Potential: ₹{max_sal:,.0f}\n"
                response_text += f"\nBased on your current skills, you can target roles in this range!"
            else:
                response_text = "I need more information about your skills to provide salary insights."
        else:
            response_text = "Unable to fetch salary data right now. Please try again."
    
    # --- Intent: Add/Update Skills ---
    elif intent == "add_skills":
        if skills:
            success = update_user_skills(user_id, skills)
            if success:
                response_text = f"✅ Great! I've added {len(skills)} new skills to your profile: "
                response_text += f"{', '.join(skills)}. "
                response_text += "This will improve your job recommendations!"
            else:
                response_text = "I detected skills but couldn't update your profile. Please try again."
        else:
            response_text = "I didn't detect any specific skills in your message. Try mentioning skills like 'Python', 'React', 'Machine Learning', etc."
    
    # --- Intent: Career Advice ---
    elif intent == "career_advice":
        # Get user's current skills for context
        current_skills = fetch_user_skills(user_id)
        context = f"User has skills: {', '.join(current_skills[:5]) if current_skills else 'None yet'}"
        
        # Use AI to generate personalized advice
        ai_response = generate_ai_response(query, intent, context)
        response_text = f"💼 **Career Advice:**\n\n{ai_response}\n\n"
        response_text += "💡 Tip: Use 'show jobs' to see personalized recommendations or 'skill gap' to identify areas for growth!"
    
    # --- Intent: General Query ---
    else:  # general_query
        # Use AI for general conversational responses
        ai_response = generate_ai_response(query, intent)
        response_text = ai_response
        response_text += "\n\n💬 You can ask me to:\n• Show job recommendations\n• Analyze skill gaps\n• Check salary ranges\n• Add new skills\n• Get career advice"
    
    return {
        "response": response_text,
        "job_recommendations": job_recs,
        "skill_gap_analysis": skill_gap
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chatbot endpoint.
    Detects intent, extracts skills, calls appropriate APIs, and generates response.
    """
    try:
        # 1. Detect intent
        intent = detect_intent(request.query)
        
        # 2. Extract skills from query
        extracted_skills = extract_skills_with_ner(request.query)
        
        print(f"User: {request.user_id} | Query: {request.query}")
        print(f"Intent: {intent} | Skills: {extracted_skills}")
        
        # 3. Generate response based on intent
        result = generate_response(request.user_id, request.query, intent, extracted_skills)
        
        return ChatResponse(
            success=True,
            user_id=request.user_id,
            query=request.query,
            intent=intent,
            response=result["response"],
            extracted_skills=extracted_skills if extracted_skills else None,
            job_recommendations=result["job_recommendations"],
            skill_gap_analysis=result["skill_gap_analysis"]
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Career Chatbot API v2.0",
        "status": "running",
        "models": {
            "intent": "facebook/bart-large-mnli",
            "ner": "dslim/bert-base-NER", 
            "response": "google/flan-t5-small"
        },
        "endpoints": {
            "chat": "/api/chat (POST)"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": all([intent_model, ner_model, response_model])
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
