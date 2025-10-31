# 🏗️ Chatbot API Architecture

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│  "Show me jobs", "My skills are Python", "Career advice"        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CHATBOT API (30MB)                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Intent Classifier (Rule-Based, 1KB)                     │  │
│  │  - Regex pattern matching                                │  │
│  │  - 6 intent types                                        │  │
│  │  - <1ms classification time                              │  │
│  └────────────┬─────────────────────────────────────────────┘  │
│               │                                                 │
│               ↓                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Router (FastAPI)                                        │  │
│  │  - Routes based on intent                                │  │
│  │  - Error handling                                        │  │
│  │  - Response formatting                                   │  │
│  └──┬──────┬──────┬──────┬──────┬─────────────────────────┘  │
│     │      │      │      │      │                             │
└─────┼──────┼──────┼──────┼──────┼─────────────────────────────┘
      │      │      │      │      │
      ↓      ↓      ↓      ↓      ↓      ↓
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │ │ 6  │
   └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
   JOBS   SKILL  UPDATE CAREER HELLO  UNKNOWN
          GAP    SKILLS ADVICE
```

---

## 🎯 Intent Flow Details

### 1️⃣ Job Recommendations Flow

```
User Query: "Show me job recommendations"
     │
     ↓
Intent Classifier → Intent: SHOW_JOBS
     │
     ↓
Services Layer
     │
     ├─→ Call External API
     │   https://apex-backend-zmeq.onrender.com/api/recommend
     │   POST { "user_id": "user123", "top_n": 5 }
     │
     ↓
API Response: { recommendations: [...] }
     │
     ↓
LLM Handler → Generate intro message
     │
     ↓
Return: {
  "intent": "show_jobs",
  "response": "Great news! I found 5 jobs! 🎯",
  "data": { "jobs": [...] }
}
```

### 2️⃣ Skill Gap Analysis Flow

```
User Query: "What skills should I learn?"
     │
     ↓
Intent Classifier → Intent: SHOW_SKILL_GAP
     │
     ↓
Services Layer
     │
     ├─→ Call External API
     │   https://apex-backend-skill-gap.onrender.com/api/skill-gap
     │   POST { "user_id": "user123", "top_n": 5 }
     │
     ↓
API Response: { skill_gaps: [...] }
     │
     ↓
LLM Handler → Generate intro message
     │
     ↓
Return: {
  "intent": "show_skill_gap",
  "response": "I analyzed 5 opportunities! 📈",
  "data": { "skill_gaps": [...] }
}
```

### 3️⃣ Skill Update Flow

```
User Query: "My skills are Python, React, AWS, Docker"
     │
     ↓
Intent Classifier → Intent: UPDATE_SKILLS
     │
     ↓
Skill Extractor (500+ skills database)
     │
     ├─→ Regex pattern matching
     ├─→ Handle variations (js → javascript)
     ├─→ Case insensitive
     │
     ↓
Extracted: ["python", "react", "aws", "docker"]
     │
     ↓
Services Layer
     │
     ├─→ Fetch existing skills from DB
     ├─→ Merge with new skills (deduplicate)
     ├─→ Update Supabase: "aws, docker, python, react"
     │
     ↓
LLM Handler → Generate confirmation
     │
     ↓
Return: {
  "intent": "update_skills",
  "response": "Updated with 4 skills! ✅",
  "extracted_skills": ["python", "react", "aws", "docker"]
}
```

### 4️⃣ Career Advice Flow

```
User Query: "Give me career advice on skill development"
     │
     ↓
Intent Classifier → Intent: CAREER_ADVICE
     │
     ↓
LLM Handler
     │
     ├─→ Analyze query keywords
     ├─→ Determine advice category: "skill_development"
     ├─→ Select from curated templates
     │
     ↓
Generate Response: Professional career guidance
     │
     ↓
Services Layer
     │
     ├─→ Check if user exists in DB
     ├─→ Add personalized recommendation
     │
     ↓
Return: {
  "intent": "career_advice",
  "response": "[Professional advice]...",
  "data": { "user_exists": true }
}
```

### 5️⃣ Greeting Flow

```
User Query: "Hello!" / "Hi" / "Thanks"
     │
     ↓
Intent Classifier → Intent: GREETING
     │
     ↓
LLM Handler
     │
     ├─→ Select random greeting
     ├─→ Explain features
     │
     ↓
Return: {
  "intent": "greeting",
  "response": "Hi! I'm your career assistant. How can I help?"
}
```

### 6️⃣ Unknown Flow

```
User Query: "What's the weather?"
     │
     ↓
Intent Classifier → Intent: UNKNOWN
     │
     ↓
LLM Handler
     │
     ├─→ Select random unknown response
     ├─→ List available features
     │
     ↓
