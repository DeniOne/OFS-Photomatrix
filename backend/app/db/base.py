from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from typing import AsyncGenerator
import os

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ofs_user:111@localhost:5432/ofs_photomatrix")

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для всех моделей
Base = declarative_base()

# Общие поля и методы для всех моделей
class BaseModel:
    """Базовый класс для всех моделей с общими атрибутами и методами"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Автоматически генерирует имя таблицы из имени класса"""
        return cls.__name__.lower()
    
    def __repr__(self):
        """Строковое представление объекта"""
        attrs = ", ".join(f"{key}={getattr(self, key)}" for key in self.__mapper__.columns.keys())
        return f"{self.__class__.__name__}({attrs})"

# Функция для получения сессии БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию БД"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() 