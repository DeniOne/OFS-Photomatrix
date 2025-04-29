import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения из корневого .env файла
root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env')
load_dotenv(root_env_path)

class Settings(BaseSettings):
    """
    Настройки приложения с использованием переменных окружения из корневого .env файла
    """
    API_V1_STR: str = "/api/v1"
    # Используем SECRET_KEY из корневого .env файла
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me-please-1234567890")
    # Используем время жизни токена из .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 8))
    
    # CORS настройки из .env
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    _cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173")
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Настройки PostgreSQL из корневого .env файла
    POSTGRES_SERVER: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("DB_USER", "ofs_user")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "111")
    POSTGRES_DB: str = os.getenv("DB_NAME", "ofs_photomatrix")
    POSTGRES_PORT: int = int(os.getenv("DB_PORT", "5432"))
    
    # Используем DATABASE_URL из корневого .env файла, если он есть
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    
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
        db_encoding = os.getenv("DB_ENCODING", "utf8")
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
            query={"client_encoding": db_encoding}
        )
    
    # Настройки Email
    EMAILS_ENABLED: bool = False
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    
    # Первый суперпользователь из корневого .env
    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "adminadmin")
    
    # Дополнительная информация о файле .env
    @property
    def env_file_info(self) -> str:
        return f"Используется .env файл: {root_env_path} (существует: {os.path.exists(root_env_path)})"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

# Создание объекта настроек
settings = Settings()
print(f"Загружены настройки из: {settings.env_file_info}") 