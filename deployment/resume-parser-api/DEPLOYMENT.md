# 🚀 Render Deployment Guide - Resume Parser API

## 📋 Pre-Deployment Checklist

✅ All files created  
✅ Database configured (Supabase PostgreSQL)  
✅ Dependencies listed in requirements.txt  
✅ Python version specified (3.11.9)  
✅ Environment variables ready  

---

## 🔧 Deployment Steps

### **Method 1: Deploy from GitHub (Recommended)**

#### **Step 1: Push to GitHub**

```powershell
# Navigate to project directory
cd "d:\carrier velocity\deployment\resume-parser-api"

# Initialize git (if not already)
git init

# Add files
git add .
git commit -m "Add resume parser API for Render deployment"

# Push to your repository
git remote add origin https://github.com/Abhiram1103/apex_backend.git
git push origin main
```

#### **Step 2: Create Render Web Service**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Abhiram1103/apex_backend`
4. Configure the service:

**Basic Settings:**
```
Name: resume-parser-api
Region: Singapore (or closest to your users)
Branch: main
Root Directory: deployment/resume-parser-api
```

**Build Settings:**
```
Runtime: Python 3
Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Plan:**
```
Instance Type: Free (or Starter $7/month for better performance)
```

#### **Step 3: Set Environment Variables**

In Render Dashboard → Environment tab, add:

```
Key: PYTHON_VERSION
Value: 3.11.9

Key: DATABASE_URL
Value: postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
```

#### **Step 4: Deploy**

1. Click **"Create Web Service"**
2. Wait for build to complete (3-5 minutes)
3. Service will be live at: `https://resume-parser-api.onrender.com`

---

### **Method 2: Deploy with render.yaml (Auto-Deploy)**

The `render.yaml` file is already configured. Render will auto-detect it.

1. Push code to GitHub
2. In Render Dashboard: **New +** → **Blueprint**
3. Connect repository
4. Render will use `render.yaml` for configuration
5. Click **"Apply"**

---

## 🌐 After Deployment

### **Your API will be available at:**
```
https://resume-parser-api.onrender.com
```

### **Test Endpoints:**

**Health Check:**
```bash
curl https://resume-parser-api.onrender.com/health
```

**API Docs:**
```
https://resume-parser-api.onrender.com/docs
```

**Parse Resume:**
```bash
curl -X POST "https://resume-parser-api.onrender.com/parse-resume" \
  -F "file=@resume.pdf" \
  -F "uuid=test-user-123"
```

---

## 📊 Render Configuration Summary

| Setting | Value |
|---------|-------|
| **Service Name** | resume-parser-api |
| **Type** | Web Service |
| **Region** | Singapore |
| **Runtime** | Python 3.11.9 |
| **Build Command** | `pip install -r requirements.txt && python -m spacy download en_core_web_sm` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance** | Free / Starter |
| **Auto-Deploy** | Yes (on git push) |

---

## 🔒 Environment Variables

Set these in Render Dashboard:

```bash
DATABASE_URL=postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
PYTHON_VERSION=3.11.9
```

**Note:** Don't commit `.env` file to GitHub (it's in `.gitignore`)

---

## 📈 Performance Expectations

### **Free Tier:**
- ⏱️ Cold start: 30-60 seconds (after inactivity)
- 💾 Memory: 512MB
- ⚡ Response: 2-5 seconds per resume
- 🔄 Sleeps after 15 min inactivity

### **Starter Tier ($7/month):**
- ⏱️ Always on (no cold starts)
- 💾 Memory: 512MB
- ⚡ Response: 2-4 seconds per resume
- 🔄 Never sleeps

---

## 🐛 Troubleshooting

### **Issue: Build Failed**

**Check:**
1. `requirements.txt` is correct
2. Python version is 3.11.9 in `runtime.txt`
3. Build command includes spaCy download

**Solution:**
```bash
# Build command should be:
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

### **Issue: Application Failed to Start**

**Check:**
1. Start command is correct
2. Port is `$PORT` (not hardcoded)
3. Host is `0.0.0.0`

**Solution:**
```bash
# Start command should be:
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Issue: Database Connection Error**

**Check:**
1. DATABASE_URL environment variable is set
2. Supabase allows connections from Render IPs
3. Database credentials are correct

**Solution:**
- Verify DATABASE_URL in Render environment variables
- Check Supabase connection pooler settings

### **Issue: Module Not Found**

**Check:**
1. All dependencies in `requirements.txt`
2. Build logs show successful pip installs
3. spaCy model downloaded

**Solution:**
```bash
# Rebuild with:
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

---

## 📝 Deployment Checklist

Before deploying, ensure:

- [x] `main.py` - API code
- [x] `requirements.txt` - All dependencies
- [x] `runtime.txt` - Python 3.11.9
- [x] `render.yaml` - Render configuration
- [x] `Procfile` - Start command
- [x] `.gitignore` - Exclude sensitive files
- [x] `README.md` - Documentation
- [x] Database table created in Supabase

---

## 🔄 Update Deployment

To update your deployed API:

```bash
# Make changes to code
# Commit changes
git add .
git commit -m "Update API"
git push origin main

# Render will auto-deploy the changes
```

---

## 💰 Cost Estimate

**Free Plan:**
- Cost: $0/month
- Limitations: Sleeps after 15 min, cold starts

**Starter Plan:**
- Cost: $7/month
- Benefits: Always on, faster, no cold starts

**Recommended:** Start with Free, upgrade to Starter if needed

---

## 🔗 Important Links

- **Render Dashboard:** https://dashboard.render.com/
- **API Docs (after deploy):** https://resume-parser-api.onrender.com/docs
- **Health Check:** https://resume-parser-api.onrender.com/health
- **Logs:** Available in Render Dashboard → Logs tab

---

## 📞 Next Steps After Deployment

1. ✅ Test health endpoint
2. ✅ Test resume parsing with sample PDF
3. ✅ Verify database saves skills correctly
4. ✅ Update frontend to use new API URL
5. ✅ Set up custom domain (optional)
6. ✅ Monitor logs for errors
7. ✅ Configure CORS if needed (already enabled in code)

---

## 🎯 Production URL

Once deployed, update your frontend to use:

```javascript
const API_URL = "https://resume-parser-api.onrender.com";

// Upload resume
const formData = new FormData();
formData.append('file', resumeFile);
formData.append('uuid', userUuid);

const response = await fetch(`${API_URL}/parse-resume`, {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Extracted skills:', result.skills);
```

---

**Your Resume Parser API is ready for deployment! 🚀**