Return: {
  "intent": "unknown",
  "response": "I can help with: jobs, skills, advice..."
}
```

---

## 🗄️ Database Integration

```
┌─────────────────────────────────────────┐
│         Supabase PostgreSQL             │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  users table                      │  │
│  │  ────────────────────────────     │  │
│  │  user_id (TEXT PRIMARY KEY)       │  │
│  │  skills (TEXT)                    │  │
│  │  created_at (TIMESTAMP)           │  │
│  │  updated_at (TIMESTAMP)           │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  "Job Roles" table                │  │
│  │  ────────────────────────────     │  │
│  │  id (UUID PRIMARY KEY)            │  │
│  │  "Job Role" (TEXT)                │  │
│  │  "Required Skills" (TEXT)         │  │
│  │  embedding (BYTEA)                │  │
│  │  ... other columns ...            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         ↑                    ↑
         │                    │
    ┌────┴────────────────────┴────┐
    │  Services Layer              │
    │  - get_user_skills()         │
    │  - update_user_skills()      │
    │  - check_user_exists()       │
    │  - get_database_stats()      │
    └──────────────────────────────┘
```

---

## 🔌 External API Integration

```
┌──────────────────────────────────────────────────────────┐
│  Chatbot API (Your API)                                  │
└────────────┬──────────────────┬──────────────────────────┘
             │                  │
             ↓                  ↓
┌────────────────────┐  ┌────────────────────┐
│  Job Rec API       │  │  Skill Gap API     │
│  (Render)          │  │  (Render)          │
│                    │  │                    │
│  POST /api/        │  │  POST /api/        │
│    recommend       │  │    skill-gap       │
│                    │  │                    │
│  Input:            │  │  Input:            │
│  - user_id         │  │  - user_id         │
│  - top_n           │  │  - top_n           │
│                    │  │                    │
│  Output:           │  │  Output:           │
│  - recommendations │  │  - skill_gaps      │
│  - user_skills     │  │  - user_skills     │
│  - total_jobs      │  │  - total_analysis  │
└────────────────────┘  └────────────────────┘
```

---

## 🧠 Intent Classification Logic

```
User Query
     │
     ↓
┌────────────────────────────────────────────┐
│  Intent Classifier (Rule-Based)           │
│                                            │
│  Priority Order:                           │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Greeting (most common)            │  │
│  │    Keywords: "hi", "hello", "thanks" │  │
│  └──────────────────────────────────────┘  │
│               ↓ No match                   │
│  ┌──────────────────────────────────────┐  │
│  │ 2. Update Skills (most specific)     │  │
│  │    Keywords: "my skills are", "i     │  │
│  │    know", "i am skilled in"          │  │
│  └──────────────────────────────────────┘  │
│               ↓ No match                   │
│  ┌──────────────────────────────────────┐  │
│  │ 3. Show Jobs                         │  │
│  │    Keywords: "find jobs", "show me   │  │
│  │    jobs", "job recommendations"      │  │
│  └──────────────────────────────────────┘  │
│               ↓ No match                   │
│  ┌──────────────────────────────────────┐  │
│  │ 4. Skill Gap                         │  │
│  │    Keywords: "skill gap", "skills to │  │
│  │    learn", "what am i missing"       │  │
│  └──────────────────────────────────────┘  │
│               ↓ No match                   │
│  ┌──────────────────────────────────────┐  │
│  │ 5. Career Advice                     │  │
│  │    Keywords: "career advice", "what  │  │
│  │    should i do", "career path"       │  │
│  └──────────────────────────────────────┘  │
│               ↓ No match                   │
│  ┌──────────────────────────────────────┐  │
│  │ 6. Unknown (fallback)                │  │
│  │    Action: Help user understand      │  │
│  │    available features                │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

---

## 🔍 Skill Extraction Logic

```
User Input: "My skills are Python, JavaScript, React, and AWS"
     │
     ↓
┌──────────────────────────────────────────────────────┐
│  Skill Extractor (Regex-Based)                      │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Step 1: Tokenization                         │  │
│  │  Split on: , ; \n \t ( ) [ ] { }              │  │
│  │  Result: ["My", "skills", "are", "Python",    │  │
│  │           "JavaScript", "React", "and", "AWS"] │  │
│  └────────────────────────────────────────────────┘  │
│                     ↓                                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Step 2: Match Against Database (500+ skills) │  │
│  │  - programming_languages: python ✓             │  │
│  │  - web_technologies: javascript ✓, react ✓    │  │
│  │  - cloud_devops: aws ✓                         │  │
│  └────────────────────────────────────────────────┘  │
│                     ↓                                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Step 3: Handle Variations                    │  │
│  │  - "js" → "javascript"                         │  │
│  │  - "k8s" → "kubernetes"                        │  │
│  │  - "node.js" or "nodejs" → "node.js"           │  │
│  └────────────────────────────────────────────────┘  │
│                     ↓                                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Step 4: Special Cases                        │  │
│  │  - "C++" (with symbols)                        │  │
│  │  - "C#" (with symbols)                         │  │
│  │  - Multi-word: "machine learning"              │  │
│  └────────────────────────────────────────────────┘  │
│                     ↓                                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Step 5: Deduplicate & Sort                   │  │
│  │  Result: ["aws", "javascript", "python",       │  │
│  │           "react"]                             │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 💾 Memory Layout

```
┌──────────────────────────────────────────┐
│  TOTAL MEMORY: 30MB / 512MB (6%)        │
├──────────────────────────────────────────┤
│                                          │
│  FastAPI Framework         15MB  ████   │
│  Python Runtime            10MB  ███    │
│  psycopg2 (DB driver)       3MB  █      │
│  Requests (HTTP)            1MB  █      │
│  Skill Database          500KB  █       │
│  Intent Patterns           1KB  █       │
│  Response Templates       50KB  █       │
│                                          │
│  Free Memory:            482MB  ████████│
│                                 ████████│
│                                 ████████│
│                                 ████████│
│                                          │
└──────────────────────────────────────────┘

