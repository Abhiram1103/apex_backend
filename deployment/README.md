# 🚀 Deployment Package - Career Recommendation System

## 📦 What's Included

This deployment package contains everything you need to deploy your complete career recommendation system:

### Backend APIs (3 Services for Render)
1. **Job Recommendation API** - SBERT-based job matching
2. **Skill Gap Analysis API** - ROI calculation with salary insights
3. **AI Chatbot API** - Intelligent conversational interface

### Documentation
- **MASTER_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
- **FRONTEND_INTEGRATION_GUIDE.md** - React/Next.js integration examples
- Individual deployment guides for each API

---

## 🎯 Quick Start

### 1. Deploy Backend APIs to Render

Follow this order:

```
1️⃣ Job Recommendation API → Get URL
2️⃣ Skill Gap API → Get URL  
3️⃣ Chatbot API → Use URLs from 1️⃣ & 2️⃣
```

**Read:** `MASTER_DEPLOYMENT_GUIDE.md` for detailed instructions

### 2. Deploy Frontend to Vercel

- Set environment variables with your 3 API URLs
- Deploy your React/Next.js app

**Read:** `FRONTEND_INTEGRATION_GUIDE.md` for code examples

---

## 📁 Directory Structure

```
deployment/
├── README.md (this file)
├── MASTER_DEPLOYMENT_GUIDE.md
├── FRONTEND_INTEGRATION_GUIDE.md
│
├── job-recommendation-api/
│   ├── main.py
│   ├── requirements.txt
│   └── DEPLOYMENT_GUIDE.md
│
├── skill-gap-api/
│   ├── main.py
│   ├── requirements.txt
│   └── DEPLOYMENT_GUIDE.md
│
└── chatbot-api/
    ├── main.py
    ├── requirements.txt
    └── DEPLOYMENT_GUIDE.md
```

---

## 🔑 Environment Variables Needed

### For Each API on Render:
```env
DATABASE_URL=postgresql://...
FRONTEND_URL=https://your-frontend.vercel.app
```

### Additional for Chatbot API:
```env
JOB_RECOMMENDATION_API=https://job-api.onrender.com/api/recommend
SKILL_GAP_API=https://skill-gap-api.onrender.com/api/skill-gap
```

### For Frontend on Vercel:
```env
NEXT_PUBLIC_JOB_API_URL=https://job-api.onrender.com
NEXT_PUBLIC_SKILL_GAP_API_URL=https://skill-gap-api.onrender.com
NEXT_PUBLIC_CHATBOT_API_URL=https://chatbot-api.onrender.com
```

---

## 📊 API Endpoints Summary

### Job Recommendation API
- `POST /api/recommend` - Get job recommendations
- `GET /health` - Health check

**Input:** `{ "user_id": "string", "top_n": 10 }`
**Output:** `{ "recommendations": [{job_id, similarity_score}] }`

### Skill Gap API
- `POST /api/skill-gap` - Analyze skill gaps
- `GET /health` - Health check

**Input:** `{ "user_id": "string", "top_n": 10 }`
**Output:** `{ "top_opportunities": [...], "user_skills": [...] }`

### Chatbot API
- `POST /api/chat` - Chat with AI
- `GET /health` - Health check

**Input:** `{ "user_id": "string", "query": "string" }`
**Output:** `{ "intent": "...", "response": "...", ... }`

---

## 🎨 Frontend Integration

### Quick Example:

```javascript
// Job Recommendations
const jobs = await fetch('https://job-api.onrender.com/api/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user123', top_n: 10 })
});

// Skill Gap Analysis
const gaps = await fetch('https://skill-gap-api.onrender.com/api/skill-gap', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user123', top_n: 10 })
});

// Chatbot
const chat = await fetch('https://chatbot-api.onrender.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user123', query: 'Show me jobs' })
});
```

**See `FRONTEND_INTEGRATION_GUIDE.md` for complete React components!**

---

## ⚡ Key Features

### Job Recommendation API
- ✅ SBERT embeddings (all-MiniLM-L6-v2)
- ✅ Cosine similarity matching
- ✅ User skill-based recommendations
- ✅ Cached job embeddings for fast responses

### Skill Gap API
- ✅ ROI-based job ranking
- ✅ Salary normalization (Min-Max)
- ✅ Combined scoring (70% skill match + 30% salary)
- ✅ Missing skills identification

### Chatbot API
- ✅ 6 intent types (show jobs, skill gap, salary info, add skills, career advice, general)
- ✅ NER-based skill extraction
- ✅ Calls other APIs dynamically
- ✅ AI-generated responses (FLAN-T5)
- ✅ Auto-updates user skills in database

