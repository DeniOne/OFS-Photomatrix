import sqlite3
import os
import sys

def add_admin_to_db(telegram_id, full_name="Админ", permission_level=2):
    """Добавляет новую запись администратора в базу данных"""
    
    # Путь к базе данных
    db_path = os.path.join("..", "data", "bot_data.db")
    
    if not os.path.exists(db_path):
        print(f"Ошибка: База данных не найдена по пути {db_path}")
        return False
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли уже такой админ
        cursor.execute("SELECT * FROM admins WHERE telegram_id = ?", (telegram_id,))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            # Обновляем существующего админа
            cursor.execute("""
                UPDATE admins 
                SET full_name = ?, permission_level = ?, is_active = 1
                WHERE telegram_id = ?
            """, (full_name, permission_level, telegram_id))
            print(f"Админ с ID {telegram_id} обновлён")
        else:
            # Добавляем нового админа
            cursor.execute("""
                INSERT INTO admins (telegram_id, full_name, permission_level, is_active)
                VALUES (?, ?, ?, 1)
            """, (telegram_id, full_name, permission_level))
            print(f"Админ с ID {telegram_id} добавлен")
        
        # Сохраняем изменения
        conn.commit()
        print("Операция выполнена успешно!")
        return True
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False
    
    finally:
        # Закрываем соединение с базой данных
        if conn:
            conn.close()

if __name__ == "__main__":
    # Получаем аргументы командной строки
    if len(sys.argv) < 2:
        print("Использование: python add_admin.py <telegram_id> [имя] [уровень_доступа]")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    full_name = sys.argv[2] if len(sys.argv) > 2 else "Админ"
    
    try:
        permission_level = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    except ValueError:
        print("Ошибка: уровень доступа должен быть числом (1 или 2)")
        sys.exit(1)
    
    add_admin_to_db(telegram_id, full_name, permission_level) 