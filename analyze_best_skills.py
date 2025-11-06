"""
Script to analyze the Job Roles database and find the best skills for demo.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from collections import Counter
import re

# Database connection
DATABASE_URL = "postgresql://postgres.rpzkywwzmcaawjmcqnrq:ApexIsTheBest@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def analyze_skills():
    """
    Analyze all skills in the database to find the most common ones.
    """
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all required skills
        print("📊 Fetching all job skills...")
        cursor.execute('SELECT "Required Skills", "Category", "Job Role" FROM "Job Roles"')
        jobs = cursor.fetchall()
        
        print(f"✅ Analyzing {len(jobs)} jobs\n")
        
        # Count all skills
        skill_counter = Counter()
        category_skills = {}
        
        for job in jobs:
            skills_text = job['Required Skills'] or ''
            category = job['Category'] or 'Other'
            
            # Split by comma and clean
            skills = [s.strip() for s in skills_text.split(',') if s.strip()]
            
            for skill in skills:
                skill_counter[skill] += 1
                
                # Track by category
                if category not in category_skills:
                    category_skills[category] = Counter()
                category_skills[category][skill] += 1
        
        # Top overall skills
        print("="*80)
        print("🏆 TOP 30 MOST IN-DEMAND SKILLS (Across All Jobs)")
        print("="*80)
        for i, (skill, count) in enumerate(skill_counter.most_common(30), 1):
            percentage = (count / len(jobs)) * 100
            print(f"{i:2d}. {skill:40s} - {count:4d} jobs ({percentage:5.1f}%)")
        
        # Top skills by category
        print("\n" + "="*80)
        print("📊 TOP SKILLS BY CATEGORY")
        print("="*80)
        
        top_categories = ['Data Science', 'Software Development', 'Cloud Computing', 
                         'Finance', 'Marketing', 'Healthcare']
        
        for category in top_categories:
            if category in category_skills:
                print(f"\n🎯 {category}:")
                for i, (skill, count) in enumerate(category_skills[category].most_common(10), 1):
                    print(f"   {i}. {skill} ({count} jobs)")
        
        # Find high-paying job roles
        print("\n" + "="*80)
        print("💰 HIGH-PAYING JOB ROLES (With Skills)")
        print("="*80)
        
        cursor.execute("""
            SELECT "Job Role", "Required Skills", "Max Salary", "Category"
            FROM "Job Roles"
            WHERE "Max Salary" IS NOT NULL
            ORDER BY "Max Salary" DESC
            LIMIT 15
        """)
        high_paying = cursor.fetchall()
        
        for i, job in enumerate(high_paying, 1):
            role = job['Job Role']
            skills = job['Required Skills'] or 'N/A'
            salary = job['Max Salary']
            category = job['Category']
            print(f"\n{i:2d}. {role} ({category})")
            print(f"    💰 Max Salary: ₹{salary:,.0f}")
            print(f"    🔧 Skills: {skills[:100]}{'...' if len(skills) > 100 else ''}")
        
        cursor.close()
        conn.close()
        
        # Create demo prompts
        print("\n" + "="*80)
        print("🎤 RECOMMENDED DEMO PROMPTS FOR JUDGES")
        print("="*80)
        
        # Get top 10 skills
        top_skills = [skill for skill, _ in skill_counter.most_common(15)]
        
        print("\n📌 OPTION 1: Data Science Professional")
        print("-" * 80)
        ds_skills = ['Python', 'Machine Learning', 'SQL', 'Data analysis', 'Excel', 
                     'Communication', 'Statistics', 'Deep learning', 'TensorFlow']
        ds_skills = [s for s in ds_skills if s in top_skills][:6]
        prompt1 = f"Hi! I'm a data science professional with expertise in {', '.join(ds_skills[:-1])}, and {ds_skills[-1]}. Can you recommend some relevant job opportunities for me?"
        print(prompt1)
        
        print("\n📌 OPTION 2: Full Stack Developer")
        print("-" * 80)
        dev_skills = ['Python', 'JavaScript', 'React', 'SQL', 'Communication', 
                      'Problem solving', 'Leadership']
        dev_skills = [s for s in dev_skills if s in top_skills][:6]
        prompt2 = f"Hello! I have {len(dev_skills)} years of experience in full stack development. My skills include {', '.join(dev_skills[:-1])}, and {dev_skills[-1]}. What jobs would you recommend?"
        print(prompt2)
        
        print("\n📌 OPTION 3: Business Analyst")
        print("-" * 80)
        ba_skills = ['Excel', 'Communication', 'Data analysis', 'SQL', 'Problem solving', 
                     'Analytical thinking', 'PowerPoint']
        ba_skills = [s for s in ba_skills if s in top_skills][:6]
        prompt3 = f"I'm looking for business analyst roles. I'm skilled in {', '.join(ba_skills[:-1])}, and {ba_skills[-1]}. Show me the best matches."
        print(prompt3)
        
        print("\n📌 OPTION 4: AI/ML Engineer (Most Impressive)")
        print("-" * 80)
        ml_skills = ['Python', 'Machine Learning', 'Deep learning', 'TensorFlow', 'SQL', 
                     'Data analysis', 'Algorithms', 'NLP']
        ml_skills = [s for s in ml_skills if s in top_skills][:7]
        prompt4 = f"I'm an AI/ML engineer specializing in {', '.join(ml_skills[:4])}. I also have strong skills in {', '.join(ml_skills[4:])}. Can you find job opportunities that match my expertise and analyze my skill gaps for top positions?"
        print(prompt4)
        
        print("\n📌 OPTION 5: Fresh Graduate (Shows Versatility)")
        print("-" * 80)
        fresh_skills = ['Python', 'Communication', 'Excel', 'SQL', 'Problem solving']
        fresh_skills = [s for s in fresh_skills if s in top_skills][:5]
        prompt5 = f"Hi! I'm a fresh graduate with skills in {', '.join(fresh_skills)}. I'm open to various roles in tech. What career paths would you suggest based on my current skillset?"
        print(prompt5)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    analyze_skills()
