@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo =            ЗАПУСК ОФС ФОТОМАТРИКС          =
echo ===============================================

REM Проверка наличия корневого .env файла
if not exist ".env" (
    echo [!] Корневой .env файл не найден
    echo [!] Создаю файл .env с настройками по умолчанию...
    
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
        echo # Настройки для бота Telegram
        echo BOT_TOKEN=ваш_токен_бота
        echo ADMIN_IDS=ваш_telegram_id
        echo STORAGE_PATH=./data
        echo.
        echo # Настройки логирования
        echo LOG_LEVEL=INFO
        echo LOG_FILE=app.log
    ) > .env
    
    echo [i] Создан файл .env с настройками по умолчанию
    echo [!] ВНИМАНИЕ: Необходимо отредактировать файл .env и указать правильные настройки
    pause
)

REM Синхронизируем данные из БД в JSON
echo [i] Синхронизация данных из БД...
cd telegram_bot
if exist "sync_db.bat" (
    call sync_db.bat
) else (
    python -c "from sync_db import sync_all_data; sync_all_data()"
)
cd ..

REM Запускаем бэкенд в отдельном окне cmd
echo [i] Запуск бэкенда...
start "ОФС Фотоматрикс - Бэкенд" cmd /c "cd backend && python main.py"

REM Запускаем фронтенд в отдельном окне cmd, если доступен
if exist "frontend/package.json" (
    echo [i] Запуск фронтенда...
    start "ОФС Фотоматрикс - Фронтенд" cmd /c "cd frontend && npm run dev"
)

REM Запускаем телеграм-бот в текущем окне
echo [i] Запуск Telegram бота...
cd telegram_bot
python bot.py

echo.
echo [+] Все компоненты успешно запущены!
echo [i] Для завершения работы закройте все открытые окна cmd.
pause
