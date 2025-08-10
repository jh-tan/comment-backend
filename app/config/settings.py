import secrets
import os
from typing import Any, List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Comment-Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  
    
    @property
    def POSTGRES_SERVER(self) -> str:
        if os.getenv("ENVIRONMENT") == "local":
            return os.getenv("POSTGRES_SERVER_LOCAL", "localhost")
        return "db"
    
    @property
    def POSTGRES_USER(self) -> str:
        if os.getenv("ENVIRONMENT") == "local":
            return os.getenv("POSTGRES_USER_LOCAL", "postgres")
        return "postgres"
    
    @property  
    def POSTGRES_PORT(self) -> str:
        return "5432"
    
    # User-configurable settings
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "comment_backend"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        
        temp_settings = cls.__new__(cls)
        temp_settings.__dict__.update(values.data)
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=temp_settings.POSTGRES_USER,
            password=values.data.get("POSTGRES_PASSWORD"),
            host=temp_settings.POSTGRES_SERVER,
            port=int(temp_settings.POSTGRES_PORT),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )          
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