---

## 🔒 Security & CORS

All APIs are configured to:
- ✅ Accept requests from your Vercel frontend
- ✅ Support local development (localhost:3000, localhost:5173)
- ✅ Allow all Vercel preview deployments

**For production:** Update CORS to only allow your specific domain.

---

## 💰 Cost Estimate

### Render (Monthly)
- Job API: $7 (Starter - 512MB)
- Skill Gap API: $7 (Starter - 512MB)
- Chatbot API: $25 (Professional - 1GB)
- **Total: ~$39/month**

### Vercel
- Hobby: **FREE** (perfect for most projects)

### Database
- Supabase: FREE tier includes your database

---

## 📊 Resource Requirements

| API | RAM | Disk | Startup Time | Response Time |
|-----|-----|------|--------------|---------------|
| Job Recommendation | 512MB | 2GB | 30-60s | 100-500ms |
| Skill Gap | 512MB | 2GB | 30-60s | 200-700ms |
| Chatbot | 1GB | 2.5GB | 60-90s | 2-5s |

---

## 🐛 Common Issues

### Issue: "Model not loaded"
**Fix:** Wait 2-3 minutes after deployment. Models download on first startup.

### Issue: CORS errors
**Fix:** Verify FRONTEND_URL is set correctly in all 3 APIs.

### Issue: Chatbot API calls fail
**Fix:** Ensure JOB_RECOMMENDATION_API and SKILL_GAP_API URLs are correct.

### Issue: Database errors
**Fix:** Verify DATABASE_URL is correct and database allows external connections.

---

## ✅ Deployment Checklist

### Render (Backend)
- [ ] Job Recommendation API deployed
- [ ] Skill Gap API deployed
- [ ] Chatbot API deployed (with other API URLs)
- [ ] All environment variables configured
- [ ] All /health endpoints return 200
- [ ] Test all endpoints with Postman

### Vercel (Frontend)
- [ ] Frontend deployed
- [ ] All 3 API URLs configured
- [ ] No CORS errors in console
- [ ] All components working
- [ ] Tested on different devices/browsers

---

## 📚 Documentation Files

1. **MASTER_DEPLOYMENT_GUIDE.md**
   - Complete step-by-step guide
   - Deploy all 3 APIs + frontend
   - Environment variables
   - Testing instructions

2. **FRONTEND_INTEGRATION_GUIDE.md**
   - Complete React components
   - API service files
   - TypeScript interfaces
   - Usage examples

3. **job-recommendation-api/DEPLOYMENT_GUIDE.md**
   - Specific to Job API
   - Endpoint documentation
   - Frontend integration code

4. **skill-gap-api/DEPLOYMENT_GUIDE.md**
   - Specific to Skill Gap API
   - Endpoint documentation
   - Frontend integration code

5. **chatbot-api/DEPLOYMENT_GUIDE.md**
   - Specific to Chatbot API
   - All 6 intents explained
   - Frontend integration code

---

## 🎯 Recommended Reading Order

1. **Start here:** `MASTER_DEPLOYMENT_GUIDE.md`
2. **Deploy APIs:** Follow individual `DEPLOYMENT_GUIDE.md` files
3. **Integrate frontend:** `FRONTEND_INTEGRATION_GUIDE.md`
4. **Test everything:** Use examples in guides

---

## 🚀 Getting Started

```bash
# 1. Push your code to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Open MASTER_DEPLOYMENT_GUIDE.md
# Follow step-by-step instructions

# 3. Deploy to Render (3 services)
# Job API → Skill Gap API → Chatbot API

# 4. Deploy to Vercel (frontend)
# Configure environment variables

# 5. Test everything!
```

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   - Render: Each service has logs tab
   - Vercel: Check build and function logs
   - Browser: Check console for errors

2. **Verify configuration:**
   - Environment variables set correctly
   - API URLs match deployed services
   - Database connection string is correct

3. **Test incrementally:**
   - Test each API individually
   - Then test API-to-API communication
   - Finally test from frontend

---

## 🎉 You're Ready!

This deployment package has everything you need to:
- ✅ Deploy 3 production-ready APIs
- ✅ Integrate with React/Next.js frontend
- ✅ Handle all CORS and communication
- ✅ Ensure no errors occur

**Start with `MASTER_DEPLOYMENT_GUIDE.md` and you'll be live in 30-45 minutes!** 🚀

---

**Last Updated:** October 30, 2025
**Version:** 1.0.0

**Questions?** Check the individual deployment guides for detailed information.
