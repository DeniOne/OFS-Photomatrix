from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declared_attr
from typing import AsyncGenerator
import os

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ofs_user:111@localhost:5432/ofs_photomatrix")

# Создание асинхронного движка с настройками для решения проблемы greenlet
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    # Следующие настройки помогают решить проблему с greenlet
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=20,
    future=True,
    # Дополнительные настройки для решения проблем с отсоединенными объектами
    pool_use_lifo=True,  # Использовать LIFO вместо FIFO для пула соединений
    connect_args={"server_settings": {"application_name": "OFS-Photomatrix"}},
)
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
        """Безопасное строковое представление объекта даже при отсоединении от сессии"""
        try:
            # Проверяем, не отсоединен ли объект от сессии
            from sqlalchemy.orm.base import instance_state
            state = instance_state(self)
            if state.detached:
                return f"{self.__class__.__name__}(detached, id={getattr(self, 'id', 'unknown')})"
            
            # Только для объектов, привязанных к сессии
            attrs = []
            for key in self.__mapper__.columns.keys():
                try:
                    # Безопасное получение атрибута без автозагрузки
                    if hasattr(self, key):
                        value = getattr(self, key)
                        attrs.append(f"{key}={value}")
                except Exception:
                    # В случае проблем с атрибутом, просто пропускаем его
                    pass
            return f"{self.__class__.__name__}({', '.join(attrs)})"
        except Exception as e:
            # Если что-то пошло не так, просто вернем имя класса и id объекта
            return f"{self.__class__.__name__}(id={getattr(self, 'id', 'unknown')}, error={str(e)[:30]})"

# Функция для получения сессии БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию БД"""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        # Подробно логируем ошибку, но не включаем объекты, которые могут вызвать проблемы при сериализации
        error_msg = str(e)
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        print(f"Database error: {error_msg}")
        raise
    finally:
        await session.close() 