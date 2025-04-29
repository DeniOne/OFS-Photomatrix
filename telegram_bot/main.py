import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from config import Config
from admin_handlers import register_admin_handlers
from registration_handlers import register_registration_handlers
from database import BotDatabase

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

# Инициализация конфигурации
config = Config()

async def main():
    """Основная функция запуска бота"""
    logger.info("Запуск бота для регистрации сотрудников OFS Global")
    
    # Синхронизируем данные из БД перед запуском бота
    try:
        # Исправляем импорт - без префикса telegram_bot, так как мы уже в этой директории
        from sync_db import sync_all_data, sync_divisions_from_db, sync_sections_from_db, sync_positions_from_db
        
        logger.info("Начинаю синхронизацию всех данных из БД...")
        if sync_all_data():
            logger.info("✅ Все данные успешно синхронизированы из БД")
        else:
            logger.warning("⚠️ Не удалось синхронизировать все данные из БД")
    except Exception as e:
        logger.error(f"❌ Ошибка при попытке синхронизации данных: {str(e)}")
        logger.exception("Подробная информация об ошибке:")
    
    # Проверяем, есть ли токен бота
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в .env файле")
        sys.exit(1)
    
    # Инициализация базы данных
    db = BotDatabase()
    
    # Инициализация хранилища состояний
    if config.USE_REDIS:
        # Используем Redis для хранения состояний, если настроено
        storage = RedisStorage.from_url(config.REDIS_URL)
        logger.info("Используется Redis для хранения состояний")
    else:
        # Используем память для хранения состояний
        storage = MemoryStorage()
        logger.info("Используется MemoryStorage для хранения состояний")

    # Инициализация бота и диспетчера - совместимо с aiogram 3.x
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    # Регистрация обработчиков
    register_admin_handlers(dp)
    register_registration_handlers(dp)
    
    # Удаляем все обновления, накопившиеся за время остановки бота
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Установка команд бота
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="admin", description="Панель администратора"),
        BotCommand(command="cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)
    
    # Запуск поллинга
    logger.info("Бот запущен и ожидает сообщений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}")
        sys.exit(1) 