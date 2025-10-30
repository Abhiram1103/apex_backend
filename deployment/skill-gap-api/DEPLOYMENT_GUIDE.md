# Skill Gap Analysis API - Deployment Guide

## 🚀 Deploy to Render

### Step 1: Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Select this directory: `deployment/skill-gap-api`

### Step 2: Configure Service

**Build & Deploy Settings:**
- **Name:** `skill-gap-api` (or your choice)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Instance Type:** Choose based on needs (Free tier available)

**Important:** This API needs at least **512MB RAM** due to the SBERT model.

### Step 3: Environment Variables

Add these environment variables in Render:

```
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres

FRONTEND_URL=https://your-frontend-domain.vercel.app

PORT=10000
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (first time takes 5-10 minutes)
3. Watch logs for: `✅ Successfully cached X jobs with embeddings!`

---

## 📡 API Endpoints

Once deployed, your API will be available at: `https://skill-gap-api.onrender.com`

### Root Endpoint
```
GET https://skill-gap-api.onrender.com/
```

### Health Check
```
GET https://skill-gap-api.onrender.com/health
```

### Get Skill Gap Analysis
```
POST https://skill-gap-api.onrender.com/api/skill-gap

Request Body:
{
  "user_id": "user123",
  "top_n": 10
}

Response:
{
  "success": true,
  "user_id": "user123",
  "user_skills": ["python", "sql", "pandas"],
  "top_opportunities": [
    {
      "job_id": "uuid",
      "job_role": "Data Scientist",
      "company": "Tech Corp",
      "avg_salary": 850000,
      "min_salary": 700000,
      "max_salary": 1000000,
      "similarity_score": 0.75,
      "normalized_salary": 0.85,
      "combined_score": 0.78,
      "missing_skills": ["machine learning", "tensorflow"],
      "matching_skills": ["python", "sql"]
    }
  ],
  "total_jobs_analyzed": 500
}
```

---

## 🔧 How Frontend Should Call This API

### React/Next.js Example

```javascript
// Create a service file: services/skillGapAnalysis.js

const SKILL_GAP_API_URL = process.env.NEXT_PUBLIC_SKILL_GAP_API_URL || 
                          'https://skill-gap-api.onrender.com';

export const getSkillGapAnalysis = async (userId, topN = 10) => {
  try {
    const response = await fetch(`${SKILL_GAP_API_URL}/api/skill-gap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        top_n: topN
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get skill gap analysis:', error);
    throw error;
  }
};

// Usage in component:
import { getSkillGapAnalysis } from '../services/skillGapAnalysis';

function SkillGapDashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const data = await getSkillGapAnalysis('user123', 10);
      setAnalysis(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  if (loading) return <p>Loading analysis...</p>;
  if (!analysis) return <p>No data available</p>;

  return (
    <div>
      <h2>Your Skills: {analysis.user_skills.join(', ')}</h2>
      
      <h3>Top Opportunities:</h3>
      {analysis.top_opportunities.map(opp => (
        <div key={opp.job_id} className="opportunity-card">
          <h4>{opp.job_role} at {opp.company}</h4>
          <p>💰 Salary: ₹{opp.avg_salary.toLocaleString()}</p>
          <p>📊 Match: {(opp.similarity_score * 100).toFixed(1)}%</p>
          <p>🎯 Combined Score: {(opp.combined_score * 100).toFixed(1)}%</p>
          
          <div className="skills-section">
            <p>✅ Matching Skills: {opp.matching_skills.join(', ')}</p>
            {opp.missing_skills.length > 0 && (
              <p>📚 Skills to Learn: {opp.missing_skills.join(', ')}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Axios Example

```javascript
import axios from 'axios';

const skillGapApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_SKILL_GAP_API_URL || 
           'https://skill-gap-api.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getSkillGapAnalysis = async (userId, topN = 10) => {
  const { data } = await skillGapApi.post('/api/skill-gap', {
    user_id: userId,
    top_n: topN
  });
  return data;
};
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

- **Minimum RAM:** 512MB (1GB recommended)
- **Disk Space:** ~2GB (for model files)
- **Startup Time:** 30-60 seconds (model loading)
- **Request Time:** 200-700ms per request

---

## 🐛 Troubleshooting

### "Model not loaded" error
- Wait 1-2 minutes after deployment
- Check logs for model download progress
- Ensure instance has enough RAM

### Database connection errors
- Verify `DATABASE_URL` is correct
- Check if database allows connections from Render IPs
- Test connection from Render shell

### Slow cold starts
- Free tier on Render spins down after inactivity
- Consider paid tier for persistent instances

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
NEXT_PUBLIC_SKILL_GAP_API_URL=https://skill-gap-api.onrender.com
```

---

## ✅ Deployment Checklist

- [ ] Repository connected to Render
- [ ] Environment variables configured
- [ ] Database URL is correct
- [ ] Frontend URL is set
- [ ] Build command is correct
- [ ] Start command is correct
- [ ] Health check returns 200
- [ ] Test API call from Postman
- [ ] Test from frontend
- [ ] Monitor logs for errors

---

## 📞 Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Test database connection
4. Check CORS settings

Your API URL will be: `https://your-service-name.onrender.com`
