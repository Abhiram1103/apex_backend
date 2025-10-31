from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import re
import requests

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Chatbot API - Production",
    description="Lightweight chatbot for skill extraction and job recommendations",
    version="3.0.0"
)

# CORS middleware - Configure for production
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

# Allow multiple origins
allowed_origins = ["*"] if FRONTEND_URL == "*" else [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
    "https://*.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
)

# Job Recommendation API URL
JOB_RECOMMENDATION_API = os.getenv(
    "JOB_RECOMMENDATION_API",
    "https://apex-backend-zmeq.onrender.com/api/recommend"
)


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    user_id: str
    query: str
    n: Optional[int] = 10  # Number of job recommendations to fetch

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "cde634c5-77c0-4004-834f-4f9caec051e6",
                "query": "I know Python, Machine Learning, and React. Show me relevant jobs.",
                "n": 10
            }
        }


class ChatResponse(BaseModel):
    success: bool
    user_id: str
    query: str
    message: str
    extracted_skills: List[str]
    skills_saved: bool
    job_recommendations: Optional[List[Dict]] = None
    total_jobs: Optional[int] = 0


# ==================== Skill Extraction ====================

# Comprehensive skill patterns (600+ common tech skills)
SKILL_PATTERNS = {
    # Programming Languages
    'languages': [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|golang|rust|swift|kotlin|'
        r'php|perl|scala|r|matlab|shell|bash|powershell|objective-c|dart|elixir|haskell|'
        r'lua|groovy|coffeescript|vb\.net|visual basic|fortran|cobol|assembly|lisp|prolog)\b'
    ],
    
    # Web Frameworks
    'web_frameworks': [
        r'\b(react|angular|vue|svelte|next\.?js|nuxt|gatsby|ember|backbone|meteor|'
        r'express|koa|fastify|nest\.?js|django|flask|fastapi|rails|laravel|symfony|'
        r'spring|spring boot|asp\.net|blazor|play framework|gin|echo|fiber)\b'
    ],
    
    # Databases
    'databases': [
        r'\b(mysql|postgresql|postgres|mongodb|redis|elasticsearch|cassandra|oracle|'
        r'sql server|mariadb|sqlite|dynamodb|couchdb|neo4j|influxdb|timescaledb|'
        r'firebase|supabase|cockroachdb|fauna|prisma|sequelize|typeorm|mongoose|'
        r'sql|nosql|plsql|tsql)\b'
    ],
    
    # Cloud & DevOps
    'cloud_devops': [
        r'\b(aws|azure|gcp|google cloud|kubernetes|k8s|docker|jenkins|gitlab ci|'
        r'github actions|circleci|travis ci|terraform|ansible|puppet|chef|vagrant|'
        r'helm|istio|prometheus|grafana|datadog|new relic|splunk|elk stack|'
        r'cloudformation|lambda|ec2|s3|rds|eks|ecs|fargate|cloud functions|'
        r'app engine|cloud run|azure functions|devops|ci/cd|continuous integration|'
        r'continuous deployment)\b'
    ],
    
    # AI/ML/Data Science
    'ai_ml': [
        r'\b(machine learning|ml|deep learning|dl|artificial intelligence|ai|nlp|'
        r'natural language processing|computer vision|cv|tensorflow|pytorch|keras|'
        r'scikit-learn|sklearn|pandas|numpy|scipy|matplotlib|seaborn|plotly|'
        r'jupyter|neural network|cnn|rnn|lstm|gru|transformer|bert|gpt|llm|'
        r'large language model|hugging face|opencv|yolo|object detection|'
        r'classification|regression|clustering|xgboost|lightgbm|catboost|'
        r'reinforcement learning|gan|generative adversarial network|'
        r'data science|data analysis|data mining|statistical analysis)\b'
    ],
    
    # Big Data
    'big_data': [
        r'\b(hadoop|spark|kafka|flink|storm|hive|pig|hbase|impala|presto|'
        r'airflow|luigi|dask|ray|databricks|snowflake|redshift|bigquery|'
        r'etl|data warehouse|data lake|data pipeline|stream processing)\b'
    ],
    
    # Mobile Development
    'mobile': [
        r'\b(android|ios|react native|flutter|xamarin|ionic|cordova|'
        r'swift ui|jetpack compose|kotlin multiplatform|mobile development)\b'
    ],
    
    # Testing
    'testing': [
        r'\b(jest|mocha|chai|jasmine|pytest|unittest|selenium|cypress|'
        r'playwright|testcafe|puppeteer|junit|testng|cucumber|behave|'
        r'unit testing|integration testing|e2e testing|tdd|bdd)\b'
    ],
    
    # API & Architecture
    'api_architecture': [
        r'\b(rest api|restful|graphql|grpc|soap|microservices|monolith|'
        r'event-driven|message queue|rabbitmq|activemq|mqtt|websocket|'
        r'api gateway|service mesh|serverless|lambda architecture)\b'
    ],
    
    # Version Control & Tools
    'tools': [
        r'\b(git|github|gitlab|bitbucket|svn|mercurial|jira|confluence|'
        r'trello|asana|slack|teams|notion|figma|adobe xd|sketch|invision|'
        r'postman|insomnia|swagger|openapi)\b'
    ],
    
    # Frontend Technologies
    'frontend': [
        r'\b(html|html5|css|css3|sass|scss|less|tailwind|bootstrap|'
        r'material ui|mui|ant design|chakra ui|styled components|'
        r'emotion|webpack|vite|rollup|parcel|babel|eslint|prettier|'
        r'redux|mobx|zustand|recoil|context api|rxjs|jquery)\b'
    ],
    
    # Backend Technologies
    'backend': [
        r'\b(node\.?js|deno|bun|nginx|apache|tomcat|iis|gunicorn|uvicorn|'
        r'celery|redis queue|bull|resque|sidekiq|oauth|jwt|passport|'
        r'authentication|authorization|session management)\b'
    ],
    
    # Blockchain
    'blockchain': [
        r'\b(blockchain|ethereum|solidity|web3|bitcoin|cryptocurrency|'
        r'smart contract|nft|defi|polygon|binance|hyperledger)\b'
    ],
    
    # Game Development
    'game_dev': [
        r'\b(unity|unreal engine|godot|game development|opengl|directx|'
        r'vulkan|metal|shader|3d modeling|blender)\b'
    ],
    
    # Security
    'security': [
        r'\b(cybersecurity|penetration testing|ethical hacking|owasp|'
        r'encryption|ssl|tls|vpn|firewall|ids|ips|siem|vulnerability|'
        r'security audit|compliance|gdpr|hipaa)\b'
    ],
    
    # Methodologies
    'methodologies': [
        r'\b(agile|scrum|kanban|waterfall|lean|six sigma|prince2|pmp|'
        r'project management|product management|business analysis)\b'
    ],
    
    # Soft Skills
    'soft_skills': [
        r'\b(leadership|communication|teamwork|problem solving|critical thinking|'
        r'collaboration|presentation|negotiation|time management|adaptability)\b'
    ],
    
    # Data Visualization
    'visualization': [
        r'\b(power bi|tableau|looker|metabase|superset|d3\.js|chart\.js|'
        r'highcharts|data visualization|dashboard|reporting)\b'
    ],
    
    # Other Technologies
    'other': [
        r'\b(linux|unix|windows|macos|bash|vim|emacs|vscode|intellij|'
        r'pycharm|eclipse|netbeans|sublime|excel|powerpoint|word|'
        r'ms office|google workspace|sap|salesforce|erp|crm)\b'
    ]
}


