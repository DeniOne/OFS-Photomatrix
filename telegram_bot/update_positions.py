#!/usr/bin/env python
import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = Config()
DATA_DIR = config.STORAGE_PATH
POSITIONS_FILE = os.path.join(DATA_DIR, 'positions.json')
API_POSITIONS_ENDPOINT = config.API_POSITIONS_ENDPOINT
API_KEY = config.API_KEY


async def fetch_positions_from_api() -> List[Dict[str, Any]]:
    """Получает список должностей из API"""
    logger.info(f"Запрос списка должностей из API: {API_POSITIONS_ENDPOINT}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Пробуем разные варианты заголовков
            headers_variants = [
                {"X-API-Key": API_KEY},
                {},  # Без ключа
                {"Api-Key": API_KEY},
                {"Authorization": f"Bearer {API_KEY}"}
            ]
                
            for headers in headers_variants:
                try:
                    logger.info(f"Пробуем запрос с заголовками: {headers}")
                    async with session.get(API_POSITIONS_ENDPOINT, headers=headers) as response:
                        if response.status == 200:
                            positions = await response.json()
                            logger.info(f"Успешно получены должности из API: {len(positions)}")
                            return positions
                        
                        # Если получили ошибку 405 (Method Not Allowed), пробуем POST-запрос
                        elif response.status == 405:
                            logger.info("Получили ошибку 405, пробуем POST-запрос")
                            async with session.post(API_POSITIONS_ENDPOINT, headers=headers) as post_response:
                                if post_response.status == 200:
                                    positions = await post_response.json()
                                    logger.info(f"Успешно получены должности через POST: {len(positions)}")
                                    return positions
                except Exception as e:
                    logger.warning(f"Исключение при запросе с заголовками {headers}: {str(e)}")
                    continue
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {str(e)}")
    
    return []


def load_current_positions() -> List[Dict[str, Any]]:
    """Загружает текущие должности из JSON-файла"""
    try:
        if os.path.exists(POSITIONS_FILE):
            with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                positions = data.get('positions', [])
                logger.info(f"Загружено {len(positions)} должностей из файла")
                return positions
    except Exception as e:
        logger.error(f"Ошибка при чтении файла должностей: {str(e)}")
    
    return []


def save_positions(positions: List[Dict[str, Any]]) -> bool:
    """Сохраняет должности в JSON-файл"""
    # Создаем директорию, если ее нет
    os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
    
    # Формируем структуру данных
    data = {"positions": positions}
    
    try:
        with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Сохранено {len(positions)} должностей в файл {POSITIONS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении должностей: {str(e)}")
        return False


def fetch_positions_from_database() -> List[Dict[str, Any]]:
    """Получает список должностей напрямую из базы данных основной системы"""
    try:
        logger.info("Пробуем подключиться к базе данных...")
        
        # Пытаемся импортировать нужные модули из основной системы
        # sys.path.append(os.path.abspath('../backend')) # Старый вариант
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.abspath(os.path.join(script_dir, '..', 'backend'))
        project_root = os.path.dirname(backend_dir) # Путь к корню проекта
        # Добавляем пути в начало sys.path, чтобы они имели приоритет
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root) # Это позволит делать import app...
        logger.info(f"Добавлены пути в sys.path: {project_root}, {backend_dir}")
        
        # Пробуем разные варианты импорта
        try:
            # Сначала пробуем из основного окружения
            from app.db.session import get_db
            from app.models.position import Position
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy.future import select
            db_import_path = "app.db"
        except ImportError:
            try:
                # Затем из локального окружения бэкенда
                from backend.app.db.session import get_db
                from backend.app.models.position import Position
                from sqlalchemy.ext.asyncio import AsyncSession
                from sqlalchemy.future import select
                db_import_path = "backend.app.db"
            except ImportError:
                logger.error("Не удалось импортировать модули для работы с БД")
                return []
        
        logger.info(f"Успешно импортированы модули из пути {db_import_path}")
        
        # Функция для запуска асинхронного кода в синхронном контексте
        def run_async(coro):
            return asyncio.get_event_loop().run_until_complete(coro)
        
        # Асинхронная функция для получения должностей из БД
        async def get_positions_from_db():
            positions = []
            async for db in get_db():
                try:
                    # Создаем запрос для выборки всех активных должностей
                    stmt = select(Position).where(Position.is_active == True)
                    result = await db.execute(stmt)
                    db_positions = result.scalars().all()
                    
                    # Преобразуем объекты должностей в словари
                    for position in db_positions:
                        positions.append({
                            "id": position.id,
                            "name": position.name,
                            "description": position.description or "",
                            "section_id": position.section_id,
                            "code": position.code
                        })
                    
                    logger.info(f"Получено {len(positions)} должностей из базы данных")
                    return positions
                except Exception as e:
                    logger.error(f"Ошибка при запросе к БД: {str(e)}")
                    break
            return []
        
        # Запускаем асинхронную функцию
        return run_async(get_positions_from_db())
    except Exception as e:
        logger.error(f"Ошибка при доступе к базе данных: {str(e)}")
        return []


async def main():
    # Получаем должности из API
    api_positions = await fetch_positions_from_api()
    
    # Если не удалось получить из API, пробуем из базы данных
    if not api_positions:
        logger.warning("Не удалось получить должности из API, пробуем из базы данных...")
        db_positions = fetch_positions_from_database()
        
        if db_positions:
            logger.info(f"Получено {len(db_positions)} должностей из базы данных")
            api_positions = db_positions
        else:
            logger.error("Не удалось получить должности ни из API, ни из базы данных")
            
            # Загружаем текущие должности
            current_positions = load_current_positions()
            
            if current_positions:
                logger.info(f"Используем текущие {len(current_positions)} должностей из файла")
                print(f"Должности не обновлены. Используется текущий файл с {len(current_positions)} должностями.")
                sys.exit(0)
            else:
                logger.error("Нет доступных должностей")
                print("Ошибка: не удалось получить список должностей")
                sys.exit(1)
    
    # Загружаем текущие должности для сравнения
    current_positions = load_current_positions()
    
    # Сравниваем количество должностей
    if len(api_positions) == len(current_positions):
        logger.info("Количество должностей не изменилось")
    else:
        logger.info(f"Количество должностей изменилось: было {len(current_positions)}, стало {len(api_positions)}")
    
    # Сохраняем новые должности
    if save_positions(api_positions):
        logger.info("Файл positions.json успешно обновлен")
        print(f"Готово! Файл positions.json обновлен ({len(api_positions)} должностей)")
    else:
        logger.error("Не удалось обновить файл positions.json")
        print("Ошибка: не удалось сохранить файл positions.json")
        sys.exit(1)


if __name__ == "__main__":
    print("Обновление файла должностей из API или БД...")
    asyncio.run(main()) 