Compare to Transformer Approach:
┌──────────────────────────────────────────┐
│  TOTAL MEMORY: 550MB / 512MB (107%) ❌  │
├──────────────────────────────────────────┤
│  DialoGPT-small         245MB  ████████  │
│  BERT Classifier        220MB  ████████  │
│  SpaCy NER               50MB  ██        │
│  FastAPI                 15MB  █         │
│  Python Runtime          10MB  █         │
│  Other                   10MB  █         │
│                                           │
│  EXCEEDS LIMIT BY 38MB! ❌               │
└──────────────────────────────────────────┘
```

---

## ⚡ Response Time Breakdown

```
User Request → Chatbot API → Response
    ↓              ↓             ↑
    │              │             │
    │              ↓             │
    │     Intent Classification │
    │           <1ms            │
    │              ↓             │
    │     ┌────────────────┐    │
    │     │ Intent Router  │    │
    │     └────────────────┘    │
    │              ↓             │
    │     ┌────────────────────────────┐
    │     │                            │
    │     ↓                            │
    │  show_jobs                       │
    │     │                            │
    │     ↓                            │
    │  External API Call               │
    │     200-500ms                    │
    │     (or 10-30s if sleeping)      │
    │     │                            │
    │     ↓                            │
    │  Process Response                │
    │     10-20ms                      │
    │     │                            │
    │     ↓                            │
    │  Generate Message                │
    │     1-5ms                        │
    │     │                            │
    └─────┴────────────────────────────┘
         Total: 300-600ms ✅
```

---

## 🔒 Security Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (Vercel)              │
└────────────┬────────────────────────────────┘
             │ HTTPS
             ↓
┌─────────────────────────────────────────────┐
│          Chatbot API (Render)               │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  CORS Middleware                   │    │
│  │  - Validates origin                │    │
│  │  - Allows credentials              │    │
│  └────────────────────────────────────┘    │
│                ↓                            │
│  ┌────────────────────────────────────┐    │
│  │  Pydantic Validation               │    │
│  │  - Type checking                   │    │
│  │  - Required fields                 │    │
│  │  - Value constraints               │    │
│  └────────────────────────────────────┘    │
│                ↓                            │
│  ┌────────────────────────────────────┐    │
│  │  Business Logic                    │    │
│  │  - Intent classification           │    │
│  │  - Skill extraction                │    │
│  │  - Response generation             │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
             │
             ↓ Environment Variables
┌─────────────────────────────────────────────┐
│       Supabase PostgreSQL (SSL)             │
│  - Parameterized queries (SQL injection)    │
│  - Connection pooling                       │
│  - SSL encryption                           │
└─────────────────────────────────────────────┘
```

---

## 📈 Scalability

```
Single Instance (512MB Render):
┌──────────────────────────────────────┐
│  Chatbot API (30MB base)             │
│                                      │
│  Max Concurrent Requests: ~50        │
│  Memory per request: 5-10MB          │
│  Request timeout: 30s                │
│                                      │
│  Bottleneck: External API calls      │
│  Solution: Cache frequently used     │
│            responses                 │
└──────────────────────────────────────┘

Multiple Instances (Load Balanced):
┌──────────────────────────────────────┐
│  Load Balancer                       │
└────┬────────────┬────────────┬───────┘
     │            │            │
     ↓            ↓            ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│ API #1  │  │ API #2  │  │ API #3  │
│  30MB   │  │  30MB   │  │  30MB   │
└─────────┘  └─────────┘  └─────────┘
     │            │            │
     └────────────┴────────────┘
                  │
                  ↓
        Shared Database
```

---

## 🎯 Key Advantages

### 1. Memory Efficiency
```
30MB vs 550MB = 95% reduction ✅
```

### 2. Startup Speed
```
2-3 seconds vs 10-30 seconds ✅
```

### 3. Response Time
```
300-600ms average ✅
```

### 4. Predictability
```
Rule-based = 100% reproducible ✅
```

### 5. Cost
```
$0-7/month vs $25+/month ✅
```

### 6. Maintainability
```
Easy to debug & extend ✅
```

---

**Architecture**: ✅ Optimized  
**Memory**: ✅ Efficient (6% usage)  
**Performance**: ✅ Fast (<1s)  
**Cost**: ✅ Minimal ($0-7/month)  
**Status**: ✅ Production Ready
