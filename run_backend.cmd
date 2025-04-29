@echo off
setlocal EnableDelayedExpansion

echo ===============================================
echo =          ЗАПУСК BACKEND ПРИЛОЖЕНИЯ         =
echo ===============================================

REM Проверка наличия Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python не установлен или не добавлен в PATH
    echo [!] Пожалуйста, установите Python версии 3.8 или выше
    pause
    exit /b 1
)

REM Проверяем версию Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo [i] Обнаружен Python %PYTHON_VERSION%

REM Проверяем наличие корневого .env файла
if not exist "..\\.env" (
    echo [!] Корневой .env файл не найден
    echo [!] Создайте .env файл в корне проекта с необходимыми настройками
    pause
    exit /b 1
)

REM Переходим в директорию backend
cd /d "%~dp0"

REM Активируем виртуальное окружение, если оно существует
if exist ".venv\Scripts\activate.bat" (
    echo [i] Активация виртуального окружения (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [i] Активация виртуального окружения (venv)...
    call venv\Scripts\activate.bat
)

REM Проверяем, установлены ли зависимости
if not exist ".deps_installed" (
    echo [i] Зависимости не установлены. Устанавливаем...
    
    REM Пробуем использовать и pip, и poetry для установки зависимостей
    
    REM Сначала попробуем poetry
    where poetry >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [i] Установка зависимостей с помощью Poetry...
        poetry install
        if %ERRORLEVEL% EQU 0 (
            echo [+] Зависимости успешно установлены с помощью Poetry
            echo 1 > .deps_installed
        ) else (
            echo [!] Ошибка при установке зависимостей с помощью Poetry
        )
    ) else (
        echo [i] Poetry не найден, используем pip...
        
        REM Если есть requirements.txt, используем его
        if exist "requirements.txt" (
            python -m pip install -r requirements.txt
            if %ERRORLEVEL% EQU 0 (
                echo [+] Зависимости успешно установлены с помощью pip
                echo 1 > .deps_installed
            ) else (
                echo [!] Ошибка при установке зависимостей с помощью pip
            )
        ) else (
            echo [!] Файл requirements.txt не найден, установка зависимостей невозможна
        )
    )
)

REM Проверка, были ли установлены зависимости
if not exist ".deps_installed" (
    echo [!] Не удалось установить зависимости. Запуск приложения невозможен.
    pause
    exit /b 1
)

REM Запуск приложения
echo [i] Запуск backend-приложения...
echo.

REM Запускаем без перенаправления вывода, чтобы видеть ошибки
python main.py

REM Перенаправление вывода в логи (альтернативный вариант)
REM python main.py > ..\backend_output.log 2> ..\backend_errors.log

echo.
if %ERRORLEVEL% EQU 0 (
    echo [+] Приложение успешно запущено
) else (
    echo [!] Ошибка при запуске приложения (код %ERRORLEVEL%)
)

echo.
echo [i] Для выхода нажмите Ctrl+C
pause 