@echo off
chcp 65001 > nul
color 0A
title ЗАПУСК ПРОЕКТА OFS-PHOTOMATRIX

echo ╔════════════════════════════════════════════════════════════╗
echo ║          УНИВЕРСАЛЬНЫЙ ЗАПУСК OFS-PHOTOMATRIX               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Создаем папку logs, если её еще нет
if not exist "logs" mkdir logs

REM Очищаем старые лог-файлы
echo Очищаем старые логи...
if exist "logs\backend.log" del /q "logs\backend.log"
if exist "logs\frontend.log" del /q "logs\frontend.log"
if exist "logs\backend_error.log" del /q "logs\backend_error.log"
if exist "logs\frontend_error.log" del /q "logs\frontend_error.log"

REM Проверяем наличие основных директорий
if not exist "backend" (
    echo [ОШИБКА] Директория backend не найдена!
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ОШИБКА] Директория frontend не найдена!
    pause
    exit /b 1
)

REM =================== ПОДГОТОВКА BACKEND ======================

echo [1] Проверка и настройка бэкенда...

REM Проверяем наличие Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Python не установлен или не добавлен в PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do (
    echo [√] Python %%I
)

REM Проверка наличия корневого .env файла
if not exist ".env" (
    echo [!] Файл .env не найден, создаем с настройками по умолчанию...
    
    (
        echo # Общие настройки подключения к БД
        echo DATABASE_URL=postgresql+asyncpg://ofs_user:111@localhost:5432/ofs_photomatrix
        echo DB_USER=ofs_user
        echo DB_PASSWORD=111
        echo DB_HOST=localhost
        echo DB_PORT=5432
        echo DB_NAME=ofs_photomatrix
        echo DB_ENCODING=utf8
        echo.
        echo # Настройки API бэкенда
        echo API_URL=http://localhost:8000/api/v1
        echo API_KEY=test_api_key_1234567890
        echo SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
        echo.
        echo # Настройки логирования
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/app.log
        echo.
        echo # Настройки безопасности
        echo BACKEND_CORS_ORIGINS=["http://localhost:5173"]
    ) > .env
    
    echo [√] Файл .env создан
)

REM Убедимся, что все необходимые файлы инициализации существуют
if not exist "backend\app\api\__init__.py" (
    echo [!] Создаем файл backend\app\api\__init__.py
    echo # API package > backend\app\api\__init__.py
)

REM !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
REM !!! БОЛЬШЕ НЕ ПЕРЕЗАПИСЫВАЕМ __init__.py И api.py АВТОМАТИЧЕСКИ !!!
REM !!! Проверяем их наличие. Если их нет - используйте fix_backend.cmd !!!
REM !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo [i] Проверяем, что файлы __init__.py и api.py существуют...
if not exist "backend\app\api\endpoints\__init__.py" (
    echo [ОШИБКА] Файл backend\app\api\endpoints\__init__.py не найден! 
    echo Пожалуйста, восстановите его вручную или используйте fix_backend.cmd
    pause
    exit /b 1
)
if not exist "backend\app\api\api.py" (
    echo [ОШИБКА] Файл backend\app\api\api.py не найден! 
    echo Пожалуйста, восстановите его вручную или используйте fix_backend.cmd
    pause
    exit /b 1
)

REM Очищаем кэш Python
echo [!] Очистка кэша Python...
for /d /r "backend" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d"
)

REM =================== ПОДГОТОВКА FRONTEND ======================

echo [2] Проверка и настройка фронтенда...

REM Проверка наличия Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Node.js не установлен или не добавлен в PATH
    pause
    exit /b 1
)

for /f "tokens=1" %%n in ('node --version') do (
    echo [√] Node.js %%n
)

REM Проверка наличия package.json в директории frontend
if not exist "frontend\package.json" (
    echo [ОШИБКА] Файл frontend\package.json не найден!
    echo Проверьте структуру проекта.
    pause
    exit /b 1
)

