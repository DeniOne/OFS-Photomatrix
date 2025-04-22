import asyncio
import sys
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Добавляем текущую директорию в путь импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Создаем экземпляр движка БД
DATABASE_URL = "sqlite+aiosqlite:///app.db"  # Путь к нашей SQLite базе
engine = create_async_engine(DATABASE_URL, echo=True)

async def add_type_column():
    """Добавляет колонку type в таблицу division, если она не существует"""
    async with engine.begin() as conn:
        # Проверяем, существует ли колонка type
        result = await conn.execute(text("PRAGMA table_info(division)"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'type' not in column_names:
            print("Добавление колонки 'type' в таблицу division...")
            await conn.execute(
                text("ALTER TABLE division ADD COLUMN type VARCHAR NOT NULL DEFAULT 'DEPARTMENT'")
            )
            print("Колонка 'type' успешно добавлена!")
        else:
            print("Колонка 'type' уже существует в таблице division")

async def main():
    """Обновляет схему базы данных"""
    # Добавляем колонку type, если она не существует
    await add_type_column()
    
    print("Схема базы данных успешно обновлена!")

if __name__ == "__main__":
    asyncio.run(main()) 