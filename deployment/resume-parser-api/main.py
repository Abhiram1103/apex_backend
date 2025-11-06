from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional
import tempfile
import shutil
import re
import PyPDF2
import docx2txt
import spacy

app = FastAPI(
    title="Resume Parser API",
    description="Extract skills from resumes and save to database",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DATABASE_URL = "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

# Load spaCy model
nlp = None

def get_nlp_model():
    """Lazy load spaCy model"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
    return nlp

# Response Models
class SkillsResponse(BaseModel):
    uuid: Optional[str] = None
    skills: List[str]
    message: str
    success: bool

class HealthResponse(BaseModel):
    status: str
    message: str

# Database Functions
def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def save_skills_to_database(uuid: str, skills: List[str]):
    """Save extracted skills to users table"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (uuid,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            # Update existing user's skills (PostgreSQL array format)
            cursor.execute(
                'UPDATE users SET skills = %s WHERE user_id = %s',
                (skills, uuid)
            )
            message = f"Skills updated for user {uuid}"
        else:
            # Insert new user with skills (PostgreSQL array format)
            cursor.execute(
                'INSERT INTO users (user_id, skills) VALUES (%s, %s)',
                (uuid, skills)
            )
            message = f"New user created with skills: {uuid}"
        
        conn.commit()
        cursor.close()
        return message
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")
    
    finally:
        if conn:
            conn.close()

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extract text from resume file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

# Comprehensive skill patterns (600+ skills from chatbot API)
SKILL_PATTERNS = {
    'languages': [
        r'\b(python|java|javascript|typescript|c\+\+|c#|csharp|ruby|php|swift|kotlin|go|golang|rust|scala|perl|r|matlab|julia|dart|lua|haskell|elixir|clojure|f#|groovy|objective-c|visual basic|vb\.net|assembly|fortran|cobol|pascal|lisp|scheme|prolog|erlang|ocaml)\b'
    ],
    'web_frameworks': [
        r'\b(react|reactjs|react\.js|angular|angularjs|vue|vuejs|vue\.js|svelte|next\.js|nextjs|nuxt\.js|nuxtjs|gatsby|ember|backbone|django|flask|fastapi|express|expressjs|node\.js|nodejs|nest\.js|nestjs|spring|spring boot|asp\.net|laravel|symfony|rails|ruby on rails|jquery|bootstrap|tailwind|material-ui|mui|chakra ui)\b'
    ],
    'databases': [
        r'\b(sql|mysql|postgresql|postgres|mongodb|sqlite|oracle|microsoft sql server|mssql|redis|cassandra|dynamodb|couchdb|neo4j|mariadb|elasticsearch|firebase|firestore|realm|influxdb|timescaledb|cockroachdb|fauna|supabase)\b'
    ],
    'cloud_devops': [
        r'\b(aws|amazon web services|azure|microsoft azure|gcp|google cloud|google cloud platform|docker|kubernetes|k8s|jenkins|travis ci|circle ci|gitlab ci|github actions|terraform|ansible|puppet|chef|vagrant|openshift|heroku|netlify|vercel|digitalocean|linode|circleci|teamcity)\b'
    ],
    'ai_ml': [
        r'\b(machine learning|ml|deep learning|neural networks|artificial intelligence|ai|tensorflow|pytorch|keras|scikit-learn|sklearn|pandas|numpy|opencv|nlp|natural language processing|computer vision|data science|matplotlib|seaborn|plotly|jupyter|notebook|xgboost|lightgbm|catboost|hugging face|transformers|bert|gpt|llm|large language models|generative ai|prompt engineering)\b'
    ],
    'mobile': [
        r'\b(android|ios|react native|flutter|xamarin|ionic|cordova|phonegap|swift|swiftui|kotlin|java android|objective-c)\b'
    ],
    'testing': [
        r'\b(jest|mocha|chai|jasmine|pytest|unittest|selenium|cypress|puppeteer|playwright|testng|junit|cucumber|postman|insomnia|jmeter|test automation|unit testing|integration testing|e2e testing|tdd|test driven development)\b'
    ],
    'version_control': [
        r'\b(git|github|gitlab|bitbucket|svn|mercurial|version control|source control)\b'
    ],
    'api': [
        r'\b(rest|restful|rest api|graphql|grpc|soap|api|microservices|websocket|webhooks)\b'
    ],
    'frontend': [
        r'\b(html|html5|css|css3|sass|scss|less|webpack|vite|rollup|parcel|babel|typescript|javascript|responsive design|ui|ux|figma|adobe xd|sketch|zeplin)\b'
    ],
    'backend': [
        r'\b(node|nodejs|express|django|flask|spring|laravel|asp\.net|ruby on rails|php|servlets|jsp|api development|rest api|microservices)\b'
    ],
    'data_tools': [
        r'\b(sql|nosql|data analysis|data visualization|tableau|power bi|excel|google sheets|apache spark|hadoop|kafka|airflow|dbt|etl|data warehouse|data pipeline|big data)\b'
    ],
    'blockchain': [
        r'\b(blockchain|ethereum|solidity|web3|smart contracts|bitcoin|cryptocurrency|nft|defi|hyperledger)\b'
    ],
    'game_dev': [
        r'\b(unity|unreal engine|godot|game development|c\+\+|c#|blender|3d modeling)\b'
    ],
    'security': [
        r'\b(cybersecurity|penetration testing|ethical hacking|owasp|ssl|tls|encryption|oauth|jwt|authentication|authorization|security testing)\b'
    ],
    'methodologies': [
        r'\b(agile|scrum|kanban|waterfall|devops|ci/cd|continuous integration|continuous deployment|tdd|bdd|pair programming)\b'
    ],
    'soft_skills': [
        r'\b(communication|teamwork|leadership|problem solving|critical thinking|time management|project management|collaboration|presentation|documentation)\b'
    ],
    'other_tech': [
        r'\b(linux|unix|windows|macos|bash|shell scripting|powershell|vim|emacs|vscode|intellij|eclipse|pycharm|api|rest|graphql|json|xml|yaml|markdown|regex|data structures|algorithms|oop|object oriented programming|functional programming|design patterns|clean code|solid principles)\b'
    ]
}

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using pattern matching"""
    text_lower = text.lower()
    skills = set()
    
    # Extract using regex patterns
    for category, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            skills.update(matches)
    
    # Clean and normalize skills
    normalized_skills = []
    skill_mapping = {
        'reactjs': 'React',
        'react.js': 'React',
        'nodejs': 'Node.js',
        'node.js': 'Node.js',
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'c++': 'C++',
        'c#': 'C#',
        'csharp': 'C#',
        'golang': 'Go',
        'k8s': 'Kubernetes',
        'ml': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'nlp': 'Natural Language Processing',
        'sklearn': 'Scikit-learn',
        'aws': 'AWS',
        'gcp': 'Google Cloud',
        'sql': 'SQL',
        'nosql': 'NoSQL',
        'postgresql': 'PostgreSQL',
        'mongodb': 'MongoDB',
        'mysql': 'MySQL',
        'mssql': 'Microsoft SQL Server',
        'ci/cd': 'CI/CD',
        'tdd': 'Test Driven Development',
        'oop': 'Object Oriented Programming',
    }
    
    for skill in skills:
        # Normalize skill name
        normalized = skill_mapping.get(skill.lower(), skill.title())
        if normalized not in normalized_skills:
            normalized_skills.append(normalized)
    
    return sorted(normalized_skills)

def extract_skills_from_resume(file_path: str) -> List[str]:
    """Extract skills from resume file"""
    try:
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Could not extract meaningful text from resume")
        
        # Extract skills using pattern matching
        skills = extract_skills_from_text(text)
        
        if not skills:
            # Try using spaCy as fallback
            try:
                nlp_model = get_nlp_model()
                doc = nlp_model(text)
                
                # Extract noun phrases as potential skills
                for chunk in doc.noun_chunks:
                    chunk_text = chunk.text.strip()
                    if len(chunk_text.split()) <= 3:  # Only short phrases
                        skills.append(chunk_text.title())
            except Exception as e:
                print(f"spaCy extraction failed: {e}")
        
        return skills if skills else []
    
    except Exception as e:
        print(f"Resume parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Resume Parser API is running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check with database connectivity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "message": "API and database are operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

@app.post("/parse-resume", response_model=SkillsResponse)
async def parse_resume(
    file: UploadFile = File(...),
    uuid: Optional[str] = Form(None)
):
    """
    Parse resume and extract skills
    
    - **file**: Resume file (PDF, DOCX, DOC, TXT)
    - **uuid**: Optional user UUID to save skills to database
    
    Returns extracted skills and saves to database if uuid provided
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Extract skills from resume
        skills = extract_skills_from_resume(temp_file_path)
        
        if not skills:
            raise HTTPException(
                status_code=400,
                detail="No skills found in resume. Please ensure the resume contains technical skills."
            )
        
        # Save to database if uuid provided
        message = f"Skills extracted successfully: {len(skills)} skills found"
        if uuid:
            db_message = save_skills_to_database(uuid, skills)
            message = f"{message}. {db_message}"
        
        return {
            "uuid": uuid,
            "skills": skills,
            "message": message,
            "success": True
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"Error processing resume: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Failed to delete temp file: {e}")

@app.get("/users/{uuid}/skills")
async def get_user_skills(uuid: str):
    """
    Get skills for a specific user from database
    
    - **uuid**: User UUID to fetch skills for
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            'SELECT user_id, skills FROM users WHERE user_id = %s',
            (uuid,)
        )
        
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {uuid} not found")
        
        # Skills is already an array from PostgreSQL
        skills_list = user['skills'] if user['skills'] else []
        
        return {
            "uuid": user['user_id'],
            "skills": skills_list,
            "message": "Skills retrieved successfully",
            "success": True
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch skills: {str(e)}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
