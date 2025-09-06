from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/app_db"
    
    # JWT
    SECRET_KEY: str = "your_secret_key_change_this_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Environment
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # App
    APP_NAME: str = "FastAPI Microservice Boilerplate"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-ready FastAPI boilerplate with microservice architecture"
    
    # CORS
    ALLOWED_HOSTS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
