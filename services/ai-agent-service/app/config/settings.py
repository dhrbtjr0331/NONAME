from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # AI Provider Configuration
    AI_PROVIDER: str = "mock"  # Options: mock, openai, anthropic, bedrock
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Anthropic Configuration
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"  # haiku, sonnet, opus
    
    # AWS Configuration (for Bedrock)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Database Configuration (using same pattern as core API)
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_agent.db"
    
    # JWT Configuration (for integration with core API)
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY: int = 20
    MAX_MESSAGE_LENGTH: int = 2000
    CONVERSATION_TIMEOUT_MINUTES: int = 30
    
    # Agent Configuration
    DEFAULT_MODEL_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()