@echo off
chcp 65001 > nul
color 0A
title Запуск OFS-Photomatrix Backend

echo ╔════════════════════════════════════════╗
echo ║   ЗАПУСКАЕМ OFS-PHOTOMATRIX BACKEND    ║
echo ╚════════════════════════════════════════╝

:: Проверяем аргументы для специальных режимов
if "%1"=="reset" (
    echo Режим полного сброса активирован
    if exist "backend\.deps_installed" del /f /q "backend\.deps_installed"
    goto START_SCRIPT
)

:START_SCRIPT
echo [1] Проверяем окружение...
python --version
pip --version

echo [2] Останавливаем предыдущие процессы...

:: Найти и убить процессы uvicorn
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "uvicorn" > nul
    if not errorlevel 1 (
        echo     - Завершаем процесс uvicorn с PID: %%p
        taskkill /F /PID %%p > nul 2>&1
    )
)

:: Найти и убить процессы main.py
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "main.py" > nul
    if not errorlevel 1 (
        echo     - Завершаем процесс main.py с PID: %%p
        taskkill /F /PID %%p > nul 2>&1
    )
)

echo [3] Переходим в директорию бэкенда...
cd backend

echo [4] Проверяем зависимости...
if not exist ".deps_installed" (
    echo     - Зависимости не установлены! Устанавливаем...
    goto INSTALL
)

:START
echo [5] Запускаем бэкенд...
set PYTHONPATH=%cd%

:: Предварительное сообщение, что сервер готов
echo ╔════════════════════════════════════════╗
echo ║   СЕРВЕР ЗАПУЩЕН И ГОТОВ К РАБОТЕ      ║
echo ╚════════════════════════════════════════╝
echo.
echo * Документация API доступна по адресу: http://127.0.0.1:8000/docs
echo * Endpoint проверки работы:      http://127.0.0.1:8000/health
echo * Чтобы остановить сервер, нажмите Ctrl+C
echo.
echo Лог работы сервера:
echo -------------------------------------------------

:: Запускаем сервер с выводом в консоль
python main.py

if errorlevel 1 (
    cls
    color 0C
    echo ╔════════════════════════════════════════╗
    echo ║              ОШИБКА!                   ║
    echo ╚════════════════════════════════════════╝
    echo Произошла ошибка запуска. Проверьте ошибки выше.
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║           ВЫБЕРИТЕ ДЕЙСТВИЕ            ║
    echo ╚════════════════════════════════════════╝
    echo 1 - Переустановить зависимости и попробовать снова
    echo 2 - Выйти
    echo 3 - Полный сброс (удалить все зависимости и переустановить)
    choice /c 123 /n /m "Ваш выбор (1/2/3): "
    
    if errorlevel 3 (
        if exist ".deps_installed" del /f /q ".deps_installed"
        goto INSTALL
    )
    if errorlevel 2 goto END
    if errorlevel 1 goto INSTALL
)
goto END

:INSTALL
echo ╔════════════════════════════════════════╗
echo ║        УСТАНОВКА ЗАВИСИМОСТЕЙ          ║
echo ╚════════════════════════════════════════╝

echo [1] Обновляем pip...
python -m pip install --upgrade pip

echo [2] Устанавливаем основные зависимости...
pip install -r requirements.txt 2>nul

:: Если requirements.txt нет, пробуем через poetry
if errorlevel 1 (
    echo [3] Пробуем установить через poetry...
    pip install poetry 2>nul
    poetry install
)

:: Если и это не сработает, устанавливаем основные зависимости напрямую
if errorlevel 1 (
    echo [4] Устанавливаем необходимые пакеты напрямую...
    pip install fastapi uvicorn sqlalchemy asyncpg psycopg2 psycopg2-binary alembic email-validator "pydantic[email]" python-multipart python-jose[cryptography] passlib[bcrypt] requests jinja2 typing-extensions pydantic-settings tenacity
    
    :: Проверяем, что всё установилось
    echo [5] Проверяем установку модулей...
    pip list
)

:: Создаем файл-флаг, указывающий, что зависимости установлены
echo 1 > .deps_installed
echo Установка завершена!
color 0A
goto START

:END
echo Приложение завершило работу
pause 