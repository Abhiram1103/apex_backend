# 🚀 Complete Deployment Guide - All 3 APIs to Render + Frontend to Vercel

## 📋 Overview

This guide will help you deploy:
- **3 Backend APIs** to Render.com
- **1 React Frontend** to Vercel.com

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           Frontend (Vercel)                         │
│  https://your-app.vercel.app                        │
└────────────┬────────────────────────────────────────┘
             │
             ├──────────────────────────┬──────────────────────┐
             ↓                          ↓                      ↓
┌────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  Job Recommendation    │  │   Skill Gap API      │  │    Chatbot API       │
│  API (Render)          │  │   (Render)           │  │    (Render)          │
│  Port 10000            │  │   Port 10000         │  │    Port 10000        │
└────────┬───────────────┘  └──────────┬───────────┘  └────────┬─────────────┘
         │                             │                        │
         └─────────────────────────────┼────────────────────────┘
                                       ↓
                          ┌────────────────────────┐
                          │  PostgreSQL Database   │
                          │  (Supabase)            │
                          └────────────────────────┘
```

---

## 📦 What's in the Deployment Folder

```
deployment/
├── job-recommendation-api/
│   ├── main.py
│   ├── requirements.txt
│   └── DEPLOYMENT_GUIDE.md
├── skill-gap-api/
│   ├── main.py
│   ├── requirements.txt
│   └── DEPLOYMENT_GUIDE.md
└── chatbot-api/
    ├── main.py
    ├── requirements.txt
    └── DEPLOYMENT_GUIDE.md
```

---

## 🎯 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add deployment configurations"
git push origin main
```

2. **Verify structure:**
```
your-repo/
├── deployment/
│   ├── job-recommendation-api/
│   ├── skill-gap-api/
│   └── chatbot-api/
└── frontend/ (your React app)
```

---

### Step 2: Deploy APIs to Render (IN ORDER!)

#### 🥇 2.1 Deploy Job Recommendation API (First)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. **Root Directory:** `deployment/job-recommendation-api`
5. **Name:** `job-recommendation-api`
6. **Environment:** Python 3
7. **Build Command:** `pip install -r requirements.txt`
8. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
9. **Instance Type:** Starter (512MB RAM minimum)

**Environment Variables:**
```
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
FRONTEND_URL=https://your-frontend.vercel.app
```

10. Click **"Create Web Service"**
11. Wait for deployment (~5-10 minutes)
12. **Copy the URL:** `https://job-recommendation-api-xxxx.onrender.com`
13. **Test:** Visit `https://job-recommendation-api-xxxx.onrender.com/health`

---

#### 🥈 2.2 Deploy Skill Gap API (Second)

Repeat steps 1-4 from above, then:

5. **Name:** `skill-gap-api`
6. **Root Directory:** `deployment/skill-gap-api`
7. Same build/start commands

**Environment Variables:**
```
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
FRONTEND_URL=https://your-frontend.vercel.app
```

12. **Copy the URL:** `https://skill-gap-api-xxxx.onrender.com`
13. **Test:** Visit `https://skill-gap-api-xxxx.onrender.com/health`

---

#### 🥉 2.3 Deploy Chatbot API (Third - REQUIRES URLs from Step 2.1 & 2.2)

Repeat steps 1-4 from above, then:

5. **Name:** `chatbot-api`
6. **Root Directory:** `deployment/chatbot-api`
7. Same build/start commands
8. **Instance Type:** Professional (1GB RAM minimum - this one needs more memory!)

**Environment Variables:**
```
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres

FRONTEND_URL=https://your-frontend.vercel.app

JOB_RECOMMENDATION_API=https://job-recommendation-api-xxxx.onrender.com/api/recommend

SKILL_GAP_API=https://skill-gap-api-xxxx.onrender.com/api/skill-gap
```

**⚠️ Important:** Replace `xxxx` with the actual URLs from steps 2.1 and 2.2!

12. **Copy the URL:** `https://chatbot-api-xxxx.onrender.com`
13. **Test:** Visit `https://chatbot-api-xxxx.onrender.com/health`

---

### Step 3: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Import your GitHub repository
4. **Framework Preset:** Next.js (or your framework)
5. **Root Directory:** `frontend` (if applicable)
6. **Build Command:** `npm run build` or `yarn build`
7. **Output Directory:** `.next` or `build`

