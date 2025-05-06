import os
import sys
import uvicorn
from fastapi import FastAPI, APIRouter

# Добавляем путь для импортов относительно backend
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Создаем базовое приложение FastAPI
app = FastAPI(
    title="OFS Photomatrix - Simple Server",
    description="Упрощенный сервер для проверки работоспособности",
    version="0.1.0",
)

# Создаем роутер для API
router = APIRouter()

@router.get("/")
async def root():
    """Корневой endpoint для проверки работоспособности"""
    return {"status": "ok", "message": "Сервер работает!"}

@router.get("/check-imports")
async def check_imports():
    """Проверка импортов основных модулей"""
    result = {"imports": {}}
    # Список модулей для проверки
    modules_to_check = [
        "fastapi", "uvicorn", "sqlalchemy", "asyncpg", 
        "pydantic", "jose", "passlib", "python-multipart"
    ]
    # Проверяем каждый модуль
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            result["imports"][module_name] = "ok"
        except ImportError as e:
            result["imports"][module_name] = f"error: {str(e)}"
    # Добавляем пути импорта
    result["sys_path"] = sys.path
    return result

# Подключаем роутер к приложению
app.include_router(router, prefix="/api")

# Точка входа для запуска сервера
if __name__ == "__main__":
    print("Запуск упрощенного сервера FastAPI...")
    print(f"Python: {sys.executable}")
    print(f"Sys.path: {sys.path}")
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8000, reload=True)
