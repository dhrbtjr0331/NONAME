from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration (should match auth service exactly)
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # Add this field
    
    # Database Configuration - point to shared SQLite file
    DATABASE_URL: str = "sqlite+aiosqlite:///./shared/database/test.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This ignores extra fields instead of raising an error

settings = Settings()