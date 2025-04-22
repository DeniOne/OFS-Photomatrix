import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash

# Настройка подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/photomatrix")

async def create_admin_user():
    # Создаем движок для асинхронного подключения
    engine = create_async_engine(DATABASE_URL)
    
    # Создаем фабрику сессий
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Создаем админа
    admin_data = {
        "email": "admin@example.com",
        "password": "admin123",  # Пароль будет хешироваться
        "full_name": "Administrator",
        "is_superuser": True,
        "is_active": True,
    }
    
    # Хешируем пароль
    hashed_password = get_password_hash(admin_data["password"])
    
    # Создаем пользователя
    async with async_session() as session:
        # Проверяем, существует ли уже админ
        admin = await session.get(User, 1)
        
        if not admin:
            print("Создаем нового администратора...")
            admin = User(
                email=admin_data["email"],
                hashed_password=hashed_password,
                full_name=admin_data["full_name"],
                is_superuser=admin_data["is_superuser"],
                is_active=admin_data["is_active"],
            )
            session.add(admin)
            await session.commit()
            print(f"Администратор создан! Email: {admin_data['email']}, Пароль: {admin_data['password']}")
        else:
            print(f"Администратор уже существует: {admin.email}")
            # Обновляем пароль если нужно
            admin.hashed_password = hashed_password
            await session.commit()
            print(f"Пароль обновлен: {admin_data['password']}")
    
    # Закрываем соединение
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
    print("Готово!") 