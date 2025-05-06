import asyncio
import os
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Используем URL из переменной окружения или дефолтное значение
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://ofs_user:111@localhost:5432/ofs_photomatrix")

async def check_db():
    print(f"Подключаемся к БД: {DATABASE_URL}")
    
    # Создаем асинхронный движок
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Включаем логирование SQL
        future=True
    )
    
    # Создаем фабрику сессий
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            print("\n--- Проверка соединения с БД ---")
            result = await session.execute(text("SELECT 1"))
            print(f"Результат проверки: {result.scalar()}")
            
            print("\n--- Список таблиц в базе данных ---")
            tables = await session.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = tables.fetchall()
            if tables:
                for table in tables:
                    print(f"Таблица: {table[0]}")
            else:
                print("Таблиц нет")
            
            print("\n--- Проверка таблицы organizations ---")
            try:
                orgs = await session.execute(text("SELECT COUNT(*) FROM organization"))
                count = orgs.scalar()
                print(f"Количество организаций: {count}")
                
                if count > 0:
                    # Если есть данные, покажем первую запись
                    org_data = await session.execute(text("SELECT id, name, code FROM organization LIMIT 1"))
                    org = org_data.fetchone()
                    print(f"Пример организации: ID={org[0]}, Название={org[1]}, Код={org[2]}")
            except Exception as e:
                print(f"Ошибка при проверке таблицы organizations: {e}")
            
    except Exception as e:
        print(f"Ошибка при подключении к БД: {e}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db()) 