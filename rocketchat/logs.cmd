@echo off
echo ===================================================
echo       Просмотр логов Rocket.Chat
echo ===================================================
echo.

REM Проверка, установлен ли Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Docker не установлен или не найден в PATH.
    echo Пожалуйста, установите Docker Desktop с сайта https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

REM Проверка, запущен ли Docker
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Docker не запущен. Пожалуйста, запустите Docker Desktop.
    echo.
    pause
    exit /b 1
)

REM Получение текущей директории скрипта
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

echo [ИНФО] Просмотр логов Rocket.Chat...
echo Текущая директория: %SCRIPT_DIR%
echo.
echo Для выхода из режима просмотра логов нажмите Ctrl+C
echo.
echo Ожидайте...
echo.

docker-compose -f "%SCRIPT_DIR%docker-compose.yml" logs -f

REM Скрипт не дойдет до этой точки пока пользователь не нажмет Ctrl+C
echo.
echo [ИНФО] Просмотр логов завершен.
echo.

REM Ожидание нажатия клавиши перед выходом
pause 