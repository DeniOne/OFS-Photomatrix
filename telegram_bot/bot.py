import os
import logging
import asyncio
import json
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties

from database import BotDatabase
from config import Config

print("Начинаю инициализацию бота...")

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()  # Добавляем вывод в консоль
    ]
)
logger = logging.getLogger(__name__)
print("Логирование настроено")

# Загрузка конфигурации (теперь из корневого .env файла)
config = Config()
print(f"Настройки бота загружены. Токен: {config.BOT_TOKEN[:5]}...")
logger.info(f"Настройки бота загружены успешно. Токен: {config.BOT_TOKEN[:5]}...")

# Инициализация базы данных
db = BotDatabase()
print("База данных инициализирована")

# Функция для отправки данных в основную систему
async def send_data_to_main_system(employee_data: dict) -> bool:
    """
    Отправляет данные о сотруднике в основную систему через API
    
    Args:
        employee_data: Словарь с данными сотрудника
    
    Returns:
        bool: True если данные успешно отправлены, False в противном случае
    """
    try:
        endpoint = config.API_WEBHOOK_ENDPOINT
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=employee_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Данные успешно отправлены в основную систему: {result}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при отправке данных: {response.status} - {error_text}")
                    return False
    except Exception as e:
        logger.error(f"Исключение при отправке данных: {str(e)}")
        return False

# Обновление функции подтверждения данных в handlers.py
async def confirm_employee_data_and_send(user_id: int, state: FSMContext):
    """
    Сохраняет данные сотрудника и отправляет их в основную систему
    
    Args:
        user_id: ID пользователя в Telegram
        state: Текущее состояние FSM
    
    Returns:
        bool: True если данные успешно сохранены и отправлены, False в противном случае
    """
    # Получаем данные из состояния
    data = await state.get_data()
    
    # Сохраняем данные в локальную базу
    db.add_employee(
        name=data.get("name", ""),
        position=data.get("position", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        telegram_id=data.get("telegram_id", ""),
        photo_id=data.get("photo_id", ""),
        competencies=data.get("competencies", [])
    )
    
    # Отправляем данные в основную систему
    success = await send_data_to_main_system(data)
    
    return success

async def start_bot():
    """Запускает бота."""
    print("Вызвана функция start_bot()")
    try:
        # Инициализация бота (более совместимый способ)
        bot = Bot(token=config.BOT_TOKEN)
        
        # Настраиваем default_parse_mode через DefaultBotProperties
        bot.default = DefaultBotProperties(parse_mode="HTML")
        
        # Выбор хранилища состояний
        storage = MemoryStorage()
        logger.info("Используется MemoryStorage для хранения состояний")
        
        # Инициализация диспетчера
        dp = Dispatcher(storage=storage)
        
        # Импортируем и регистрируем обработчики здесь, чтобы избежать циклических импортов
        from registration_handlers import register_registration_handlers
        from admin_handlers import register_admin_handlers
        from handlers import register_handlers
        
        # Регистрация обработчиков
        register_registration_handlers(dp)
        register_admin_handlers(dp)
        
        # Передаем функцию подтверждения в register_handlers
        register_handlers(dp, confirm_employee_data_and_send)
        
        # Удаляем webhook перед запуском
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Вывод информации о запуске
        bot_info = await bot.get_me()
        logger.info(f"Бот {bot_info.full_name} (@{bot_info.username}) запущен!")
        logger.info(f"ID бота: {bot_info.id}")
        
        # Информация о конфигурации
        logger.info(f"API URL: {config.API_URL}")
        logger.info(f"Путь к хранилищу данных: {config.STORAGE_PATH}")
        logger.info(f"Загруженные админы: {config.ADMIN_IDS}")
        
        # Загружаем данные из БД при запуске
        try:
            from sync_db import sync_all_data
            logger.info("Синхронизируем данные из БД...")
            if sync_all_data():
                logger.info("✅ Данные успешно синхронизированы!")
            else:
                logger.warning("⚠️ Синхронизация данных не выполнена или выполнена с ошибками")
        except Exception as e:
            logger.error(f"❌ Ошибка при синхронизации данных: {str(e)}")
        
        # Запуск поллинга
        logger.info("Запускаем поллинг...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}", exc_info=True)
    finally:
        logger.info("Работа бота завершена")

if __name__ == "__main__":
    try:
        # Проверка наличия корневого .env файла
        root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if not os.path.exists(root_env_path):
            print(f"Корневой .env файл не найден: {root_env_path}")
            logger.warning(f"Корневой .env файл не найден: {root_env_path}")
            logger.warning("Будут использованы настройки по умолчанию. Рекомендуется создать .env файл.")
        else:
            print(f"Используется корневой .env файл: {root_env_path}")
            logger.info(f"Используется корневой .env файл: {root_env_path}")
        
        # Запуск бота
        print("Запускаю бота...")
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True) 