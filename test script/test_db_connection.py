"""Test database connection"""
import sys
from backend.core.config import settings
from backend.core.database import engine
from sqlalchemy import text

try:
    print("Testing database connection...")
    print(f"Database URL: {settings.database_url.replace(settings.DB_PASSWORD, '***')}")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Check if database exists
        result = conn.execute(text("SELECT DATABASE()"))
        db_name = result.scalar()
        print(f"✅ Connected to database: {db_name}")
        
        # Check if tables exist
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        if tables:
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
        else:
            print("⚠️  No tables found. Run database/schema.sql to create tables.")
            
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

