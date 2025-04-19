import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Настройки приложения с использованием переменных окружения
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 минут * 24 часа * 8 дней = 8 дней
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Настройки PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "ofs_user"
    POSTGRES_PASSWORD: str = "111"
    POSTGRES_DB: str = "ofs_photomatrix"
    POSTGRES_PORT: int = 5432
    
    # Поле для значения из переменной окружения
    DATABASE_URL: Optional[str] = None
    
    # Поле для SQLAlchemy URL
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # Если есть DATABASE_URL в переменных окружения, используем его
        db_url = values.data.get("DATABASE_URL")
        if db_url:
            return db_url
            
        # Иначе строим URL из отдельных компонентов
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )
    
    # Настройки Email
    EMAILS_ENABLED: bool = False
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    
    # Первый суперпользователь
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "adminadmin"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

# Создание объекта настроек
settings = Settings() 