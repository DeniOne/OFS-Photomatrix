import os
import psycopg2

# Получаем параметры подключения из .env
DB_USER = os.getenv("DB_USER", "ofs_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "111")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ofs_photomatrix")

def check_users():
    """Проверяет пользователей в базе данных"""
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
        
        # Выполняем запрос для получения пользователей
        cursor.execute("SELECT id, email, is_active, is_superuser, hashed_password FROM users")
        
        # Получаем все строки
        users = cursor.fetchall()
        
        # Выводим результаты
        print("Список пользователей в базе данных:")
        print("-" * 80)
        if users:
            for user in users:
                user_id, email, is_active, is_superuser, hashed_password = user
                print(f"ID: {user_id}")
                print(f"Email: {email}")
                print(f"Активен: {is_active}")
                print(f"Суперпользователь: {is_superuser}")
                print(f"Пароль установлен: {'Да' if hashed_password else 'Нет'}")
                print("-" * 80)
        else:
            print("Пользователи не найдены в базе данных!")
        
        # Проверим суперпользователя из .env
        first_superuser = os.getenv("FIRST_SUPERUSER", "admin@example.com")
        first_superuser_password = os.getenv("FIRST_SUPERUSER_PASSWORD", "adminadmin")
        
        print(f"\nСуперпользователь из .env:")
        print(f"Email: {first_superuser}")
        print(f"Пароль: {first_superuser_password}")
        
    except Exception as e:
        print(f"Ошибка при работе с PostgreSQL: {e}")
    finally:
        # Закрываем соединение
        if conn:
            cursor.close()
            conn.close()
            print("\nСоединение с PostgreSQL закрыто")

if __name__ == "__main__":
    check_users() 