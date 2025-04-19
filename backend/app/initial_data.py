import asyncio
import logging

from app.db.base import async_session_maker # Импортируем async_session_maker
from app.crud import user as crud_user
from app.schemas.user import UserCreate
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_first_superuser() -> None:
    """Создает первого суперпользователя, если он еще не существует."""
    logger.info("Проверка наличия первого суперпользователя...")
    email = settings.FIRST_SUPERUSER
    password = settings.FIRST_SUPERUSER_PASSWORD

    # Используем async_session_maker как контекстный менеджер
    async with async_session_maker() as db:
        user = await crud_user.get_by_email(db=db, email=email)
        if user:
            logger.info(f"Суперпользователь с email {email} уже существует. Пропуск создания.")
        else:
            logger.info(f"Создание суперпользователя с email: {email}")
            # Предполагаем, что UserCreate ожидает email, password, full_name
            # Убедись, что твоя схема UserCreate именно такая
            user_in = UserCreate(
                email=email,
                password=password,
                full_name="Admin",
                # is_active по умолчанию True в схеме, если она есть
            )
            try:
                new_user = await crud_user.create(db=db, obj_in=user_in)
                # Явно устанавливаем флаг суперпользователя после создания
                new_user.is_superuser = True
                db.add(new_user) # Добавляем объект в сессию для обновления
                # commit будет вызван автоматически контекстным менеджером get_db,
                # но так как мы используем session_maker напрямую, нужен commit здесь
                await db.commit()
                logger.info(f"Суперпользователь {email} успешно создан.")
            except Exception as e:
                logger.error(f"Ошибка при создании суперпользователя: {e}")
                await db.rollback() # Откатываем транзакцию в случае ошибки

async def main() -> None:
    logger.info("Запуск скрипта инициализации данных...")
    await create_first_superuser()
    logger.info("Скрипт инициализации данных завершен.")

if __name__ == "__main__":
    asyncio.run(main()) 