import os
import logging
import psycopg2
import asyncio
import asyncpg
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получение данных подключения из переменных окружения
from dotenv import load_dotenv
# Загружаем .env из корневой директории
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

DB_USER = os.getenv("DB_USER", "ofs_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "111")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ofs_photomatrix")

# Глобальный кеш для данных
_divisions_cache = None
_sections_cache = None
_positions_cache = None

async def get_db_connection():
    """Устанавливает асинхронное соединение с БД"""
    try:
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        logger.info(f"✅ Успешное подключение к БД: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return conn
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        return None

async def check_table_exists(conn, table_name):
    """Проверяет существование таблицы в БД"""
    try:
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            )
        """
        exists = await conn.fetchval(query, table_name)
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке таблицы {table_name}: {e}")
        return False

async def get_divisions_from_db() -> List[Dict[str, Any]]:
    """Получает отделы из БД"""
    global _divisions_cache
    
    # Если данные уже в кеше, возвращаем их
    if _divisions_cache is not None:
        return _divisions_cache
    
    conn = await get_db_connection()
    if not conn:
        logger.warning("⚠️ Не удалось подключиться к БД при получении отделов")
        return []
    
    try:
        # Проверяем существование таблицы
        if not await check_table_exists(conn, 'divisions'):
            logger.warning("⚠️ Таблица 'divisions' не существует в БД")
            return []
            
        query = """
            SELECT id, name, code, is_active
            FROM divisions
            WHERE is_active = true
            ORDER BY name
        """
        rows = await conn.fetch(query)
        
        divisions = [dict(row) for row in rows]
        _divisions_cache = divisions
        
        logger.info(f"✅ Получено {len(divisions)} отделов из БД")
        return divisions
    
    except Exception as e:
        logger.error(f"❌ Ошибка при получении отделов из БД: {e}")
        return []
    
    finally:
        await conn.close()

async def get_sections_from_db() -> List[Dict[str, Any]]:
    """Получает секции из БД"""
    global _sections_cache
    
    # Если данные уже в кеше, возвращаем их
    if _sections_cache is not None:
        return _sections_cache
    
    conn = await get_db_connection()
    if not conn:
        logger.warning("⚠️ Не удалось подключиться к БД при получении секций")
        return []
    
    try:
        # Проверяем существование таблицы
        if not await check_table_exists(conn, 'sections'):
            logger.warning("⚠️ Таблица 'sections' не существует в БД")
            return []
            
        query = """
            SELECT id, name, code, division_id, is_active
            FROM sections
            WHERE is_active = true
            ORDER BY name
        """
        rows = await conn.fetch(query)
        
        sections = [dict(row) for row in rows]
        _sections_cache = sections
        
        logger.info(f"✅ Получено {len(sections)} секций из БД")
        return sections
    
    except Exception as e:
        logger.error(f"❌ Ошибка при получении секций из БД: {e}")
        return []
    
    finally:
        await conn.close()

async def get_positions_from_db() -> List[Dict[str, Any]]:
    """Получает должности из БД"""
    global _positions_cache
    
    # Если данные уже в кеше, возвращаем их
    if _positions_cache is not None:
        return _positions_cache
    
    conn = await get_db_connection()
    if not conn:
        logger.warning("⚠️ Не удалось подключиться к БД при получении должностей")
        return []
    
    try:
        # Проверяем существование таблицы
        if not await check_table_exists(conn, 'positions'):
            logger.warning("⚠️ Таблица 'positions' не существует в БД")
            return []
            
        query = """
            SELECT id, name, code, division_id, section_id, is_active
            FROM positions
            WHERE is_active = true
            ORDER BY name
        """
        rows = await conn.fetch(query)
        
        positions = [dict(row) for row in rows]
        _positions_cache = positions
        
        logger.info(f"✅ Получено {len(positions)} должностей из БД")
        return positions
    
    except Exception as e:
        logger.error(f"❌ Ошибка при получении должностей из БД: {e}")
        return []
    
    finally:
        await conn.close()

def clear_cache():
    """Очищает кеш данных"""
    global _divisions_cache, _sections_cache, _positions_cache
    _divisions_cache = None
    _sections_cache = None
    _positions_cache = None
    logger.info("Кеш данных очищен")

async def sync_all_data() -> bool:
    """Обновляет кеш данных из БД"""
    logger.info("🔄 Начинаю обновление кеша данных из БД...")
    
    # Очищаем кеш
    clear_cache()
    
    # Получаем данные в кеш
    divisions = await get_divisions_from_db()
    sections = await get_sections_from_db()
    positions = await get_positions_from_db()
    
    if divisions or sections or positions:
        logger.info(f"✅ Кеш обновлен: {len(divisions)} отделов, {len(sections)} секций, {len(positions)} должностей")
        return True
    else:
        logger.warning("⚠️ Не удалось получить данные из БД для обновления кеша")
        return False

# Функции для совместимости с предыдущей версией кода
sync_divisions_from_db = get_divisions_from_db
sync_sections_from_db = get_sections_from_db
sync_positions_from_db = get_positions_from_db

# Для запуска из командной строки
if __name__ == "__main__":
    asyncio.run(sync_all_data()) 