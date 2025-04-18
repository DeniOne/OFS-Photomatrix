@echo off
chcp 65001 > nul

echo Останавливаю предыдущие процессы...

:: Найти и убить процессы uvicorn
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "uvicorn" > nul
    if not errorlevel 1 (
        echo Завершаю процесс uvicorn с PID: %%p
        taskkill /F /PID %%p
    )
)

:: Найти и убить процессы main.py
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "main.py" > nul
    if not errorlevel 1 (
        echo Завершаю процесс main.py с PID: %%p
        taskkill /F /PID %%p
    )
)

echo Переходим в директорию бэкенда...
cd backend

:: Проверяем зависимости
if not exist ".deps_installed" (
    echo Зависимости не установлены! Запустите install_backend.cmd из корня проекта
    pause
    exit /b 1
)

echo Запускаю бэкенд...
set PYTHONPATH=%cd%
python main.py
if errorlevel 1 (
    echo Ошибка запуска приложения!
    echo Возможно не хватает зависимостей. Запустите install_backend.cmd из корня проекта.
    pause
    exit /b %errorlevel%
) 