import uvicorn
import logging
import os
import sys
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles  # Импорт для статических файлов

# Добавляем корневую директорию проекта в путь импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir.endswith('backend'):
    # Если запуск из backend, добавляем родительскую директорию
    sys.path.append(os.path.dirname(current_dir))
    # Используем относительные импорты
    from app.api.api import api_router
    from app.core.logging import setup_logging, api_logger
else:
    # Если запуск из корня проекта
    from backend.app.api.api import api_router
    from backend.app.core.logging import setup_logging, api_logger

# Инициализация логгера
logger = setup_logging()

# Создание приложения FastAPI
app = FastAPI(
    title="OFS Photomatrix",
    description="Organizational Framework System",
    version="0.1.0",
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Получаем информацию о запросе
    start_time = time.time()
    method = request.method
    url = request.url.path
    client_host = request.client.host if request.client else "unknown"
    
    api_logger.info(f"Запрос: {method} {url} от {client_host}")
    
    try:
        # Выполняем запрос
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Логируем ответ
        api_logger.info(f"Ответ на {method} {url}: статус {response.status_code}, время {process_time:.2f}ms")
        
        return response
    except Exception as e:
        # Логируем ошибки
        api_logger.error(f"Ошибка при обработке {method} {url}: {str(e)}")
        raise

# Настройка CORS - РАЗРЕШАЕМ ВСЁ ДЛЯ ОТЛАДКИ!
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
    "http://localhost",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1",
    "*",  # Все источники (для отладки)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"],  # Делаем видимыми все заголовки для JS
    max_age=86400,  # Увеличиваем время кэширования preflight запросов (24 часа)
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")

# Настройка статических файлов
uploads_dir = os.path.join(os.getcwd(), "uploads")
if os.path.exists(uploads_dir):
    logger.info(f"Монтирование директории статических файлов: {uploads_dir}")
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
else:
    logger.warning(f"Директория для загрузок не найдена: {uploads_dir}")

@app.get("/")
async def root():
    logger.info("Запрос к корневому эндпоинту /")
    return {"message": "OFS Photomatrix API"}

@app.get("/health")
async def health_check():
    logger.info("Проверка здоровья системы")
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info("Запуск сервера через точку входа main.py")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 