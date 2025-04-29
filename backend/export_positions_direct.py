#!/usr/bin/env python
import os
import json
import asyncio
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# База данных
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "ofs_photomatrix")

# Путь к файлу должностей
TELEGRAM_BOT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telegram_bot', 'data')
POSITIONS_FILE = os.path.join(TELEGRAM_BOT_DATA_DIR, 'positions.json')


def get_connection():
    """Подключение к базе данных"""
    try:
        # Добавляем options для решения проблем с кодировкой
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        return connection
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise


def get_positions_hardcoded() -> List[Dict[str, Any]]:
    """Жестко закодированные должности для аварийного случая"""
    return [
        {"id": 1, "name": "Генеральный директор", "description": "Руководитель компании"},
        {"id": 2, "name": "Финансовый директор", "description": "Руководитель финансового отдела"},
        {"id": 3, "name": "Технический директор", "description": "Руководитель технического отдела"},
        {"id": 4, "name": "Менеджер проектов", "description": "Управление проектами"},
        {"id": 5, "name": "Старший разработчик", "description": "Разработка и архитектура"},
        {"id": 6, "name": "Разработчик", "description": "Программист"},
        {"id": 7, "name": "Тестировщик", "description": "QA инженер"},
        {"id": 8, "name": "Дизайнер", "description": "UI/UX дизайнер"},
        {"id": 9, "name": "Маркетолог", "description": "Специалист по маркетингу"},
        {"id": 10, "name": "HR-менеджер", "description": "Управление персоналом"},
        {"id": 11, "name": "DevOps инженер", "description": "Настройка и поддержка инфраструктуры"},
        {"id": 12, "name": "QA инженер", "description": "Тестирование и обеспечение качества"},
        {"id": 13, "name": "Менеджер проекта", "description": "Управление проектом и командой"},
        {"id": 14, "name": "Системный администратор", "description": "Администрирование систем"},
        {"id": 15, "name": "Аналитик данных", "description": "Анализ и визуализация данных"},
        {"id": 16, "name": "Бизнес-аналитик", "description": "Анализ бизнес-процессов"},
        {"id": 17, "name": "Руководитель отдела разработки", "description": "Управление отделом разработки"},
        {"id": 18, "name": "Frontend-разработчик", "description": "Разработка пользовательских интерфейсов"},
        {"id": 19, "name": "Backend-разработчик", "description": "Разработка серверной части"},
        {"id": 20, "name": "Fullstack-разработчик", "description": "Полный стек разработки"}
    ]


def get_positions() -> List[Dict[str, Any]]:
    """Получение списка должностей из БД"""
    positions = []
    
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Явно устанавливаем кодировку для сессии
            try:
                cursor.execute("SET client_encoding = 'UTF8'")
                logger.info("Установлена кодировка сессии client_encoding = UTF8")
            except Exception as e:
                logger.warning(f"Не удалось установить client_encoding для сессии: {e}")
                # Продолжаем выполнение в любом случае
            
            # Запрос на получение всех активных должностей
            cursor.execute("""
                SELECT id, name, description, code
                FROM position
                WHERE is_active = TRUE
                ORDER BY name
            """)
            
            # Читаем строки по одной, чтобы локализовать ошибку
            processed_ids = set() # Для отслеживания уже обработанных ID
            while True:
                row_data = None # Сюда сохраним данные перед ошибкой
                try:
                    row = cursor.fetchone()
                    if row is None:
                        break # Строки закончились
                    
                    row_data = dict(row) # Попытка декодирования происходит здесь
                    row_id = row_data['id']
                    processed_ids.add(row_id)
                    logger.info(f"Успешно прочитана строка ID: {row_id}, Name: {row_data['name'][:30]}...") # Лог прочитанной строки
                    positions.append(row_data) # Добавляем в результат, если все ок
                except UnicodeDecodeError as ude:
                    logger.error(f"Ошибка UnicodeDecodeError после ID {list(processed_ids)[-1] if processed_ids else 'N/A'}: {ude}")
                    if row: # Если сама строка прочиталась, но упала при конвертации в dict
                        logger.warning(f"Проблемная строка (сырые данные курсора): {row}")
                        # Попробуем декодировать вручную с игнорированием
                        try:
                            decoded_row = {}
                            for key, value in row.items():
                                if isinstance(value, bytes):
                                    # Пробуем самые распространенные кодировки для кириллицы
                                    try:
                                        decoded_value = value.decode('utf-8')
                                    except UnicodeDecodeError:
                                        try:
                                            decoded_value = value.decode('cp1251')
                                        except UnicodeDecodeError:
                                            decoded_value = value.decode('utf-8', errors='replace') # Заменяем ошибки
                                else:
                                    decoded_value = value
                                decoded_row[key] = decoded_value
                            
                            row_id = decoded_row.get('id', 'ERROR_ID')
                            logger.warning(f"Строка ID {row_id} декодирована с заменой ошибок: {decoded_row}")
                            positions.append(decoded_row) # Добавляем частично декодированную строку
                            processed_ids.add(row_id)
                        except Exception as inner_e:
                            logger.error(f"Не удалось даже частично декодировать строку: {inner_e}")
                    else:
                        logger.error("Ошибка произошла при самом fetchone()")
                    # Не будем падать, продолжим со следующей строки
                    # raise # Убираем перевыброс ошибки
                except Exception as e:
                    # Другие ошибки все еще могут быть фатальными
                    logger.error(f"Неизвестная ошибка при обработке строки после ID {list(processed_ids)[-1] if processed_ids else 'N/A'}: {e}")
                    raise # Перевыбрасываем неизвестные ошибки
            
            logger.info(f"Обработано {len(positions)} должностей из БД (возможно, с ошибками декодирования)")
        
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка при получении должностей: {e}")
        
        # В случае ошибки используем жестко закодированные должности
        logger.info("Используем жестко закодированные должности")
        positions = get_positions_hardcoded()
    
    return positions


def save_positions(positions: List[Dict[str, Any]]) -> bool:
    """Сохранение должностей в JSON-файл"""
    try:
        # Создаем директорию, если не существует
        os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
        
        # Очищаем и форматируем данные
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                "id": pos["id"],
                "name": pos["name"],
                "description": pos.get("description") or f"Должность: {pos['name']}"
            })
        
        # Сохраняем в JSON-файл
        with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"positions": formatted_positions}, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Должности сохранены в файл {POSITIONS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении должностей: {e}")
        return False


if __name__ == "__main__":
    print("Прямой экспорт должностей из БД в JSON...")
    print(f"Целевой файл: {POSITIONS_FILE}")
    
    try:
        # Получаем должности из БД
        positions = get_positions()
        
        if not positions:
            print("Ошибка: не удалось получить должности из БД или использовать жестко закодированные")
            exit(1)
        
        print(f"Получено {len(positions)} должностей")
        
        # Сохраняем в JSON-файл
        if save_positions(positions):
            print(f"✅ Готово! {len(positions)} должностей сохранено в файл.")
        else:
            print("❌ Ошибка при сохранении файла.")
            exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        exit(1) 