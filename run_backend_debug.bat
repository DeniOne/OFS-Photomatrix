@echo off
echo === Запуск бэкенда в режиме отладки ===
cd backend
echo Текущая директория: %CD%

echo Удаляем orgchart.py, если он существует...
if exist app\api\endpoints\orgchart.py (
    rename app\api\endpoints\orgchart.py orgchart.py.bak
    echo Файл переименован в orgchart.py.bak
)

echo Восстанавливаем исходное состояние api.py...
echo from fastapi import APIRouter> app\api\api.py.new
echo.>> app\api\api.py.new
echo from app.api.endpoints import (>> app\api\api.py.new
echo     login,>> app\api\api.py.new
echo     users,>> app\api\api.py.new
echo     divisions,>> app\api\api.py.new
echo     organizations,>> app\api\api.py.new
echo     positions,>> app\api\api.py.new
echo     staff,>> app\api\api.py.new
echo     value_products,>> app\api\api.py.new
echo     functions>> app\api\api.py.new
echo )>> app\api\api.py.new
echo import logging>> app\api\api.py.new
echo.>> app\api\api.py.new
echo logger = logging.getLogger(__name__)>> app\api\api.py.new
echo.>> app\api\api.py.new
echo api_router = APIRouter()>> app\api\api.py.new
echo api_router.include_router(login.router, tags=["login"])>> app\api\api.py.new
echo api_router.include_router(users.router, prefix="/users", tags=["users"])>> app\api\api.py.new
echo api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])>> app\api\api.py.new
echo api_router.include_router(divisions.router, prefix="/divisions", tags=["divisions"])>> app\api\api.py.new
echo api_router.include_router(positions.router, prefix="/positions", tags=["positions"])>> app\api\api.py.new
echo api_router.include_router(staff.router, prefix="/staff", tags=["staff"])>> app\api\api.py.new
echo api_router.include_router(value_products.router, prefix="/value_products", tags=["value_products"])>> app\api\api.py.new
echo api_router.include_router(functions.router, prefix="/functions", tags=["functions"])>> app\api\api.py.new
echo.>> app\api\api.py.new
echo logger.info("API роутеры настроены")>> app\api\api.py.new

move /y app\api\api.py.new app\api\api.py
echo Файл api.py восстановлен

echo Запускаем бэкенд с выводом ошибок...
python -c "import traceback; from app.main import app; print('Бэкенд запущен успешно!')" 2> error.log

if %ERRORLEVEL% NEQ 0 (
    echo Ошибка при запуске бэкенда! Детали:
    type error.log
) else (
    echo Бэкенд успешно инициализирован
    echo Запускаем HTTP сервер...
    uvicorn app.main:app --reload --port 8000
)

echo === Завершение работы ===
pause 