import requests
import sys
import json

API_URL = "http://localhost:8000"

def test_login(email, password):
    """Тестирование аутентификации с указанными учетными данными"""
    login_url = f"{API_URL}/api/v1/login"
    
    # Создаем данные формы
    form_data = {
        "username": email,
        "password": password
    }
    
    print(f"Отправка запроса на {login_url}")
    print(f"Данные: {form_data}")
    
    try:
        # Отправляем запрос
        response = requests.post(
            login_url, 
            data=form_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Выводим статус и ответ
        print(f"Статус: {response.status_code}")
        try:
            print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Ответ (текст): {response.text}")
        
        # Возвращаем результат
        return response.status_code, response.text
    except Exception as e:
        print(f"Ошибка: {e}")
        return None, str(e)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        # Используем тестовые данные по умолчанию
        email = "admin@example.com"
        password = "admin"
    
    test_login(email, password) 