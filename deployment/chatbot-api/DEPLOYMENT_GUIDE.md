# Chatbot API - Deployment Guide

## 🚀 Deploy to Render

### Step 1: Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Select this directory: `deployment/chatbot-api`

### Step 2: Configure Service

**Build & Deploy Settings:**
- **Name:** `chatbot-api` (or your choice)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Instance Type:** Choose based on needs (Minimum 1GB RAM recommended)

**Important:** This API needs at least **1GB RAM** due to the AI models (BART, BERT-NER, FLAN-T5).

### Step 3: Environment Variables

Add these environment variables in Render:

```
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres

FRONTEND_URL=https://your-frontend-domain.vercel.app

JOB_RECOMMENDATION_API=https://job-recommendation-api.onrender.com/api/recommend

SKILL_GAP_API=https://skill-gap-api.onrender.com/api/skill-gap

PORT=10000
```

**Important:** Deploy the Job Recommendation API and Skill Gap API first, then use their URLs here.

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (first time takes 5-15 minutes - downloads 3 models)
3. Watch logs for: `✅ All models loaded successfully!`

---

## 📡 API Endpoints

Once deployed, your API will be available at: `https://chatbot-api.onrender.com`

### Root Endpoint
```
GET https://chatbot-api.onrender.com/
```

### Health Check
```
GET https://chatbot-api.onrender.com/health
```

### Chat with AI
```
POST https://chatbot-api.onrender.com/api/chat

Request Body:
{
  "user_id": "user123",
  "query": "Show me job recommendations"
}

Response:
{
  "success": true,
  "user_id": "user123",
  "query": "Show me job recommendations",
  "intent": "show_jobs",
  "response": "🎯 I found 10 job recommendations for you...",
  "extracted_skills": null,
  "job_recommendations": [
    {
      "job_id": "uuid",
      "similarity_score": 0.85
    }
  ],
  "skill_gap_analysis": null
}
```

---

## 🔧 How Frontend Should Call This API

### React/Next.js Example

```javascript
// Create a service file: services/chatbot.js

const CHATBOT_API_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 
                        'https://chatbot-api.onrender.com';

export const sendChatMessage = async (userId, query) => {
  try {
    const response = await fetch(`${CHATBOT_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        query: query
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to send chat message:', error);
    throw error;
  }
};

