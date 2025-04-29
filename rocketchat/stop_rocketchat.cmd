@echo off
echo ===================================================
echo       Остановка Rocket.Chat для Photomatrix
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

echo [ИНФО] Остановка контейнеров Rocket.Chat...
echo Текущая директория: %SCRIPT_DIR%
echo.

docker-compose -f "%SCRIPT_DIR%docker-compose.yml" down

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Не удалось остановить контейнеры Rocket.Chat.
    echo.
    pause
    exit /b 1
)

echo.
echo [УСПЕХ] Контейнеры Rocket.Chat успешно остановлены!
echo.

REM Ожидание нажатия клавиши перед выходом
pause 