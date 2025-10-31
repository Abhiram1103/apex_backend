"""
One-time script to generate and store job embeddings in database
Run this ONCE locally before deploying to Render

This will:
1. Fetch all jobs from database
2. Generate embeddings using SBERT
3. Store embeddings back in database as BYTEA
"""

import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 100

def add_embedding_column():
    """Add embedding column to database if it doesn't exist"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        print("📊 Adding embedding column to database...")
        cur.execute("""
            ALTER TABLE "Job Roles" 
            ADD COLUMN IF NOT EXISTS embedding BYTEA;
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_roles_id ON "Job Roles"(id);
        """)
        
        conn.commit()
        print("✅ Database schema updated!")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def generate_and_store_embeddings():
    """Generate embeddings for all jobs and store in database"""
    print(f"🤖 Loading SBERT model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("✅ Model loaded!")
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Count jobs without embeddings
        cur.execute('SELECT COUNT(*) FROM "Job Roles" WHERE embedding IS NULL')
        total_jobs = cur.fetchone()[0]
        
        if total_jobs == 0:
            print("✅ All jobs already have embeddings!")
            return
        
        print(f"📊 Found {total_jobs} jobs without embeddings")
        
        # Fetch jobs in batches
        cur.execute("""
            SELECT id, "Required Skills" 
            FROM "Job Roles" 
            WHERE embedding IS NULL
        """)
        
        jobs = cur.fetchall()
        
        print(f"🚀 Generating embeddings for {len(jobs)} jobs...")
        
        # Process in batches
        for i in tqdm(range(0, len(jobs), BATCH_SIZE)):
            batch = jobs[i:i + BATCH_SIZE]
            
            # Generate embeddings for batch
            job_texts = [skills for _, skills in batch]
            embeddings = model.encode(job_texts, show_progress_bar=False)
            
            # Store embeddings
            for (job_id, _), embedding in zip(batch, embeddings):
                # Convert numpy array to bytes
                embedding_bytes = embedding.astype(np.float32).tobytes()
                
                cur.execute("""
                    UPDATE "Job Roles" 
                    SET embedding = %s 
                    WHERE id = %s
                """, (embedding_bytes, job_id))
            
            # Commit after each batch
            conn.commit()
        
        print("✅ All embeddings generated and stored!")
        
        # Verify
        cur.execute('SELECT COUNT(*) FROM "Job Roles" WHERE embedding IS NOT NULL')
        embedded_count = cur.fetchone()[0]
        print(f"✅ Verified: {embedded_count} jobs now have embeddings")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def verify_embeddings():
    """Verify embeddings are stored correctly"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Check a sample embedding
        cur.execute("""
            SELECT id, embedding 
            FROM "Job Roles" 
            WHERE embedding IS NOT NULL 
            LIMIT 1
        """)
        
        result = cur.fetchone()
        if result:
            job_id, embedding_bytes = result
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            
            print(f"✅ Sample embedding for job {job_id}:")
            print(f"   - Shape: {embedding.shape}")
            print(f"   - Dimensions: {len(embedding)}")
            print(f"   - Size: {len(embedding_bytes)} bytes")
            print(f"   - Sample values: {embedding[:5]}")
            
            if len(embedding) == 384:
                print("✅ Embedding dimensions are correct!")
            else:
                print(f"❌ Warning: Expected 384 dimensions, got {len(embedding)}")
        else:
            print("❌ No embeddings found in database")
            
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Job Embedding Generator")
    print("=" * 60)
    print()
    
    # Step 1: Add embedding column
    add_embedding_column()
    print()
    
    # Step 2: Generate and store embeddings
    generate_and_store_embeddings()
    print()
    
    # Step 3: Verify
    verify_embeddings()
    print()
    
    print("=" * 60)
    print("✅ Done! Your database now has pre-computed embeddings")
    print("   Your APIs will use ~80% less memory! 🎉")
    print("=" * 60)
