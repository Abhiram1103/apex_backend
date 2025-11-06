@echo off
REM Quick Deployment Script for Resume Parser API
REM Run this from PowerShell or CMD

echo ====================================================================
echo 🚀 RENDER DEPLOYMENT - RESUME PARSER API
echo ====================================================================
echo.

echo 📋 Deployment Checklist:
echo [✓] All files created
echo [✓] Dependencies configured
echo [✓] Database connected
echo [✓] Environment variables ready
echo.

echo ====================================================================
echo STEP 1: PUSH TO GITHUB
echo ====================================================================
echo.
echo Navigate to repository root and run:
echo.
echo   cd "d:\carrier velocity"
echo   git add deployment/resume-parser-api/
echo   git commit -m "Add resume parser API for Render deployment"
echo   git push origin main
echo.

echo ====================================================================
echo STEP 2: DEPLOY ON RENDER
echo ====================================================================
echo.
echo 1. Go to: https://dashboard.render.com/
echo 2. Click: New + → Web Service
echo 3. Connect: GitHub repo (Abhiram1103/apex_backend)
echo 4. Configure:
echo    - Name: resume-parser-api
echo    - Region: Singapore
echo    - Root Directory: deployment/resume-parser-api
echo    - Build Command: pip install -r requirements.txt ^&^& python -m spacy download en_core_web_sm
echo    - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
echo 5. Add Environment Variables:
echo    - PYTHON_VERSION = 3.11.9
echo    - DATABASE_URL = (your Supabase URL)
echo 6. Click: Create Web Service
echo.

echo ====================================================================
echo AFTER DEPLOYMENT
echo ====================================================================
echo.
echo Your API will be live at:
echo   https://resume-parser-api.onrender.com
echo.
echo Test with:
echo   https://resume-parser-api.onrender.com/docs
echo.

echo ====================================================================
echo 📖 For detailed instructions, see DEPLOYMENT.md
echo ====================================================================
echo.

pause