def extract_skills_from_query(query: str) -> List[str]:
    """
    Extract skills from user query using regex pattern matching.
    Returns deduplicated list of detected skills.
    """
    query_lower = query.lower()
    detected_skills = set()
    
    # Check all skill patterns
    for category, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            detected_skills.update(matches)
    
    # Clean and format skills
    cleaned_skills = []
    for skill in detected_skills:
        # Remove extra spaces and normalize
        skill = skill.strip()
        
        # Handle special cases
        skill_mappings = {
            'k8s': 'kubernetes',
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'node.js': 'nodejs',
            'node js': 'nodejs',
            'next.js': 'nextjs',
            'next js': 'nextjs',
            'vue.js': 'vue',
            'react.js': 'react',
            'angular.js': 'angular',
            'd3.js': 'd3',
            'c++': 'cpp',
            'c#': 'csharp',
            'asp.net': 'aspnet',
            'vb.net': 'vbnet',
        }
        
        skill = skill_mappings.get(skill, skill)
        
        # Only include skills with length > 1
        if len(skill) > 1:
            # Capitalize properly
            if skill in ['html', 'css', 'sql', 'api', 'aws', 'gcp', 'nlp', 'tdd', 'bdd', 'jwt', 'ai', 'ml', 'cv', 'dl']:
                cleaned_skills.append(skill.upper())
            elif skill in ['nodejs', 'nextjs', 'nestjs', 'fastapi', 'pytorch', 'tensorflow', 'mongodb', 'postgresql', 'mysql', 'github', 'gitlab', 'bitbucket']:
                cleaned_skills.append(skill.title())
            else:
                cleaned_skills.append(skill.capitalize())
    
    return sorted(list(set(cleaned_skills)))


