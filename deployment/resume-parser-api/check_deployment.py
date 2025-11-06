"""
Deployment Readiness Check Script
Verifies all files are ready for Render deployment
"""

import os
import sys

print("=" * 70)
print("🚀 RENDER DEPLOYMENT READINESS CHECK")
print("=" * 70)
print()

# Required files
required_files = {
    'main.py': 'Main API application',
    'requirements.txt': 'Python dependencies',
    'runtime.txt': 'Python version specification',
    'render.yaml': 'Render configuration',
    'Procfile': 'Process file for deployment',
    '.gitignore': 'Git ignore file',
    'README.md': 'Documentation',
    'DEPLOYMENT.md': 'Deployment guide'
}

# Check files
all_present = True
for file, description in required_files.items():
    if os.path.exists(file):
        file_size = os.path.getsize(file)
        print(f"✅ {file:20} - {description:30} ({file_size:,} bytes)")
    else:
        print(f"❌ {file:20} - MISSING!")
        all_present = False

print()
print("=" * 70)

if all_present:
    print("✅ ALL FILES PRESENT - READY FOR DEPLOYMENT!")
    print()
    print("📋 NEXT STEPS:")
    print("1. Push code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add resume parser API'")
    print("   git push origin main")
    print()
    print("2. Deploy on Render:")
    print("   - Go to https://dashboard.render.com/")
    print("   - Click 'New +' → 'Web Service'")
    print("   - Connect GitHub repo: Abhiram1103/apex_backend")
    print("   - Root Directory: deployment/resume-parser-api")
    print("   - Deploy!")
    print()
    print("📖 See DEPLOYMENT.md for detailed instructions")
else:
    print("❌ SOME FILES MISSING - CHECK ABOVE")
    sys.exit(1)

print("=" * 70)

# Check requirements.txt content
print()
print("📦 DEPENDENCIES CHECK:")
print("=" * 70)
with open('requirements.txt', 'r') as f:
    deps = f.read().strip().split('\n')
    for dep in deps:
        print(f"   • {dep}")

print()
print("=" * 70)
print("🌐 EXPECTED API URL:")
print("   https://resume-parser-api.onrender.com")
print("=" * 70)
