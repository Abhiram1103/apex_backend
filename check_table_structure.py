"""
Check the structure of Job Roles table
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get table columns
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'Job Roles'
    ORDER BY ordinal_position;
""")

print("📊 Columns in 'Job Roles' table:")
print("-" * 60)
columns = cur.fetchall()
for col_name, col_type in columns:
    print(f"  - {col_name:30} {col_type}")
print("-" * 60)
print(f"\nTotal columns: {len(columns)}")

# Get sample row
cur.execute('SELECT * FROM "Job Roles" LIMIT 1')
print("\n📋 Sample row:")
if cur.description:
    col_names = [desc[0] for desc in cur.description]
    print(f"Columns: {col_names}")
    row = cur.fetchone()
    if row:
        for i, val in enumerate(row):
            print(f"  {col_names[i]}: {val}")

# Get row count
cur.execute('SELECT COUNT(*) FROM "Job Roles"')
count = cur.fetchone()[0]
print(f"\n📊 Total rows in table: {count}")

cur.close()
conn.close()