# ==================== Database Functions ====================

def get_db_connection():
    """
    Create and return a database connection with optimized settings.
    Uses minimal memory configuration for Render's 512MB plan.
    """
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            connect_timeout=10,
            options='-c statement_timeout=30000'  # 30 second timeout
        )
        # Use autocommit mode to reduce memory overhead
        conn.set_session(autocommit=False)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


def save_skills_to_database(user_id: str, new_skills: List[str]) -> bool:
    """
    Save extracted skills to the Users table.
    Merges with existing skills (no duplicates).
    """
    if not new_skills:
        return False
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Fetch existing skills
        cursor.execute("SELECT skills FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        existing_skills = []
        if result and result['skills']:
            if isinstance(result['skills'], list):
                existing_skills = result['skills']
            elif isinstance(result['skills'], str):
                existing_skills = [s.strip() for s in result['skills'].split(',') if s.strip()]
        
        # Merge and deduplicate
        all_skills = list(set(existing_skills + new_skills))
        
        # Update database
        if result:
            # User exists, update skills
            cursor.execute(
                "UPDATE users SET skills = %s WHERE user_id = %s",
                (all_skills, user_id)
            )
        else:
            # User doesn't exist, insert new record
            cursor.execute(
                "INSERT INTO users (user_id, skills) VALUES (%s, %s)",
                (user_id, all_skills)
            )
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving skills to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ==================== External API Calls ====================

def call_job_recommendation_api(user_id: str, n: int = 10) -> Optional[Dict]:
    """
    Call the job recommendation API hosted on Render.
    Returns job recommendations based on user skills.
    Optimized with proper timeouts and connection reuse.
    """
    try:
        payload = {
            "user_id": user_id,
            "n": n
        }
        
        print(f"📡 Calling Job Recommendation API: {JOB_RECOMMENDATION_API}")
        print(f"📦 Payload: {payload}")
        
        # Use a session for connection reuse (reduces memory)
        with requests.Session() as session:
            response = session.post(
                JOB_RECOMMENDATION_API,
                json=payload,
                timeout=30,  # 30 second timeout
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job API returned {len(data.get('recommendations', []))} recommendations")
            return data
        else:
            print(f"❌ Job API error: {response.status_code} - {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏱️ Job API request timed out (30s)")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection error to Job API: {e}")
        return None
    except Exception as e:
        print(f"❌ Error calling job recommendation API: {e}")
        return None


# ==================== API Endpoints ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chatbot endpoint.
    
    Process:
    1. Extract skills from user query
    2. Save skills to database (Users table)
    3. Call job recommendation API with user_id and n parameters
    4. Return response with extracted skills and job recommendations
    """
    try:
        print(f"\n{'='*60}")
        print(f"🗣️ User {request.user_id} said: {request.query}")
        print(f"{'='*60}")
        
        # Step 1: Extract skills from query
        extracted_skills = extract_skills_from_query(request.query)
        print(f"🔍 Extracted {len(extracted_skills)} skills: {extracted_skills}")
        
        # Step 2: Save skills to database
        skills_saved = False
        if extracted_skills:
            skills_saved = save_skills_to_database(request.user_id, extracted_skills)
            if skills_saved:
                print(f"💾 Skills saved to database for user {request.user_id}")
            else:
                print(f"⚠️ Failed to save skills to database")
        else:
            print(f"ℹ️ No skills detected in query")
        
        # Step 3: Call job recommendation API
        job_data = call_job_recommendation_api(request.user_id, request.n)
        
        # Step 4: Generate response message
        if extracted_skills:
            if skills_saved:
                message = f"✅ Great! I've added {len(extracted_skills)} skills to your profile: {', '.join(extracted_skills[:5])}"
                if len(extracted_skills) > 5:
                    message += f" and {len(extracted_skills) - 5} more"
                message += ". "
            else:
                message = f"⚠️ Detected {len(extracted_skills)} skills but couldn't save them to your profile. "
        else:
            message = "ℹ️ I didn't detect any specific skills in your message. Try mentioning skills like Python, React, Machine Learning, etc. "
        
        # Add job recommendation info
        if job_data and job_data.get("success"):
            recommendations = job_data.get("recommendations", [])
            if recommendations:
                message += f"\n\n🎯 Found {len(recommendations)} job recommendations for you! "
                top_job = recommendations[0]
                message += f"Top match: {top_job.get('Job Role', 'N/A')} with {top_job.get('similarity_score', 0):.1%} compatibility."
            else:
                message += "\n\n😔 No job matches found yet. Add more skills to get better recommendations!"
        else:
            message += "\n\n⚠️ Couldn't fetch job recommendations at the moment. Please try again."
        
        return ChatResponse(
            success=True,
            user_id=request.user_id,
            query=request.query,
            message=message,
            extracted_skills=extracted_skills,
            skills_saved=skills_saved,
            job_recommendations=job_data.get("recommendations") if job_data else None,
            total_jobs=len(job_data.get("recommendations", [])) if job_data else 0
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Career Chatbot API - Production Ready",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "Skill extraction from natural language",
            "Database storage of user skills",
            "Job recommendation integration",
            "Lightweight and memory-efficient"
        ],
        "endpoints": {
            "chat": "POST /api/chat",
            "health": "GET /health"
        },
        "usage": {
            "example": {
                "user_id": "your-user-id",
                "query": "I know Python, Machine Learning, and React",
                "n": 10
            }
        }
    }


@app.get("/health")
async def health():
    """
    Health check endpoint with memory monitoring.
    Reports database and API connectivity status.
    """
    import sys
    
    # Check database connection
    db_connected = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_connected = True
    except Exception as e:
        print(f"⚠️ Database health check failed: {e}")
    
    # Check Job API reachability
    api_reachable = False
    try:
        health_url = JOB_RECOMMENDATION_API.replace("/api/recommend", "/health")
        response = requests.get(health_url, timeout=5)
        api_reachable = response.status_code == 200
    except Exception as e:
        print(f"⚠️ Job API health check failed: {e}")
    
    # Get memory info (approximate)
    try:
        import psutil
        import os as os_module
        process = psutil.Process(os_module.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
    except:
        memory_mb = None
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "database_connected": db_connected,
        "job_api_reachable": api_reachable,
        "version": "3.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "memory_mb": round(memory_mb, 2) if memory_mb else "unavailable",
        "memory_optimized": True,
        "skill_patterns": len(SKILL_PATTERNS),
        "job_api_url": JOB_RECOMMENDATION_API,
        "cors_enabled": True
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    print(f"🚀 Starting Career Chatbot API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
