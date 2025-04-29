@echo off
echo ===================================================
echo       Запуск Rocket.Chat для Photomatrix
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

echo [ИНФО] Запуск контейнеров Rocket.Chat...
echo Текущая директория: %SCRIPT_DIR%
echo.

docker-compose -f "%SCRIPT_DIR%docker-compose.yml" up -d

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Не удалось запустить контейнеры Rocket.Chat.
    echo.
    REM Проверим логи контейнеров
    echo Вывод логов последнего запуска:
    docker-compose -f "%SCRIPT_DIR%docker-compose.yml" logs --tail=50
    echo.
    pause
    exit /b 1
)

echo.
echo [УСПЕХ] Контейнеры Rocket.Chat успешно запущены!
echo.
echo Проверка статуса контейнеров:
docker-compose -f "%SCRIPT_DIR%docker-compose.yml" ps
echo.
echo Rocket.Chat доступен по адресу: http://localhost:3333
echo.
echo Учетные данные по умолчанию:
echo   Логин: admin
echo   Пароль: photomatrix2024
echo.
echo [!] ВАЖНО: Рекомендуется сменить пароль администратора после первого входа.
echo.
echo Для просмотра логов используйте команду:
echo docker-compose -f "%SCRIPT_DIR%docker-compose.yml" logs -f
echo.

REM Ожидание нажатия клавиши перед выходом
pause 