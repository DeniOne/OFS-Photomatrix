import asyncio
import json
import os
import sys

# Добавляем корневую директорию проекта в путь импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)  # Добавляем текущую директорию backend

# Импортируем из локальных модулей
from app.db.base import async_session_maker
from app.models.position import Position
from sqlalchemy import select

# Путь для сохранения JSON файла в формате telegram_bot/data/positions.json
OUTPUT_FILE = os.path.join(os.path.dirname(current_dir), 'telegram_bot', 'data', 'positions.json')

async def export_positions():
    """Экспортирует должности из БД в JSON файл"""
    print(f"Начинаю экспорт должностей в файл {OUTPUT_FILE}...")
    
    # Создаем сессию базы данных
    async with async_session_maker() as db:
        # Получаем все активные должности из БД
        query = select(Position).where(Position.is_active == True)
        result = await db.execute(query)
        positions = result.scalars().all()
        
        # Форматируем данные для JSON
        positions_data = {
            "positions": [
                {
                    "id": position.id,
                    "name": position.name,
                    "description": position.description or f"Должность {position.name}"
                }
                for position in positions
            ]
        }
        
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Сохраняем данные в JSON файл с правильной кодировкой и отступами
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(positions_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Экспорт завершен! Экспортировано {len(positions_data['positions'])} должностей.")
        print(f"Файл сохранен: {OUTPUT_FILE}")

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(export_positions()) 