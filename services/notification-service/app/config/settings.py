from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite+aiosqlite:///./shared/database/test.db"
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@marketplace.com"
    FROM_NAME: str = "Marketplace Platform"
    
    # Background job settings
    NOTIFICATION_BATCH_SIZE: int = 100
    RETRY_DELAY_MINUTES: int = 5
    MAX_RETRY_ATTEMPTS: int = 3
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()