import asyncio
import logging
import sys

print("1. Скрипт запущен")
print(f"2. Используемый Python: {sys.executable}")
print(f"3. Версия Python: {sys.version}")

try:
    print("4. Пытаюсь импортировать aiogram...")
    from aiogram import Bot, Dispatcher, types
    print("5. Импорт aiogram успешен!")
    
    print("6. Пытаюсь импортировать dotenv...")
    from dotenv import load_dotenv
    print("7. Импорт dotenv успешен!")
    
    print("8. Запуск завершен успешно!")

    # Настройка логирования в консоль и файл
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log", mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    print("9. Логирование настроено")

    # Загрузка переменных окружения
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
    TOKEN = os.getenv("BOT_TOKEN")
    print(f"10. Токен бота загружен: {TOKEN[:5]}..." if TOKEN else "10. Токен бота не найден!")

    if not TOKEN:
        logger.error("BOT_TOKEN отсутствует в переменных окружения!")
        exit(1)

    print("11. Создаю бота и диспетчера")
    # Создание бота и диспетчера (без DefaultBotProperties)
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    print("12. Бот и диспетчер созданы")

    # Обработчик команды /start
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        print(f"Получена команда start от {message.from_user.id}")
        await message.answer(f"Привет, {message.from_user.first_name}! Это тестовый бот.")
        logger.info(f"Пользователь {message.from_user.id} отправил команду /start")

    # Обработчик текстовых сообщений
    @dp.message()
    async def echo(message: types.Message):
        print(f"Получено сообщение от {message.from_user.id}: {message.text}")
        await message.answer(f"Вы отправили: {message.text}")
        logger.info(f"Пользователь {message.from_user.id} отправил сообщение: {message.text}")

    async def main():
        # Запуск бота
        print("13. Вошли в main()")
        logger.info("Бот запускается...")
        try:
            print("14. Запускаю polling...")
            await dp.start_polling(bot)
            print("15. Polling завершен")
        except Exception as e:
            print(f"Ошибка при запуске бота: {e}")
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            print("16. Освобождаю ресурсы")
            logger.info("Бот остановлен")

    if __name__ == "__main__":
        print("17. Входим в точку входа")
        try:
            # Запускаем бота
            print("18. Запускаем asyncio.run(main())")
            asyncio.run(main())
            print("19. asyncio.run завершился")
        except KeyboardInterrupt:
            print("Бот остановлен пользователем")
            logger.info("Бот остановлен пользователем")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            logger.error(f"Критическая ошибка: {e}")
except ImportError:
    print("Ошибка при импорте aiogram или dotenv")
    logger.error("Ошибка при импорте aiogram или dotenv") 