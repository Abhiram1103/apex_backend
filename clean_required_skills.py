"""
Script to clean the Required Skills column in Job Roles table.
Replaces all '/' and '.' characters with spaces.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def clean_required_skills():
    """
    Replace all '/' and '.' with spaces in the Required Skills column.
    """
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all jobs
        print("📊 Fetching all jobs from 'Job Roles' table...")
        cursor.execute('SELECT id, "Required Skills" FROM "Job Roles"')
        jobs = cursor.fetchall()
        
        print(f"✅ Found {len(jobs)} jobs")
        
        # Count how many will be updated
        updated_count = 0
        
        print("\n🔄 Processing jobs...")
        for job in jobs:
            job_id = job['id']
            original_skills = job['Required Skills']
            
            if original_skills:
                # Replace '/' and '.' with spaces
                cleaned_skills = original_skills.replace('/', ' ').replace('.', ' ')
                
                # Only update if there's a change
                if cleaned_skills != original_skills:
                    cursor.execute(
                        'UPDATE "Job Roles" SET "Required Skills" = %s WHERE id = %s',
                        (cleaned_skills, job_id)
                    )
                    updated_count += 1
                    
                    if updated_count <= 5:  # Show first 5 examples
                        print(f"\n📝 Example {updated_count}:")
                        print(f"   Before: {original_skills[:100]}...")
                        print(f"   After:  {cleaned_skills[:100]}...")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS!")
        print(f"{'='*60}")
        print(f"Total jobs processed: {len(jobs)}")
        print(f"Jobs updated: {updated_count}")
        print(f"Jobs unchanged: {len(jobs) - updated_count}")
        print(f"\n💾 Changes saved to database!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    print("="*60)
    print("🧹 CLEANING REQUIRED SKILLS COLUMN")
    print("="*60)
    print("Task: Replace '/' and '.' with spaces")
    print("Table: Job Roles")
    print("Column: Required Skills")
    print("="*60)
    
    # Confirm before proceeding
    confirm = input("\n⚠️  This will modify the database. Continue? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        print("\n🚀 Starting cleanup...\n")
        clean_required_skills()
    else:
        print("\n❌ Operation cancelled.")
