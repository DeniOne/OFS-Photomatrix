#!/usr/bin/env python
import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any

# Добавляем текущую директорию и родительскую директорию в путь поиска
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройки экспорта
TELEGRAM_BOT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_bot', 'data')
POSITIONS_FILE = os.path.join(TELEGRAM_BOT_DATA_DIR, 'positions.json')

# Проверка существования директории бота
if not os.path.exists(TELEGRAM_BOT_DATA_DIR):
    os.makedirs(TELEGRAM_BOT_DATA_DIR, exist_ok=True)
    logger.info(f"Создана директория для данных бота: {TELEGRAM_BOT_DATA_DIR}")

# Импорт моделей и подключения к БД
try:
    # Пробуем несколько вариантов импорта
    try:
        # Сначала пробуем напрямую
        from app.db.session import async_session
        from app.models.position import Position
        from sqlalchemy import select
        logger.info("Импортированы модули из app.db")
    except ImportError:
        try:
            # Затем пробуем с префиксом backend
            from backend.app.db.session import async_session
            from backend.app.models.position import Position
            from sqlalchemy import select
            logger.info("Импортированы модули из backend.app.db")
        except ImportError:
            # Затем пробуем из текущей директории
            sys.path.insert(0, os.path.join(current_dir, 'app'))
            from db.session import async_session
            from models.position import Position
            from sqlalchemy import select
            logger.info("Импортированы модули из текущей директории")
except Exception as e:
    logger.error(f"Не удалось импортировать модули для работы с БД: {str(e)}")
    sys.exit(1)


async def export_positions_to_json() -> bool:
    """Экспортирует должности из БД в JSON-файл для телеграм-бота"""
    
    # Получаем должности из БД
    positions = []
    try:
        async with async_session() as db:
            # Создаем запрос для выборки всех активных должностей
            query = select(Position).where(Position.is_active == True)
            result = await db.execute(query)
            db_positions = result.scalars().all()
            
            logger.info(f"Найдено {len(db_positions)} активных должностей в базе данных")
            
            # Преобразуем объекты должностей в словари
            positions = [
                {
                    "id": position.id, 
                    "name": position.name,
                    "description": position.description or f"Должность: {position.name}" 
                }
                for position in db_positions
            ]
    except Exception as e:
        logger.error(f"Ошибка при получении должностей из БД: {str(e)}")
        return False
    
    if not positions:
        logger.warning("Не найдено активных должностей в базе данных")
        return False
    
    # Создаем директорию для данных бота, если она не существует
    os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
    
    # Сохраняем должности в JSON-файл
    try:
        # Формируем структуру данных
        data = {"positions": positions}
        
        with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Экспортировано {len(positions)} должностей в файл {POSITIONS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении должностей в файл: {str(e)}")
        return False


if __name__ == "__main__":
    print("Экспорт должностей из базы данных в JSON для телеграм-бота...")
    
    # Информация о путях
    print(f"Текущая директория: {os.getcwd()}")
    print(f"Путь к данным бота: {TELEGRAM_BOT_DATA_DIR}")
    print(f"Путь к файлу: {POSITIONS_FILE}")
    
    # Выполняем экспорт
    result = asyncio.run(export_positions_to_json())
    
    if result:
        print("Готово! Файл успешно создан.")
    else:
        print("Ошибка при экспорте должностей.")
        sys.exit(1) 