"""
Script to create platform admin user
Run this after setting up the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from sqlalchemy import create_engine, text
from backend.core.config import settings

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string (bcrypt format: $2b$...)
    return hashed.decode('utf-8')

def create_admin_user(username: str, email: str, password: str):
    """Create platform admin user in database"""
    engine = create_engine(settings.DATABASE_URL)
    
    password_hash = hash_password(password)
    
    with engine.connect() as conn:
        # Check if user exists
        result = conn.execute(text("SELECT id FROM platform_admins WHERE username = :username"), {"username": username})
        if result.fetchone():
            print(f"User '{username}' already exists!")
            return
        
        # Insert new admin
        conn.execute(text("""
            INSERT INTO platform_admins (username, email, password_hash)
            VALUES (:username, :email, :password_hash)
        """), {
            "username": username,
            "email": email,
            "password_hash": password_hash
        })
        conn.commit()
        print(f"Platform admin '{username}' created successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create platform admin user")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@prismtrack.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    
    args = parser.parse_args()
    create_admin_user(args.username, args.email, args.password)