// Usage in component:
import { useState } from 'react';
import { sendChatMessage } from '../services/chatbot';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage('user123', input);
      
      const botMessage = {
        role: 'assistant',
        content: response.response,
        intent: response.intent,
        data: {
          job_recommendations: response.job_recommendations,
          skill_gap_analysis: response.skill_gap_analysis,
          extracted_skills: response.extracted_skills
        }
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            
            {/* Show job recommendations if available */}
            {msg.data?.job_recommendations && (
              <div className="job-recommendations">
                <h4>Job Recommendations:</h4>
                <ul>
                  {msg.data.job_recommendations.map(job => (
                    <li key={job.job_id}>
                      Job ID: {job.job_id} | 
                      Match: {(job.similarity_score * 100).toFixed(1)}%
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Show skill gap analysis if available */}
            {msg.data?.skill_gap_analysis && (
              <div className="skill-gap">
                <h4>Skill Gap Analysis:</h4>
                {/* Render skill gap data */}
              </div>
            )}
          </div>
        ))}

        {loading && <div className="loading">Thinking...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything about jobs and careers..."
        />
        <button onClick={handleSend} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
```

### All 6 Intents Examples

```javascript
// 1. Show Jobs
await sendChatMessage('user123', 'Show me job recommendations');

// 2. Skill Gap
await sendChatMessage('user123', 'What skills do I need for high paying jobs?');

// 3. Salary Info
await sendChatMessage('user123', "What's the average salary I can get?");

// 4. Add Skills
await sendChatMessage('user123', 'I want to add Python and React to my skills');

// 5. Career Advice
await sendChatMessage('user123', 'Should I learn machine learning?');

// 6. General Query
await sendChatMessage('user123', 'Hello, how are you?');
```

### TypeScript Interface

```typescript
interface ChatRequest {
  user_id: string;
  query: string;
}

interface ChatResponse {
  success: boolean;
  user_id: string;
  query: string;
  intent: string;
  response: string;
  extracted_skills: string[] | null;
  job_recommendations: Array<{
    job_id: string;
    similarity_score: number;
  }> | null;
  skill_gap_analysis: {
    success: boolean;
    user_skills: string[];
    top_opportunities: Array<{
      job_id: string;
      job_role: string;
      company: string;
      avg_salary: number;
      missing_skills: string[];
      matching_skills: string[];
    }>;
  } | null;
}
```

---

## 🔒 CORS Configuration

The API is configured to accept requests from:
- Your Vercel frontend (set via `FRONTEND_URL`)
- Local development (`localhost:3000`, `localhost:5173`)
- All Vercel preview deployments

**For Production:** Update the CORS settings in `main.py` to only allow your specific frontend domain.

---

## 📊 Resource Requirements

- **Minimum RAM:** 1GB (1.5GB recommended)
- **Disk Space:** ~2.5GB (for 3 AI models)
- **Startup Time:** 60-90 seconds (model loading)
- **Request Time:** 2-5 seconds per chat message

**Models Used:**
- facebook/bart-large-mnli (~400MB) - Intent classification
- dslim/bert-base-NER (~110MB) - Skill extraction
- google/flan-t5-small (~77MB) - Response generation

---

## 🐛 Troubleshooting

### "Models not loading" error
- Wait 2-3 minutes after deployment
- Check logs for model download progress
- Ensure instance has at least 1GB RAM
- Models download from HuggingFace (requires internet)

### "API timeout" errors
- First request after cold start is slow (model loading)
- Implement loading state in frontend
- Consider keep-alive pings

### Other APIs not responding
- Verify `JOB_RECOMMENDATION_API` and `SKILL_GAP_API` URLs
- Ensure those APIs are deployed and running
- Check if those APIs allow requests from Render IPs

---

## 🔄 Updating the API

1. Push changes to your GitHub repository
2. Render auto-deploys from main branch
3. Monitor deployment logs
4. Test with health check endpoint

---

## 📝 Environment Variables for Frontend

Add to your `.env.local` (Vercel):

```env
NEXT_PUBLIC_CHATBOT_API_URL=https://chatbot-api.onrender.com
NEXT_PUBLIC_JOB_API_URL=https://job-recommendation-api.onrender.com
NEXT_PUBLIC_SKILL_GAP_API_URL=https://skill-gap-api.onrender.com
```

---

## 🎯 Communication Flow

```
Frontend (Vercel)
      ↓
Chatbot API (Render)
      ↓
  ┌───┴───┐
  ↓       ↓
Job API   Skill Gap API
(Render)  (Render)
  ↓       ↓
  └───┬───┘
      ↓
  PostgreSQL
  (Supabase)
```

---

## ✅ Deployment Checklist

- [ ] Job Recommendation API deployed first
- [ ] Skill Gap API deployed second
- [ ] Repository connected to Render
- [ ] Environment variables configured (all 5)
- [ ] Database URL is correct
- [ ] Frontend URL is set
- [ ] Other API URLs are correct
- [ ] Build command is correct
- [ ] Start command is correct
- [ ] Health check returns 200
- [ ] Test all 6 intents from Postman
- [ ] Test from frontend
- [ ] Monitor logs for errors

---

## 🚀 Deployment Order (IMPORTANT!)

1. **First:** Deploy Job Recommendation API
2. **Second:** Deploy Skill Gap API
3. **Third:** Deploy Chatbot API (this one) - use URLs from steps 1 & 2

---

## 📞 Support

If you encounter issues:
1. Check Render logs for all 3 services
2. Verify environment variables (especially API URLs)
3. Test database connection
4. Check CORS settings
5. Verify other APIs are responsive

Your API URL will be: `https://your-service-name.onrender.com`
