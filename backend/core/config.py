"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pydantic import field_validator

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "prismtrack")
    
    @property
    def database_url(self) -> str:
        """Build DATABASE_URL from components if not provided, handling special characters in password"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # URL-encode password to handle special characters like @, #, etc.
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    
    # CORS - parse from comma-separated string
    CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    @field_validator("CORS_ORIGINS_STR", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Allow CORS_ORIGINS to be set from environment"""
        return v
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS_STR == "*":
            # If "*" is set, return default list for development
            # Note: Cannot use "*" when allow_credentials=True, must specify exact origins
            return [
                "http://localhost:3000",
                "http://localhost:8000", 
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
        # Split by comma and clean up whitespace
        origins = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
        # Ensure localhost:8080 is always included for development
        if "http://localhost:8080" not in origins:
            origins.append("http://localhost:8080")
        if "http://127.0.0.1:8080" not in origins:
            origins.append("http://127.0.0.1:8080")
        return origins
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment

settings = Settings()

