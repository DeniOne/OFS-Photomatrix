@echo off 
chcp 65001 > nul 
color 0B 
title Бэкенд OFS-Photomatrix 
 
cd backend 
 
echo ===== ЗАПУСК БЭКЕНДА OFS-PHOTOMATRIX ===== 
echo. 
 
REM Активируем виртуальное окружение, если оно существует 
if exist ".venv\Scripts\activate.bat" ( 
    call .venv\Scripts\activate.bat 
    echo [√] Виртуальное окружение .venv активировано 
) else if exist "venv\Scripts\activate.bat" ( 
    call venv\Scripts\activate.bat 
    echo [√] Виртуальное окружение venv активировано 
) else ( 
    echo [!] Виртуальное окружение не найдено 
    echo [!] Используем глобальный Python и устанавливаем зависимости, если нужно 
    python -c "import fastapi, uvicorn, sqlalchemy, asyncpg" 2>nul 
    if %ERRORLEVEL% NEQ 0 ( 
        echo [!] Устанавливаем необходимые зависимости глобально... 
        pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary python-multipart python-jose[cryptography] passlib[bcrypt] pydantic pydantic-settings 
    ) 
) 
 
REM Запускаем сервер с перенаправлением вывода 
echo [*] Запуск сервера... 
echo [*] Логи сохраняются в ..\logs\backend.log 
echo [*] Для завершения нажмите Ctrl+C 
 
python main.py 2>> ..\logs\backend_error.log 1>> ..\logs\backend.log 
 
echo [!] Сервер остановлен или произошла ошибка 
echo [!] Проверьте логи ошибок в ..\logs\backend_error.log 
pause 
