import asyncio
import json
import os
import sys

# Добавляем корневую директорию проекта в путь импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)  # Добавляем текущую директорию backend

# Импортируем из локальных модулей
from app.db.base import async_session_maker
from app.models.division import Division
from sqlalchemy import select

# Путь для сохранения JSON файла в формате telegram_bot/data/divisions.json
OUTPUT_FILE = os.path.join(os.path.dirname(current_dir), 'telegram_bot', 'data', 'divisions.json')

async def export_divisions():
    """Экспортирует департаменты/подразделения из БД в JSON файл"""
    print(f"Начинаю экспорт департаментов в файл {OUTPUT_FILE}...")
    
    # Создаем сессию базы данных
    async with async_session_maker() as db:
        # Получаем все активные департаменты из БД
        query = select(Division).where(Division.is_active == True)
        result = await db.execute(query)
        divisions = result.scalars().all()
        
        # Форматируем данные для JSON
        divisions_data = {
            "divisions": [
                {
                    "id": division.id,
                    "name": division.name,
                    "description": division.description or f"Департамент {division.name}"
                }
                for division in divisions
            ]
        }
        
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Сохраняем данные в JSON файл с правильной кодировкой и отступами
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(divisions_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Экспорт завершен! Экспортировано {len(divisions_data['divisions'])} департаментов.")
        print(f"Файл сохранен: {OUTPUT_FILE}")

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(export_divisions()) 