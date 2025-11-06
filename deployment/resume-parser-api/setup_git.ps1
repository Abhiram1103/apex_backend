# Git Setup and Push to GitHub
# Run this in PowerShell

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🚀 GIT SETUP FOR RENDER DEPLOYMENT" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Navigate to the directory
Set-Location "d:\carrier velocity\deployment\resume-parser-api"

Write-Host "📂 Current Directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Check if git is initialized
if (Test-Path ".git") {
    Write-Host "✅ Git already initialized" -ForegroundColor Green
} else {
    Write-Host "📝 Initializing Git repository..." -ForegroundColor Yellow
    git init
}

Write-Host ""
Write-Host "📋 Files to commit:" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "➕ Adding files to Git..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💬 Creating commit..." -ForegroundColor Yellow
git commit -m "Add resume parser API with skill extraction"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ FILES COMMITTED LOCALLY" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "📤 NEXT STEP: Push to GitHub" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: If already connected to GitHub repo:" -ForegroundColor Cyan
Write-Host "   git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: If setting up for first time:" -ForegroundColor Cyan
Write-Host "   cd ../../.." -ForegroundColor White
Write-Host "   git add deployment/resume-parser-api/" -ForegroundColor White
Write-Host "   git commit -m 'Add resume parser API'" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🌐 AFTER PUSHING TO GITHUB:" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com/" -ForegroundColor Yellow
Write-Host "2. Click: 'New +' → 'Web Service'" -ForegroundColor Yellow
Write-Host "3. Connect: GitHub repo (Abhiram1103/apex_backend)" -ForegroundColor Yellow
Write-Host "4. Set Root Directory: deployment/resume-parser-api" -ForegroundColor Yellow
Write-Host "5. Click: 'Create Web Service'" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 See DEPLOYMENT.md for detailed instructions" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
