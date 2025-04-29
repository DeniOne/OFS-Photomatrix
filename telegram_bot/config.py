import os
import logging
from typing import List
from dotenv import load_dotenv

# Загрузка переменных окружения из корневого .env файла
root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(root_env_path)

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

class Config:
    """Класс для доступа к конфигурационным параметрам из корневого .env файла"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        # Токен бота из корневого .env
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not self.BOT_TOKEN:
            logger.error("Не задан токен бота (BOT_TOKEN) в .env файле!")
            raise ValueError("Отсутствует обязательный параметр BOT_TOKEN")
        
        # ID администраторов из корневого .env
        admin_ids = os.getenv("ADMIN_IDS", "")
        logger.info(f"🔑 Загружаем список админов из .env, строка ADMIN_IDS: '{admin_ids}'")
        
        # Поддержка как числовых ID, так и юзернеймов с @
        self.ADMIN_IDS = []
        
        if not admin_ids.strip():
            logger.warning(f"⚠️ Строка ADMIN_IDS в .env пуста или не задана")
        else:
            # Разбиваем строку по запятым
            admin_ids_list = admin_ids.split(",")
            logger.info(f"📋 Список админов после разделения по запятым: {admin_ids_list}")
            
            for admin_id in admin_ids_list:
                admin_id = admin_id.strip()
                if not admin_id:
                    logger.warning(f"⚠️ Пропускаем пустой элемент в списке админов")
                    continue
                
                logger.info(f"🔍 Обрабатываем идентификатор админа: '{admin_id}'")
                
                # Если начинается с @, сохраняем как строку (юзернейм)
                if admin_id.startswith('@'):
                    logger.info(f"👤 Определен юзернейм: '{admin_id}'")
                    self.ADMIN_IDS.append(admin_id)
                # Иначе пробуем преобразовать в число (ID)
                else:
                    try:
                        admin_id_int = int(admin_id)
                        logger.info(f"🔢 Преобразован в число: {admin_id} -> {admin_id_int}")
                        self.ADMIN_IDS.append(admin_id_int)
                    except ValueError:
                        # Если не получается, сохраняем как строку
                        logger.warning(f"⚠️ Не удалось преобразовать '{admin_id}' в число, сохраняем как строку")
                        self.ADMIN_IDS.append(admin_id)
        
        # Логирование загруженных админов
        logger.info(f"✅ Загружены администраторы: {self.ADMIN_IDS}")
        logger.info(f"📊 Типы данных в списке админов: {[f'{x} ({type(x)})' for x in self.ADMIN_IDS]}")
        
        # Настройки логирования из корневого .env
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "bot.log")
        
        # Настройки Redis для хранения состояний из корневого .env
        self.USE_REDIS = os.getenv("USE_REDIS", "False").lower() == "true"
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # URL API основной системы из корневого .env
        self.API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
        
        # Эндпоинты берем напрямую из переменных окружения или формируем из базового URL
        self.API_WEBHOOK_ENDPOINT = os.getenv("API_WEBHOOK_ENDPOINT", f"{self.API_URL}/telegram-bot/webhook")
        self.API_TOKEN_VALIDATION_ENDPOINT = os.getenv("API_TOKEN_VALIDATION_ENDPOINT", f"{self.API_URL}/telegram-bot/validate-token")
        self.API_ORGANIZATIONS_ENDPOINT = os.getenv("API_ORGANIZATIONS_ENDPOINT", f"{self.API_URL}/organizations")
        
        # Добавляем эндпоинты для работы с позициями и отделами
        self.API_POSITIONS_ENDPOINT = os.getenv("API_POSITIONS_ENDPOINT", f"{self.API_URL}/positions")
        self.API_DIVISIONS_ENDPOINT = os.getenv("API_DIVISIONS_ENDPOINT", f"{self.API_URL}/divisions")
        self.API_SECTIONS_ENDPOINT = os.getenv("API_SECTIONS_ENDPOINT", f"{self.API_URL}/sections")
        self.API_STAFF_ENDPOINT = os.getenv("API_STAFF_ENDPOINT", f"{self.API_URL}/staff")
        
        # API ключ для авторизации запросов из корневого .env
        self.API_KEY = os.getenv("API_KEY", "")
        
        # Дополнительные проверки и логирование
        if not self.API_URL.startswith("http"):
            logger.warning(f"Некорректный URL API: {self.API_URL}, добавляем http://")
            self.API_URL = f"http://{self.API_URL}"
        
        # Проверка доступности портов
        if "localhost" in self.API_URL or "127.0.0.1" in self.API_URL:
            logger.info(f"Используется локальный API на: {self.API_URL}")
            # Проверяем другие возможные порты, если исходный URL недоступен
            parsed_url = self.API_URL.split(':')
            if len(parsed_url) >= 3:
                base_part = ':'.join(parsed_url[:-1])
                port_part = parsed_url[-1].split('/')[0]
                try:
                    port = int(port_part)
                    # Запоминаем альтернативные URL для возможного использования
                    self.API_URL_ALTERNATIVES = [
                        f"{base_part}:{port}/api/v1",
                        f"{base_part}:{port+1}/api/v1",
                        f"{base_part}:{port-1}/api/v1"
                    ]
                    logger.info(f"Альтернативные порты API: {self.API_URL_ALTERNATIVES}")
                except ValueError:
                    logger.warning(f"Не удалось определить порт из URL: {self.API_URL}")
        
        # Информация о файле .env
        logger.info(f"Используется .env файл: {root_env_path} (существует: {os.path.exists(root_env_path)})")
        
        # Настройки безопасности из корневого .env
        self.MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
        self.MAX_REGISTRATION_ATTEMPTS = int(os.getenv("MAX_REGISTRATION_ATTEMPTS", "3"))
        
        # Убедимся, что директория для логов существует
        self._ensure_log_directory()
        
        logger.info("Конфигурация загружена успешно")
        logger.info(f"URL API: {self.API_URL}")
        logger.info(f"Endpoint позиций: {self.API_POSITIONS_ENDPOINT}")
        logger.info(f"API ключ: {'Установлен' if self.API_KEY else 'Не установлен'}")
    
    def _ensure_log_directory(self):
        """Создает директорию для логов, если она не существует"""
        # Если лог-файл не содержит путь директории, считаем что файл создается в корневой директории
        if os.path.dirname(self.LOG_FILE) == '':
            logger.info(f"Лог-файл будет создан в текущей директории: {self.LOG_FILE}")
            return
            
        # Иначе создаем нужную директорию
        log_dir = os.path.dirname(self.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            logger.info(f"Создана директория для логов: {log_dir}")
    
    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        logger.info(f"🛡️ Проверка прав админа в Config: user_id={user_id} (тип: {type(user_id)})")
        logger.info(f"📊 Список админов в конфиге: {self.ADMIN_IDS}")
        logger.info(f"📊 Типы данных в списке админов: {[f'{x} ({type(x)})' for x in self.ADMIN_IDS]}")
        
        # Проверяем прямое совпадение
        direct_match = user_id in self.ADMIN_IDS
        logger.info(f"🔍 Прямое совпадение ID: {direct_match}")
        
        # Если прямое совпадение не найдено, проверяем как строку
        if not direct_match:
            str_id = str(user_id)
            str_match = str_id in self.ADMIN_IDS
            logger.info(f"🔢 Преобразовали ID в строку: {user_id} -> '{str_id}', результат проверки: {str_match}")
            return str_match
        
        logger.info(f"✅ Результат проверки админа в Config: {direct_match}")
        return direct_match

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8" 