REM =================== ЗАПУСК ПРОЕКТА ======================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ЗАПУСК ПРОЕКТА                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Создаем скрипт запуска бэкенда с отображением ошибок
echo @echo off > run_backend_persistent.cmd
echo chcp 65001 ^> nul >> run_backend_persistent.cmd
echo color 0B >> run_backend_persistent.cmd
echo title Бэкенд OFS-Photomatrix >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo cd backend >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo echo ===== ЗАПУСК БЭКЕНДА OFS-PHOTOMATRIX ===== >> run_backend_persistent.cmd
echo echo. >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo REM Активируем виртуальное окружение, если оно существует >> run_backend_persistent.cmd
echo if exist ".venv\Scripts\activate.bat" ( >> run_backend_persistent.cmd
echo     call .venv\Scripts\activate.bat >> run_backend_persistent.cmd
echo     echo [√] Виртуальное окружение .venv активировано >> run_backend_persistent.cmd
echo ) else if exist "venv\Scripts\activate.bat" ( >> run_backend_persistent.cmd
echo     call venv\Scripts\activate.bat >> run_backend_persistent.cmd
echo     echo [√] Виртуальное окружение venv активировано >> run_backend_persistent.cmd
echo ) else ( >> run_backend_persistent.cmd
echo     echo [!] Виртуальное окружение не найдено >> run_backend_persistent.cmd
echo     echo [!] Используем глобальный Python и устанавливаем зависимости, если нужно >> run_backend_persistent.cmd
echo     python -c "import fastapi, uvicorn, sqlalchemy, asyncpg" 2^>nul >> run_backend_persistent.cmd
echo     if %%ERRORLEVEL%% NEQ 0 ( >> run_backend_persistent.cmd
echo         echo [!] Устанавливаем необходимые зависимости глобально... >> run_backend_persistent.cmd
echo         pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary python-multipart python-jose[cryptography] passlib[bcrypt] pydantic pydantic-settings >> run_backend_persistent.cmd
echo     ) >> run_backend_persistent.cmd
echo ) >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo REM Запускаем сервер с перенаправлением вывода >> run_backend_persistent.cmd
echo echo [*] Запуск сервера... >> run_backend_persistent.cmd
echo echo [*] Логи сохраняются в ..\logs\backend.log >> run_backend_persistent.cmd
echo echo [*] Для завершения нажмите Ctrl+C >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo python main.py 2^>^> ..\logs\backend_error.log 1^>^> ..\logs\backend.log >> run_backend_persistent.cmd
echo. >> run_backend_persistent.cmd
echo echo [!] Сервер остановлен или произошла ошибка >> run_backend_persistent.cmd
echo echo [!] Проверьте логи ошибок в ..\logs\backend_error.log >> run_backend_persistent.cmd
echo pause >> run_backend_persistent.cmd

REM Создаем скрипт запуска фронтенда с отображением ошибок
echo @echo off > run_frontend_persistent.cmd
echo chcp 65001 ^> nul >> run_frontend_persistent.cmd
echo color 0A >> run_frontend_persistent.cmd
echo title Фронтенд OFS-Photomatrix >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo cd frontend >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo echo ===== ЗАПУСК ФРОНТЕНДА OFS-PHOTOMATRIX ===== >> run_frontend_persistent.cmd
echo echo. >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo if not exist "node_modules" ( >> run_frontend_persistent.cmd
echo     echo [!] Установка зависимостей npm... >> run_frontend_persistent.cmd
echo     call npm install >> run_frontend_persistent.cmd
echo ) >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo REM Запускаем фронтенд с перенаправлением вывода >> run_frontend_persistent.cmd
echo echo [*] Запуск сервера разработки... >> run_frontend_persistent.cmd
echo echo [*] Адрес: http://localhost:5173/ >> run_frontend_persistent.cmd
echo echo [*] Логи сохраняются в ..\logs\frontend.log >> run_frontend_persistent.cmd 
echo echo [*] Для завершения нажмите Ctrl+C >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo npm run dev 2^>^> ..\logs\frontend_error.log 1^>^> ..\logs\frontend.log >> run_frontend_persistent.cmd
echo. >> run_frontend_persistent.cmd
echo echo [!] Сервер остановлен или произошла ошибка >> run_frontend_persistent.cmd
echo echo [!] Проверьте логи ошибок в ..\logs\frontend_error.log >> run_frontend_persistent.cmd
echo pause >> run_frontend_persistent.cmd

REM Запускаем бэкенд и фронтенд в отдельных окнах
echo [3] Запуск проекта...
start "Бэкенд OFS-Photomatrix" cmd /c run_backend_persistent.cmd
echo [√] Бэкенд запущен в отдельном окне

echo [i] Ждем 5 секунд перед запуском фронтенда...
timeout /t 5 /nobreak > nul

start "Фронтенд OFS-Photomatrix" cmd /c run_frontend_persistent.cmd
echo [√] Фронтенд запущен в отдельном окне

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                     ПРОЕКТ ЗАПУЩЕН                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [i] Проект OFS-Photomatrix успешно запущен!
echo.
echo [i] ВАЖНО: Окна терминалов останутся открытыми даже в случае ошибок.
echo [i] Логи можно найти в директории logs:
echo     - logs\backend.log - стандартный вывод бэкенда
echo     - logs\backend_error.log - ошибки бэкенда
echo     - logs\frontend.log - стандартный вывод фронтенда
echo     - logs\frontend_error.log - ошибки фронтенда
echo.
echo [i] Для доступа к приложению откройте в браузере: http://localhost:5173/
echo.

REM Удаляем устаревшие скрипты (оставляем fix_backend.cmd на всякий случай)
echo [4] Очистка устаревших скриптов...

REM Список скриптов для удаления 
set "scripts_to_delete=fix_backend_env.cmd start_backend.cmd start_backend_with_env.cmd run_backend.cmd run_frontend.cmd start_project.cmd"

for %%s in (%scripts_to_delete%) do (
    if exist "%%s" (
        del "%%s"
        echo [√] Удален устаревший скрипт: %%s
    )
)

echo.
echo [i] Для завершения работы закройте все открытые окна терминалов
echo [i] или нажмите Ctrl+C в каждом из них.
echo.
pause 