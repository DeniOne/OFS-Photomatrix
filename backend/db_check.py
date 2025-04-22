import sqlite3

def main():
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Проверяем организации
        cursor.execute('SELECT id, name FROM organizations')
        print('Организации:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # Проверяем подразделения
        cursor.execute('SELECT id, name, parent_id, organization_id FROM divisions')
        print('\nПодразделения:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]} (Родитель: {row[2]}, Организация: {row[3]})')
        
        conn.close()
        print("\nУспешно получены данные из базы")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main() 