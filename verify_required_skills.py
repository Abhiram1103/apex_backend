"""
Script to verify the Required Skills column content.
Shows examples of skills to check for '/' and '.' characters.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def verify_required_skills():
    """
    Check the Required Skills column for '/' and '.' characters.
    """
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get sample jobs
        print("📊 Fetching sample jobs...")
        cursor.execute('SELECT "Job Role", "Required Skills" FROM "Job Roles" LIMIT 10')
        jobs = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"📝 SAMPLE OF REQUIRED SKILLS (First 10 jobs)")
        print(f"{'='*80}")
        
        for i, job in enumerate(jobs, 1):
            skills = job['Required Skills'] or 'None'
            role = job['Job Role']
            
            # Check for '/' and '.'
            has_slash = '/' in skills
            has_dot = '.' in skills
            
            print(f"\n{i}. {role}")
            print(f"   Skills: {skills[:150]}{'...' if len(skills) > 150 else ''}")
            
            if has_slash or has_dot:
                print(f"   ⚠️  Contains: {', '.join(['/' if has_slash else '', '.' if has_dot else '']).strip(', ')}")
            else:
                print(f"   ✅ No '/' or '.' found")
        
        # Count total jobs with '/' or '.'
        print(f"\n{'='*80}")
        print("📊 STATISTICS")
        print(f"{'='*80}")
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN "Required Skills" LIKE '%/%' THEN 1 ELSE 0 END) as with_slash,
                   SUM(CASE WHEN "Required Skills" LIKE '%.%' THEN 1 ELSE 0 END) as with_dot
            FROM "Job Roles"
        """)
        stats = cursor.fetchone()
        
        print(f"Total jobs: {stats['total']}")
        print(f"Jobs with '/': {stats['with_slash']}")
        print(f"Jobs with '.': {stats['with_dot']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    verify_required_skills()
