@echo off
chcp 65001 > nul
color 0E
title Остановка проекта OFS-Photomatrix

echo ╔════════════════════════════════════════╗
echo ║    ОСТАНОВКА ПРОЕКТА OFS-PHOTOMATRIX   ║
echo ╚════════════════════════════════════════╝

echo [1] Останавливаем процессы бэкенда...

:: Найти и убить процессы uvicorn
set "found_backend=0"
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "uvicorn" > nul
    if not errorlevel 1 (
        echo     - Завершаем процесс uvicorn с PID: %%p
        taskkill /F /PID %%p > nul 2>&1
        set "found_backend=1"
    )
)

:: Найти и убить процессы main.py
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /i "python.exe"') do (
    wmic process %%p get commandline | find /i "main.py" > nul
    if not errorlevel 1 (
        echo     - Завершаем процесс main.py с PID: %%p
        taskkill /F /PID %%p > nul 2>&1
        set "found_backend=1"
    )
)

if "%found_backend%"=="0" (
    echo     - Процессы бэкенда не найдены
)

echo [2] Останавливаем процессы фронтенда...

:: Найти и убить процессы vite
set "found_frontend=0"
FOR /F "tokens=2" %%p in ('tasklist /FI "IMAGENAME eq node.exe" ^| find /i "node.exe"') do (
    wmic process %%p get commandline | find /i "vite" > nul
    if not errorlevel 1 (
        echo     - Завершаем процесс vite с PID: %%p
        taskkill /F /PID %%p > nul 2>&1
        set "found_frontend=1"
    )
)

if "%found_frontend%"=="0" (
    echo     - Процессы фронтенда не найдены
)

echo [3] Проверяем, освободились ли порты...

:: Проверяем порт бэкенда (8000)
netstat -ano | findstr 0.0.0.0:8000 > nul
if not errorlevel 1 (
    echo     - Внимание: порт 8000 (бэкенд) все еще занят
)

:: Проверяем порт фронтенда (5173)
netstat -ano | findstr 0.0.0.0:5173 > nul
if not errorlevel 1 (
    echo     - Внимание: порт 5173 (фронтенд) все еще занят
)

echo.
color 0A
echo ╔════════════════════════════════════════╗
echo ║     ПРОЕКТ OFS-PHOTOMATRIX ОСТАНОВЛЕН  ║
echo ╚════════════════════════════════════════╝
echo.

pause 