# Job Recommendation API - Deployment Guide

## 🚀 Deploy to Render

### Step 1: Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Select this directory: `deployment/job-recommendation-api`

### Step 2: Configure Service

**Build & Deploy Settings:**
- **Name:** `job-recommendation-api` (or your choice)
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

**Note:** Render automatically provides the `PORT` variable, but you can set it explicitly.

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (first time takes 5-10 minutes)
3. Watch logs for: `✅ Successfully cached X jobs with embeddings!`

---

## 📡 API Endpoints

Once deployed, your API will be available at: `https://job-recommendation-api.onrender.com`

### Root Endpoint
```
GET https://job-recommendation-api.onrender.com/
```

### Health Check
```
GET https://job-recommendation-api.onrender.com/health
```

### Get Job Recommendations
```
POST https://job-recommendation-api.onrender.com/api/recommend

Request Body:
{
  "user_id": "user123",
  "top_n": 10
}

Response:
{
  "success": true,
  "recommendations": [
    {
      "job_id": "uuid-here",
      "similarity_score": 0.85
    }
  ],
  "total_jobs_analyzed": 500
}
```

### Refresh Cache
```
POST https://job-recommendation-api.onrender.com/api/refresh-cache
```

### Get Statistics
```
GET https://job-recommendation-api.onrender.com/api/stats
```

---

## 🔧 How Frontend Should Call This API

### React/Next.js Example

```javascript
// Create a service file: services/jobRecommendation.js

const JOB_API_URL = process.env.NEXT_PUBLIC_JOB_API_URL || 
                    'https://job-recommendation-api.onrender.com';

export const getJobRecommendations = async (userId, topN = 10) => {
  try {
    const response = await fetch(`${JOB_API_URL}/api/recommend`, {
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
    console.error('Failed to get job recommendations:', error);
    throw error;
  }
};

// Usage in component:
import { getJobRecommendations } from '../services/jobRecommendation';

function JobRecommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const data = await getJobRecommendations('user123', 10);
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  return (
    <div>
      {loading ? (
        <p>Loading recommendations...</p>
      ) : (
        <ul>
          {recommendations.map(rec => (
            <li key={rec.job_id}>
              Job ID: {rec.job_id} | 
              Match: {(rec.similarity_score * 100).toFixed(1)}%
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Axios Example

```javascript
import axios from 'axios';

const jobApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_JOB_API_URL || 
           'https://job-recommendation-api.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getJobRecommendations = async (userId, topN = 10) => {
  const { data } = await jobApi.post('/api/recommend', {
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
- **Request Time:** 100-500ms per request

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
- Implement a keep-alive ping from frontend

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
NEXT_PUBLIC_JOB_API_URL=https://job-recommendation-api.onrender.com
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
