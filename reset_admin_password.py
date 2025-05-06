import os
import psycopg2
from passlib.context import CryptContext

# Получаем параметры подключения из .env
DB_USER = os.getenv("DB_USER", "ofs_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "111")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ofs_photomatrix")

# Админский email
ADMIN_EMAIL = "admin@example.com"

# Пароль для сброса
NEW_PASSWORD = "admin"  # Если хотим установить пароль из .env

# Контекст для хеширования пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Получить хеш пароля"""
    return pwd_context.hash(password)

def reset_admin_password():
    """Сбрасывает пароль администратора на значение по умолчанию"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        
        # Создаем курсор
        cursor = conn.cursor()
        
        # Выводим информацию о подключении
        print("Информация о PostgreSQL:")
        print(conn.get_dsn_parameters(), "\n")
        
        # Получаем хеш нового пароля
        hashed_password = get_password_hash(NEW_PASSWORD)
        
        # Обновляем пароль для admin@example.com
        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE email = %s",
            (hashed_password, ADMIN_EMAIL)
        )
        
        # Фиксируем изменения
        conn.commit()
        
        # Проверяем, сколько строк было обновлено
        rows_updated = cursor.rowcount
        
        if rows_updated > 0:
            print(f"Пароль пользователя {ADMIN_EMAIL} успешно обновлен!")
            print(f"Новый пароль: {NEW_PASSWORD}")
        else:
            print(f"Пользователь {ADMIN_EMAIL} не найден в базе данных!")
        
    except Exception as e:
        print(f"Ошибка при работе с PostgreSQL: {e}")
    finally:
        # Закрываем соединение
        if conn:
            cursor.close()
            conn.close()
            print("\nСоединение с PostgreSQL закрыто")

if __name__ == "__main__":
    reset_admin_password() 