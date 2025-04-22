import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Создаем директорию для логов, если ее нет
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Формат вывода логов
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Настройка файлов логов
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
DB_LOG_FILE = os.path.join(LOG_DIR, "db.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
API_LOG_FILE = os.path.join(LOG_DIR, "api.log")
AUTH_LOG_FILE = os.path.join(LOG_DIR, "auth.log")

# Инициализация логгеров
logger = logging.getLogger("app")
api_logger = logging.getLogger("app.api")
auth_logger = logging.getLogger("app.auth")
db_logger = logging.getLogger("app.db")

# Флаг для отслеживания инициализации
_logging_initialized = False

def setup_logging():
    """
    Настраивает логирование для приложения
    """
    global _logging_initialized
    
    # Избегаем повторной инициализации
    if _logging_initialized:
        return logger
        
    # Базовая настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Очищаем обработчики, если они были добавлены ранее
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Форматтеры
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    detailed_formatter = logging.Formatter(DETAILED_FORMAT, DATE_FORMAT)

    # Настройка вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Настройка файла логов приложения с ротацией
    try:
        app_file_handler = RotatingFileHandler(
            APP_LOG_FILE, 
            maxBytes=10 * 1024 * 1024,  # 10 МБ
            backupCount=5
        )
        app_file_handler.setLevel(logging.INFO)
        app_file_handler.setFormatter(formatter)
        logger.addHandler(app_file_handler)
        
        # Настройка логгера для ошибок
        error_file_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 МБ
            backupCount=10  # Больше резервных копий для ошибок
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_file_handler)
        
        # Настройка логгера для API запросов
        api_file_handler = RotatingFileHandler(
            API_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 МБ
            backupCount=5
        )
        api_file_handler.setLevel(logging.DEBUG)
        api_file_handler.setFormatter(detailed_formatter)
        api_logger.addHandler(api_file_handler)
        
        # Настройка логгера для аутентификации
        auth_file_handler = RotatingFileHandler(
            AUTH_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 МБ
            backupCount=5
        )
        auth_file_handler.setLevel(logging.DEBUG)
        auth_file_handler.setFormatter(detailed_formatter)
        auth_logger.addHandler(auth_file_handler)
        
        # Настройка логгера для SQLAlchemy (база данных)
        db_logger_sqlalchemy = logging.getLogger("sqlalchemy.engine")
        db_file_handler = RotatingFileHandler(
            DB_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 МБ
            backupCount=5
        )
        db_file_handler.setLevel(logging.INFO)
        db_file_handler.setFormatter(formatter)
        db_logger_sqlalchemy.addHandler(db_file_handler)
        
    except Exception as e:
        # В случае ошибки с файлами логирования - выводим только в консоль
        console_handler.setLevel(logging.DEBUG)
        root_logger.error(f"Ошибка при настройке файловых обработчиков логов: {str(e)}")
    
    # Логирование сообщения о запуске
    root_logger.info("="*50)
    root_logger.info(f"Запуск логирования: {datetime.now().strftime(DATE_FORMAT)}")
    root_logger.info("="*50)
    
    _logging_initialized = True
    return logger 