import sqlite3

def check_tables():
    """Проверяет существующие таблицы в базе данных"""
    try:
        # Подключаемся к БД
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Таблицы в базе данных:")
        for table in tables:
            print(f" - {table[0]}")
            
            # Для каждой таблицы получаем информацию о столбцах
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            
            print("   Столбцы:")
            for col in columns:
                print(f"     {col[1]}: {col[2]} (NULL: {col[3]}, Default: {col[4]})")
            print("")
            
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_tables() 