**Environment Variables (Vercel):**
```
NEXT_PUBLIC_JOB_API_URL=https://job-recommendation-api-xxxx.onrender.com
NEXT_PUBLIC_SKILL_GAP_API_URL=https://skill-gap-api-xxxx.onrender.com
NEXT_PUBLIC_CHATBOT_API_URL=https://chatbot-api-xxxx.onrender.com
```

**⚠️ Important:** Replace `xxxx` with your actual Render URLs!

8. Click **"Deploy"**
9. Wait for deployment (~2-5 minutes)
10. **Copy your frontend URL:** `https://your-app.vercel.app`

---

### Step 4: Update CORS Settings

Now that you have your frontend URL, go back to each Render service and update:

1. **Job Recommendation API** → Settings → Environment Variables
   - Update `FRONTEND_URL` to your actual Vercel URL
   
2. **Skill Gap API** → Settings → Environment Variables
   - Update `FRONTEND_URL` to your actual Vercel URL
   
3. **Chatbot API** → Settings → Environment Variables
   - Update `FRONTEND_URL` to your actual Vercel URL

After updating, manually trigger a new deployment for each service.

---

## 🧪 Testing Your Deployment

### Test APIs

**1. Test Job Recommendation API:**
```bash
curl -X POST https://job-recommendation-api-xxxx.onrender.com/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123", "top_n": 5}'
```

**2. Test Skill Gap API:**
```bash
curl -X POST https://skill-gap-api-xxxx.onrender.com/api/skill-gap \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123", "top_n": 5}'
```

**3. Test Chatbot API:**
```bash
curl -X POST https://chatbot-api-xxxx.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123", "query": "Show me job recommendations"}'
```

### Test from Frontend

Add this to your React component:

```javascript
// Test connection to all APIs
const testAPIs = async () => {
  const jobApiUrl = process.env.NEXT_PUBLIC_JOB_API_URL;
  const skillGapApiUrl = process.env.NEXT_PUBLIC_SKILL_GAP_API_URL;
  const chatbotApiUrl = process.env.NEXT_PUBLIC_CHATBOT_API_URL;

  console.log('Testing APIs...');

  // Test Job API
  try {
    const res = await fetch(`${jobApiUrl}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'test', top_n: 5 })
    });
    console.log('Job API:', res.status === 200 ? '✅ OK' : '❌ Failed');
  } catch (e) {
    console.error('Job API Error:', e);
  }

  // Test Skill Gap API
  try {
    const res = await fetch(`${skillGapApiUrl}/api/skill-gap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'test', top_n: 5 })
    });
    console.log('Skill Gap API:', res.status === 200 ? '✅ OK' : '❌ Failed');
  } catch (e) {
    console.error('Skill Gap API Error:', e);
  }

  // Test Chatbot API
  try {
    const res = await fetch(`${chatbotApiUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'test', query: 'hello' })
    });
    console.log('Chatbot API:', res.status === 200 ? '✅ OK' : '❌ Failed');
  } catch (e) {
    console.error('Chatbot API Error:', e);
  }
};
```

---

## 📊 API Communication in Frontend

### Complete Service Files

Create these in your frontend:

**`services/api.js`**
```javascript
const API_URLS = {
  job: process.env.NEXT_PUBLIC_JOB_API_URL,
  skillGap: process.env.NEXT_PUBLIC_SKILL_GAP_API_URL,
  chatbot: process.env.NEXT_PUBLIC_CHATBOT_API_URL
};

export const jobAPI = {
  getRecommendations: async (userId, topN = 10) => {
    const res = await fetch(`${API_URLS.job}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, top_n: topN })
    });
    return res.json();
  }
};

export const skillGapAPI = {
  getAnalysis: async (userId, topN = 10) => {
    const res = await fetch(`${API_URLS.skillGap}/api/skill-gap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, top_n: topN })
    });
    return res.json();
  }
};

