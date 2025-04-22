@echo off
chcp 65001 > nul
color 0A
title Запуск проекта OFS-Photomatrix

echo ╔════════════════════════════════════════╗
echo ║      ЗАПУСК ПРОЕКТА OFS-PHOTOMATRIX    ║
echo ╚════════════════════════════════════════╝
echo.

:: Проверяем наличие скрипта для бэкенда
if not exist "start_backend.cmd" (
    color 0C
    echo Ошибка: Файл start_backend.cmd не найден!
    echo Убедитесь, что он находится в той же папке, что и этот скрипт.
    goto END
)
echo [1] Запускаем бэкенд (start_backend.cmd) в новом окне...
start "OFS-Photomatrix Backend" cmd /c start_backend.cmd
echo    - Окно бэкенда запущено. Смотрите логи там.

echo [2] Запускаем фронтенд...
:: Проверяем папку frontend
if not exist "frontend" (
    color 0C
    echo Ошибка: Директория frontend не найдена!
    echo Убедитесь, что скрипт запущен из корневой папки проекта.
    goto END
)
:: Проверяем package.json
if not exist "frontend\package.json" (
    color 0C
    echo Ошибка: package.json не найден в папке frontend!
    goto END
)

:: Надежный запуск фронтенда
cd frontend
start "OFS-Photomatrix Frontend" cmd /k "npm run dev"
cd ..
echo    - Окно фронтенда запущено. Смотрите логи там.

echo.
echo [3] Пауза 5 секунд для инициализации серверов...
timeout /t 5 /nobreak > nul
echo.
echo ╔════════════════════════════════════════╗
echo ║        СЕРВЕРЫ ДОЛЖНЫ БЫТЬ ГОТОВЫ     ║
echo ╚════════════════════════════════════════╝
echo.
echo * Бэкенд (API Docs): http://127.0.0.1:8000/docs
echo * Фронтенд:         http://localhost:5173
echo.
echo Для остановки закройте окна серверов (Backend и Frontend) или нажмите Ctrl+C в них.
echo.
echo ╔════════════════════════════════════════╗
echo ║   СОВЕТЫ ПО ОПТИМИЗАЦИИ ПРОИЗВОДИТ.   ║
echo ╚════════════════════════════════════════╝
echo.
echo * Для ускорения загрузки фронтенда вы можете:
echo   1. Закрыть окно фронтенда
echo   2. Запустить скрипт frontend\clean-simple.ps1 отдельно
echo      (через PowerShell с флагом -ExecutionPolicy Bypass)
echo.

:END
pause
