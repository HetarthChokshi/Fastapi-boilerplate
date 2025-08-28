from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "FastAPI JWT Auth Boilerplate"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