export const chatbotAPI = {
  sendMessage: async (userId, query) => {
    const res = await fetch(`${API_URLS.chatbot}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, query })
    });
    return res.json();
  }
};
```

**Usage:**
```javascript
import { jobAPI, skillGapAPI, chatbotAPI } from '../services/api';

// Get job recommendations
const jobs = await jobAPI.getRecommendations('user123', 10);

// Get skill gap analysis
const analysis = await skillGapAPI.getAnalysis('user123', 10);

// Chat with bot
const response = await chatbotAPI.sendMessage('user123', 'Show me jobs');
```

---

## 🔒 Security Best Practices

### For Production (Update CORS):

In each API's `main.py`, update CORS settings:

```python
# Replace this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Allows all origins
    ...
)

# With this:
FRONTEND_URL = os.getenv("FRONTEND_URL")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # ✅ Only your frontend
    ...
)
```

Then redeploy all 3 APIs.

---

## 💰 Cost Estimate

### Render (3 APIs)

- **Job API:** $7/month (Starter - 512MB)
- **Skill Gap API:** $7/month (Starter - 512MB)
- **Chatbot API:** $25/month (Professional - 1GB, needs more RAM)
- **Total:** ~$39/month

**Free Tier Option:**
- Render offers free tier but spins down after inactivity
- First request after spin-down is very slow (30s+)
- Not recommended for production

### Vercel (Frontend)

- **Hobby Plan:** FREE (perfect for most projects)
- **Pro Plan:** $20/month (if you need more)

---

## 🐛 Common Issues & Fixes

### Issue: "Model not loaded" error
**Fix:** Wait 2-3 minutes after deployment. Models download on first startup.

### Issue: "Database connection failed"
**Fix:** Verify DATABASE_URL is correct in all 3 APIs.

### Issue: CORS errors in frontend
**Fix:** 
1. Check FRONTEND_URL is set correctly in APIs
2. Verify you're using the correct API URLs in frontend
3. Check browser console for specific CORS error

### Issue: Chatbot API calls fail
**Fix:** 
1. Verify JOB_RECOMMENDATION_API and SKILL_GAP_API URLs are correct
2. Ensure those two APIs are deployed and running
3. Test those APIs directly first

### Issue: Slow responses
**Fix:**
1. Render free tier spins down - consider paid tier
2. Implement loading states in frontend
3. Add caching if needed

---

## ✅ Final Checklist

### Render Deployment
- [ ] Job Recommendation API deployed and healthy
- [ ] Skill Gap API deployed and healthy
- [ ] Chatbot API deployed and healthy
- [ ] All environment variables set correctly
- [ ] All APIs returning 200 on /health endpoint
- [ ] Database connection working for all APIs

### Vercel Deployment
- [ ] Frontend deployed successfully
- [ ] All environment variables set (3 API URLs)
- [ ] No build errors
- [ ] No runtime errors in browser console

### Testing
- [ ] Test Job API from Postman
- [ ] Test Skill Gap API from Postman
- [ ] Test Chatbot API from Postman
- [ ] Test all APIs from frontend
- [ ] Verify CORS works (no errors in console)
- [ ] Test all 6 chatbot intents
- [ ] Verify database updates (add skills)

### Production Ready
- [ ] Update CORS to specific frontend URL
- [ ] Monitor Render logs for errors
- [ ] Test on different devices/browsers
- [ ] Set up error tracking (optional: Sentry)
- [ ] Set up uptime monitoring (optional: UptimeRobot)

---

## 📞 Support & Resources

### Documentation
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Monitoring
- Render Dashboard: Check logs and metrics
- Vercel Analytics: Check frontend performance
- Browser DevTools: Check network requests

---

## 🎉 You're Done!

Your complete career recommendation system is now live:

🌐 **Frontend:** `https://your-app.vercel.app`

🔧 **APIs:**
- Job Recommendations: `https://job-recommendation-api-xxxx.onrender.com`
- Skill Gap Analysis: `https://skill-gap-api-xxxx.onrender.com`
- AI Chatbot: `https://chatbot-api-xxxx.onrender.com`

---

## 📝 Quick Reference

### API Endpoints Summary

| API | Endpoint | Method | Purpose |
|-----|----------|--------|---------|
| Job Rec | `/api/recommend` | POST | Get job recommendations |
| Skill Gap | `/api/skill-gap` | POST | Get skill gap analysis |
| Chatbot | `/api/chat` | POST | Chat with AI assistant |

### Environment Variables Summary

**Render (All 3 APIs):**
- `DATABASE_URL` - PostgreSQL connection string
- `FRONTEND_URL` - Your Vercel frontend URL

**Render (Chatbot API Only):**
- `JOB_RECOMMENDATION_API` - Job API URL
- `SKILL_GAP_API` - Skill Gap API URL

**Vercel (Frontend):**
- `NEXT_PUBLIC_JOB_API_URL` - Job API URL
- `NEXT_PUBLIC_SKILL_GAP_API_URL` - Skill Gap API URL
- `NEXT_PUBLIC_CHATBOT_API_URL` - Chatbot API URL

---

**Last Updated:** October 30, 2025
**Version:** 1.0.0
