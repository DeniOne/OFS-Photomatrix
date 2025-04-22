import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from fastapi import FastAPI, Request
import time
import os
from app.core.logging import setup_logging, api_logger

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники для отладки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Добавляем специальное middleware для добавления CORS-заголовков вручную (ЗАКОММЕНТИРОВАНО - может конфликтовать)
# @app.middleware("http")
# async def add_cors_headers(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     return response

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    logger.info("Запрос к корневому эндпоинту /")
    return {"message": "OFS Photomatrix API"}

@app.get("/health")
async def health_check():
    logger.info("Проверка здоровья системы")
    return {"status": "ok"}

# Обработчик OPTIONS-запросов для preflight CORS
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    return {}

if __name__ == "__main__":
    logger.info("Запуск сервера через точку входа main.py")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 