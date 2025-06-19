from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite+aiosqlite:///./shared/database/test.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()